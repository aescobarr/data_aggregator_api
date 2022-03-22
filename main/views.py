from django.shortcuts import render
from rest_framework import viewsets
from main.models import Observation
from main.serializers import ObservationSerializer
from django_filters import rest_framework as filters
from django.shortcuts import redirect
import django_filters.rest_framework
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter


class ObservationFilter(filters.FilterSet):
    species = filters.CharFilter(field_name="species", lookup_expr='icontains')
    origin = filters.CharFilter(field_name="origin", lookup_expr='icontains')

    class Meta:
        model = Observation
        fields = ['species','origin']


class ObservationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Observation.objects.all()
    serializer_class = ObservationSerializer
    #filterset_class = ObservationFilter
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    #filter_backends = [ObservationFilter, OrderingFilter]
    filterset_fields = ['species', 'origin']
    ordering_fields = ['species', 'origin', 'observation_time']


def map_demo(request):
    return render(request, 'main/map_demo.html', {})
