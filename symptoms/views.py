from rest_framework import mixins, viewsets, permissions, status
from rest_framework.response import Response
from .models import SymptomCheck
from .serializers import SymptomCheckSerializer


class SymptomCheckViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    queryset = SymptomCheck.objects.none()
    serializer_class = SymptomCheckSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user).order_by("-created_at")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except Exception as e:  
            return Response(
                {"error": "Diagnosis failed: " + str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
