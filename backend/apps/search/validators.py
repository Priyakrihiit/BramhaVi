from django.core.exceptions import ValidationError

def validate_query_string(value):
    """
    Validates search query string length and content.
    """
    if not value or not value.strip():
        raise ValidationError("Search query cannot be empty.")
    if len(value) > 255:
        raise ValidationError("Search query cannot exceed 255 characters.")

def validate_boost_score(value):
    """
    Validates search ranking boost score.
    """
    if value < 0.0:
        raise ValidationError("Boost score cannot be negative.")
