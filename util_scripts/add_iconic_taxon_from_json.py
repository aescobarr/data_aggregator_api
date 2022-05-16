import init_project
import os
import json
from data_aggregator_api import settings


PATH = str(settings.BASE_DIR) + "/"

result = [os.path.join(dp, f) for dp, dn, filenames in os.walk(PATH) for f in filenames if os.path.splitext(f)[1] == '.json']
for file in result:
    json_data = open(file)
    data = json.load(json_data)
    for d in data:
        id = d['id']
        try:
            taxon_id = d['taxon']['iconic_taxon_id']
            taxon = d['taxon']['iconic_taxon_name']
            print("update main_observation set iconic_taxon_id={0}, iconic_taxon_name='{1}' where native_id='{2}';".format(taxon_id,taxon,id))
        except KeyError:
            print("-- not found key for observation {0}".format(id))

