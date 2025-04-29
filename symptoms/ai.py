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
    """
    Call Google Gemini to analyze a list of symptoms.
    Returns a dict with 'conditions', 'recommendations', 'urgency' on success,
    or {'error': ..., 'details': ...} on failure.
    """
    configure_gemini()
    model = genai.GenerativeModel("gemini-2.0-flash")

    symptom_list = [s.name for s in symptoms]
    prompt = (
        f"Analyze these symptoms: {', '.join(symptom_list)}. "
        "Respond only with raw JSON, no markdown, using keys: "
        "conditions (list of condition names), recommendations (list of steps), urgency (low/medium/high)."
    )

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            logger.info(f"Gemini attempt {attempt}: sending prompt")
            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.3,
                    max_output_tokens=500,
                ),
                # remove safety_settings to simplify initial debugging
            )
            raw = response.text.strip()
            logger.debug(f"Raw Gemini response: {raw}")

            # strip code fences if present
            if raw.startswith("```json"):
                raw = raw[len("```json"):].strip()
            if raw.endswith("```"):
                raw = raw[:-3].strip()

            diagnosis = json.loads(raw)
            # ensure required keys
            missing = {k for k in ["conditions","recommendations","urgency"] if k not in diagnosis}
            if missing:
                raise ValueError(f"Missing keys: {missing}")
            return diagnosis

        except json.JSONDecodeError as je:
            logger.warning(f"JSON parse error on attempt {attempt}: {je}")
        except Exception as e:
            logger.error(f"Gemini error on attempt {attempt}: {e}")

        if attempt < MAX_RETRIES:
            sleep(attempt * 0.5)

    return {"error": str(_("Failed to get valid diagnosis after multiple attempts"))}
