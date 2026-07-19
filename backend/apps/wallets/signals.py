"""
Wallet and Ledger Event Signals - BrahmaVidya Galaxy
Purpose: Listens to payment and transaction saves and dispatches notifications.
"""

import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.wallets.models import Transaction, Payment, PaymentAudit

logger = logging.getLogger("signals")

@receiver(post_save, sender=Transaction)
def on_transaction_created(sender, instance, created, **kwargs) -> None:
    """
    Triggers automatically when a new Transaction record is saved.
    - If the transaction is a credit or debit greater than 1000, inserts a PaymentAudit record.
    - Dispatches a 'wallet' transaction notification to the user's registered email.
    """
    if created:
        if instance.amount > 1000:
            PaymentAudit.objects.create(
                action="LARGE_TRANSACTION_ALERT",
                actor_email="system@brahmavidya.edu",
                details={
                    "transaction_id": str(instance.id),
                    "amount": str(instance.amount),
                    "type": instance.type,
                    "description": instance.description
                }
            )

        # Dispatch wallet notification
        try:
            from apps.notifications.services import EmailService
            user = instance.wallet.user
            if user and user.email:
                context = {
                    "type": instance.type.lower(),
                    "amount": str(instance.amount),
                    "currency": "INR",
                    "ref": str(instance.id)[:12].upper()
                }
                EmailService.send_email(
                    to_email=user.email,
                    template_code="wallet",
                    context_data=context
                )
        except Exception as e:
            logger.error(f"Failed to dispatch wallet signal notification: {str(e)}")


@receiver(post_save, sender=Payment)
def on_payment_saved(sender, instance, created, **kwargs) -> None:
    """
    Triggers on payment status transitions.
    - When a Payment goes to SUCCESS, dispatches a 'payment' receipt confirmation email.
    """
    if instance.status in ["SUCCESS", "COMPLETED"]:
        try:
            from apps.notifications.services import EmailService
            if instance.user and instance.user.email:
                context = {
                    "amount": str(instance.amount),
                    "currency": instance.currency,
                    "order_id": str(instance.id)[:8].upper()
                }
                EmailService.send_email(
                    to_email=instance.user.email,
                    template_code="payment",
                    context_data=context
                )
        except Exception as e:
            logger.error(f"Failed to dispatch payment success notification: {str(e)}")
