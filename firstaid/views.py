# firstaid/views.py
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework import filters, permissions, status, pagination
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


class FirstAidPagination(pagination.PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 50


class FirstAidBaseAPIView:
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "firstaid"
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_param = "q"
    ordering = ["-created_at"]
    pagination_class = FirstAidPagination


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
        OpenApiParameter(
            name="ordering",
            type=str,
            description="Order by field (prefix with '-' for descending)",
            examples=[
                OpenApiExample("Created Date", value="-created_at"),
                OpenApiExample("Severity", value="-severity_level"),
                OpenApiExample("Title", value="title"),
            ],
        ),
    ]
)
class FirstAidListAPIView(FirstAidBaseAPIView, ListAPIView):
    serializer_class = FirstAidInstructionSerializer
    search_fields = ["title", "description", "condition__name"]

    def get_ordering_fields(self):
        """Return appropriate ordering fields based on the item type"""
        item_type = self.request.query_params.get("type", "firstaid").lower()

        if item_type == "homeremedy":
            return ["created_at", "name"]
        return ["created_at", "severity_level", "title"]

    def get_ordering(self):
        """Get the ordering based on the item type"""
        ordering = self.request.query_params.get("ordering")
        if ordering:
            # Validate ordering field based on item type
            item_type = self.request.query_params.get("type", "firstaid").lower()
            valid_fields = set(self.get_ordering_fields())

            # Remove the '-' prefix for descending order when checking validity
            field = ordering[1:] if ordering.startswith("-") else ordering

            if field not in valid_fields:
                return self.ordering  # Default ordering

        return ordering or self.ordering

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
            # Improved search for JSON field - convert ingredients to string representation
            # for text search and use a more efficient approach
            queryset = queryset.filter(
                Q(name__icontains=search_query)
                | Q(symptoms__name__icontains=search_query)
                # Use a custom filter for JSON array items
                | Q(preparation__icontains=search_query)
            ).distinct()

            # Manual filtering for ingredients (JSON field)
            # This is more efficient than using icontains on JSON fields
            if not queryset.exists():
                all_remedies = HomeRemedy.objects.all()
                filtered_ids = []

                for remedy in all_remedies:
                    # Case-insensitive search in ingredients list
                    if any(
                        search_query.lower() in ingredient.lower()
                        for ingredient in remedy.ingredients
                    ):
                        filtered_ids.append(remedy.id)

                if filtered_ids:
                    queryset = HomeRemedy.objects.filter(
                        id__in=filtered_ids
                    ).prefetch_related("symptoms")

        return queryset

    def list(self, request, *args, **kwargs):
        import logging

        logger = logging.getLogger(__name__)

        try:
            return super().list(request, *args, **kwargs)
        except pagination.InvalidPage as e:
            logger.warning(f"Invalid page error: {str(e)}")
            return Response(
                {"error": _("Invalid page number")},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            logger.error(
                f"Unexpected error in FirstAidListAPIView.list: {str(e)}", exc_info=True
            )
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


@extend_schema(
    tags=["First Aid"],
    description="""Get detailed home remedy by ID""",
    parameters=[
        OpenApiParameter(
            name="id",
            type=int,
            location=OpenApiParameter.PATH,
            description="Home remedy ID",
        )
    ],
    responses={
        200: HomeRemedySerializer,
        404: OpenApiResponse(
            description="Not Found",
            examples=[OpenApiExample("Error Response", value={"detail": "Not found."})],
        ),
    },
)
class HomeRemedyDetailAPIView(FirstAidBaseAPIView, RetrieveAPIView):
    queryset = HomeRemedy.objects.prefetch_related("symptoms")
    serializer_class = HomeRemedySerializer
    lookup_field = "id"


@extend_schema(
    tags=["First Aid"],
    description="""List all home remedies with optional filtering""",
    parameters=[
        OpenApiParameter(
            name="q",
            type=str,
            description="Search query (searches name, preparation, and symptoms)",
        ),
        OpenApiParameter(
            name="ordering",
            type=str,
            description="Order by field (prefix with '-' for descending)",
            examples=[
                OpenApiExample("Created Date", value="-created_at"),
                OpenApiExample("Name", value="name"),
            ],
        ),
    ],
    responses={
        200: HomeRemedySerializer(many=True),
        400: OpenApiResponse(
            description="Bad Request",
            examples=[
                OpenApiExample("Error Response", value={"error": "Invalid page number"})
            ],
        ),
    },
)
class HomeRemedyListAPIView(FirstAidBaseAPIView, ListAPIView):
    serializer_class = HomeRemedySerializer
    search_fields = ["name", "preparation", "symptoms__name"]
    ordering_fields = ["created_at", "name"]
    ordering = ["-created_at"]

    def get_queryset(self):
        queryset = HomeRemedy.objects.prefetch_related("symptoms")
        search_query = self.request.query_params.get("q", "")

        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query)
                | Q(symptoms__name__icontains=search_query)
                | Q(preparation__icontains=search_query)
            ).distinct()

            # Manual filtering for ingredients (JSON field)
            if not queryset.exists():
                all_remedies = HomeRemedy.objects.all()
                filtered_ids = []

                for remedy in all_remedies:
                    # Case-insensitive search in ingredients list
                    if any(
                        search_query.lower() in ingredient.lower()
                        for ingredient in remedy.ingredients
                    ):
                        filtered_ids.append(remedy.id)

                if filtered_ids:
                    queryset = HomeRemedy.objects.filter(
                        id__in=filtered_ids
                    ).prefetch_related("symptoms")

        return queryset

    def list(self, request, *args, **kwargs):
        import logging

        logger = logging.getLogger(__name__)

        try:
            return super().list(request, *args, **kwargs)
        except pagination.InvalidPage as e:
            logger.warning(f"Invalid page error: {str(e)}")
            return Response(
                {"error": _("Invalid page number")},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            logger.error(
                f"Unexpected error in HomeRemedyListAPIView.list: {str(e)}",
                exc_info=True,
            )
            return Response(
                {"error": _("Failed to retrieve data")},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
