from rest_framework import viewsets, status, permissions, serializers
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from .models import DoctorProfile, Availability, Teleconsultation
from .serializers import (
    DoctorProfileSerializer,
    DoctorRegistrationSerializer,
    AvailabilitySerializer,
    TeleconsultationSerializer,
)
from .permissions import IsDoctorOrReadOnly, IsPatientOwner


class DoctorRegistrationAPI(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = DoctorRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DoctorProfileViewSet(viewsets.ModelViewSet):
    serializer_class = DoctorProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_superuser:
            return DoctorProfile.objects.all()
        return DoctorProfile.objects.filter(available=True)

    @action(detail=False, methods=["get", "patch"], url_path="me")
    def me(self, request):
        """
        GET: Return the authenticated doctor's profile
        PATCH: Partially update the authenticated doctor's profile
        """
        try:
            doctor_profile = DoctorProfile.objects.get(user=request.user)
        except DoctorProfile.DoesNotExist:
            raise NotFound("Doctor profile not found for the authenticated user.")

        if request.method == "GET":
            serializer = self.get_serializer(doctor_profile)
            return Response(serializer.data)

        elif request.method == "PATCH":
            serializer = self.get_serializer(
                doctor_profile, data=request.data, partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)


class AvailabilityViewSet(viewsets.ModelViewSet):
    serializer_class = AvailabilitySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # For superusers, return all availabilities
        if self.request.user.is_superuser:
            return Availability.objects.all().order_by("day", "start_time")

        # For doctors, return their own availabilities
        try:
            doctor_profile = DoctorProfile.objects.get(user=self.request.user)
            return Availability.objects.filter(doctor=doctor_profile).order_by(
                "day", "start_time"
            )
        except DoctorProfile.DoesNotExist:
            # If the user is not a doctor, return an empty queryset
            return Availability.objects.none()

    def perform_create(self, serializer):
        try:
            doctor_profile = DoctorProfile.objects.get(user=self.request.user)
            serializer.save(doctor=doctor_profile)
        except DoctorProfile.DoesNotExist:
            raise serializers.ValidationError(
                {"doctor": "You must be a doctor to create availability slots"}
            )

    def perform_update(self, serializer):
        # Ensure users can only update their own availability slots
        instance = self.get_object()
        if (
            instance.doctor.user != self.request.user
            and not self.request.user.is_superuser
        ):
            raise serializers.ValidationError(
                {"permission": "You can only update your own availability slots"}
            )
        serializer.save()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        try:
            context["doctor"] = DoctorProfile.objects.get(user=self.request.user)
        except DoctorProfile.DoesNotExist:
            # Don't add doctor to context if the user doesn't have a doctor profile
            pass
        return context


class TeleconsultationViewSet(viewsets.ModelViewSet):
    serializer_class = TeleconsultationSerializer
    permission_classes = [permissions.IsAuthenticated, IsPatientOwner]

    def get_queryset(self):
        user = self.request.user

        # Print debug information
        print(f"User: {user.email}, Role: {user.role}")

        if user.role == "doctor":
            try:
                doctor_profile = DoctorProfile.objects.get(user=user)
                queryset = Teleconsultation.objects.filter(doctor=doctor_profile)
                print(f"Doctor teleconsults count: {queryset.count()}")
                return queryset
            except DoctorProfile.DoesNotExist:
                print("No doctor profile found")
                return Teleconsultation.objects.none()
        else:
            # For patients or other roles
            queryset = Teleconsultation.objects.filter(patient=user)
            print(f"Patient teleconsults count: {queryset.count()}")
            return queryset

    def perform_create(self, serializer):
        serializer.save(patient=self.request.user)
