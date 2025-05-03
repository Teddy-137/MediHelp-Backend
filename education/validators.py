import re
from rest_framework.exceptions import ValidationError


def validate_image_url(value):
    """
    Validates that a URL points to an image file.

    Checks if the URL ends with a common image extension.
    """
    if not value:  # Allow empty values (blank=True)
        return

    image_extensions = [".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg"]
    url_lower = value.lower()

    # Check if URL ends with an image extension
    if not any(url_lower.endswith(ext) for ext in image_extensions):
        # If no extension, check if it contains image-related keywords
        image_services = [
            "imgur",
            "flickr",
            "unsplash",
            "pexels",
            "pixabay",
            "cloudinary",
        ]
        if not any(service in url_lower for service in image_services):
            raise ValidationError(
                "URL does not appear to point to an image. "
                "Please provide a URL ending with .jpg, .jpeg, .png, .gif, .webp, or .svg, "
                "or from a known image hosting service."
            )


def validate_youtube_url(value):
    """
    Validates that a URL is a valid YouTube video URL.

    Supports formats:
    - https://www.youtube.com/watch?v=VIDEO_ID
    - https://youtu.be/VIDEO_ID
    - https://youtube.com/watch?v=VIDEO_ID
    - http://www.youtube.com/watch?v=VIDEO_ID
    - www.youtube.com/watch?v=VIDEO_ID
    - youtu.be/VIDEO_ID

    Also validates that the video ID is exactly 11 characters and contains
    only alphanumeric characters, hyphens, and underscores.
    """
    # More comprehensive regex for YouTube URLs
    youtube_regex = (
        r"^(https?://)?(www\.)?(youtube\.com/watch\?v=|youtu\.be/)([\w-]{11})($|&.*$)"
    )
    match = re.match(youtube_regex, value)

    if not match:
        raise ValidationError(
            "Invalid YouTube URL. Valid formats: "
            "https://www.youtube.com/watch?v=ID or https://youtu.be/ID"
        )

    # Extract and validate the video ID
    video_id = match.group(4)
    if not re.match(r"^[\w-]{11}$", video_id):
        raise ValidationError(
            "Invalid YouTube video ID. Must be exactly 11 characters and "
            "contain only letters, numbers, hyphens, and underscores."
        )


def validate_string_list(
    value,
    max_items=20,
    max_length=200,
    allow_empty=False,
    allow_blank=False,
    trim_whitespace=True,
    error_messages=None,
):
    """
    Validates a list of strings with configurable constraints

    Args:
        value: Input value to validate
        max_items: Maximum number of allowed items
        max_length: Maximum length per string item
        allow_empty: Allow empty list if True
        allow_blank: Allow blank/empty strings if True
        trim_whitespace: Automatically strip whitespace
        error_messages: Custom error messages dictionary

    Returns:
        List of validated strings (with whitespace trimmed if enabled)
    """
    default_errors = {
        "not_list": "Value must be a list",
        "empty_list": "List cannot be empty",
        "max_items": "List cannot contain more than {max} items",
        "item_not_string": "All items must be strings",
        "empty_string": "Empty strings are not allowed",
        "max_length": "String length cannot exceed {max} characters",
    }
    errors = {**default_errors, **(error_messages or {})}

    if not isinstance(value, list):
        raise ValidationError(errors["not_list"])

    if not allow_empty and not value:
        raise ValidationError(errors["empty_list"])

    if len(value) > max_items:
        raise ValidationError(errors["max_items"].format(max=max_items))

    cleaned_items = []
    for index, item in enumerate(value):
        if not isinstance(item, str):
            raise ValidationError({index: errors["item_not_string"]})

        if trim_whitespace:
            item = item.strip()

        if not allow_blank and not item:
            raise ValidationError({index: errors["empty_string"]})

        if len(item) > max_length:
            raise ValidationError({index: errors["max_length"].format(max=max_length)})

        cleaned_items.append(item)

    return cleaned_items


def validate_duration_minutes(value):
    """
    Validates that the duration in minutes does not exceed 600 (10 hours).
    """
    if value > 600:
        raise ValidationError("Duration cannot exceed 600 minutes (10 hours)")
    return value
