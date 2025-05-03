"""
Mock implementation of the AI module for testing purposes.
This can be used when the Gemini API is not available.
"""

import logging
import json
from time import sleep

logger = logging.getLogger(__name__)

# Use the same prompt template as the real AI implementation
CHAT_PROMPT_TEMPLATE = """
You are a medical assistant for Ethiopian patients. Respond in friendly, simple English.
Analyze this message: {user_input}

If it contains:
1. Specific symptoms -> Use symptom analysis mode
2. General health questions -> Provide helpful advice
3. Requests for first aid -> Give step-by-step guidance

Always respond with valid JSON format (no markdown) using one of these structures:

Symptom Analysis Mode:
{{
  "mode": "symptoms",
  "conditions": ["condition1", "condition2"],
  "recommendations": ["step1", "step2"],
  "urgency": "low/medium/high"
}}

General Advice Mode:
{{
  "mode": "advice",
  "response": "helpful information here"
}}

First Aid Mode:
{{
  "mode": "firstaid",
  "procedure": "step-by-step instructions",
  "warning": "important caution note"
}}
"""


def _validate_response(response_data):
    """
    Ensure AI response matches expected structure.
    This mimics the validation in the real AI implementation.
    """
    valid_modes = ["symptoms", "advice", "firstaid", "error"]
    mode = response_data.get("mode")

    if mode not in valid_modes:
        raise ValueError(f"Invalid response mode: {mode}")

    required_fields = {
        "symptoms": ["conditions", "recommendations", "urgency"],
        "advice": ["response"],
        "firstaid": ["procedure", "warning"],
        "error": ["response"],
    }.get(mode, [])

    missing = [field for field in required_fields if field not in response_data]
    if missing:
        raise ValueError(
            f"Missing required fields for {mode} mode: {', '.join(missing)}"
        )

    return response_data


def _enhance_with_symptom_checker(response_data):
    """
    Enhance symptom responses with numbered recommendations.
    This mimics the enhancement in the real AI implementation.
    """
    if isinstance(response_data.get("recommendations"), list):
        response_data["recommendations"] = [
            f"{idx+1}. {step.strip()}"
            for idx, step in enumerate(response_data["recommendations"])
            if step.strip()
        ]
    return response_data


