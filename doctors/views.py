from rest_framework import viewsets, status, permissions, serializers, pagination
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, ValidationError
from django.db import transaction
from django.db.utils import IntegrityError
import logging
from .models import DoctorProfile, Availability, Teleconsultation
from .serializers import (
    DoctorProfileSerializer,
    DoctorRegistrationSerializer,
    AvailabilitySerializer,
    TeleconsultationSerializer,
)
from .permissions import IsDoctorOrReadOnly, IsPatientOwner, IsDoctorProfileOwner

logger = logging.getLogger(__name__)


class DoctorsPagination(pagination.PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


class DoctorRegistrationAPI(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        try:
            serializer = DoctorRegistrationSerializer(data=request.data)
            if serializer.is_valid():
                with transaction.atomic():
                    serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Doctor registration failed: {str(e)}", exc_info=True)
            return Response(
                {"error": "Registration failed. Please try again."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class DoctorProfileViewSet(viewsets.ModelViewSet):
    serializer_class = DoctorProfileSerializer
    permission_classes = [permissions.IsAuthenticated, IsDoctorProfileOwner]
    pagination_class = DoctorsPagination

    def get_queryset(self):
        if self.request.user.is_superuser:
            return DoctorProfile.objects.all()

        # For regular users, show only available doctors
        # For doctors, also include their own profile even if not available
        queryset = DoctorProfile.objects.filter(available=True)

        # If the user is a doctor, add their profile to the queryset
        if self.request.user.role == "doctor":
            try:
                own_profile = DoctorProfile.objects.get(user=self.request.user)
                # Use distinct() to avoid duplicates if the profile is already available
                return (
                    queryset | DoctorProfile.objects.filter(id=own_profile.id)
                ).distinct()
            except DoctorProfile.DoesNotExist:
                pass

        return queryset

    def perform_update(self, serializer):
        """
        Additional security check to ensure a doctor can only update their own profile.
        This is a belt-and-suspenders approach in addition to the permission class.
        """
        instance = self.get_object()
        if instance.user != self.request.user and not self.request.user.is_superuser:
            raise serializers.ValidationError(
                {"permission": "You can only update your own profile"}
            )
        serializer.save()

    def perform_destroy(self, instance):
        """
        Additional security check to ensure a doctor can only delete their own profile.
        This is a belt-and-suspenders approach in addition to the permission class.
        """
        if instance.user != self.request.user and not self.request.user.is_superuser:
            raise serializers.ValidationError(
                {"permission": "You can only delete your own profile"}
            )
        instance.delete()

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
    pagination_class = DoctorsPagination

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

            # Use transaction to prevent race conditions
            with transaction.atomic():
                # Check for overlapping availabilities within the transaction
                day = serializer.validated_data.get("day")
                start_time = serializer.validated_data.get("start_time")
                end_time = serializer.validated_data.get("end_time")

                # Check for overlaps
                from django.db import models

                overlapping = Availability.objects.filter(
                    doctor=doctor_profile,
                    day=day,
                ).filter(
                    # Either the new start time is within an existing slot
                    # or the new end time is within an existing slot
                    # or the new slot completely contains an existing slot
                    (
                        models.Q(start_time__lte=start_time, end_time__gt=start_time)
                        | models.Q(start_time__lt=end_time, end_time__gte=end_time)
                        | models.Q(start_time__gte=start_time, end_time__lte=end_time)
                    )
                )

                if overlapping.exists():
                    raise serializers.ValidationError(
                        {
                            "time_range": "This availability overlaps with an existing one"
                        }
                    )

                # Save the availability
                serializer.save(doctor=doctor_profile)

        except DoctorProfile.DoesNotExist:
            raise serializers.ValidationError(
                {"doctor": "You must be a doctor to create availability slots"}
            )
        except Exception as e:
            logger.error(f"Error creating availability: {str(e)}", exc_info=True)
            raise serializers.ValidationError(
                {"error": "Failed to create availability. Please try again."}
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
    pagination_class = DoctorsPagination

    def get_queryset(self):
        user = self.request.user

        # Use select_related to optimize queries
        if user.role == "doctor":
            try:
                doctor_profile = DoctorProfile.objects.get(user=user)
                return Teleconsultation.objects.filter(
                    doctor=doctor_profile
                ).select_related("patient", "doctor__user")
            except DoctorProfile.DoesNotExist:
                return Teleconsultation.objects.none()
        else:
            # For patients or other roles
            return Teleconsultation.objects.filter(patient=user).select_related(
                "doctor", "doctor__user"
            )

    def create(self, request, *args, **kwargs):
        """
        Override create method to handle unique constraint errors gracefully.
        """
        try:
            return super().create(request, *args, **kwargs)
        except ValidationError as e:
            # Check if this is a unique constraint error
            if "__all__" in e.detail and any(
                "already exists" in str(msg) for msg in e.detail["__all__"]
            ):
                return Response(
                    {
                        "error": "You already have a teleconsultation scheduled with this doctor at this time."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            # Re-raise other validation errors
            raise
        except IntegrityError as e:
            # Handle database-level integrity errors (like unique constraint violations)
            if (
                "unique constraint" in str(e).lower()
                or "duplicate key" in str(e).lower()
            ):
                return Response(
                    {
                        "error": "You already have a teleconsultation scheduled with this doctor at this time."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            # Log and re-raise other integrity errors
            logger.error(f"Database integrity error: {str(e)}", exc_info=True)
            return Response(
                {"error": "Database constraint violation. Please check your input."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            logger.error(f"Error creating teleconsultation: {str(e)}", exc_info=True)
            return Response(
                {"error": "Failed to create teleconsultation. Please try again."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def update(self, request, *args, **kwargs):
        """
        Override update method to handle validation errors gracefully.
        """
        try:
            return super().update(request, *args, **kwargs)
        except ValidationError as e:
            # Check if this is a unique constraint error
            if "__all__" in e.detail and any(
                "already exists" in str(msg) for msg in e.detail["__all__"]
            ):
                return Response(
                    {
                        "error": "Another teleconsultation is already scheduled with this doctor at this time."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            # For other validation errors, return the error details
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except IntegrityError as e:
            # Handle database-level integrity errors
            logger.error(
                f"Database integrity error during update: {str(e)}", exc_info=True
            )
            return Response(
                {"error": "Database constraint violation. Please check your input."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            logger.error(f"Error updating teleconsultation: {str(e)}", exc_info=True)
            return Response(
                {"error": "Failed to update teleconsultation. Please try again."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def perform_create(self, serializer):
        serializer.save(patient=self.request.user)
