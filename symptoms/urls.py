# urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r"symptoms", views.SymptomViewSet, basename="symptom")
router.register(r"conditions", views.ConditionViewSet, basename="condition")
router.register(r"checks", views.SymptomCheckViewSet, basename="symptom-check")

urlpatterns = [
    path("", include(router.urls)),
]
