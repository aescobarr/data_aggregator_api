import os, sys

proj_path = "/home/webuser/dev/django/data_aggregator_api/"
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "data_aggregator_api.settings")
sys.path.append(proj_path)

os.chdir(proj_path + "util_scripts/")

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()

from main.utils import get_adapter_for_origin, replay_event
from main.models import Observation, LoadEvent
import json
from base64 import b64encode
from data_aggregator_api import settings


# def init_load_gbif(dataset_uuid):
#     origin = 'gbif_obervation_org'
#     adapter = get_adapter_for_origin(origin)
#     arr = bytes("{0}:{1}".format( settings.GBIF_AUTH_USERNAME, settings.GBIF_AUTH_PASSWORD ), 'utf-8')
#     userAndPass = b64encode(arr).decode("ascii")
#     params = {
#         'datasetKey': dataset_uuid,
#         'limit': 100,
#         'pause': 5,
#         'credentials': userAndPass
#     }
#     obs = adapter.load_raw_from_source(params)
#     filename = 'data_{0}_{1}.json'.format(origin, adapter.load_event.id)
#     with open(proj_path + filename, 'w') as outfile:
#         json.dump(obs, outfile)
#
#     Observation.objects.filter(origin=origin).delete()
#     hydrated = adapter.hydrate_all(obs)
#     Observation.objects.bulk_create(hydrated)
#     adapter.load_event.data_file = filename
#     adapter.load_event.save()


def init_load_inaturalist(project_slug):
    origin = 'inaturalist'
    adapter = get_adapter_for_origin(origin)
    params = {
        'project_slug': project_slug,
        'pause': 2
    }
    adapter.load_raw_from_source(params)

    Observation.objects.filter(origin=origin).delete()
    hydrated = adapter.hydrate_all()
    Observation.objects.bulk_create(hydrated)
    #adapter.load_event.data_file = filename
    #adapter.load_event.save()


def update_inaturalist(project_slug):
    origin = 'inaturalist'
    adapter = get_adapter_for_origin(origin)
    try:
        latest_observation = Observation.objects.filter(origin=origin).filter(observation_date__isnull=False).latest('observation_date')
        latest_observation_datetime = latest_observation.observation_date
        filter_date = latest_observation_datetime.strftime('%Y-%m-%d')
        # earliest_upload = Observation.objects.filter(origin=origin).earliest('record_creation_time')
        # earliest_upload_datetime = earliest_upload.record_creation_time
        # filter_date = earliest_upload_datetime.strftime('%Y-%m-%dT%H:%M:%S%z')
    except Observation.DoesNotExist:
        filter_date = None
    params = {
        'project_slug': project_slug,
        'pause': 2,
        'filter_date': filter_date
    }
    adapter.load_raw_from_source(params)
    hydrated = adapter.hydrate_all()
    for raw_obs in hydrated:
        try:
            existing_obs = Observation.objects.filter(origin=origin).get(native_id=raw_obs['id'])
            updated_obs = adapter.copy(existing_obs, raw_obs)
            updated_obs.save()
        except Observation.DoesNotExist:
            observation = adapter.hydrate(raw_obs)
            observation.save()


def main():
    #init_load_inaturalist('stephen-s-yard')
    #update_inaturalist('stephen-s-yard')
    #init_load_gbif('8a863029-f435-446a-821e-275f4f641165')
    l = LoadEvent.objects.get(pk=36)
    replay_event(l,clear=False)


if __name__ == "__main__":
    main()
