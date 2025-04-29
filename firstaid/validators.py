from rest_framework.exceptions import ValidationError


def validate_json_array(value, max_items=20, max_length=200):
    if not isinstance(value, list):
        raise ValidationError("Must be a list of strings")
        
    if len(value) > max_items:
        raise ValidationError(f"List cannot contain more than {max_items} items")
        
    if not value:
        raise ValidationError("List cannot be empty")
        
    for item in value:
        if not isinstance(item, str):
            raise ValidationError("All items must be strings")
        if not item.strip():
            raise ValidationError("Empty strings are not allowed")
        if len(item) > max_length:
            raise ValidationError(f"String length cannot exceed {max_length} characters")
