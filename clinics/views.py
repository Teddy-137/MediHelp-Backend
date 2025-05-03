# clinics/views.py
from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import Distance
from rest_framework import viewsets, permissions, status, pagination
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import filters
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from django_filters.rest_framework import DjangoFilterBackend, FilterSet, CharFilter
from .models import Clinic
from .serializers import ClinicSerializer
import logging
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from datetime import datetime


class ClinicUserRateThrottle(UserRateThrottle):
    """
    Throttle for authenticated users accessing clinic endpoints.
    """

    rate = "100/hour"
    scope = "clinic_user"


class ClinicAnonRateThrottle(AnonRateThrottle):
    """
    Throttle for anonymous users accessing clinic endpoints.
    """

    rate = "20/hour"
    scope = "clinic_anon"


class ClinicPagination(pagination.PageNumberPagination):
    """
    Custom pagination for clinics.
    """

    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 50


class ClinicFilter(FilterSet):
    """
    Custom filter set for clinics.
    """

    day = CharFilter(method="filter_by_day")
    time = CharFilter(method="filter_by_time")

    class Meta:
        model = Clinic
        fields = ["day", "time"]

    def filter_by_day(self, queryset, name, value):
        """
        Filter clinics by day of the week.
        """
        # Validate day
        valid_days = [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        ]

        if value not in valid_days:
            return queryset.none()

        # Filter clinics that are open on the specified day
        return queryset.filter(opening_hours__has_key=value)

    def filter_by_time(self, queryset, name, value):
        """
        Filter clinics by time of day.
        Format: HH:MM (24-hour format)
        """
        # Validate time format
        try:
            # Get current day of the week
            current_day = datetime.now().strftime("%A")

            # Parse the time
            hour, minute = map(int, value.split(":"))
            if not (0 <= hour <= 23 and 0 <= minute <= 59):
                return queryset.none()

            # Convert to comparable format
            query_time = f"{hour:02d}:{minute:02d}"

            # Filter clinics that are open at the specified time
            # This is a simplified approach and may not work for all cases
            # A more robust solution would involve parsing the time ranges
            filtered_clinics = []
            for clinic in queryset:
                if current_day in clinic.opening_hours:
                    hours = clinic.opening_hours[current_day]
                    if hours.lower() == "closed":
                        continue

                    start, end = hours.split("-")
                    if start <= query_time <= end:
                        filtered_clinics.append(clinic.id)

            return queryset.filter(id__in=filtered_clinics)
        except (ValueError, TypeError):
            return queryset.none()


logger = logging.getLogger(__name__)


class ClinicViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for clinics.
    Provides list, retrieve, and nearby actions.

    Filtering:
    - day: Filter by day of the week (e.g., Monday, Tuesday, etc.)
    - time: Filter by time of day in 24-hour format (e.g., 14:30)

    Searching:
    - q: Search by name or address
    """

    queryset = Clinic.objects.all()
    serializer_class = ClinicSerializer
    permission_classes = [permissions.AllowAny]
    search_fields = ["name", "address"]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = ClinicFilter
    pagination_class = ClinicPagination
    throttle_classes = [ClinicUserRateThrottle, ClinicAnonRateThrottle]

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

        # Filter out clinics with null locations and then annotate with distance
        qs = (
            Clinic.objects.filter(location__isnull=False)
            .annotate(distance=Distance("location", user_loc))
            .filter(distance__lte=max_m)
            .order_by("distance")
        )

        # Log if no clinics are found
        if not qs.exists():
            logger.info(f"No clinics found within {distance_km} km of ({lat}, {lng})")

        page = self.paginate_queryset(qs)
        serializer = self.get_serializer(page or qs, many=True)
        return self.get_paginated_response(serializer.data)
