import os, sys

proj_path = "/home/webuser/dev/django/data_aggregator_api/"
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "data_aggregator_api.settings")
sys.path.append(proj_path)

os.chdir(proj_path + "util_scripts/")

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
