from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils.translation import gettext_lazy as _

from .models import User
from .serializers import (
    UserRegisterSerializer,
    UserLoginSerializer,
    UserProfileSerializer,
)


from rest_framework_simplejwt.tokens import RefreshToken  # Add this import


class UserRegisterView(generics.CreateAPIView):
    serializer_class = UserRegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.perform_create(serializer)

        refresh = RefreshToken.for_user(user)
        access = refresh.access_token

        return Response(
            {
                "message": _("User created successfully."),
                "tokens": {"refresh": str(refresh), "access": str(access)},
            },
            status=status.HTTP_201_CREATED,
        )

    def perform_create(self, serializer):
        user = serializer.save()
        return user


class UserLoginView(TokenObtainPairView):
    serializer_class = UserLoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        refresh = RefreshToken.for_user(user)
        access = refresh.access_token

        return Response(
            {
                "message": _("Login successful."),
                "tokens": {"refresh": str(refresh), "access": str(access)},
            },
            status=status.HTTP_200_OK,
        )


class UserLogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        refresh_token = request.data.get("refresh_token") or request.data.get("refresh")

        if not refresh_token:
            return Response(
                {"error": _("Refresh token is required.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(
                {"message": _("Logout successful. Token invalidated.")},
                status=status.HTTP_205_RESET_CONTENT,
            )
        except TokenError:
            return Response(
                {"error": _("Invalid or expired refresh token.")},
                status=status.HTTP_400_BAD_REQUEST,
            )


class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)
