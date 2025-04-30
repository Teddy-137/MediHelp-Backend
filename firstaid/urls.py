from django.urls import path
from .views import (
    FirstAidListAPIView,
    FirstAidDetailAPIView,
    HomeRemedyDetailAPIView,
)

urlpatterns = [
    path("", FirstAidListAPIView.as_view(), name="firstaid-list"),
    path("<int:id>/", FirstAidDetailAPIView.as_view(), name="firstaid-detail"),
    path(
        "remedies/<int:id>/",
        HomeRemedyDetailAPIView.as_view(),
        name="homeremedy-detail",
    ),
]
