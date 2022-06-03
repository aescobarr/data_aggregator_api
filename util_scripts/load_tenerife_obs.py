import init_project
from django.contrib.gis.geos import GEOSGeometry
from main.models import Observation, Stats, Region
import csv

def load_obs():
    origin = 'gbif'
    tenerife = Region.objects.get(pk=60)
    Observation.objects.filter(origin=origin).delete()
    observations = []
    wkt_point = 'POINT( {0} {1} )'
    with open('datos_tenerife_gbif.csv', 'r') as csvfile:
        datareader = csv.reader(csvfile, delimiter=',', quotechar='"')
        firstrow = True
        for row in datareader:
            if not firstrow:
                native_id = row[0]
                species_id = row[2]
                location = GEOSGeometry(wkt_point.format(row[5].replace(',','.'), row[4].replace(',','.')), srid=4326)
                observation_time_string = row[8]
                picture_url = row[11]
                author = row[14]

                o = Observation(
                    native_id=native_id,
                    species_id=species_id,
                    location=location,
                    observation_time_string=observation_time_string,
                    picture_url=picture_url,
                    author=author,
                    origin=origin,
                    region=tenerife
                )

                observations.append(o)
            else:
                firstrow = False

    Observation.objects.bulk_create(observations)
    stats_tenerife = Stats.objects.get(region=tenerife)
    stats_tenerife.n_observations = len(observations)
    stats_tenerife.save()



if __name__ == '__main__':
    load_obs()
