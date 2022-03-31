from main.data_adapters import BaseAdapter
import datetime
from dateutil import parser
from django.contrib.gis.geos import GEOSGeometry
from main.models import Observation
import json
import os
import requests
import time
from urllib.parse import urlencode
from data_aggregator_api import settings

proj_path = str(settings.BASE_DIR) + "/"


class InatAdapter(BaseAdapter):
    def __init__(self, origin, load_event=None):
        BaseAdapter.__init__(self, origin, load_event)

    def hydrate(self, raw_obs):
        origin = self.origin
        try:
            species_guess = raw_obs['species_guess']
        except KeyError:
            species_guess = 'Unknown'
        try:
            species_id = raw_obs['taxon']['name']
        except KeyError:
            species_id = 'Unknown'
        native_id = raw_obs['id']
        original_url = raw_obs['uri']
        picture_url = None
        if len(raw_obs['photos']) > 0:
            picture_url = raw_obs['photos'][0]['medium_url']
        observation_time_string = raw_obs['observed_on']
        if raw_obs['time_observed_at'] is None:
            observation_time = None
            observation_date = None
        else:
            observation_time = parser.parse(raw_obs['time_observed_at'])
            observation_date = parser.parse(raw_obs['observed_on'])

        wkt_point = 'POINT( {0} {1} )'
        lat = raw_obs['latitude']
        lon = raw_obs['longitude']
        if lat is None or lon is None:
            location = None
        else:
            location = GEOSGeometry(wkt_point.format(lon, lat), srid=4326)

        o = Observation(
            species_guess = species_guess,
            species_id = species_id,
            original_url = original_url,
            picture_url = picture_url,
            observation_time_string = observation_time_string,
            observation_time = observation_time,
            origin = origin,
            location = location,
            native_id = native_id,
            load_event = self.load_event,
            observation_date = observation_date
        )
        return o

    def copy(self, original, raw_obs):
        new_o = self.hydrate(raw_obs)
        original.species_guess = new_o.species_guess
        original.species_id = new_o.species_id
        original.original_url = new_o.original_url
        original.picture_url = new_o.picture_url
        original.observation_time_string = new_o.observation_time_string
        original.observation_time = new_o.observation_time
        original.origin = new_o.origin
        original.location = new_o.location
        original.native_id = new_o.native_id
        original.load_event = new_o.load_event
        original.observation_date = new_o.observation_date
        return original

    def load_raw_from_source(self, params):
        base_event_folder = proj_path + "{0}/".format(self.load_event.origin)
        load_event_folder = base_event_folder + "{0}".format(str(self.load_event.id))
        try:
            os.mkdir(base_event_folder)
        except FileExistsError:
            pass
        try:
            os.mkdir(load_event_folder)
        except FileExistsError:
            pass

        default_params = {
            'records_per_page': 200,
            'pause': 5,
            'filter_date': None
        }
        merged_params = {**default_params, **params }

        records_per_page = merged_params['records_per_page']
        project_slug = merged_params['project_slug']
        pause = merged_params['pause']
        filter_date = merged_params['filter_date']

        chunks = []
        endloop = False
        counter = 0
        total_pulled = 0
        while not endloop:
            page = counter + 1
            params = {
                'page': page,
                'per_page': records_per_page,
                'order_by': 'date_added',
                'order': 'desc'
            }
            if filter_date is not None:
                params['updated_since'] = filter_date
            project_url = settings.INAT_API_BASE_URL + '/observations/project/{0}.json'.format(project_slug) + '?' + urlencode(params)
            response = requests.get(project_url)
            print("Obtaining page number " + str(page))
            if response.status_code == 200:
                counter = counter + 1
                try:
                    total_records = response.headers['X-Total-Entries']
                except KeyError:
                    total_records = 'unknown'
                print("Page " + str(page) + " obtained succesfully")
                pulled_data = json.loads(response.content.decode('utf-8'))
                if len(pulled_data) == 0:
                    print("Pulled no records, stopping download")
                    endloop = True
                else:
                    total_pulled += len(pulled_data)
                    filename = '{0}.json'.format(str(page))
                    with open(load_event_folder + "/" + filename, 'w') as outfile:
                        json.dump(pulled_data, outfile)
                    chunks.append(load_event_folder + "/" + filename)
                    print("Pulled {0} records, {1} accumulated of total {2} records, resuming download".format(len(pulled_data),total_pulled, total_records))
            else:
                print("Failed to obtain records from page " + str(page))
            if not endloop:
                print("Now waiting {0} seconds...".format(pause))
                time.sleep(pause)
        self.load_event.event_finish = datetime.datetime.now()
        self.load_event.data_chunks = json.dumps(chunks)
        self.load_event.save()
