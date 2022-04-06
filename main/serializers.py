from rest_framework import serializers
from main.models import Observation, Region


class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = ['name','x_min','x_max','y_min','y_max']


class ObservationSerializer(serializers.ModelSerializer):
    location = serializers.SerializerMethodField(method_name='get_location')
    id = serializers.ReadOnlyField()
    load_event = serializers.SerializerMethodField(method_name='get_load_event')
    region = RegionSerializer(many=False)

    class Meta:
        model = Observation
        fields = '__all__'

    def get_location(self,obj):
        if obj.location is not None:
            return { "lat": obj.location.y, "long": obj.location.x}
        else:
            return None

    def get_load_event(self, obj):
        if obj.load_event is not None:
            return obj.load_event.id
        else:
            return None
