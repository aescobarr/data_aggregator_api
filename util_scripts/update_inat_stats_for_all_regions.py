import init_project
from util_scripts.update_project_stats import update_project_stats
from main.models import Region, DataProject
import time


def main():
    origin = 'inaturalist'
    project_slug = 'butterflies-of-europe'
    for r in Region.objects.all():
        region_name = r.slug
        print("Updating {0} {1} {2}".format(origin,project_slug,region_name))
        update_project_stats(origin,project_slug,region_name)
        print("Sleeping 10...")
        time.sleep(10)


if __name__ == "__main__":
    main()
