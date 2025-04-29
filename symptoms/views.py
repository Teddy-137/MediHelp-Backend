from rest_framework import mixins, viewsets, permissions, status, serializers
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.pagination import PageNumberPagination
from .models import Symptom, SymptomCheck, Condition
from .serializers import SymptomSerializer, SymptomCheckSerializer, ConditionSerializer
import logging

logger = logging.getLogger(__name__)


class StandardPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100


class SymptomCheckViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = SymptomCheckSerializer
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "symptom_checks"
    pagination_class = StandardPagination

    def get_queryset(self):
        return (
            SymptomCheck.objects.filter(user=self.request.user)
            .order_by("-created_at")
            .prefetch_related("symptoms", "conditions")
            .select_related("user")
        )

    def perform_create(self, serializer):
        try:
            serializer.save(user=self.request.user)
        except Exception as e:
            logger.error(f"Check creation failed: {str(e)}")
            raise

    def create(self, request, *args, **kwargs):
        """Handle symptom check creation with standardized error responses"""
        try:
            return super().create(request, *args, **kwargs)
        except serializers.ValidationError as e:
            return Response({"error": e.detail}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.exception("Critical error in check creation")
            return Response(
                {"code": "server_error", "message": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class SymptomViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = SymptomSerializer
    pagination_class = StandardPagination
    search_fields = ["name", "description"]
    ordering_fields = ["name", "created_at"]

    def get_queryset(self):
        return Symptom.objects.all().order_by("name")


class ConditionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ConditionSerializer
    queryset = Condition.objects.all().order_by("name")
    pagination_class = StandardPagination
    search_fields = ["name", "description"]
    ordering_fields = ["name", "severity"]
