from rest_framework import viewsets, filters, pagination, permissions
from .models import FirstAidInstruction, HomeRemedy
from .serializers import FirstAidInstructionSerializer, HomeRemedySerializer


class StandardPagination(pagination.PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"


class FirstAidViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = FirstAidInstruction.objects.all()
    serializer_class = FirstAidInstructionSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = StandardPagination
    ordering_fields = ["severity_level", "created_at"]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["title", "condition__name"]
    search_param = "q"

    def get_queryset(self):
        queryset = FirstAidInstruction.objects.select_related("condition")
        if condition_id := self.request.query_params.get("condition"):
            return queryset.filter(condition_id=condition_id)
        return queryset


class HomeRemedyViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = HomeRemedySerializer
    pagination_class = StandardPagination
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ["name", "symptoms__name"]
    search_param = "q"

    def get_queryset(self):
        queryset = HomeRemedy.objects.prefetch_related("symptoms")
        if symptom_ids := self.request.query_params.get("symptoms"):
            return queryset.filter(symptoms__id__in=symptom_ids.split(","))
        return queryset
