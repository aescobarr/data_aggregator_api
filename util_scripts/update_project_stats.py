import init_project
import sys
from data_aggregator_api import settings
from main.models import Region, Stats, DataProject
from urllib.parse import urlencode
import requests
import json
import time

region_project = {
    8 : '',
    44 : '',
    53 : '',
    54 : '',
    56 : '',
    58 : 'exoticpt',
    60 : '',
    61 : 'exocat',
    41 : 'bioblitz-wien-2022',
    57 : 'bioblitz-ias-bulgaria',
    45 : 'ias-bioblitz-czech-republic',
    64 : 'turkiye-de-bulunan-bazi-egzotik-turlerin-izlenmesi',
    55 : 'ias-bioblitz-sardegna',
}

# https://www.inaturalist.org/projects/alien-csi-bioblitz - umbrella

# https://www.inaturalist.org/projects/exocat | place_id - https://www.inaturalist.org/places/61614
# https://www.inaturalist.org/projects/bioblitz-wien-2022 | place_id - https://www.inaturalist.org/places/129695
# https://www.inaturalist.org/projects/bioblitz-ias-bulgaria | place_id - https://www.inaturalist.org/places/12210
# https://www.inaturalist.org/projects/ias-bioblitz-czech-republic | place_id - https://www.inaturalist.org/places/8264
# https://www.inaturalist.org/projects/turkiye-de-bulunan-bazi-egzotik-turlerin-izlenmesi | place_id - https://www.inaturalist.org/places/7183
# https://www.inaturalist.org/projects/ias-bioblitz-sardegna | place_id - https://www.inaturalist.org/places/150929


def update_project_stats(origin,project_slug,region_name):
    if origin == 'inaturalist':
        try:
            region = Region.objects.get(slug=region_name)
        except Region.DoesNotExist:
            print("Region with name {0} not found".format(region_name))
            sys.exit(2)
        try:
            data_project = DataProject.objects.get(slug=origin)
        except DataProject.DoesNotExist:
            print("DataProject with name {0} not found".format(origin))
            sys.exit(2)
        params = {
            'project_id' : project_slug,
            'per_page': 10,
            'nelat': region.y_max,
            'nelng': region.x_max,
            'swlat': region.y_min,
            'swlng': region.x_min
        }
        project_url = settings.INAT_API_BASE_URL + 'observations/' + '?' + urlencode(params)
        response = requests.get(project_url)
        if response.status_code == 200:
            pulled_data = json.loads(response.content.decode('utf-8'))
            total_records = pulled_data['total_results']
            try:
                stats = Stats.objects.get(region=region, project=data_project)
            except Stats.DoesNotExist:
                stats = Stats(
                    region=region,
                    project=data_project
                )
            stats.n_observations = total_records
            stats.save()
        else:
            print("Server responded to url {0} with code {1}, aborting".format(project_url, str(response.status_code)))
            sys.exit(2)
    else:
        print("Origin {0} not implemented".format( origin ))
        sys.exit(2)


def update_region(origin, region_id, slug):
    print('Updating {0}'.format( slug ))
    params = {
        'project_id': slug,
        'per_page': 1
    }
    data_project = DataProject.objects.get(slug=origin)
    region = Region.objects.get(pk=region_id)
    project_url = settings.INAT_API_BASE_URL + 'observations/' + '?' + urlencode(params)
    response = requests.get(project_url)
    if response.status_code == 200:
        pulled_data = json.loads(response.content.decode('utf-8'))
        total_records = pulled_data['total_results']
        print("{0} total records".format(total_records))
        try:
            stats = Stats.objects.get(region=region, project=data_project)
        except Stats.DoesNotExist:
            stats = Stats(
                region=region,
                project=data_project
            )
        stats.n_observations = total_records
        stats.save()
    else:
        print("Server responded to url {0} with code {1}, aborting".format(project_url, str(response.status_code)))
    print("Now wait a little")
    time.sleep(10)


def update_all_regions(origin):
    for key in region_project:
        if region_project[key] != '':
            update_region(origin,key,region_project[key])


def main(argv):
    if len(argv) != 3:
        if len(argv) == 2 and argv[1] == 'all':
            update_all_regions(argv[0])
            sys.exit(0)
        else:
            print("Usage: update_project_stats.py origin project_slug region_name || update_project_stats.py origin all ")
            sys.exit(2)
    origin = argv[0]
    project_slug = argv[1]
    region_name = argv[2]
    update_project_stats(origin,project_slug,region_name)


if __name__ == "__main__":
    main(sys.argv[1:])