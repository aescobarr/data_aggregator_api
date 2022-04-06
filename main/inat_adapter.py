from main.data_adapters import BaseAdapter
import datetime
from dateutil import parser
from django.contrib.gis.geos import GEOSGeometry
from main.models import Observation, Region
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
            taxon = raw_obs['taxon']
            if taxon is not None:
                species_id = taxon['name']
            else:
                species_id = 'Unknown'
        except KeyError:
            species_id = 'Unknown'
        native_id = raw_obs['id']
        original_url = raw_obs['uri']
        updated_at = raw_obs['updated_at']
        picture_url = None
        if len(raw_obs['photos']) > 0:
            picture_url = raw_obs['photos'][0]['url'].replace("square","medium")
        observation_time_string = raw_obs['observed_on']
        if raw_obs['time_observed_at'] is None:
            observation_time = None
            observation_date = None
        else:
            observation_time = parser.parse(raw_obs['time_observed_at'])
            observation_date = parser.parse(raw_obs['observed_on'])

        wkt_point = 'POINT( {0} {1} )'

        lat = None
        lon = None
        try:
            geojson = raw_obs['geojson']
            if geojson is not None:
                lat = geojson['coordinates'][1]
                lon = geojson['coordinates'][0]
        except KeyError:
            pass

        region = None
        if lat is None or lon is None:
            location = None
        else:
            location = GEOSGeometry(wkt_point.format(lon, lat), srid=4326)
            countries = Region.objects.filter(geom__contains=location)
            if countries.exists():
                region = countries.first()

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
            observation_date = observation_date,
            observation_updated_at = updated_at,
            region = region
        )
        return o

    # def hydrate_all(self):
    #     hydrated = []
    #     data = self.read_raw_data()
    #     max_id = None
    #     min_id = None
    #     for raw_obs in data:
    #         obs = self.hydrate(raw_obs)
    #         if max_id is None or obs.native_id > max_id:
    #             max_id = obs.native_id
    #         if min_id is None or obs.native_id < min_id:
    #             min_id = obs.native_id
    #         hydrated.append(obs)
    #     if max_id is not None:
    #         self.load_event.max_id = max_id
    #         self.load_event.min_id = min_id
    #         self.load_event.save()
    #     return hydrated

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
        original.observation_updated_at = new_o.observation_updated_at
        return original

    def load_raw_from_source(self, params):
        base_event_folder = proj_path + "{0}/".format(self.load_event.origin)
        load_event_folder = base_event_folder + "{0}".format(str(self.load_event.id))

        total_records = 0
        total_pulled = 0
        project_url = None
        try:
            os.mkdir(base_event_folder)
        except FileExistsError:
            pass
        try:
            os.mkdir(load_event_folder)
        except FileExistsError:
            pass

        default_params = {
            'page': 1,
            'per_page': 100,
            'order_by': 'created_at',
            'order': 'desc',
            'project_id': None,
            'geo': True,
            'photos': True,
            'd1': None,
            'd2': None,
            'updated_since': None,
            'pause': 10,
            'page_limit': None
        }

        merged_params = {**default_params, **params }

        chunks = []
        endloop = False
        counter = 0
        total_pulled = 0
        page_limit = merged_params['page_limit']
        pause = merged_params['pause']
        for key, value in dict(merged_params).items():
            if value is None:
                del merged_params[key]
        del merged_params['pause']
        while not endloop:
            page = counter + 1
            merged_params['page'] = page
            project_url = settings.INAT_API_BASE_URL + 'observations/' + '?' + urlencode(merged_params)
            response = requests.get(project_url)
            print("Obtaining page number " + str(page))
            if response.status_code == 200:
                counter = counter + 1
                print("Page " + str(page) + " obtained succesfully")
                pulled_data = json.loads(response.content.decode('utf-8'))
                total_records = pulled_data['total_results']
                if len(pulled_data['results']) == 0:
                    print("Pulled no records, stopping download")
                    endloop = True
                else:
                    total_pulled += len(pulled_data['results'])
                    filename = '{0}.json'.format(str(page))
                    with open(load_event_folder + "/" + filename, 'w') as outfile:
                        json.dump(pulled_data['results'], outfile)
                    chunks.append(load_event_folder + "/" + filename)
                    if page_limit is not None and page == page_limit:
                        print("Pulled {0} records, {1} accumulated of total {2} records, reached page limit, stopping download".format(len(pulled_data['results']), total_pulled, total_records))
                        endloop = True
                    else:
                        print("Pulled {0} records, {1} accumulated of total {2} records, resuming download".format(len(pulled_data['results']),total_pulled, total_records))
            else:
                print("Failed to obtain records from page " + str(page))
            if not endloop:
                print("Now waiting {0} seconds...".format(pause))
                time.sleep(pause)
        self.load_event.event_finish = datetime.datetime.now()
        self.load_event.data_chunks = json.dumps(chunks)
        self.load_event.url_used = project_url
        self.load_event.n_records_origin = total_records
        self.load_event.n_records_pulled = total_pulled
        self.load_event.save()
