from django.contrib.gis import admin
from main.models import Observation, Region, DataProject


class DataProjectAdmin(admin.ModelAdmin):
    list_display = ('name','slug','url',)
    search_fields = ('name','slug','url',)

# Register your models here.
admin.site.register(Observation, admin.OSMGeoAdmin)
admin.site.register(Region, admin.OSMGeoAdmin)
admin.site.register(DataProject, DataProjectAdmin)
