from django.db.models import Manager as GeoManager
from django.contrib.gis.db import models
from django.utils import timezone


class Region(models.Model):
    name = models.TextField('Region name')
    geom = models.MultiPolygonField(blank=True, null=True)
    x_min = models.FloatField(blank=True, null=True)
    x_max = models.FloatField(blank=True, null=True)
    y_min = models.FloatField(blank=True, null=True)
    y_max = models.FloatField(blank=True, null=True)
    slug = models.TextField('Region slug',blank=True, null=True)

    objects = GeoManager()

    def __str__(self):
        return self.name

    class Meta:
        managed = True
        ordering = ['name']
        verbose_name = "region"
        verbose_name_plural = "regions"


class LoadEvent(models.Model):
    event_start = models.DateTimeField(default=timezone.now)
    event_finish = models.DateTimeField(null=True, blank=True)
    origin = models.TextField('Source of the original observation', null=True, blank=True)
    data_chunks = models.TextField('List of succesully created local pages', null=True, blank=True)
    n_records_origin = models.IntegerField('Number of records to download', null=True, blank=True)
    n_records_pulled = models.IntegerField('Number of records to download', null=True, blank=True)
    url_used = models.TextField('List of succesully created local pages', null=True, blank=True)

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
    observation_updated_at = models.DateTimeField('Observation last update', null=True, blank=True)
    record_creation_time = models.DateTimeField(auto_now_add=True)
    origin = models.TextField('Source of the original observation',null=True, blank=True)
    location = models.PointField(blank=True, null=True, srid=4326)
    native_id = models.TextField('Id of the observation in its native app',null=True, blank=True)
    load_event = models.ForeignKey(LoadEvent, on_delete=models.CASCADE, null=True)
    region = models.ForeignKey(Region, blank=True, null=True, on_delete=models.CASCADE, )
    iconic_taxon_id = models.IntegerField(blank=True, null=True)
    iconic_taxon_name = models.TextField(blank=True, null=True)
    objects = GeoManager()

    def __str__(self):
        return self.species_id

    class Meta:
        verbose_name = "observation"
        verbose_name_plural = "observations"
        ordering = ('species_id',)


class DataProject(models.Model):
    name = models.TextField('Project name')
    slug = models.TextField('Shortened project name', blank=True, null=True)
    url = models.URLField('Project url if available', blank=True, null=True)


class Stats(models.Model):
    region = models.ForeignKey(Region, blank=True, null=True, on_delete=models.CASCADE, )
    project = models.ForeignKey(DataProject, on_delete=models.CASCADE, )
    n_observations = models.IntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)
