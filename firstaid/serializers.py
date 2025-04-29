from rest_framework import serializers
from .models import FirstAidInstruction, HomeRemedy
from symptoms.models import Condition, Symptom


class ConditionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Condition
        fields = ["id", "name", "severity"]


class FirstAidInstructionSerializer(serializers.ModelSerializer):
    condition = ConditionSerializer(read_only=True)
    condition_id = serializers.PrimaryKeyRelatedField(
        queryset=Condition.objects.all(),
        source="condition",
        write_only=True,
        help_text="ID of related condition",
    )
    severity_level_display = serializers.CharField(source='get_severity_level_display', read_only=True)

    class Meta:
        model = FirstAidInstruction
        fields = ["id", "title", "condition", "condition_id", "steps", "severity_level", "severity_level_display", "description", "created_at"]


class HomeRemedySerializer(serializers.ModelSerializer):
    symptoms = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Symptom.objects.all(),
        help_text="List of symptom IDs this remedy addresses",
    )

    class Meta:
        model = HomeRemedy
        fields = ["id", "name", "symptoms", "ingredients", "preparation", "created_at"]
