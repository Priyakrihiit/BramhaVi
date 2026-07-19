"""
Wallet and Payments Selectors - BrahmaVidya Galaxy
Purpose: Database query selectors fetching formatted results for payment entities.
"""

from django.utils import timezone
from django.db.models import QuerySet
from django.shortcuts import get_object_or_404
from apps.wallets.models import (
    Wallet, Transaction, Payment, SubscriptionPlan, UserSubscription,
    Invoice, Refund, Coupon, CouponUsage, Referral, TeacherPayout,
    RevenueSummary, GSTRecord, PaymentAudit
)

def get_active_user_subscription(user) -> UserSubscription:
    """
    Retrieves the currently active user subscription.
    """
    return UserSubscription.objects.filter(
        user=user,
        status="ACTIVE",
        expires_at__gt=timezone.now()
    ).select_related("plan").first()

def get_user_invoices(user) -> QuerySet[Invoice]:
    """
    Retrieves all invoices associated with a user.
    """
    return Invoice.objects.filter(user=user).order_by("-created_at")

def get_coupon_by_code(code: str) -> Coupon:
    """
    Retrieves an active coupon by its code name.
    """
    return Coupon.objects.filter(
        code__iexact=code.strip(),
        is_active=True,
        expiry_date__gte=timezone.now().date()
    ).first()

def get_teacher_payouts(teacher) -> QuerySet[TeacherPayout]:
    """
    Retrieves all payouts requested by a teacher.
    """
    return TeacherPayout.objects.filter(teacher=teacher).order_by("-created_at")

def get_revenue_summaries(start_date=None, end_date=None) -> QuerySet[RevenueSummary]:
    """
    Retrieves daily revenue summaries.
    """
    qs = RevenueSummary.objects.all()
    if start_date:
        qs = qs.filter(date__gte=start_date)
    if end_date:
        qs = qs.filter(date__lte=end_date)
    return qs.order_by("-date")

def get_payment_refunds(payment) -> QuerySet[Refund]:
    """
    Retrieves all refund records associated with a payment.
    """
    return Refund.objects.filter(payment=payment).order_by("-created_at")
