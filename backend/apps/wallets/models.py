import uuid
from django.db import models
from django.utils import timezone
from apps.base_models import BaseModel


class Wallet(models.Model):
    """
    Personal point wallet ledger balances.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        "users.User",
        on_delete=models.RESTRICT,
        related_name="wallet",
        help_text="User owner of the wallet."
    )
    balance = models.DecimalField(
        max_digits=15,
        decimal_places=4,
        default=0.0000,
        help_text="Compute/cache sum of transaction ledgers."
    )
    currency = models.CharField(
        max_length=10,
        default="VIDYA",
        help_text="Platform token ledger currency representation."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "wallets"
        verbose_name = "Wallet"
        verbose_name_plural = "Wallets"

    def __str__(self):
        return f"{self.user.email}'s Wallet ({self.balance} {self.currency})"


class Transaction(models.Model):
    """
    Append-only double-entry point transaction registers.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    wallet = models.ForeignKey(
        Wallet,
        on_delete=models.RESTRICT,
        related_name="transactions",
        help_text="Associated point ledger wallet."
    )
    type = models.CharField(
        max_length=20,
        choices=[
            ("CREDIT", "Credit"),
            ("DEBIT", "Debit")
        ],
        help_text="Point direction classification flow."
    )
    amount = models.DecimalField(
        max_digits=15,
        decimal_places=4,
        help_text="Ledger value quantity."
    )
    description = models.CharField(max_length=255, blank=True, null=True, help_text="Short narrative summarizing event details.")
    reference_id = models.UUIDField(blank=True, null=True, help_text="Reference linking back to enrollment, project, or event.")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "transactions"
        verbose_name = "Transaction"
        verbose_name_plural = "Transactions"
        indexes = [
            models.Index(fields=["wallet"], name="idx_transactions_wallet")
        ]

    def __str__(self):
        return f"{self.type} of {self.amount} (Wallet: {self.wallet.user.email})"


class Payment(models.Model):
    """
    Invoices and external monetary payments transactions.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        "users.User",
        on_delete=models.RESTRICT,
        related_name="payments",
        help_text="Payer student account user."
    )
    enrollment = models.ForeignKey(
        "lms.StudentEnrollment",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="payments",
        help_text="Associated course registry subscription link."
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2, help_text="Invoiced currency sum.")
    currency = models.CharField(max_length=3, default="USD", help_text="Currency ISO code.")
    payment_gateway = models.CharField(max_length=50, default="STRIPE", help_text="Gateway billing provider name.")
    gateway_transaction_id = models.CharField(
        max_length=255,
        unique=True,
        blank=True,
        null=True,
        help_text="Unique external transaction reference ID from provider gateway."
    )
    status = models.CharField(
        max_length=50,
        default="PENDING",
        choices=[
            ("PENDING", "Pending"),
            ("COMPLETED", "Completed"),
            ("FAILED", "Failed")
        ],
        help_text="Current transaction invoicing state."
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "payments"
        verbose_name = "Payment"
        verbose_name_plural = "Payments"

    def __str__(self):
        return f"Payment {self.id} (User: {self.user.email}, Status: {self.status})"


class SubscriptionPlan(models.Model):
    """
    Model representing available subscription offerings.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True, help_text="Plan tier name.")
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Monthly subscription rate.")
    duration_days = models.IntegerField(default=30, help_text="Billing duration in days.")
    is_active = models.BooleanField(default=True, help_text="Whether this plan is currently active.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "subscription_plans"
        verbose_name = "Subscription Plan"
        verbose_name_plural = "Subscription Plans"

    def __str__(self):
        return f"{self.name} (${self.price})"


class UserSubscription(models.Model):
    """
    Links users to subscription plans and handles renewal states.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        "users.User",
        on_delete=models.RESTRICT,
        related_name="subscriptions",
        help_text="Subscribing user."
    )
    plan = models.ForeignKey(
        SubscriptionPlan,
        on_delete=models.RESTRICT,
        related_name="user_subscriptions",
        help_text="Selected subscription plan."
    )
    status = models.CharField(
        max_length=50,
        default="ACTIVE",
        choices=[
            ("ACTIVE", "Active"),
            ("CANCELLED", "Cancelled"),
            ("EXPIRED", "Expired"),
            ("PENDING", "Pending")
        ],
        help_text="Subscription status."
    )
    starts_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "user_subscriptions"
        verbose_name = "User Subscription"
        verbose_name_plural = "User Subscriptions"

    def __str__(self):
        return f"{self.user.email} - {self.plan.name} ({self.status})"


class Invoice(models.Model):
    """
    Persists structured invoice sheets.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    invoice_number = models.CharField(max_length=50, unique=True, help_text="Invoice reference serial number.")
    payment = models.OneToOneField(
        Payment,
        on_delete=models.RESTRICT,
        related_name="invoice",
        help_text="Linked gateway payment."
    )
    user = models.ForeignKey(
        "users.User",
        on_delete=models.RESTRICT,
        related_name="invoices",
        help_text="Billed user account."
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2, help_text="Net taxable amount.")
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text="GST tax collected.")
    total = models.DecimalField(max_digits=10, decimal_places=2, help_text="Gross invoice total.")
    status = models.CharField(
        max_length=50,
        default="PAID",
        choices=[
            ("PAID", "Paid"),
            ("UNPAID", "Unpaid"),
            ("CANCELLED", "Cancelled")
        ],
        help_text="Invoicing billing status."
    )
    gst_number = models.CharField(max_length=15, default="27AAAAA1111A1Z1", help_text="Client GSTIN registration.")
    items = models.JSONField(default=list, help_text="Serialized dynamic invoice item list.")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "invoices"
        verbose_name = "Invoice"
        verbose_name_plural = "Invoices"

    def __str__(self):
        return f"Invoice {self.invoice_number} (Total: ${self.total})"


