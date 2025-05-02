from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ChatViewSet

router = DefaultRouter()
router.register(r"sessions", ChatViewSet, basename="chat-session")

urlpatterns = [
    path("", include(router.urls)),
    path(
        "interact/",
        ChatViewSet.as_view({"post": "chat_interaction"}),
        name="chat-interact",
    ),
]
