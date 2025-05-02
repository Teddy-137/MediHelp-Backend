# firstaid/views.py
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework import filters, permissions, status
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
    OpenApiExample,
    OpenApiResponse,
)
from .models import FirstAidInstruction, HomeRemedy
from .serializers import (
    FirstAidInstructionSerializer,
    HomeRemedySerializer,
)


class FirstAidBaseAPIView:
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "firstaid"
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    ordering_fields = ["created_at", "severity_level"]
    search_param = "q"
    ordering = ["-created_at"]


@extend_schema(
    parameters=[
        OpenApiParameter(
            name="type",
            type=str,
            enum=["firstaid", "homeremedy"],
            description="Filter by instruction type",
        ),
        OpenApiParameter(
            name="q",
            type=str,
            description="Search query (searches title, description, and symptoms)",
        ),
    ]
)
class FirstAidListAPIView(FirstAidBaseAPIView, ListAPIView):
    serializer_class = FirstAidInstructionSerializer
    search_fields = ["title", "description", "condition__name"]

    def get_queryset(self):
        item_type = self.request.query_params.get("type", "firstaid").lower()
        search_query = self.request.query_params.get("q", "")

        if item_type == "homeremedy":
            return self.get_homeremedies_queryset(search_query)
        return self.get_firstaids_queryset(search_query)

    def get_firstaids_queryset(self, search_query):
        queryset = FirstAidInstruction.objects.select_related("condition")
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query)
                | Q(description__icontains=search_query)
                | Q(condition__name__icontains=search_query)
            )
        return queryset

    def get_homeremedies_queryset(self, search_query):
        queryset = HomeRemedy.objects.prefetch_related("symptoms")
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query)
                | Q(ingredients__icontains=search_query)
                | Q(symptoms__name__icontains=search_query)
            ).distinct()
        return queryset

    def list(self, request, *args, **kwargs):
        try:
            return super().list(request, *args, **kwargs)
        except Exception as e:
            return Response(
                {"error": _("Failed to retrieve data")},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


@extend_schema(
    tags=["First Aid"],
    description="""Get detailed first aid instruction by ID""",
    parameters=[
        OpenApiParameter(
            name="id",
            type=int,
            location=OpenApiParameter.PATH,
            description="First aid instruction ID",
        )
    ],
    responses={
        200: FirstAidInstructionSerializer,
        404: OpenApiResponse(
            description="Not Found",
            examples=[OpenApiExample("Error Response", value={"detail": "Not found."})],
        ),
    },
)
class FirstAidDetailAPIView(FirstAidBaseAPIView, RetrieveAPIView):
    queryset = FirstAidInstruction.objects.select_related("condition")
    serializer_class = FirstAidInstructionSerializer
    lookup_field = "id"


class HomeRemedyDetailAPIView(FirstAidBaseAPIView, RetrieveAPIView):
    queryset = HomeRemedy.objects.prefetch_related("symptoms")
    serializer_class = HomeRemedySerializer
    lookup_field = "id"
