from rest_framework import viewsets, filters, pagination, permissions
from django_filters.rest_framework import DjangoFilterBackend
from .models import Article, Video
from .serializers import ArticleSerializer, VideoSerializer


class EducationPagination(pagination.PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


class ArticleViewSet(viewsets.ModelViewSet):
    serializer_class = ArticleSerializer
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,
        permissions.DjangoModelPermissions,
    ]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = {
        "related_conditions": ["exact"],
        "is_published": ["exact"],
        "published_date": ["gte", "lte"],
    }
    search_fields = ["title", "summary", "content", "tags"]
    ordering_fields = ["published_date", "updated_at"]
    pagination_class = EducationPagination

    def get_queryset(self):
        return Article.objects.prefetch_related("related_conditions").all()


class VideoViewSet(viewsets.ModelViewSet):
    serializer_class = VideoSerializer
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,
        permissions.DjangoModelPermissions,
    ]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = {
        "related_symptoms": ["exact"],
        "is_published": ["exact"],
        "duration_minutes": ["gte", "lte"],
    }
    search_fields = ["title"]
    ordering_fields = ["published_date", "duration_minutes"]
    pagination_class = EducationPagination

    def get_queryset(self):
        return Video.objects.prefetch_related("related_symptoms").all()
