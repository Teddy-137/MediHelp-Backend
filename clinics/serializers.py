from rest_framework_gis.serializers import GeoFeatureModelSerializer
from rest_framework import serializers
from .models import Clinic


class ClinicSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = Clinic
        geo_field = "location"
        fields = ("id", "name", "address", "phone", "opening_hours")
        id_field = "id"
        distance = serializers.SerializerMethodField()

        def get_distance(self, obj):
            return obj.distance.km if hasattr(obj, "distance") else None
