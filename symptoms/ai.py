import os
import json
import logging
import google.generativeai as genai
from django.utils.translation import gettext_lazy as _
from time import sleep

logger = logging.getLogger(__name__)
MAX_RETRIES = 3


def configure_gemini():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        logger.error("GEMINI_API_KEY environment variable not set")
        raise ValueError("GEMINI_API_KEY environment variable not set")
    genai.configure(api_key=api_key)


def generate_diagnosis(symptoms):
    configure_gemini()
    model = genai.GenerativeModel("gemini-2.0-flash")

    symptom_list = [s.name for s in symptoms]
    prompt = f"""Analyze these symptoms: {', '.join(symptom_list)}.
    Respond in raw JSON format only (no markdown) with these keys:
    {{
        "conditions": ["list", "of", "possible", "conditions"],
        "recommendations": ["list", "of", "recommended", "actions"],
        "urgency": "low/medium/high"
    }}"""

    for attempt in range(MAX_RETRIES):
        try:
            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.3, max_output_tokens=500
                ),
                safety_settings={
                    "HARM_CATEGORY_MEDICAL": "BLOCK_NONE",
                },
            )

            content = response.text.strip()
            if content.startswith("```json"):
                content = content.removeprefix("```json").strip()
            if content.endswith("```"):
                content = content.removesuffix("```").strip()

            diagnosis = json.loads(content)

            required_keys = {"conditions", "recommendations", "urgency"}
            if not all(key in diagnosis for key in required_keys):
                raise ValueError("Missing required keys in AI response")

            return diagnosis

        except json.JSONDecodeError:
            logger.warning(f"Invalid JSON response (attempt {attempt+1}): {content}")
            if attempt < MAX_RETRIES - 1:
                sleep(0.5 * (attempt + 1))
                continue
            return {"error": _("Invalid response format from AI service")}

        except Exception as e:
            logger.error(f"AI service error: {str(e)}")
            if attempt < MAX_RETRIES - 1:
                sleep(1)
                continue
            return {"error": _("AI service unavailable"), "details": str(e)}

    return {"error": _("Failed to get valid diagnosis after multiple attempts")}