def generate_chat_response(user_input, context=None, retry_count=0):
    """
    Generate a mock chat response for testing purposes.

    Args:
        user_input (str): The user's message
        context (dict, optional): The conversation context
        retry_count (int): Current retry attempt (used internally)

    Returns:
        dict: A mock response that matches the format of the real AI
    """
    logger.info(f"Generating mock response for: {user_input}")

    # Initialize empty context if none provided
    if context is None:
        context = {}
        logger.warning("Context is None, initializing empty context")
    else:
        logger.info(f"Received context: {context}")

    # Extract history from context
    history = context.get("history", [])
    if not history:
        logger.warning("No history found in context, initializing empty history")
    else:
        logger.info(f"Extracted history from context: {len(history)} messages")

    # Log the history for debugging
    if history:
        logger.info(f"Found {len(history)} previous messages in history")
        # Log the last 3 exchanges (or fewer if there aren't 3)
        for i, entry in enumerate(history[-6:]):  # Show up to 3 exchanges (6 messages)
            role = entry.get("role", "unknown")
            content_preview = str(entry.get("content", ""))[:50]
            logger.info(f"History [{i}]: {role}: {content_preview}...")

    try:
        # Detect headache-related keywords
        headache_keywords = ["headache", "migraine", "head pain", "head ache"]
        if any(keyword in user_input.lower() for keyword in headache_keywords):
            response_data = {
                "mode": "symptoms",
                "conditions": ["Tension headache", "Migraine", "Dehydration"],
                "recommendations": [
                    "Rest in a quiet, dark room",
                    "Drink plenty of water",
                    "Take over-the-counter pain relievers if appropriate",
                    "Apply a cold or warm compress to your head",
                ],
                "urgency": "low",
            }

            # Enhance with symptom checker (like the real AI)
            response_data = _enhance_with_symptom_checker(response_data)

            # Create new history entry
            new_history = history + [
                {"role": "user", "content": user_input},
                {
                    "role": "assistant",
                    "content": "I've analyzed your headache symptoms.",
                },
            ]

            # Limit history to last 3 exchanges (6 messages)
            if len(new_history) > 6:
                new_history = new_history[-6:]
                logger.info(f"Trimmed history to last 3 exchanges (6 messages)")

            # Add updated context
            response_data["updated_context"] = {
                "history": new_history,
                "last_query": user_input,
            }

            return response_data

        # Detect fever-related keywords
        fever_keywords = ["fever", "temperature", "hot", "chills"]
        if any(keyword in user_input.lower() for keyword in fever_keywords):
            response_data = {
                "mode": "symptoms",
                "conditions": ["Common cold", "Flu", "Infection"],
                "recommendations": [
                    "Rest and stay hydrated",
                    "Take acetaminophen or ibuprofen to reduce fever",
                    "Use a light blanket if you have chills",
                    "Seek medical attention if fever is high or persistent",
                ],
                "urgency": "medium",
            }

            # Enhance with symptom checker (like the real AI)
            response_data = _enhance_with_symptom_checker(response_data)

            # Create new history entry
            new_history = history + [
                {"role": "user", "content": user_input},
                {
                    "role": "assistant",
                    "content": "I've analyzed your fever symptoms.",
                },
            ]

            # Limit history to last 3 exchanges (6 messages)
            if len(new_history) > 6:
                new_history = new_history[-6:]
                logger.info(f"Trimmed history to last 3 exchanges (6 messages)")

            # Add updated context
            response_data["updated_context"] = {
                "history": new_history,
                "last_query": user_input,
            }

            return response_data

        # Detect pregnancy-related keywords
        pregnancy_keywords = [
            "pregnant",
            "pregnancy",
            "expecting",
            "baby",
            "trimester",
            "birth",
        ]
        if any(keyword in user_input.lower() for keyword in pregnancy_keywords):
            response_data = {
                "mode": "advice",
                "response": "Congratulations on your pregnancy! It's important to schedule regular prenatal check-ups, take prenatal vitamins with folic acid, maintain a balanced diet, stay hydrated, and get adequate rest. Would you like more specific advice about pregnancy care?",
            }

            # Create new history entry
            new_history = history + [
                {"role": "user", "content": user_input},
                {
                    "role": "assistant",
                    "content": "I've provided pregnancy advice.",
                },
            ]

            # Limit history to last 3 exchanges (6 messages)
            if len(new_history) > 6:
                new_history = new_history[-6:]
                logger.info(f"Trimmed history to last 3 exchanges (6 messages)")

            # Add updated context
            response_data["updated_context"] = {
                "history": new_history,
                "last_query": user_input,
            }

            return response_data

        # Detect first aid keywords
        firstaid_keywords = ["cut", "bleeding", "wound", "burn", "bandage", "first aid"]
        if any(keyword in user_input.lower() for keyword in firstaid_keywords):
            response_data = {
                "mode": "firstaid",
                "procedure": "1. Clean the wound with clean water\n2. Apply gentle pressure to stop bleeding\n3. Apply an antiseptic if available\n4. Cover with a clean bandage\n5. Seek medical attention for deep wounds",
                "warning": "Seek immediate medical attention for severe bleeding or deep wounds.",
            }

            # Create new history entry
            new_history = history + [
                {"role": "user", "content": user_input},
                {
                    "role": "assistant",
                    "content": "I've provided first aid guidance.",
                },
            ]

            # Limit history to last 3 exchanges (6 messages)
            if len(new_history) > 6:
                new_history = new_history[-6:]
                logger.info(f"Trimmed history to last 3 exchanges (6 messages)")

            # Add updated context
            response_data["updated_context"] = {
                "history": new_history,
                "last_query": user_input,
            }

            return response_data

        # Check if this is a follow-up question by analyzing history
        is_follow_up = False
        previous_topics = []
        previous_symptoms = []

        # Extract topics and symptoms from history
        if len(history) >= 2:  # At least one exchange
            for entry in history:
                if entry.get("role") == "assistant":
                    content = entry.get("content", "")
                    if "headache" in content.lower() or "migraine" in content.lower():
                        previous_symptoms.append("headache")
                    if "fever" in content.lower() or "temperature" in content.lower():
                        previous_symptoms.append("fever")
                    if "first aid" in content.lower() or "wound" in content.lower():
                        previous_topics.append("first aid")
                    if "pregnancy" in content.lower() or "pregnant" in content.lower():
                        previous_topics.append("pregnancy")

            # Remove duplicates
            previous_symptoms = list(set(previous_symptoms))
            previous_topics = list(set(previous_topics))

            # Determine if this is a follow-up
            follow_up_phrases = [
                "still",
                "again",
                "more",
                "another",
                "also",
                "continue",
                "follow up",
                "following up",
            ]
            if any(phrase in user_input.lower() for phrase in follow_up_phrases):
                is_follow_up = True

        # Generate response based on conversation history
        if is_follow_up and (previous_symptoms or previous_topics):
            logger.info(
                f"Detected follow-up question about: {', '.join(previous_symptoms + previous_topics)}"
            )

            if "headache" in previous_symptoms:
                response_data = {
                    "mode": "advice",
                    "response": f"Regarding your headache that we discussed earlier: If over-the-counter pain relievers and rest haven't helped after 24 hours, or if the headache is severe or accompanied by other symptoms like confusion or stiff neck, you should consult a healthcare provider. Would you like me to provide more specific advice about your headache?",
                }
            elif "fever" in previous_symptoms:
                response_data = {
                    "mode": "advice",
                    "response": f"About your fever that we discussed earlier: If it persists for more than 3 days, rises above 103°F (39.4°C), or is accompanied by severe symptoms, you should seek medical attention. Is your fever still present, and have you noticed any new symptoms?",
                }
            elif "first aid" in previous_topics:
                response_data = {
                    "mode": "advice",
                    "response": f"Regarding the first aid situation we discussed: How is the wound healing? Remember to keep it clean and watch for signs of infection such as increased redness, swelling, warmth, or pus. Would you like more specific advice about wound care?",
                }
            elif "pregnancy" in previous_topics:
                response_data = {
                    "mode": "advice",
                    "response": f"Regarding your pregnancy that we discussed earlier: It's important to continue with regular prenatal check-ups. Common questions at this stage might be about diet, exercise, and managing common pregnancy symptoms. Is there a specific aspect of pregnancy care you'd like more information about?",
                }
            else:
                response_data = {
                    "mode": "advice",
                    "response": f"I remember our previous conversation. Is there something specific about what we discussed that you'd like more information on?",
                }
        else:
            # Default response for other queries
            response_data = {
                "mode": "advice",
                "response": f"I understand you're saying: '{user_input}'. If you're experiencing health issues, please describe your symptoms in detail so I can provide better guidance.",
            }

        # Create new history entry
        new_history = history + [
            {"role": "user", "content": user_input},
            {
                "role": "assistant",
                "content": "I've provided some general health advice.",
            },
        ]

        # Limit history to last 3 exchanges (6 messages)
        if len(new_history) > 6:
            new_history = new_history[-6:]
            logger.info(f"Trimmed history to last 3 exchanges (6 messages)")

        # Add updated context
        response_data["updated_context"] = {
            "history": new_history,
            "last_query": user_input,
        }

        return response_data

    except Exception as e:
        logger.error(f"Error generating mock response: {str(e)}", exc_info=True)

        # Create new history entry for the error
        new_history = history + [
            {"role": "user", "content": user_input},
            {
                "role": "assistant",
                "content": "I had trouble understanding that.",
            },
        ]

        # Limit history to last 3 exchanges (6 messages)
        if len(new_history) > 6:
            new_history = new_history[-6:]
            logger.info(f"Trimmed history to last 3 exchanges (6 messages)")

        return {
            "mode": "error",
            "response": "I'm having trouble understanding. Could you rephrase your question?",
            "updated_context": {"history": new_history, "last_query": user_input},
        }


