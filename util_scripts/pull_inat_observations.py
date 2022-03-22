import os, sys

proj_path = "/home/webuser/dev/django/data_aggregator_api/"
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "data_aggregator_api.settings")
sys.path.append(proj_path)

os.chdir(proj_path + "util_scripts/")

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()

from main.data_adapters import InatAdapter
from main.models import Observation, LoadEvent
import json


def get_adapter_for_origin(origin):
    if origin == 'inaturalist':
        return InatAdapter(origin=origin)
    else:
        raise KeyError


def init_load_inaturalist(project_slug):
    origin = 'inaturalist'
    adapter = get_adapter_for_origin(origin)
    params = {
        'project_slug': project_slug,
        'pause': 2
    }
    obs = adapter.load_raw_from_source(params)

    filename = 'data_{0}_{1}.json'.format(origin, adapter.load_event.id)
    with open(proj_path + filename, 'w') as outfile:
         json.dump(obs, outfile)

    Observation.objects.filter(origin=origin).delete()
    hydrated = adapter.hydrate_all(obs)
    Observation.objects.bulk_create(hydrated)
    adapter.load_event.data_file = filename
    adapter.load_event.save()


def update_inaturalist(project_slug):
    origin = 'inaturalist'
    adapter = get_adapter_for_origin(origin)
    try:
        earliest_upload = Observation.objects.filter(origin=origin).earliest('record_creation_time')
        earliest_upload_datetime = earliest_upload.record_creation_time
        filter_date = earliest_upload_datetime.strftime('%Y-%m-%dT%H:%M:%S%z')
    except Observation.DoesNotExist:
        filter_date = None
    params = {
        'project_slug': project_slug,
        'pause': 2,
        'filter_date': filter_date
    }
    obs = adapter.load_raw_from_source(params)
    for raw_obs in obs:
        try:
            existing_obs = Observation.objects.filter(origin=origin).get(native_id=raw_obs['id'])
            updated_obs = adapter.copy(existing_obs, raw_obs)
            updated_obs.save()
        except Observation.DoesNotExist:
            observation = adapter.hydrate(raw_obs)
            observation.save()


def main():
    #init_load_inaturalist('stephen-s-yard')
    update_inaturalist('stephen-s-yard')


if __name__ == "__main__":
    main()
