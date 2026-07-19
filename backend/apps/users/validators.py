"""
Identity Verification Validators - BrahmaVidya Galaxy
Purpose: Validates structural criteria for user parameters (emails, passwords, handles).
"""

import re
from django.core.exceptions import ValidationError

def validate_password_complexity(password: str) -> None:
    """
    Enforces a strict corporate password criteria:
    - Minimum length of 8 characters
    - At least 1 uppercase letter, 1 lowercase letter, 1 digit, and 1 special symbol.
    """
    if len(password) < 8:
        raise ValidationError("Password must contain at least 8 characters.")
        
    if not re.search(r"[A-Z]", password):
        raise ValidationError("Password must contain at least one uppercase letter.")
        
    if not re.search(r"[a-z]", password):
        raise ValidationError("Password must contain at least one lowercase letter.")
        
    if not re.search(r"\d", password):
        raise ValidationError("Password must contain at least one digit.")
        
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        raise ValidationError("Password must contain at least one special character.")

def validate_academic_email(email: str) -> None:
    """
    Restricts registry entries to academic email domains if strict registration rules are enforced.
    """
    # Placeholder: e.g. verify email ends with '.edu' or matches approved organization listings
    if not email.endswith(".edu") and os.getenv("STRICT_EDU_REGISTRATION", "False").lower() == "true":
        raise ValidationError("Registration is restricted to .edu academic domains.")
