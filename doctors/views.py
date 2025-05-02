from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.response import Response
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
    lookup_field = 'user__id'

    def get_queryset(self):
        """Return all profiles for superuser, otherwise only the current user's profile."""
        if self.request.user.is_superuser:
            return DoctorProfile.objects.all()
        return DoctorProfile.objects.filter(user=self.request.user)

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
            serializer = self.get_serializer(doctor_profile, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

class AvailabilityViewSet(viewsets.ModelViewSet):
    serializer_class = AvailabilitySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Availability.objects.filter(
            doctor__user=self.request.user
        ).order_by('day', 'start_time')

    def perform_create(self, serializer):
        serializer.save(doctor=self.request.user.doctorprofile)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['doctor'] = self.request.user.doctorprofile
        return context

class TeleconsultationViewSet(viewsets.ModelViewSet):
    serializer_class = TeleconsultationSerializer
    permission_classes = [IsPatientOwner]

    def get_queryset(self):
        if self.request.user.role == "doctor":
            return Teleconsultation.objects.filter(doctor__user=self.request.user)
        return Teleconsultation.objects.filter(patient=self.request.user)

    def perform_create(self, serializer):
        serializer.save(patient=self.request.user)
