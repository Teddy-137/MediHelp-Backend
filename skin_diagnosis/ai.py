import json
import logging
from django.conf import settings
from google.generativeai import configure, GenerativeModel
from google.api_core.exceptions import GoogleAPIError
import mimetypes  # Import mimetypes to guess the file type

logger = logging.getLogger(__name__)


def analyze_skin_image(image_path: str) -> dict:
    """
    Returns structured analysis:
    {
        "conditions": list[str],
        "confidence": float,
        "recommendations": list[str],
        "urgency": "low|medium|high",
        "raw_response": str
    }
    """
    try:
        if not getattr(settings, "GEMINI_API_KEY", None):
            raise ValueError("Missing Gemini API key in settings")

        configure(api_key="AIzaSyCc_Gw2Oi9NO3s96du3N9bhNQlH3fXQbBo")
        # Use the appropriate model for vision tasks
        model = GenerativeModel("models/gemini-1.5-flash")

        prompt = """Analyze this skin condition image and provide:
        1. Top 3 possible conditions (array)
        2. Confidence score (0-1)
        3. 3 recommended actions (array)
        4. Urgency level (low/medium/high)

        Return ONLY valid JSON format:
        {
            "conditions": [],
            "confidence": 0.0,
            "recommendations": [],
            "urgency": ""
        }"""

        # --- FIX START ---
        # Read the image file content
        try:
            with open(image_path, "rb") as f:
                image_data = f.read()
        except FileNotFoundError:
            logger.error(f"Image file not found at {image_path}")
            return {"error": "Image file not found"}
        except IOError as e:
            logger.error(f"Could not read image file {image_path}: {e}")
            return {"error": "Could not read image file"}

        # Guess the MIME type of the image
        mime_type, _ = mimetypes.guess_type(image_path)
        if mime_type is None or not mime_type.startswith("image/"):
            logger.warning(
                f"Could not determine image MIME type or it's not an image: {image_path}"
            )
            # Fallback to a common type or return error
            mime_type = "image/jpeg"  # Or handle as an error

        # Pass the prompt and image data with MIME type to the model
        image_part = {"mime_type": mime_type, "data": image_data}

        response = model.generate_content([prompt, image_part])
        # --- FIX END ---

        try:
            # This parsing logic is fragile and depends on the model's exact output format.
            # A more robust approach might be needed if the format varies.
            json_str = response.text.split("```json")[1].split("```")[0].strip()
            result = json.loads(json_str)
            result["raw_response"] = response.text
            return result
        except (IndexError, json.JSONDecodeError) as e:
            logger.warning(
                f"Failed to parse response: {e}. Raw response: {response.text}"
            )
            return {
                "error": "Analysis format error",
                "raw_response": response.text,
                "conditions": [],
                "confidence": 0.0,
                "recommendations": ["Consult a dermatologist"],
                "urgency": "medium",
            }
        except AttributeError:
            # Handle cases where response might not have a .text attribute
            logger.warning(
                f"Response object has no text attribute. Response: {response}"
            )
            return {
                "error": "Unexpected response format",
                "raw_response": str(response),  # Try to represent response as string
                "conditions": [],
                "confidence": 0.0,
                "recommendations": ["Consult a dermatologist"],
                "urgency": "medium",
            }

    except GoogleAPIError as e:
        logger.error(f"Gemini API error: {str(e)}")
        return {"error": "AI service unavailable"}
    except ValueError as e:  # Catch the specific ValueError for missing API key
        logger.error(f"Configuration error: {str(e)}")
        return {"error": str(e)}
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return {"error": "Analysis failed"}
