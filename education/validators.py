import re
from rest_framework.exceptions import ValidationError


def validate_youtube_url(value):
    youtube_regex = r"^(https?://)?(www\.)?(youtube\.com/watch\?v=|youtu\.be/)[\w-]{11}"
    if not re.match(youtube_regex, value):
        raise ValidationError(
            "Invalid YouTube URL. Valid formats: "
            "https://www.youtube.com/watch?v=ID or https://youtu.be/ID"
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
