from rest_framework import serializers
from .models import Article, Video
from symptoms.serializers import ConditionSerializer, SymptomSerializer
from symptoms.models import Condition, Symptom


class ArticleSerializer(serializers.ModelSerializer):
    related_conditions = ConditionSerializer(many=True, read_only=True)
    condition_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Condition.objects.all(),
        source="related_conditions",
        write_only=True,
        help_text="List of related condition IDs",
    )

    class Meta:
        model = Article
        fields = [
            "id",
            "title",
            "summary",
            "content",
            "cover_image",
            "tags",
            "is_published",
            "related_conditions",
            "condition_ids",
            "published_date",
            "updated_at",
        ]
        read_only_fields = ["published_date", "updated_at"]


class VideoSerializer(serializers.ModelSerializer):
    related_symptoms = SymptomSerializer(many=True, read_only=True)
    symptom_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Symptom.objects.all(),
        source="related_symptoms",
        write_only=True,
        help_text="List of related symptom IDs",
    )

    class Meta:
        model = Video
        fields = [
            "id",
            "title",
            "video_url",
            "duration_minutes",
            "related_symptoms",
            "symptom_ids",
            "is_published",
            "published_date",
            "updated_at",
        ]
        read_only_fields = ["published_date", "updated_at"]
