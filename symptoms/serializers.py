from rest_framework import serializers
from .models import Symptom, Condition, SymptomCheck
from .ai import generate_diagnosis
import logging
from django.urls import reverse

logger = logging.getLogger(__name__)


class ConditionSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="condition-detail", lookup_field="pk"
    )

    class Meta:
        model = Condition
        fields = ["id", "url", "name", "severity", "description"]
        read_only_fields = ["id", "url"]


class SymptomCheckSerializer(serializers.ModelSerializer):
    symptoms = serializers.HyperlinkedRelatedField(
        many=True,
        view_name="symptom-detail",
        queryset=Symptom.objects.all(),
        lookup_field="pk",
    )
    conditions = ConditionSerializer(many=True, read_only=True)
    recommendations = serializers.ListField(
        child=serializers.CharField(),
        source="ai_diagnosis.recommendations",
        read_only=True,
    )
    urgency = serializers.CharField(source="ai_diagnosis.urgency", read_only=True)
    links = serializers.SerializerMethodField()

    class Meta:
        model = SymptomCheck
        fields = [
            "id",
            "user",
            "symptoms",
            "conditions",
            "recommendations",
            "urgency",
            "created_at",
            "links",
        ]
        read_only_fields = ["user", "created_at", "conditions"]

    def get_links(self, obj):
        request = self.context.get("request")
        return {
            "self": request.build_absolute_uri(
                reverse("symptom-check-detail", kwargs={"pk": obj.pk})
            ),
            "user": request.build_absolute_uri(
                reverse("user-detail", kwargs={"pk": obj.user.pk})
            ),
        }

    def validate_symptoms(self, value):
        """Validate at least one symptom is provided"""
        if len(value) < 1:
            raise serializers.ValidationError(
                "At least one symptom is required for diagnosis"
            )
        return value

    def create(self, validated_data):
        """Create symptom check with AI integration"""
        try:
            user = self.context["request"].user
            symptoms = validated_data.pop("symptoms")

            # Create check instance
            check = SymptomCheck.objects.create(user=user)
            check.symptoms.set(symptoms)

            # Process AI diagnosis
            diagnosis_data = generate_diagnosis(symptoms)

            if isinstance(diagnosis_data, dict) and "error" in diagnosis_data:
                check.ai_diagnosis = diagnosis_data
                check.save()
                return check

            # Process conditions
            if "conditions" in diagnosis_data:
                conditions = []
                for name in diagnosis_data["conditions"]:
                    condition, _ = Condition.objects.get_or_create(
                        name=name.strip().title()
                    )
                    conditions.append(condition)
                check.conditions.set(conditions)

            # Store structured diagnosis data
            check.ai_diagnosis = {
                "recommendations": diagnosis_data.get("recommendations", []),
                "urgency": diagnosis_data.get("urgency", "unknown"),
            }
            check.save()

            return check

        except Exception as e:
            logger.error(f"Symptom check creation failed: {str(e)}")
            raise serializers.ValidationError(
                {
                    "code": "diagnosis_failed",
                    "message": "Failed to process diagnosis. Please try again.",
                }
            )


class SymptomSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Symptom
        fields = ["id", "url", "name", "description"]
        read_only_fields = ["id", "url"]
        extra_kwargs = {"url": {"view_name": "symptom-detail", "lookup_field": "pk"}}
