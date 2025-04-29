import os
import google.generativeai as genai
from django.utils.translation import gettext_lazy as _


def configure_gemini():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not set")
    genai.configure(api_key=api_key)


def generate_diagnosis(symptoms):
    try:
        configure_gemini()
        model = genai.GenerativeModel("gemini-2.0-flash")
        symptom_list = [s.name for s in symptoms]

        prompt = f"""Analyze these symptoms: {', '.join(symptom_list)}.
        Respond in JSON format:
        {{
            "conditions": ["list", "of", "conditions"],
            "recommendations": ["list", "of", "steps"],
            "urgency": "low/medium/high"
        }}"""

        response = model.generate_content(prompt)
        return response.text

    except Exception as e:
        return {"error": _("AI service unavailable"), "details": str(e)}
