from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    path("register/", views.UserRegisterView.as_view(), name="user-register"),
    path("login/", views.UserLoginView.as_view(), name="user-login"),
    path("logout/", views.UserLogoutView.as_view(), name="user-logout"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("me/", views.UserProfileView.as_view(), name="user-profile"),
]
