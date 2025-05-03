from rest_framework import viewsets, filters, pagination, permissions, status
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema_view, extend_schema
from django_filters.rest_framework import DjangoFilterBackend
from django.utils.translation import gettext_lazy as _
from django.db.utils import IntegrityError
from .models import Article, Video
from .serializers import ArticleSerializer, VideoSerializer
import logging

logger = logging.getLogger(__name__)


class EducationPagination(pagination.PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


class EducationAdminPermission(permissions.BasePermission):
    message = "Only admin users can modify educational content"

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff


@extend_schema_view(
    list=extend_schema(description="List educational articles"),
    retrieve=extend_schema(description="Get article details"),
)
class ArticleViewSet(viewsets.ModelViewSet):
    serializer_class = ArticleSerializer
    permission_classes = [
        EducationAdminPermission,
    ]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = {
        "related_conditions": ["exact"],
        "is_published": ["exact"],
        "published_date": ["gte", "lte"],
    }
    search_fields = ["title", "summary", "content", "tags"]
    search_param = "q"
    ordering_fields = ["published_date", "updated_at"]
    pagination_class = EducationPagination

    # Custom filter for tags (JSONField)
    def get_queryset(self):
        queryset = Article.objects.prefetch_related("related_conditions").all()

        # Filter by tag if provided
        tag = self.request.query_params.get("tag", None)
        if tag:
            # Filter articles that have the specified tag in their tags list
            queryset = queryset.filter(tags__contains=[tag])

        return queryset

    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except IntegrityError as e:
            logger.error(f"Database integrity error: {str(e)}")
            return Response(
                {"error": _("Could not create article due to database constraints")},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            logger.error(f"Unexpected error creating article: {str(e)}", exc_info=True)
            return Response(
                {"error": _("Failed to create article")},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def update(self, request, *args, **kwargs):
        try:
            return super().update(request, *args, **kwargs)
        except IntegrityError as e:
            logger.error(f"Database integrity error: {str(e)}")
            return Response(
                {"error": _("Could not update article due to database constraints")},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            logger.error(f"Unexpected error updating article: {str(e)}", exc_info=True)
            return Response(
                {"error": _("Failed to update article")},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def list(self, request, *args, **kwargs):
        try:
            return super().list(request, *args, **kwargs)
        except pagination.InvalidPage as e:
            logger.warning(f"Invalid page error: {str(e)}")
            return Response(
                {"error": _("Invalid page number")}, status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Unexpected error listing articles: {str(e)}", exc_info=True)
            return Response(
                {"error": _("Failed to retrieve articles")},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    # Removed duplicate get_queryset method


@extend_schema_view(
    list=extend_schema(description="List educational videos"),
    retrieve=extend_schema(description="Get video details"),
)
class VideoViewSet(viewsets.ModelViewSet):
    serializer_class = VideoSerializer
    permission_classes = [
        EducationAdminPermission,
    ]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = {
        "related_symptoms": ["exact"],
        "is_published": ["exact"],
        "duration_minutes": ["gte", "lte"],
    }
    search_fields = ["title", "related_symptoms__name"]
    search_param = "q"
    ordering_fields = ["published_date", "duration_minutes"]
    pagination_class = EducationPagination

    def get_queryset(self):
        return Video.objects.prefetch_related("related_symptoms").all()

    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except IntegrityError as e:
            logger.error(f"Database integrity error: {str(e)}")
            return Response(
                {"error": _("Could not create video due to database constraints")},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            logger.error(f"Unexpected error creating video: {str(e)}", exc_info=True)
            return Response(
                {"error": _("Failed to create video")},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def update(self, request, *args, **kwargs):
        try:
            return super().update(request, *args, **kwargs)
        except IntegrityError as e:
            logger.error(f"Database integrity error: {str(e)}")
            return Response(
                {"error": _("Could not update video due to database constraints")},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            logger.error(f"Unexpected error updating video: {str(e)}", exc_info=True)
            return Response(
                {"error": _("Failed to update video")},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def list(self, request, *args, **kwargs):
        try:
            return super().list(request, *args, **kwargs)
        except pagination.InvalidPage as e:
            logger.warning(f"Invalid page error: {str(e)}")
            return Response(
                {"error": _("Invalid page number")}, status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Unexpected error listing videos: {str(e)}", exc_info=True)
            return Response(
                {"error": _("Failed to retrieve videos")},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
