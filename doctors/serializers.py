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
    class Meta:
        model = Availability
        fields = ['id', 'day', 'start_time', 'end_time']
        read_only_fields = ['id']

    def validate(self, data):
        existing = Availability.objects.filter(
            doctor=self.context['doctor'],
            day=data['day'],
            start_time__lt=data['end_time'],
            end_time__gt=data['start_time']
        ).exists()
        
        if existing:
            raise serializers.ValidationError("This slot overlaps with existing availability")
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
        ]
        read_only_fields = ["id"]

    def validate(self, attrs):
        scheduled_time = attrs.get("scheduled_time")
        duration = attrs.get("duration")

        if scheduled_time < timezone.now():
            raise serializers.ValidationError(
                {"scheduled_time": "Scheduled time cannot be in the past."}
            )

        if not (15 <= duration <= 60):
            raise serializers.ValidationError(
                {"duration": "Duration must be between 15 and 60 minutes."}
            )

        return attrs

    def validate_doctor(self, value):
        if not value.available:
            raise serializers.ValidationError(
                "Doctor is not available for consultations"
            )
        return value
