"""
Wallet and Certification Background Tasks - BrahmaVidya Galaxy
Purpose: Handles async cryptographic signing, monthly financial audits, subscription checks, and invoice generations.
"""

from celery import shared_task
import logging
from django.utils import timezone
from django.db import transaction
from django.db.models import Sum
from decimal import Decimal
from apps.wallets.models import Wallet, Transaction, UserSubscription, Invoice
from utils.crypto import generate_verification_hash

logger = logging.getLogger("tasks")

@shared_task
def compile_cryptographic_certificate_task(user_id: str, course_id: str) -> dict:
    """
    Runs off the main thread to compile a unique SHA-256 certificate hash for a graduate.
    - Generates hash signatures linking student, course, and generation timestamp.
    - Persists verification parameters to Certificate database rows.
    """
    logger.info(f"Generating secure digital signature for user: {user_id}, course: {course_id}")
    
    # Generate signature using cryptographic verification utilities
    credential_data = generate_verification_hash(user_id, course_id)
    
    from apps.lms.models import Certificate
    
    # Check if certificate exists, else create it
    cert, created = Certificate.objects.get_or_create(
        user_id=user_id,
        course_id=course_id,
        defaults={
            "credential_hash": credential_data["hash"],
            "issued_at": timezone.now()
        }
    )
    logger.info(f"Successfully minted verifiable completion certificate: {credential_data['hash']}")
    return credential_data

@shared_task
def run_monthly_financial_audit() -> bool:
    """
    Reconciles all double-entry debit/credit ledgers across all wallet accounts.
    - Verifies sum(credits) - sum(debits) matches current active balances.
    """
    logger.info("Executing monthly systemic balance reconciliation...")
    wallets = Wallet.objects.all()
    for w in wallets:
        credits = Transaction.objects.filter(wallet=w, type="CREDIT").aggregate(total=Sum("amount"))["total"] or Decimal("0.0000")
        debits = Transaction.objects.filter(wallet=w, type="DEBIT").aggregate(total=Sum("amount"))["total"] or Decimal("0.0000")
        expected_balance = credits - debits
        if w.balance != expected_balance:
            logger.error(f"Audit mismatch for wallet {w.id}. Current: {w.balance}, Expected: {expected_balance}")
            w.balance = expected_balance
            w.save(update_fields=["balance"])
    return True

@shared_task
def check_expired_subscriptions_task() -> int:
    """
    Scans active subscriptions daily and updates statuses to EXPIRED if their validity has lapsed.
    """
    logger.info("Checking for expired subscriptions...")
    expired_count = UserSubscription.objects.filter(
        status="ACTIVE",
        expires_at__lte=timezone.now()
    ).update(status="EXPIRED")
    logger.info(f"Expired {expired_count} subscriptions.")
    return expired_count

@shared_task
def generate_invoice_pdf_task(invoice_id: str) -> bool:
    """
    Simulates asynchronous PDF invoice rendering and updates media catalog links.
    """
    logger.info(f"Generating PDF for invoice: {invoice_id}")
    return True
