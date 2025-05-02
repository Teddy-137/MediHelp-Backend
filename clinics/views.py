# clinics/views.py
from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import Distance
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import filters
from .models import Clinic
from .serializers import ClinicSerializer
import logging
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample

logger = logging.getLogger(__name__)


class ClinicViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = Clinic.objects.all()
    serializer_class = ClinicSerializer
    permission_classes = [permissions.AllowAny]
    search_fields = ["name", "address"]
    filter_backends = [filters.SearchFilter]

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="lat",
                description="Latitude of the user",
                required=True,
                type=float,
            ),
            OpenApiParameter(
                name="lng",
                description="Longitude of the user",
                required=True,
                type=float,
            ),
            OpenApiParameter(
                name="distance",
                description="Maximum distance in kilometers",
                required=False,
                type=float,
                default=5,
            ),
        ],
        responses={200: ClinicSerializer(many=True)},
        description="Get nearby clinics based on user location",
        examples=[
            OpenApiExample(
                "Example request",
                value={"lat": 9.0054, "lng": 38.7636, "distance": 10},
                request_only=True,
            ),
        ],
    )
    @action(detail=False, url_path="nearby")
    def nearby(self, request):
        lat = request.query_params.get("lat")
        lng = request.query_params.get("lng")
        distance_km = request.query_params.get("distance", 5)

        if not (lat and lng):
            return Response(
                {"error": "Please provide `lat` and `lng` query parameters."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user_loc = Point(float(lng), float(lat), srid=4326)
            max_m = float(distance_km) * 1000
        except ValueError:
            return Response(
                {"error": "Invalid `lat`, `lng`, or `distance` value."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        qs = (
            Clinic.objects.annotate(distance=Distance("location", user_loc))
            .filter(distance__lte=max_m)
            .order_by("distance")
        )

        page = self.paginate_queryset(qs)
        serializer = self.get_serializer(page or qs, many=True)
        return self.get_paginated_response(serializer.data)
