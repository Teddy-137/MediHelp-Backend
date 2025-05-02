from django.urls import path
from .views import ClinicViewSet

urlpatterns = [
    path("", ClinicViewSet.as_view({"get": "list"}), name="clinic-list"),
    path(
        "<int:pk>/",
        ClinicViewSet.as_view({"get": "retrieve"}),
        name="clinic-detail",
    ),
    path(
        "nearby/",
        ClinicViewSet.as_view({"get": "nearby"}),
        name="clinic-nearby",
    ),
]
