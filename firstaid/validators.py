from rest_framework.exceptions import ValidationError
import re


def validate_json_array(value, max_items=20, max_length=200):
    """
    Validate that the value is a list of strings with proper constraints and security checks.

    Args:
        value: The value to validate
        max_items: Maximum number of items allowed in the list
        max_length: Maximum length of each string in the list

    Raises:
        ValidationError: If the value does not meet the validation criteria
    """
    if not isinstance(value, list):
        raise ValidationError("Must be a list of strings")

    if len(value) > max_items:
        raise ValidationError(f"List cannot contain more than {max_items} items")

    if not value:
        raise ValidationError("List cannot be empty")

    # Regex pattern to detect potentially malicious content (script tags, iframes, etc.)
    dangerous_pattern = re.compile(
        r"<\s*script|<\s*iframe|javascript:|data:text/html|onerror=|onclick=",
        re.IGNORECASE,
    )

    for item in value:
        if not isinstance(item, str):
            raise ValidationError("All items must be strings")

        if not item.strip():
            raise ValidationError("Empty strings are not allowed")

        if len(item) > max_length:
            raise ValidationError(
                f"String length cannot exceed {max_length} characters"
            )

        # Check for potentially dangerous content
        if dangerous_pattern.search(item):
            raise ValidationError("Potentially unsafe content detected")

        # Check for excessive HTML tags which might indicate an attempt to inject code
        if item.count("<") > 5 and item.count(">") > 5:
            raise ValidationError("Too many HTML tags in content")
