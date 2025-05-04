from django.urls import path
from .views import (
    FirstAidListAPIView,
    FirstAidDetailAPIView,
    HomeRemedyDetailAPIView,
    HomeRemedyListAPIView,
)

urlpatterns = [
    path("", FirstAidListAPIView.as_view(), name="firstaid-list"),
    path("<int:id>/", FirstAidDetailAPIView.as_view(), name="firstaid-detail"),
    path("remedies/", HomeRemedyListAPIView.as_view(), name="homeremedy-list"),
    path(
        "remedies/<int:id>/",
        HomeRemedyDetailAPIView.as_view(),
        name="homeremedy-detail",
    ),
]