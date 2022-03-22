from django.contrib.gis import admin
from main.models import Observation

# Register your models here.
admin.site.register(Observation, admin.OSMGeoAdmin)
