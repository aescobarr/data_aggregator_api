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
        author = d['user']['login']
        print("update main_observation set author='{0}' where native_id={1};".format(author,id))




