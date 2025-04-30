from django.urls import path
from . import views

urlpatterns = [
    path("healthz/", views.HealthCheckView.as_view(), name="health-check"),
]
