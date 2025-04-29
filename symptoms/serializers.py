from rest_framework import serializers
from .models import Symptom, Condition, SymptomCheck
import json
from .ai import generate_diagnosis


class SymptomCheckSerializer(serializers.ModelSerializer):
    symptoms = serializers.PrimaryKeyRelatedField(
        queryset=Symptom.objects.all(), many=True
    )

    class Meta:
        model = SymptomCheck
        fields = ["symptoms", "conditions", "ai_diagnosis", "created_at"]
        read_only_fields = ["conditions", "ai_diagnosis", "created_at"]

    def create(self, validated_data):
        symptoms = validated_data.pop("symptoms")
        instance = SymptomCheck.objects.create(user=self.context["request"].user)
        instance.symptoms.set(symptoms)

        raw_diagnosis = generate_diagnosis(symptoms)

        if isinstance(raw_diagnosis, dict) and "error" in raw_diagnosis:
            instance.ai_diagnosis = raw_diagnosis
            instance.save()
            return instance

        try:
            diagnosis_data = json.loads(raw_diagnosis)
        except json.JSONDecodeError:
            diagnosis_data = {"error": "Invalid JSON format"}

        valid_conditions = []
        for name in diagnosis_data.get("conditions", []):
            condition, _ = Condition.objects.get_or_create(name=name)
            valid_conditions.append(condition)

        instance.conditions.set(valid_conditions)
        instance.ai_diagnosis = diagnosis_data
        instance.save()

        return instance
