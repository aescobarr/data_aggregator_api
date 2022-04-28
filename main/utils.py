from main.inat_adapter import InatAdapter
from main.models import Observation


def get_adapter_for_origin(origin, load_event=None):
    if origin == 'inaturalist':
        return InatAdapter(origin=origin, load_event=load_event)
    if origin == 'biodiversity4all':
        return InatAdapter(origin=origin, load_event=load_event)
    # elif origin == 'gbif_obervation_org':
    #     return GBIFAdapter(origin=origin)
    else:
        raise KeyError


def replay_event(event, clear=False):
    adapter = get_adapter_for_origin(event.origin, event)
    if clear:
        hydrated = adapter.hydrate_all()
        Observation.objects.filter(origin=event.origin).delete()
        Observation.objects.bulk_create(hydrated)
    else:
        raw_data = adapter.read_raw_data()
        for raw_obs in raw_data:
            try:
                existing_obs = Observation.objects.filter(origin=event.origin).get(native_id=raw_obs['id'])
                updated_obs = adapter.copy(existing_obs, raw_obs)
                updated_obs.save()
            except Observation.DoesNotExist:
                observation = adapter.hydrate(raw_obs)
                observation.save()


def load_from_file(file_name, origin):
    adapter = get_adapter_for_origin(origin)
    hydrated = adapter.hydrate_from_file(file_name)
    for obs in hydrated:
        try:
            existing_obs = Observation.objects.filter(origin=origin).get(native_id=obs.native_id)
            updated_obs = adapter.clone_overwrite(existing_obs, obs)
            updated_obs.save()
        except Observation.DoesNotExist:
            obs.save()
