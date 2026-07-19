"""
Financial Transaction Validators - BrahmaVidya Galaxy
Purpose: Validates decimal inputs, currency forms, and ledger values.
"""

from decimal import Decimal, InvalidOperation
from django.core.exceptions import ValidationError

def validate_positive_amount(value: Decimal) -> None:
    """
    Ensures transaction amounts are formatted as positive, non-zero values.
    """
    try:
        decimal_val = Decimal(str(value))
    except (ValueError, InvalidOperation):
        raise ValidationError("Amount is not a valid decimal number.")
        
    if decimal_val <= Decimal("0.00"):
        raise ValidationError("Transaction amount must be strictly greater than zero.")

def validate_wallet_withdrawal_limit(amount: Decimal, active_balance: Decimal) -> None:
    """
    Validates that a withdrawal request does not exceed current holdings.
    """
    if amount > active_balance:
        raise ValidationError(
            f"Insufficient wallet funds. Withdrawal requested: {amount}, Active Balance: {active_balance}"
        )