def get_fallback_response(context=None, user_input=""):
    """
    Provide a fallback response when the main response generation fails.

    Args:
        context (dict, optional): The conversation context
        user_input (str, optional): The user's message that caused the fallback

    Returns:
        dict: A fallback response with updated context
    """
    # Initialize empty context if none provided
    if context is None:
        context = {}
        logger.warning("Fallback: Context is None, initializing empty context")
    else:
        logger.info(f"Fallback: Received context: {context}")

    # Extract history from context
    history = context.get("history", [])
    if not history:
        logger.warning(
            "Fallback: No history found in context, initializing empty history"
        )
    else:
        logger.info(
            f"Fallback: Extracted history from context: {len(history)} messages"
        )

    # Create new history entry for the fallback
    if user_input:
        new_history = history + [
            {"role": "user", "content": user_input},
            {
                "role": "assistant",
                "content": "I had trouble processing that request.",
            },
        ]

        # Limit history to last 3 exchanges (6 messages)
        if len(new_history) > 6:
            new_history = new_history[-6:]
            logger.info(f"Trimmed history to last 3 exchanges (6 messages)")

        updated_context = {"history": new_history, "last_query": user_input}
    else:
        # If no user input provided, just pass through the context
        updated_context = context

    return {
        "mode": "error",
        "response": "I'm having trouble understanding. Could you rephrase your question?",
        "updated_context": updated_context,
    }
