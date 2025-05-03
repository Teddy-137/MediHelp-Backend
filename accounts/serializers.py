from django.core.validators import MinLengthValidator
from rest_framework import serializers
from .models import User


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[MinLengthValidator(8)],
        style={"input_type": "password"},
    )
    confirm_password = serializers.CharField(
        write_only=True,
        required=True,
        style={"input_type": "password"},
    )

    class Meta:
        model = User
        fields = [
            "email",
            "first_name",
            "last_name",
            "phone",
            "date_of_birth",
            "password",
            "confirm_password",
        ]

    def validate(self, attrs):
        if attrs["password"] != attrs["confirm_password"]:
            raise serializers.ValidationError(
                {"confirm_password": "Passwords do not match."}
            )
        return attrs

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

    def create(self, validated_data):
        validated_data.pop(
            "confirm_password"
        )  # Remove confirm_password from validated_data
        password = validated_data.pop("password")  # Remove password from validated_data
        user = User(**validated_data)  # Create user without password
        user.set_password(password)  # Set password with proper hashing
        user.save()
        return user


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(
        write_only=True, trim_whitespace=False, style={"input_type": "password"}
    )

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        user = User.objects.filter(email=email).first()

        if not user or not user.check_password(password):
            raise serializers.ValidationError("Invalid email or password.")

        attrs["user"] = user

        return attrs


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "phone",
            "date_of_birth",
            "role",
            "date_joined",
            "last_login",
        ]
        read_only_fields = ["email", "role", "date_joined", "last_login"]
