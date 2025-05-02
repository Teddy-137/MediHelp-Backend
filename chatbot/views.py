from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from .models import ChatSession, ChatMessage
from .serializers import ChatSessionSerializer
from .ai import generate_chat_response, get_fallback_response
import logging

logger = logging.getLogger(__name__)


class ChatViewSet(viewsets.ModelViewSet):
    serializer_class = ChatSessionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return (
            ChatSession.objects.filter(user=self.request.user)
            .prefetch_related("messages")
            .order_by("-created_at")
        )

    @action(detail=False, methods=["post"], url_path="interact")
    def chat_interaction(self, request):
        user = request.user
        message = (request.data.get("message") or "").strip()[
            :500
        ]  # Limit input length

        if not message:
            return Response(
                {"error": "Message cannot be empty"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            with transaction.atomic():
                session, _ = ChatSession.objects.get_or_create(
                    user=user, is_active=True
                )

                # Save user message
                user_msg = ChatMessage.objects.create(
                    session=session, content={"input": message}, is_bot=False
                )

                # Generate AI response
                try:
                    ai_response = generate_chat_response(message)
                except Exception as e:
                    logger.error(f"AI generation failed: {str(e)}", exc_info=True)
                    ai_response = get_fallback_response()

                bot_msg = ChatMessage.objects.create(
                    session=session,
                    content={"input": message, "output": ai_response},
                    is_bot=True,
                )

                return Response(ai_response, status=status.HTTP_200_OK)

        except Exception as e:
            logger.critical(f"Chat transaction failed: {str(e)}", exc_info=True)
            return Response(
                {"error": "Failed to process chat request"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=True, methods=["post"], url_path="close")
    def close_session(self, request, pk=None):
        try:
            session = self.get_object()
            session.is_active = False
            session.save(update_fields=["is_active"])
            return Response({"status": "session closed"})
        except Exception as e:
            logger.error(f"Session close failed: {str(e)}", exc_info=True)
            return Response(
                {"error": "Failed to close session"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
