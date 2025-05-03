# firstaid/serializers.py
from rest_framework import serializers
from .models import FirstAidInstruction, HomeRemedy
from symptoms.models import Condition, Symptom


class FirstAidConditionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Condition
        fields = ["id", "name", "severity"]
        read_only = True


class FirstAidInstructionSerializer(serializers.ModelSerializer):
    condition = FirstAidConditionSerializer(read_only=True)
    severity_level_display = serializers.CharField(
        source="get_severity_level_display", read_only=True
    )
    type = serializers.SerializerMethodField()

    class Meta:
        model = FirstAidInstruction
        fields = [
            "id",
            "type",
            "title",
            "condition",
            "steps",
            "severity_level",
            "severity_level_display",
            "description",
            "created_at",
        ]
        read_only_fields = ["type", "created_at"]

    def get_type(self, obj):
        return "firstaid"


class HomeRemedySerializer(serializers.ModelSerializer):
    symptoms = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Symptom.objects.all(), help_text="Related symptom IDs"
    )
    type = serializers.SerializerMethodField()

    class Meta:
        model = HomeRemedy
        fields = [
            "id",
            "type",
            "name",
            "symptoms",
            "ingredients",
            "preparation",
            "created_at",
        ]
        read_only_fields = ["type", "created_at"]

    def get_type(self, obj):
        return "homeremedy"

    # Removed redundant validation as it's already handled by validate_json_array in the model
