"""
Cryptographic Verification Utility - BrahmaVidya Galaxy
Purpose: Handles cryptographic hashing, salt generation, and certificate authenticity validation.
"""

import hashlib
import time
from django.conf import settings

def generate_verification_hash(recipient_id: str, course_id: str, salt: str = None) -> dict:
    """
    Computes a secure, tamper-proof SHA-256 signature for verifiable learning credentials.
    """
    secret_salt = salt or getattr(settings, "CRYPTO_SALT", "galaxy_default_system_salt")
    timestamp = str(int(time.time()))
    
    # Secure hash formula linking student, course, and generation timestamp
    seed_string = f"{recipient_id}:{course_id}:{timestamp}:{secret_salt}".encode("utf-8")
    signature = hashlib.sha256(seed_string).hexdigest()
    
    return {
        "hash": signature,
        "issued_at": timestamp,
        "recipient": recipient_id,
        "course": course_id
    }

def verify_certificate_authenticity(recipient_id: str, course_id: str, issued_at: str, provided_hash: str, salt: str = None) -> bool:
    """
    Validates a cryptographic certificate hash to ensure it has not been forged or altered.
    """
    secret_salt = salt or getattr(settings, "CRYPTO_SALT", "galaxy_default_system_salt")
    seed_string = f"{recipient_id}:{course_id}:{issued_at}:{secret_salt}".encode("utf-8")
    expected_hash = hashlib.sha256(seed_string).hexdigest()
    
    return expected_hash == provided_hash
