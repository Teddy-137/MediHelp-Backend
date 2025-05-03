from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.utils import timezone
from .models import DoctorProfile, Availability, Teleconsultation

User = get_user_model()


class UserPublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "first_name", "last_name", "email", "phone"]
        read_only_fields = ["id", "email", "phone"]


class DoctorProfileSerializer(serializers.ModelSerializer):
    user = UserPublicSerializer(read_only=True)
    license_number = serializers.CharField(read_only=True)

    class Meta:
        model = DoctorProfile
        fields = [
            "id",
            "user",
            "license_number",
            "specialization",
            "consultation_fee",
            "available",
        ]
        read_only_fields = ["id", "user"]


class DoctorRegistrationSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, validators=[validate_password])
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    phone = serializers.CharField()
    license_number = serializers.CharField()
    specialization = serializers.CharField()
    consultation_fee = serializers.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "password",
            "first_name",
            "last_name",
            "phone",
            "license_number",
            "specialization",
            "consultation_fee",
        ]
        read_only_fields = ["id"]

    def create(self, validated_data):
        user_data = {
            "email": validated_data["email"],
            "password": validated_data["password"],
            "first_name": validated_data["first_name"],
            "last_name": validated_data["last_name"],
            "phone": validated_data["phone"],
            "role": "doctor",
        }
        user = User.objects.create_user(**user_data)

        DoctorProfile.objects.create(
            user=user,
            license_number=validated_data["license_number"],
            specialization=validated_data["specialization"],
            consultation_fee=validated_data["consultation_fee"],
        )
        return user

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate_phone(self, value):
        if User.objects.filter(phone=value).exists():
            raise serializers.ValidationError(
                "A user with this phone number already exists."
            )
        return value

    def validate_license_number(self, value):
        if DoctorProfile.objects.filter(license_number=value).exists():
            raise serializers.ValidationError(
                "A doctor with this license number already exists."
            )
        return value

    def to_representation(self, instance):
        doctor_profile = instance.doctorprofile
        return {
            "id": instance.id,
            "email": instance.email,
            "first_name": instance.first_name,
            "last_name": instance.last_name,
        }


class AvailabilitySerializer(serializers.ModelSerializer):
    doctor = serializers.PrimaryKeyRelatedField(
        queryset=DoctorProfile.objects.all(),
        required=False,  # Not required because we'll set it in perform_create
    )

    class Meta:
        model = Availability
        fields = ["id", "doctor", "day", "start_time", "end_time"]
        read_only_fields = ["id"]

    def validate(self, data):
        # Validate time range
        start_time = data.get("start_time")
        end_time = data.get("end_time")
        day = data.get("day")

        # Validate day is not in the past
        if day and day < timezone.now().date():
            raise serializers.ValidationError(
                {"day": "Availability day cannot be in the past"}
            )

        # Only validate times if both are provided
        if start_time and end_time and start_time >= end_time:
            raise serializers.ValidationError(
                {"time_range": "End time must be after start time"}
            )

        # For partial updates (PATCH), we need to get the instance's existing values
        if self.instance:
            # Get values from data or from instance if not in data
            day = data.get("day", self.instance.day)
            start_time = data.get("start_time", self.instance.start_time)
            end_time = data.get("end_time", self.instance.end_time)
            doctor = data.get("doctor", self.instance.doctor)

            # Check for overlapping availability, excluding the current instance
            query = Availability.objects.filter(
                doctor=doctor, day=day, start_time__lt=end_time, end_time__gt=start_time
            ).exclude(pk=self.instance.pk)

            if query.exists():
                raise serializers.ValidationError(
                    {"overlap": "This slot overlaps with existing availability"}
                )

        # For new instances (POST), check if all required fields are present
        elif all(k in data for k in ["day", "start_time", "end_time"]):
            day = data["day"]
            start_time = data["start_time"]
            end_time = data["end_time"]

            # Get doctor from data or context
            doctor = data.get("doctor")
            if not doctor and "doctor" in self.context:
                doctor = self.context["doctor"]

            if doctor:
                # Check for overlapping availability
                query = Availability.objects.filter(
                    doctor=doctor,
                    day=day,
                    start_time__lt=end_time,
                    end_time__gt=start_time,
                )

                if query.exists():
                    raise serializers.ValidationError(
                        {"overlap": "This slot overlaps with existing availability"}
                    )

        return data


class TeleconsultationSerializer(serializers.ModelSerializer):
    patient = UserPublicSerializer(read_only=True)
    patient_id = serializers.PrimaryKeyRelatedField(
        source="patient", queryset=User.objects.all(), write_only=True
    )
    doctor = DoctorProfileSerializer(read_only=True)
    doctor_id = serializers.PrimaryKeyRelatedField(
        source="doctor", queryset=DoctorProfile.objects.all(), write_only=True
    )

    class Meta:
        model = Teleconsultation
        fields = [
            "id",
            "patient",
            "patient_id",
            "doctor",
            "doctor_id",
            "scheduled_time",
            "duration",
            "meeting_url",
            "status",
        ]
        read_only_fields = ["id"]

    def validate(self, attrs):
        # Validate scheduled_time if it's being updated
        scheduled_time = attrs.get("scheduled_time")
        if scheduled_time and scheduled_time < timezone.now():
            raise serializers.ValidationError(
                {"scheduled_time": "Scheduled time cannot be in the past."}
            )

        # Validate duration if it's being updated
        duration = attrs.get("duration")
        if duration and not (15 <= duration <= 180):
            raise serializers.ValidationError(
                {"duration": "Duration must be between 15 and 180 minutes."}
            )

        # Validate status if it's being updated
        status = attrs.get("status")
        if status and status not in [
            choice[0] for choice in Teleconsultation.Status.choices
        ]:
            raise serializers.ValidationError(
                {
                    "status": f"Invalid status. Must be one of: {', '.join([choice[0] for choice in Teleconsultation.Status.choices])}"
                }
            )

        return attrs

    def validate_doctor(self, value):
        if not value.available:
            raise serializers.ValidationError(
                "Doctor is not available for consultations"
            )
        return value
