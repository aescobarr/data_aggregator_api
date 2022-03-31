from django.db.models import Manager as GeoManager
from django.contrib.gis.db import models
from django.utils import timezone


class LoadEvent(models.Model):
    event_start = models.DateTimeField(default=timezone.now())
    event_finish = models.DateTimeField(null=True, blank=True)
    #data_file = models.FileField(upload_to="datafiles", null=True, blank=True)
    origin = models.TextField('Source of the original observation', null=True, blank=True)
    data_chunks = models.TextField('List of succesully created local pages', null=True, blank=True)

    class Meta:
        verbose_name = "loadevent"
        verbose_name_plural = "loadevents"

class Observation(models.Model):
    species_guess = models.TextField('Guessed species',null=True, blank=True)
    species_id = models.TextField('Species identified',null=True, blank=True)
    original_url = models.URLField('Original url of the observation, if available',null=True,blank=True)
    picture_url = models.URLField('Observation picture',null=True,blank=True)
    observation_time_string = models.CharField('Observation date in string format', max_length=500, null=True, blank=True)
    observation_time = models.DateTimeField('Observation datetime',null=True,blank=True)
    observation_date = models.DateField('Observation date year month day', null=True, blank=True)
    record_creation_time = models.DateTimeField(auto_now_add=True)
    origin = models.TextField('Source of the original observation',null=True, blank=True)
    location = models.PointField(blank=True, null=True, srid=4326)
    native_id = models.TextField('Id of the observation in its native app',null=True, blank=True)
    load_event = models.ForeignKey(LoadEvent, on_delete=models.CASCADE, null=True)
    objects = GeoManager()

    def __str__(self):
        return self.species_id

    class Meta:
        verbose_name = "observation"
        verbose_name_plural = "observations"
        ordering = ('species_id',)



