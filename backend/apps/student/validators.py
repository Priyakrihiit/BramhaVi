"""
Student Dashboard Validators — BrahmaVidya Galaxy
Sprint 20: Input validation logic for student dashboard entities.
"""

from django.core.exceptions import ValidationError
from django.utils import timezone


def validate_goal_dates(target_date) -> None:
    """Asserts target completion date is in the future."""
    if target_date and target_date < timezone.now().date():
        raise ValidationError("The target completion date must be in the future.")


def validate_note_length(content: str, max_length: int = 10000) -> None:
    """Validates note length safety thresholds."""
    if not content or not content.strip():
        raise ValidationError("Note content cannot be empty.")
    if len(content) > max_length:
        raise ValidationError(f"Note content cannot exceed {max_length} characters.")


def validate_session_duration(duration_seconds: int) -> None:
    """Validates duration of a study session."""
    if duration_seconds < 0:
        raise ValidationError("Study session duration cannot be negative.")


def validate_reminder_time(remind_at) -> None:
    """Asserts reminder scheduling time occurs in the future."""
    if remind_at and remind_at < timezone.now():
        raise ValidationError("The scheduled reminder time must be in the future.")
