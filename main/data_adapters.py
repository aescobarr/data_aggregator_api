import json
from main.models import LoadEvent

proj_path = "/home/webuser/dev/django/data_aggregator_api/"

# species = models.TextField('Observed species',null=True, blank=True)
# original_url = models.URLField('Original url of the observation, if available',null=True,blank=True)
# picture_url = models.URLField('Observation picture',null=True,blank=True)
# observation_time_string = models.CharField('Observation date in string format', max_length=500, null=True, blank=True)
# observation_time = models.DateTimeField('Observation date',null=True,blank=True)
# record_creation_time = models.DateTimeField(auto_now_add=True)
# origin = models.TextField('Source of the original observation',null=True, blank=True)
# native_id = models.TextField('Id of the observation in its native app',null=True, blank=True)

class BaseAdapter:
    def __init__(self, origin, load_event=None):
        self.origin = origin
        if load_event == None:
            l = LoadEvent(origin=origin)
            l.save()
            self.load_event = l
        else:
            self.load_event = load_event

    def hydrate(self, raw_obs):
        pass

    def read_raw_data(self):
        files = json.loads(self.load_event.data_chunks)
        raw_data = []
        for f in files:
            json_data = open(f)
            read_data = json.load(json_data)
            raw_data = raw_data + read_data
        return raw_data

    def hydrate_all(self):
        hydrated = []
        data = self.read_raw_data()
        for raw_obs in data:
            hydrated.append(self.hydrate(raw_obs))
        return hydrated

    def copy(self, original, raw_obs):
        pass

    def load_raw_from_source(self, params):
        pass

# class GBIFAdapter(BaseAdapter):
#     def __init__(self, origin):
#         BaseAdapter.__init__(self, origin)
#
#     def hydrate(self, raw_obs):
#         origin = self.origin
#         try:
#             species = raw_obs['species']
#         except KeyError:
#             species = 'Unknown'
#         native_id = raw_obs['key']
#         original_url = "https://www.gbif.org/occurrence/" + str(native_id)
#         picture_url = None
#         try:
#             if len(raw_obs['media']) > 0:
#                 picture_url = raw_obs['media'][0]['identifier']
#         except KeyError:
#             pass
#         observation_time_string = raw_obs['eventDate']
#         if observation_time_string is None:
#             observation_time = None
#         else:
#             observation_time = parser.parse(observation_time_string)
#
#         wkt_point = 'POINT( {0} {1} )'
#         lat = raw_obs['decimalLatitude']
#         lon = raw_obs['decimalLongitude']
#         if lat is None or lon is None:
#             location = None
#         else:
#             location = GEOSGeometry(wkt_point.format(lon, lat), srid=4326)
#
#         o = Observation(
#             species = species,
#             original_url = original_url,
#             picture_url = picture_url,
#             observation_time_string = observation_time_string,
#             observation_time = observation_time,
#             origin = origin,
#             location = location,
#             native_id = native_id,
#             load_event = self.load_event
#         )
#         return o
#
#     def load_raw_from_source(self, params):
#         default_params = {
#             'limit': 50
#         }
#         merged_params = {**default_params, **params }
#
#         data = []
#         endloop = False
#         counter = 0
#         while not endloop:
#             page = counter + 1
#             params = {
#                 'limit': merged_params['limit'],
#                 'offset': counter * merged_params['limit'],
#                 'datasetKey': merged_params['datasetKey']
#             }
#             pause = merged_params['pause']
#             project_url = settings.GBIF_API_BASE_URL + 'occurrence/search/' + '?' + urlencode(params)
#             headers = { 'Authorization' : 'Basic %s' %  merged_params['credentials'] }
#             response = requests.get(project_url, headers=headers)
#             print("Obtaining page number " + str(page))
#             if page == 30:
#                 endloop = True
#             if response.status_code == 200:
#                 counter = counter + 1
#                 pulled_data = json.loads(response.content.decode('utf-8'))
#                 if len(pulled_data) == 0:
#                     print("Pulled no records, stopping download")
#                     endloop = True
#                 else:
#                     data = data + pulled_data['results']
#                     print("Pulled {0} records, {1} records accumulated of total {2} records, resuming download".format(
#                         len(pulled_data['results']), len(data), pulled_data['count']))
#             else:
#                 print("Failed to obtain records from page " + str(page))
#             if not endloop:
#                 print("Now waiting {0} seconds...".format(pause))
#                 time.sleep(pause)
#         self.load_event.event_finish = datetime.datetime.now()
#         self.load_event.save()
#         return data
#
#
