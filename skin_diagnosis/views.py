from rest_framework import viewsets, permissions
from rest_framework.response import Response
from .models import SkinDiagnosis
from .serializers import SkinDiagnosisSerializer


class SkinDiagnosisViewSet(viewsets.ModelViewSet):
    serializer_class = SkinDiagnosisSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["get", "post", "head"]

    def get_queryset(self):
        return SkinDiagnosis.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
