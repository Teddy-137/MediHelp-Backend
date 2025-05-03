from rest_framework_gis.serializers import GeoFeatureModelSerializer
from rest_framework import serializers
from .models import Clinic


class ClinicSerializer(GeoFeatureModelSerializer):
    # Define the distance field at the serializer class level
    distance = serializers.SerializerMethodField()

    class Meta:
        model = Clinic
        geo_field = "location"
        fields = ("id", "name", "address", "phone", "opening_hours", "distance")
        id_field = "id"

    def get_distance(self, obj):
        """
        Return the distance in kilometers if the object has a distance attribute.
        This is used when clinics are annotated with Distance in the nearby action.
        """
        return obj.distance.km if hasattr(obj, "distance") else None