class Refund(models.Model):
    """
    Logs administrative refunds.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    payment = models.ForeignKey(
        Payment,
        on_delete=models.RESTRICT,
        related_name="refunds",
        help_text="Origin payment transaction."
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2, help_text="Refunded monetary sum.")
    reason = models.CharField(max_length=255, default="Administrative Refund", help_text="Reason for refund.")
    gateway_refund_id = models.CharField(max_length=255, unique=True, blank=True, null=True, help_text="Gateway refund reference ID.")
    status = models.CharField(
        max_length=50,
        default="SUCCEEDED",
        choices=[
            ("PENDING", "Pending"),
            ("SUCCEEDED", "Succeeded"),
            ("FAILED", "Failed")
        ],
        help_text="Refund status."
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "refunds"
        verbose_name = "Refund"
        verbose_name_plural = "Refunds"

    def __str__(self):
        return f"Refund for Payment {self.payment.id} (${self.amount})"


class Coupon(models.Model):
    """
    Discount coupons database representation.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=50, unique=True, help_text="Discount code tag.")
    type = models.CharField(
        max_length=20,
        choices=[
            ("PERCENTAGE", "Percentage"),
            ("FIXED", "Fixed")
        ],
        help_text="Discount discount calculation method."
    )
    value = models.DecimalField(max_digits=10, decimal_places=2, help_text="Discount value.")
    usage_limit = models.IntegerField(default=100, help_text="Maximum allowed usage count.")
    usage_count = models.IntegerField(default=0, help_text="Current usage count.")
    minimum_purchase = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text="Minimum cart value required.")
    expiry_date = models.DateField(help_text="Expiration limit.")
    is_active = models.BooleanField(default=True, help_text="Is the discount active.")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "coupons"
        verbose_name = "Coupon"
        verbose_name_plural = "Coupons"

    def __str__(self):
        return f"{self.code} ({self.type}: {self.value})"


class CouponUsage(models.Model):
    """
    Tracks coupons redemptions.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    coupon = models.ForeignKey(
        Coupon,
        on_delete=models.RESTRICT,
        related_name="usages",
        help_text="Redeemed coupon."
    )
    user = models.ForeignKey(
        "users.User",
        on_delete=models.RESTRICT,
        related_name="coupon_usages",
        help_text="Customer user."
    )
    payment = models.ForeignKey(
        Payment,
        on_delete=models.RESTRICT,
        related_name="coupon_usages",
        help_text="Linked checkout transaction."
    )
    used_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "coupon_usages"
        verbose_name = "Coupon Usage Record"
        verbose_name_plural = "Coupon Usage Records"
        unique_together = ("coupon", "user", "payment")

    def __str__(self):
        return f"{self.user.email} used {self.coupon.code}"


class Referral(models.Model):
    """
    Affiliate referral trackings.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    referrer = models.ForeignKey(
        "users.User",
        on_delete=models.RESTRICT,
        related_name="referrals_made",
        help_text="Referring advocate user."
    )
    referred_user = models.OneToOneField(
        "users.User",
        on_delete=models.RESTRICT,
        related_name="referred_by",
        help_text="Referred scholar account."
    )
    status = models.CharField(
        max_length=50,
        default="PENDING",
        choices=[
            ("PENDING", "Pending"),
            ("CONVERTED", "Converted"),
            ("REWARDED", "Rewarded")
        ],
        help_text="Referral onboarding status."
    )
    commission_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text="Affiliate reward earnings.")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "referrals"
        verbose_name = "Referral Linkage"
        verbose_name_plural = "Referral Linkages"

    def __str__(self):
        return f"Referral: {self.referrer.email} -> {self.referred_user.email}"


