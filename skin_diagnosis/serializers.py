from rest_framework import serializers
from .models import SkinDiagnosis
from .ai import analyze_skin_image
import logging

logger = logging.getLogger(__name__)


class SkinDiagnosisSerializer(serializers.ModelSerializer):
    class Meta:
        model = SkinDiagnosis
        fields = [
            "id",
            "user",
            "image",
            "diagnosis",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "user",
            "diagnosis",
            "status",
            "created_at",
            "updated_at",
        ]

    def validate_image(self, value):
        valid_extensions = ["jpg", "jpeg", "png", "webp"]
        extension = value.name.split(".")[-1].lower()

        if extension not in valid_extensions:
            raise serializers.ValidationError(
                f"Unsupported file extension. Allowed: {', '.join(valid_extensions)}"
            )

        max_size = 4 * 1024 * 1024
        if value.size > max_size:
            raise serializers.ValidationError(
                f"File size exceeds {max_size//1024//1024}MB limit"
            )

        return value

    def create(self, validated_data):
        try:
            instance = SkinDiagnosis.objects.create(**validated_data)
            result = analyze_skin_image(instance.image.path)

            if result.get("error"):
                instance.status = SkinDiagnosis.DiagnosisStatus.FAILED
                instance.diagnosis = {"error": result["error"]}
            else:
                instance.status = SkinDiagnosis.DiagnosisStatus.COMPLETED
                instance.diagnosis = result

            instance.save()
            return instance

        except Exception as e:
            logger.error(f"Diagnosis creation failed: {str(e)}")
            raise serializers.ValidationError(
                "Could not process diagnosis. Please try again."
            )
