from rest_framework import serializers
from .models import ChatSession, ChatMessage

class ChatMessageSerializer(serializers.ModelSerializer):
    message_type = serializers.CharField(source='get_message_type_display', read_only=True)
    metadata = serializers.JSONField(read_only=True)

    class Meta:
        model = ChatMessage
        fields = ["message_type", "content", "created_at", "metadata"]
        read_only_fields = ["message_type", "created_at", "metadata"]

class ChatSessionSerializer(serializers.ModelSerializer):
    messages = ChatMessageSerializer(many=True, read_only=True)
    status = serializers.CharField(source='get_status_display', read_only=True)
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = ChatSession
        fields = ["id", "user", "status", "context", "created_at", "messages"]
        read_only_fields = ["id", "user", "status", "created_at", "messages"]

    def validate_context(self, value):
        """Sanitize context input"""
        if not isinstance(value, dict):
            raise serializers.ValidationError("Context must be a JSON object")
        return {k: v for k, v in value.items() if k in ["history", "preferences"]}