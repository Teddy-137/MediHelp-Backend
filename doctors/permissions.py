from rest_framework import permissions


class IsDoctorOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.role == "doctor"

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user


class IsDoctorProfileOwner(permissions.BasePermission):
    """
    Permission class that ensures a doctor can only modify their own profile.
    Superusers can modify any profile.
    """

    def has_permission(self, request, view):
        # Allow all authenticated users to list and read
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Allow read access to all authenticated users
        if request.method in permissions.SAFE_METHODS:
            return True

        # For write operations, only allow the owner or superusers
        return obj.user == request.user or request.user.is_superuser


class IsPatientOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        # Allow all authenticated users to list and create
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # For read operations, allow both the patient and the doctor
        if request.method in permissions.SAFE_METHODS:
            # Check if the user is the patient
            is_patient = obj.patient == request.user

            # Check if the user is the doctor
            is_doctor = False
            if hasattr(obj, "doctor") and hasattr(obj.doctor, "user"):
                is_doctor = obj.doctor.user == request.user

            # Allow access if the user is either the patient or the doctor
            return is_patient or is_doctor

        # For write operations, check if it's a status update by a doctor
        if (
            request.method == "PATCH"
            and "status" in request.data
            and len(request.data) == 1
        ):
            # Validate the status value
            from .models import Teleconsultation

            valid_statuses = [choice[0] for choice in Teleconsultation.Status.choices]
            if request.data["status"] not in valid_statuses:
                return False

            # Allow doctors to update only the status field
            if hasattr(obj, "doctor") and hasattr(obj.doctor, "user"):
                is_doctor = obj.doctor.user == request.user
                if is_doctor:
                    return True

        # For other write operations, only allow the patient
        return obj.patient == request.user
