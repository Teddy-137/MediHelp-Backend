from rest_framework import serializers
from .models import Symptom, Condition, SymptomCheck
from .ai import generate_diagnosis
import logging
from django.urls import reverse
from django.utils.encoding import force_str

logger = logging.getLogger(__name__)


def _clean_json(value):
    """Recursively convert values to JSON-safe types"""
    if isinstance(value, dict):
        return {k: _clean_json(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_clean_json(v) for v in value]
    return force_str(value)


class SymptomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Symptom
        fields = ["id", "name", "description", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class ConditionSerializer(serializers.ModelSerializer):
    severity_display = serializers.CharField(
        source="get_severity_display", read_only=True
    )

    class Meta:
        model = Condition
        fields = [
            "id",
            "name",
            "severity",
            "severity_display",
            "description",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class SymptomCheckSerializer(serializers.ModelSerializer):
    symptoms = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Symptom.objects.all(),
        help_text="List of symptom IDs to analyze",
    )
    conditions = ConditionSerializer(many=True, read_only=True)
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    diagnosis = serializers.SerializerMethodField()

    class Meta:
        model = SymptomCheck
        fields = ["id", "user", "symptoms", "conditions", "diagnosis", "created_at"]
        read_only_fields = ["user", "conditions", "created_at"]

    def get_diagnosis(self, obj):
        """Structure AI diagnosis data for output"""
        if obj.ai_diagnosis is None:
            return {
                "urgency": "unknown",
                "recommendations": [],
            }
        return {
            "urgency": obj.ai_diagnosis.get("urgency", "unknown"),
            "recommendations": obj.ai_diagnosis.get("recommendations", []),
        }

    def validate_symptoms(self, value):
        """Ensure at least one symptom is provided"""
        if not value:
            raise serializers.ValidationError("At least one symptom is required")
        return value

    def create(self, validated_data):
        """Create symptom check with AI integration"""
        try:
            user = self.context["request"].user
            symptoms = validated_data.pop("symptoms")

            # Create check instance
            check = SymptomCheck.objects.create(user=user)
            check.symptoms.set(symptoms)

            # Generate AI diagnosis
            raw_data = generate_diagnosis(symptoms)
            diagnosis_data = _clean_json(raw_data)

            # Store and process results
            check.ai_diagnosis = diagnosis_data

            # Link conditions if available
            if isinstance(diagnosis_data, dict):
                conditions = Condition.objects.filter(
                    name__in=[
                        name.strip().title()
                        for name in diagnosis_data.get("conditions", [])
                    ]
                )
                check.conditions.set(conditions)

            check.save()
            return check

        except Exception as e:
            logger.error(f"Symptom check creation failed: {str(e)}")
            raise serializers.ValidationError(
                {
                    "code": "diagnosis_failed",
                    "message": "Could not process diagnosis. Please try again.",
                }
            )
