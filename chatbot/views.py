from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from .models import ChatSession, ChatMessage
from .serializers import ChatSessionSerializer
import logging
import os

logger = logging.getLogger(__name__)

# Try to import from the real AI module, but fall back to mock if it fails
try:
    # Check if GEMINI_API_KEY is set in environment
    if not os.environ.get("GEMINI_API_KEY"):
        logger.warning("GEMINI_API_KEY not set in environment, using mock AI")
        raise ImportError("GEMINI_API_KEY not set")

    from .ai import generate_chat_response, get_fallback_response

    logger.info("Using real AI implementation")
except (ImportError, Exception) as e:
    # Fall back to mock implementation
    logger.warning(f"Using mock AI implementation: {str(e)}")
    from .mock_ai import generate_chat_response, get_fallback_response


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
        raw_message = request.data.get("message", "")

        # Validate message
        if not raw_message or not isinstance(raw_message, str):
            return Response(
                {"error": "Message must be a non-empty string"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Sanitize and limit input length
        message = raw_message.strip()[:500]

        # Log the incoming message
        logger.info(f"Processing chat message from user {user.id}: {message[:50]}...")

        try:
            with transaction.atomic():
                # Get or create an active session
                session, created = ChatSession.objects.get_or_create(
                    user=user,
                    is_active=True,
                    defaults={
                        "context": {"history": []}
                    },  # Initialize empty history for new sessions
                )

                if created:
                    logger.info(
                        f"Created new chat session {session.id} for user {user.id}"
                    )
                else:
                    logger.info(
                        f"Using existing chat session {session.id} for user {user.id}"
                    )

                # Save user message
                ChatMessage.objects.create(
                    session=session, content={"input": message}, is_bot=False
                )

                # Generate AI response with retry logic
                try:
                    logger.info(
                        f"Generating AI response for message: {message[:50]}..."
                    )

                    # Get the session context if it exists
                    session_context = {}

                    # Refresh the session from the database to ensure we have the latest context
                    session.refresh_from_db()

                    # Check if context exists and is not empty
                    if hasattr(session, "context") and session.context:
                        session_context = session.context
                        logger.info(
                            f"Retrieved existing context from session {session.id}: "
                            f"History size: {len(session_context.get('history', []))} messages, "
                            f"Context: {session_context}"
                        )
                    else:
                        # Initialize with empty history if no context exists
                        session_context = {"history": []}
                        logger.warning(
                            f"No context found in session {session.id}, initializing empty context: {session_context}"
                        )

                    # Generate response with context
                    ai_response = generate_chat_response(message, session_context)

                    if not isinstance(ai_response, dict):
                        logger.error(f"Invalid AI response format: {type(ai_response)}")
                        ai_response = get_fallback_response(session_context, message)

                    # Update session context if response contains context
                    if (
                        isinstance(ai_response, dict)
                        and "updated_context" in ai_response
                    ):
                        # Get the updated context from the response
                        updated_context = ai_response.get("updated_context", {})

                        # Debug the context before saving
                        logger.info(f"Context before saving: {updated_context}")

                        # Set the context on the session
                        session.context = updated_context

                        # Make sure to save the session with the updated context
                        session.save(update_fields=["context", "updated_at"])

                        # Verify the context was saved correctly by retrieving it again
                        refreshed_session = ChatSession.objects.get(id=session.id)
                        logger.info(
                            f"Updated session context for session {session.id}: "
                            f"History size: {len(refreshed_session.context.get('history', []))} messages, "
                            f"Context: {refreshed_session.context}"
                        )

                except Exception as e:
                    logger.error(f"AI generation failed: {str(e)}", exc_info=True)
                    # Pass the session context to the fallback response
                    session_context = {}

                    # Refresh the session from the database to ensure we have the latest context
                    try:
                        session.refresh_from_db()
                    except Exception as refresh_error:
                        logger.error(f"Error refreshing session: {str(refresh_error)}")

                    # Check if context exists and is not empty
                    if hasattr(session, "context") and session.context:
                        session_context = session.context
                        logger.info(
                            f"Retrieved existing context for fallback from session {session.id}: "
                            f"History size: {len(session_context.get('history', []))} messages, "
                            f"Context: {session_context}"
                        )
                    else:
                        # Initialize with empty history if no context exists
                        session_context = {"history": []}
                        logger.warning(
                            f"No context found for fallback in session {session.id}, initializing empty context: {session_context}"
                        )
                    ai_response = get_fallback_response(session_context, message)

                # Save bot response
                ChatMessage.objects.create(
                    session=session,
                    content={"input": message, "output": ai_response},
                    is_bot=True,
                )

                # Make sure the session is saved with the updated context
                if (
                    not session._state.adding
                ):  # Check if the session is not a new unsaved instance
                    # Ensure context is properly set before saving
                    if "updated_context" in ai_response and isinstance(
                        ai_response["updated_context"], dict
                    ):
                        session.context = ai_response["updated_context"]
                    elif not session.context:
                        session.context = {"history": []}

                    # Save with explicit update_fields to ensure context is saved
                    session.save(update_fields=["context", "updated_at"])

                    # Verify the context was saved correctly
                    refreshed_session = ChatSession.objects.get(id=session.id)
                    logger.info(
                        f"Saved session {session.id} with updated context: "
                        f"History size: {len(refreshed_session.context.get('history', []))} messages, "
                        f"Context: {refreshed_session.context}"
                    )

                # Format the response for the client
                formatted_response = {
                    "response": ai_response,
                    "session_id": session.id,
                    "context_size": (
                        len(session.context.get("history", []))
                        if hasattr(session, "context") and session.context
                        else 0
                    ),
                }

                logger.info(
                    f"Successfully processed chat message for session {session.id}"
                )
                return Response(formatted_response, status=status.HTTP_200_OK)

        except Exception as e:
            logger.critical(f"Chat transaction failed: {str(e)}", exc_info=True)
            return Response(
                {"error": "Failed to process chat request"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=True, methods=["post"], url_path="close")
    def close_session(
        self, request, pk=None
    ):  # pk is required by DRF but used implicitly in get_object()
        """
        Close a chat session.
        """
        try:
            session = self.get_object()

            # Check if session is already closed
            if not session.is_active:
                return Response(
                    {
                        "status": "already_closed",
                        "message": "Session was already closed",
                    },
                    status=status.HTTP_200_OK,
                )

            # Close the session
            session.is_active = False
            session.save(update_fields=["is_active"])

            logger.info(f"Closed chat session {session.id} for user {request.user.id}")
            return Response(
                {"status": "closed", "message": "Session closed successfully"},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            logger.error(f"Error closing session: {str(e)}", exc_info=True)
            return Response(
                {"error": "Failed to close session", "detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )
