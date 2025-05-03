from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    DoctorRegistrationAPI,
    DoctorProfileViewSet,
    AvailabilityViewSet,
    TeleconsultationViewSet,
)

router = DefaultRouter()
router.register(r"profiles", DoctorProfileViewSet, basename="doctor-profile")
router.register(r"availability", AvailabilityViewSet, basename="availability")
router.register(r"teleconsults", TeleconsultationViewSet, basename="teleconsult")

urlpatterns = [
    path("register/", DoctorRegistrationAPI.as_view(), name="doctor-register"),
    # Removed duplicate "profiles/me/" path - use the @action decorator in the viewset instead
    path("", include(router.urls)),
]
