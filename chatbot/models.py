from django.db import models
from accounts.models import User


class ChatSession(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="chat_sessions"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    context = models.JSONField(default=dict, blank=True)  # Store conversation context

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "-created_at"]),
        ]


class ChatMessage(models.Model):
    session = models.ForeignKey(
        ChatSession, on_delete=models.CASCADE, related_name="messages"
    )
    content = models.JSONField()  # Stores both input and output
    is_bot = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]
        indexes = [
            models.Index(fields=["session", "created_at"]),
        ]
