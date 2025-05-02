from django.urls import path
from .views import SkinDiagnosisViewSet
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path(
        "",
        SkinDiagnosisViewSet.as_view({"get": "list", "post": "create"}),
        name="skin-diagnosis",
    ),
    path(
        "<int:pk>/",
        SkinDiagnosisViewSet.as_view({"get": "retrieve"}),
        name="skin-diagnosis-detail",
    ),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
