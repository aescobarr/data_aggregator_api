import datetime
from dateutil import parser
from main.models import Observation
from django.contrib.gis.geos import GEOSGeometry
from urllib.parse import urlencode
import requests
import json
import time
from data_aggregator_api import settings
from main.models import LoadEvent


# species = models.TextField('Observed species',null=True, blank=True)
# original_url = models.URLField('Original url of the observation, if available',null=True,blank=True)
# picture_url = models.URLField('Observation picture',null=True,blank=True)
# observation_time_string = models.CharField('Observation date in string format', max_length=500, null=True, blank=True)
# observation_time = models.DateTimeField('Observation date',null=True,blank=True)
# record_creation_time = models.DateTimeField(auto_now_add=True)
# origin = models.TextField('Source of the original observation',null=True, blank=True)
# native_id = models.TextField('Id of the observation in its native app',null=True, blank=True)

class BaseAdapter:
    def __init__(self, origin):
        self.origin = origin
        l = LoadEvent(origin=origin)
        l.save()
        self.load_event = l

    def hydrate(self, raw_obs):
        pass

    def hydrate_all(self, all_raw_obs):
        pass

    def copy(self, original, raw_obs):
        pass

    def load_raw_from_source(self, params):
        pass


class InatAdapter(BaseAdapter):
    def __init__(self, origin):
        BaseAdapter.__init__(self, origin)

    def hydrate_all(self, all_raw_obs):
        hydrated = []
        for raw_obs in all_raw_obs:
            hydrated.append( self.hydrate(raw_obs) )
        return hydrated

    def hydrate(self, raw_obs):
        origin = self.origin
        try:
            species = raw_obs['taxon']['name']
        except KeyError:
            species = 'Unknown'
        native_id = raw_obs['id']
        original_url = raw_obs['uri']
        picture_url = None
        if len(raw_obs['photos']) > 0:
            picture_url = raw_obs['photos'][0]['medium_url']
        observation_time_string = raw_obs['observed_on']
        if raw_obs['time_observed_at'] is None:
            observation_time = None
        else:
            observation_time = parser.parse(raw_obs['time_observed_at'])

        wkt_point = 'POINT( {0} {1} )'
        lat = raw_obs['latitude']
        lon = raw_obs['longitude']
        if lat is None or lon is None:
            location = None
        else:
            location = GEOSGeometry(wkt_point.format(lon, lat), srid=4326)

        o = Observation(
            species = species,
            original_url = original_url,
            picture_url = picture_url,
            observation_time_string = observation_time_string,
            observation_time = observation_time,
            origin = origin,
            location = location,
            native_id = native_id,
            load_event = self.load_event
        )
        return o

    def copy(self, original, raw_obs):
        new_o = self.hydrate(raw_obs)
        original.species = new_o.species
        original.original_url = new_o.original_url
        original.picture_url = new_o.picture_url
        original.observation_time_string = new_o.observation_time_string
        original.observation_time = new_o.observation_time
        original.origin = new_o.origin
        original.location = new_o.location
        original.native_id = new_o.native_id
        original.load_event = new_o.load_event
        return original

    def load_raw_from_source(self, params):
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

        data = []
        endloop = False
        counter = 0
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
                try:
                    total_records = response.headers['X-Total-Entries']
                except KeyError:
                    total_records = 'unknown'
                print("Page " + str(page) + " obtained succesfully")
                counter = counter + 1
                pulled_data = json.loads(response.content.decode('utf-8'))
                if len(pulled_data) == 0:
                    print("Pulled no records, stopping download")
                    endloop = True
                else:
                    data = data + pulled_data
                    print("Pulled {0} records, {1} records accumulated of total {2} records, resuming download".format(
                        len(pulled_data), len(data), total_records))
            else:
                print("Failed to obtain records from page " + str(page))
            if not endloop:
                print("Now waiting {0} seconds...".format(pause))
                time.sleep(pause)
        self.load_event.event_finish = datetime.datetime.now()
        self.load_event.save()
        return data


# def from_inat(inat_obs):
#         try:
#             species = inat_obs['taxon']['name']
#         except KeyError:
#             species = 'Unknown'
#         native_id = inat_obs['id']
#         original_url = inat_obs['uri']
#         picture_url = None
#         if len(inat_obs['photos']) > 0:
#             picture_url = inat_obs['photos'][0]['medium_url']
#         observation_time_string = inat_obs['observed_on']
#         observation_time = parser.parse(inat_obs['time_observed_at'])
#         origin = 'inaturalist'
#
#         wkt_point = 'POINT( {0} {1} )'
#         lat = inat_obs['latitude']
#         lon = inat_obs['longitude']
#         location = GEOSGeometry(wkt_point.format(lon, lat), srid=4326)
#
#         o = Observation(
#             species = species,
#             original_url = original_url,
#             picture_url = picture_url,
#             observation_time_string = observation_time_string,
#             observation_time = observation_time,
#             origin = origin,
#             location = location,
#             native_id = native_id
#         )
#         return o
#
# def copy_inat_fields( o, inat_obs ):
#     new_o = from_inat(inat_obs)
#     o.species = new_o.species
#     o.original_url = new_o.original_url
#     o.picture_url = new_o.picture_url
#     o.observation_time_string = new_o.observation_time_string
#     o.observation_time = new_o.observation_time
#     o.origin = new_o.origin
#     o.location = new_o.location
#     o.native_id = new_o.native_id
#     return o
