import init_project
from main.models import Observation
from django.db import connection

def main():
    observations = Observation.objects.filter(region__isnull=True)
    #print(observations.count())
    cursor = connection.cursor()
    for observation in observations:
        if observation.location is not None:
            cursor.execute("""
                                SELECT st_distance(geom, 'SRID=4326;POINT(%s %s)'::geometry) as d, name, id
                                FROM main_region
                                ORDER BY d limit 1
                            """, (observation.location.x, observation.location.y,))
            row = cursor.fetchone()
            #print("{0} {1}".format(row[1], row[2]))
            print("UPDATE main_observation set region_id = {0} where id={1};".format( row[2], observation.id ))
        else:
            #print("Null coordinates for observation {0}".format(observation.id))
            print("-- No coordinates")


if __name__ == '__main__':
    main()
