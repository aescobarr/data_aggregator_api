import init_project
from main.utils import get_adapter_for_origin, replay_event
from main.models import Observation, LoadEvent
from datetime import date
import logging

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

loadevent_log = logging.getLogger('loadevent_logger')

def init_load_inaturalist(params):
    origin = 'inaturalist'
    loadevent_log.debug("Performing initial data load from {0}".format(origin))
    adapter = get_adapter_for_origin(origin)
    loadevent_log.debug("Got adapter for {0}".format(origin))
    adapter.load_raw_from_source(params)

    loadevent_log.debug("Clearing all observations for origin {0}".format(origin))
    Observation.objects.filter(origin=origin).delete()
    hydrated = adapter.hydrate_all()
    loadevent_log.debug("Creating observations...")
    Observation.objects.bulk_create(hydrated)
    loadevent_log.debug("Created!")
    #adapter.load_event.data_file = filename
    #adapter.load_event.save()


def update_inaturalist(params):
    origin = 'inaturalist'
    adapter = get_adapter_for_origin(origin)
    adapter.load_raw_from_source(params)
    hydrated = adapter.hydrate_all()
    for raw_obs in hydrated:
        try:
            existing_obs = Observation.objects.filter(origin=origin).get(native_id=raw_obs.native_id)
            #updated_obs = adapter.copy(existing_obs, raw_obs)
            updated_obs = adapter.clone_overwrite(existing_obs, raw_obs)
            updated_obs.save()
        except Observation.DoesNotExist:
            raw_obs.save()
            # observation = adapter.hydrate(raw_obs)
            # observation.save()


def load_inaturalist(event_slug):
    loadevent_log.debug("Retrieving last event")
    last_event = LoadEvent.objects.filter(origin='inaturalist').filter(event_finish__isnull=False).order_by('-id')
    if last_event.exists():
        actual_last_event = last_event.first()
        d1_date = actual_last_event.event_finish
        d1 = d1_date.strftime('%Y-%m-%d')
        d2 = date.today().strftime('%Y-%m-%d')
        loadevent_log.debug("Last event exists, with id {0} and finish date {1}".format( actual_last_event.id, d1 ))
        # updated_since_date = actual_last_event.event_finish
        # updated_since = updated_since_date.strftime('%Y-%m-%dT%H:%M:%S%z')
        # update_inaturalist(event_slug, updated_since, page_limit)
        # latest_observation_time = Observation.objects.filter(load_event=actual_last_event).latest('observation_updated_at')
        # actual_latest_observation_time = latest_observation_time.observation_updated_at
        # updated_since = actual_latest_observation_time.strftime('%Y-%m-%dT%H:%M:%S%z')
        # update_inaturalist(event_slug, updated_since, page_limit)
        params = {
            'd1': d1,
            'd2': d2,
            'project_id': event_slug
        }
        update_inaturalist(params)
    else:
        #d1 = "2022-04-03"
        d1 = "1999-01-01"
        d2 = date.today().strftime('%Y-%m-%d')
        loadevent_log.debug("Last event does not exist, downloading observations from {0} to present".format(d1))
        params = {
            'd1': d1,
            'd2': d2,
            'project_id': event_slug
        }
        init_load_inaturalist(params)


def main():
    #init_load_inaturalist('stephen-s-yard')
    #init_load_inaturalist('butterflies-of-europe', page_limit=10)
    #update_inaturalist('stephen-s-yard')
    #update_inaturalist('butterflies-of-europe')
    #init_load_gbif('8a863029-f435-446a-821e-275f4f641165')
    #l = LoadEvent.objects.get(pk=50)
    #replay_event(l, clear=True)
    loadevent_log.debug("******** Starting LoadEvent ************")
    load_inaturalist('alien-csi-bioblitz')
    loadevent_log.debug("******** Finished LoadEvent ************")


if __name__ == "__main__":
    main()