class TeacherPayout(models.Model):
    """
    Instructor cashout transactions.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    teacher = models.ForeignKey(
        "users.User",
        on_delete=models.RESTRICT,
        related_name="payouts",
        help_text="Recipient instructor account."
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2, help_text="Payout amount.")
    status = models.CharField(
        max_length=50,
        default="PENDING",
        choices=[
            ("PENDING", "Pending"),
            ("APPROVED", "Approved"),
            ("PAID", "Paid"),
            ("FAILED", "Failed")
        ],
        help_text="Payout status."
    )
    payout_method = models.CharField(max_length=50, default="BANK_TRANSFER", help_text="Payout disbursement channel.")
    reference_id = models.CharField(max_length=255, blank=True, null=True, help_text="Bank payout transaction number.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "teacher_payouts"
        verbose_name = "Teacher Payout Record"
        verbose_name_plural = "Teacher Payout Records"

    def __str__(self):
        return f"Payout {self.id} (Teacher: {self.teacher.email}, Status: {self.status})"


class RevenueSummary(models.Model):
    """
    Caches aggregated daily financial summaries.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    date = models.DateField(unique=True, help_text="Summary period date.")
    total_revenue = models.DecimalField(max_digits=15, decimal_places=2, default=0.00, help_text="Total revenue.")
    total_tax = models.DecimalField(max_digits=15, decimal_places=2, default=0.00, help_text="Total tax.")
    total_commission = models.DecimalField(max_digits=15, decimal_places=2, default=0.00, help_text="Total platform fee.")
    total_payouts = models.DecimalField(max_digits=15, decimal_places=2, default=0.00, help_text="Total paid teacher cashouts.")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "revenue_summaries"
        verbose_name = "Revenue Summary Record"
        verbose_name_plural = "Revenue Summary Records"

    def __str__(self):
        return f"Revenue Summary ({self.date}): ${self.total_revenue}"


class GSTRecord(models.Model):
    """
    Calculates tax breakdowns.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    payment = models.OneToOneField(
        Payment,
        on_delete=models.RESTRICT,
        related_name="gst_record",
        help_text="Origin checkout payment."
    )
    invoice_number = models.CharField(max_length=50, unique=True, help_text="Linked invoice serial number.")
    net_amount = models.DecimalField(max_digits=10, decimal_places=2, help_text="Pre-tax amount.")
    cgst = models.DecimalField(max_digits=10, decimal_places=2, help_text="CGST tax portion.")
    sgst = models.DecimalField(max_digits=10, decimal_places=2, help_text="SGST tax portion.")
    igst = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text="IGST tax portion.")
    total_gst = models.DecimalField(max_digits=10, decimal_places=2, help_text="Summed GST tax.")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "gst_records"
        verbose_name = "GST Record"
        verbose_name_plural = "GST Records"

    def __str__(self):
        return f"GST {self.invoice_number} (Total Tax: ${self.total_gst})"


class PaymentAudit(models.Model):
    """
    Chronicles changes.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    action = models.CharField(max_length=100, help_text="Logged action name.")
    actor_email = models.CharField(max_length=255, help_text="User executing the action.")
    payment = models.ForeignKey(
        Payment,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="audits",
        help_text="Linked payment ledger."
    )
    details = models.JSONField(default=dict, help_text="Context metadata.")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "payment_audits"
        verbose_name = "Payment Audit Log"
        verbose_name_plural = "Payment Audit Logs"

    def __str__(self):
        return f"{self.action} by {self.actor_email} at {self.created_at}"
