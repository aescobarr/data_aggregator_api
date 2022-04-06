import init_project
import sys
from data_aggregator_api import settings
from main.models import Region, Stats, DataProject
from urllib.parse import urlencode
import requests
import json

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


def main(argv):
    if len(argv) != 3:
        print("Usage: update_project_stats.py origin project_slug region_name")
        sys.exit(2)
    origin = argv[0]
    project_slug = argv[1]
    region_name = argv[2]
    update_project_stats(origin,project_slug,region_name)


if __name__ == "__main__":
    main(sys.argv[1:])
