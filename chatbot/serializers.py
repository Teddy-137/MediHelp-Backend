from rest_framework import serializers
from .models import ChatSession, ChatMessage


class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ["content", "is_bot", "created_at"]
        read_only_fields = ["is_bot", "created_at"]


class ChatSessionSerializer(serializers.ModelSerializer):
    messages = ChatMessageSerializer(many=True, read_only=True)

    class Meta:
        model = ChatSession
        fields = ["id", "user", "created_at", "is_active", "messages"]
        read_only_fields = ["user", "created_at", "is_active"]
