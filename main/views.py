from django.shortcuts import render
from rest_framework import viewsets
from main.models import Observation, Region, Stats
from main.serializers import ObservationSerializer, RegionSerializer
from django_filters import rest_framework as filters
from django.shortcuts import redirect
import django_filters.rest_framework
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from django.contrib.auth.decorators import login_required
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response


class ObservationFilter(filters.FilterSet):
    species = filters.CharFilter(field_name="species", lookup_expr='icontains')
    origin = filters.CharFilter(field_name="origin", lookup_expr='icontains')

    class Meta:
        model = Observation
        fields = ['species','origin']


class RegionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Region.objects.all()
    serializer_class = RegionSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['name']
    ordering_fields = ['name']

class ObservationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Observation.objects.all()
    serializer_class = ObservationSerializer
    #filterset_class = ObservationFilter
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    #filter_backends = [ObservationFilter, OrderingFilter]
    filterset_fields = ['species_guess', 'species_id', 'origin', 'region_id']
    ordering_fields = ['species_guess', 'species_id', 'origin', 'observation_time']


@login_required
def map_demo(request):
    return render(request, 'main/map_demo.html', {})


@api_view(['GET'])
def stats_region(request):
    if request.method == 'GET':
        data = []
        for s in Stats.objects.all().order_by('region__name'):
            data.append( { "id": s.region.id, "region_name": s.region.name,"region_slug":s.region.slug,"n_observations": s.n_observations} )
        return Response(data=data, status=status.HTTP_200_OK)
