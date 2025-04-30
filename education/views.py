from rest_framework import viewsets, filters, pagination, permissions
from drf_spectacular.utils import extend_schema_view, extend_schema
from django_filters.rest_framework import DjangoFilterBackend
from .models import Article, Video
from .serializers import ArticleSerializer, VideoSerializer


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

    def get_queryset(self):
        return Article.objects.prefetch_related("related_conditions").all()


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
