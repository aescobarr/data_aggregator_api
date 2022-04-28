import init_project
from main.models import Observation, Region


def main():
    for o in Observation.objects.all():
        countries = Region.objects.filter(geom__contains=o.location)
        if countries.exists():
            region = countries.first()
            o.region = region
            o.save()


if __name__ == "__main__":
    main()
