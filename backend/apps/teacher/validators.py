"""
Teacher Portal Validators — BrahmaVidya Galaxy
Sprint 21: Business logic input safety guards and checks.
"""

import re
from django.core.exceptions import ValidationError
from django.utils import timezone


def validate_teacher_rating(value) -> None:
    """Asserts rating is within normal academic bounds (1.00 to 5.00)."""
    if value is not None and (value < 1.00 or value > 5.00):
        raise ValidationError("Teacher evaluations and ratings must fall within the range [1.00, 5.00].")


def validate_positive_experience(value) -> None:
    """Asserts years of teaching experience cannot be negative."""
    if value is not None and value < 0:
        raise ValidationError("Years of teaching experience cannot be negative.")


def validate_batch_dates(start_date, end_date) -> None:
    """Asserts a cohort start date precedes its termination date."""
    if start_date and end_date:
        if start_date >= end_date:
            raise ValidationError("Cohort start date must strictly precede its completion date.")


def validate_payout_amount(value) -> None:
    """Asserts payout withdrawable amount is strictly positive."""
    if value is not None and value <= 0:
        raise ValidationError("Withdrawable or transaction values must be strictly greater than 0.")


def validate_payout_address(payout_method: str, address: str) -> None:
    """Performs light checks for Stripe Connect IDs or PayPal emails."""
    if not address or not address.strip():
        raise ValidationError("Payout address/account details cannot be blank.")
    
    if payout_method == "PAYPAL":
        email_regex = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        if not re.match(email_regex, address.strip()):
            raise ValidationError("PayPal payout address must be a valid email format.")
    elif payout_method == "STRIPE":
        if not address.startswith("acct_") and not address.startswith("usr_"):
            raise ValidationError("Stripe Connect IDs should start with 'acct_' or 'usr_'.")


def validate_multiplier(value) -> None:
    """Asserts difficulty weighting multipliers remain positive."""
    if value is not None and value <= 0:
        raise ValidationError("Difficulty multiplier weight must be strictly positive.")


def validate_grade_score(grade, max_points=100) -> None:
    """Enforces grade percentage scores reside within [0.00, max_points]."""
    if grade is not None:
        if grade < 0 or grade > max_points:
            raise ValidationError(f"Grade score must reside within the valid bounds [0.0, {max_points}].")
