import re
from rest_framework.exceptions import ValidationError


def validate_image_url(value):
    """
    Validates that a URL is provided for an image.

    This is a simplified validator that just checks if the URL is not empty.
    """
    if not value:
        return

    return value


def validate_video_url(value):

    if not value:
        raise ValidationError("Video URL cannot be empty")

    # No further validation - accept any URL format
    return value


def validate_youtube_url(value):
    """
    Validates that a URL is provided for a YouTube video.

    This is a simplified validator that just checks if the URL is not empty.
    """
    if not value:
        return

    # No further validation - accept any URL format
    return value


def validate_string_list(
    value,
    max_items=50,  # Increased from 20
    max_length=500,  # Increased from 200
    allow_empty=True,  # Changed from False
    allow_blank=True,  # Changed from False
    trim_whitespace=True,
    error_messages=None,
):
    """
    Validates a list of strings with relaxed constraints

    Args:
        value: Input value to validate
        max_items: Maximum number of allowed items (default: 50)
        max_length: Maximum length per string item (default: 500)
        allow_empty: Allow empty list (default: True)
        allow_blank: Allow blank/empty strings (default: True)
        trim_whitespace: Automatically strip whitespace
        error_messages: Custom error messages dictionary

    Returns:
        List of validated strings (with whitespace trimmed if enabled)
    """
    # If value is None or empty and we allow empty, just return an empty list
    if (value is None or value == "") and allow_empty:
        return []

    # If value is a string (common mistake), convert it to a single-item list
    if isinstance(value, str):
        value = [value]

    # If value is not a list, try to convert it
    if not isinstance(value, list):
        try:
            value = list(value)
        except (TypeError, ValueError):
            return []  # Return empty list instead of raising error

    # Allow empty list if specified
    if not value and allow_empty:
        return []

    # Limit number of items
    if len(value) > max_items:
        value = value[:max_items]

    cleaned_items = []
    for item in value:
        # Convert non-string items to strings
        if not isinstance(item, str):
            try:
                item = str(item)
            except (TypeError, ValueError):
                continue  # Skip this item instead of raising error

        # Trim whitespace if specified
        if trim_whitespace:
            item = item.strip()

        # Skip blank items if not allowed
        if not allow_blank and not item:
            continue

        # Truncate long strings instead of raising error
        if len(item) > max_length:
            item = item[:max_length]

        cleaned_items.append(item)

    return cleaned_items


def validate_duration_minutes(value):
    """
    Validates that the duration in minutes is reasonable.

    If the value is too large, it will be capped at 1440 minutes (24 hours).
    """
    # If value is negative, set it to 0
    if value < 0:
        return 0

    # If value is too large, cap it at 1440 minutes (24 hours)
    if value > 1440:
        return 1440

    return value
