import re
from django.core.exceptions import ValidationError


def validate_metric_name(value):
    """
    Validates that a metric name follows the standard dot or space separated path.
    """
    if not value or len(value) < 3:
        raise ValidationError("Metric name must be at least 3 characters long.")
    if not re.match(r"^[a-zA-Z0-9_\-\.\s]+$", value):
        raise ValidationError("Metric name contains invalid characters. Only alphanumeric, space, dot, dash, and underscores are allowed.")


def validate_dwell_time(value):
    """
    Ensures dwell times are non-negative and within realistic boundaries.
    """
    if value < 0:
        raise ValidationError("Dwell time seconds cannot be negative.")
    if value > 86400:  # 24 hours
        raise ValidationError("Dwell time seconds exceeds daily limits (86400 seconds).")
