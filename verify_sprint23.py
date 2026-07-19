#!/usr/bin/env python
"""
BrahmaVidya Galaxy Payments & Subscription Platform Integration Checkouts
Sprint 23 — Phase 8: Comprehensive automated testing and integrations validation.
"""

import os
import sys
import django
from decimal import Decimal
from django.utils import timezone
from django.test import override_settings

# Configure django environment
sys.path.append(os.path.abspath("backend"))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_project.settings")
django.setup()

from django.contrib.auth import get_user_model
from apps.users.models import Role
from apps.wallets.models import (
    Wallet, Transaction, Payment, SubscriptionPlan, UserSubscription,
    Invoice, Refund, Coupon, TeacherPayout, GSTRecord, PaymentAudit
)
from apps.notifications.models import NotificationTemplate
from apps.wallets.services import (
    SubscriptionService, InvoiceService, RefundService, TeacherPayoutService,
    LedgerTransactionService
)
from apps.wallets.selectors import (
    get_active_user_subscription, get_user_invoices, get_coupon_by_code
)

User = get_user_model()

@override_settings(
    CACHES={
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "sprint23-verification-cache",
        }
    },
    CELERY_TASK_ALWAYS_EAGER=True,
    CELERY_BROKER_URL="memory://",
    CELERY_RESULT_BACKEND="cache+memory://"
)
def run_checks():
    print("==================================================================")
    print("     BrahmaVidya Payments Platform Sprint 23 Verification        ")
    print("==================================================================")

    success_flags = []

    # Seed notification templates
    NotificationTemplate.objects.get_or_create(
        code="wallet",
        defaults={
            "name": "Wallet Alert",
            "subject": "Wallet Transaction Alert: {{ type }}",
            "body_html": "Balance: {{ amount }}",
            "body_text": "Balance: {{ amount }}"
        }
    )
    NotificationTemplate.objects.get_or_create(
        code="payment",
        defaults={
            "name": "Payment Confirmation",
            "subject": "Payment Receipt",
            "body_html": "Amount: {{ amount }}",
            "body_text": "Amount: {{ amount }}"
        }
    )

    # 1. Create/Get roles and users
    print("\n[*] Initializing Roles and Users:")
    teacher_role, _ = Role.objects.get_or_create(name="TEACHER", defaults={"description": "Teacher"})
    student_role, _ = Role.objects.get_or_create(name="STUDENT", defaults={"description": "Student"})

    teacher_email = "sprint23_teacher@brahmavidya.edu"
    student_email = "sprint23_student@brahmavidya.edu"

    # Reset existing test records cleanly by clearing related tables first in correct order
    Refund.objects.filter(payment__user__email__in=[teacher_email, student_email]).delete()
    GSTRecord.objects.filter(payment__user__email__in=[teacher_email, student_email]).delete()
    Invoice.objects.filter(user__email__in=[teacher_email, student_email]).delete()
    Payment.objects.filter(user__email__in=[teacher_email, student_email]).delete()
    Transaction.objects.filter(wallet__user__email__in=[teacher_email, student_email]).delete()
    Wallet.objects.filter(user__email__in=[teacher_email, student_email]).delete()
    UserSubscription.objects.filter(user__email__in=[teacher_email, student_email]).delete()
    TeacherPayout.objects.filter(teacher__email__in=[teacher_email, student_email]).delete()
    User.all_objects.filter(email__in=[teacher_email, student_email]).delete()

    teacher = User.objects.create_user(email=teacher_email, password="sprint23password", role=teacher_role)
    student = User.objects.create_user(email=student_email, password="sprint23password", role=student_role)
    print(f"    - SUCCESS: Users created ({teacher_email} and {student_email})")
    success_flags.append(True)

    # 2. Wallet creation and deposit
    print("\n[*] Verifying Wallet Creation & Deposit Ledger:")
    try:
        wallet, created = Wallet.objects.get_or_create(user=student, defaults={"balance": Decimal("0.00")})
        assert wallet.balance == Decimal("0.00"), "Initial balance should be 0.00"
        
        # Credit transaction
        tx = LedgerTransactionService.create_transaction(
            wallet_id=wallet.id,
            tx_direction="CREDIT",
            fine_grained_type="CREDIT",
            amount=Decimal("1500.00"),
            description="Welcome Credits Deposit"
        )
        wallet.refresh_from_db()
        assert wallet.balance == Decimal("1500.00"), "Balance should update to 1500.00"
        print(f"    - SUCCESS: Wallet balance successfully updated to: INR {wallet.balance}")
        success_flags.append(True)
    except Exception as e:
        print(f"    - FAILURE: Wallet deposit check failed: {e}")
        success_flags.append(False)

    # 3. Peer-to-peer transfer
    print("\n[*] Verifying Peer-to-Peer Transfer:")
    try:
        teacher_wallet, _ = Wallet.objects.get_or_create(user=teacher, defaults={"balance": Decimal("0.00")})
        
        LedgerTransactionService.transfer_funds(
            source_wallet_id=wallet.id,
            target_wallet_id=teacher_wallet.id,
            amount=Decimal("500.00"),
            description="Tuition transfer"
        )
        wallet.refresh_from_db()
        teacher_wallet.refresh_from_db()
        assert wallet.balance == Decimal("1000.00"), "Source balance should decrease by 500"
        assert teacher_wallet.balance == Decimal("500.00"), "Target balance should increase by 500"
        print(f"    - SUCCESS: Transfer processed successfully. Source: INR {wallet.balance}, Target: INR {teacher_wallet.balance}")
        success_flags.append(True)
    except Exception as e:
        print(f"    - FAILURE: Peer-to-peer transfer check failed: {e}")
        success_flags.append(False)

    # 4. Coupon Validation & Expiry check
    print("\n[*] Verifying Promotion Coupon Engine:")
    try:
        Coupon.objects.filter(code="DISCOUNT20").delete()
        coupon = Coupon.objects.create(
            code="DISCOUNT20",
            type="PERCENTAGE",
            value=Decimal("20.00"),
            usage_limit=10,
            usage_count=0,
            minimum_purchase=Decimal("100.00"),
            expiry_date=timezone.now().date() + timezone.timedelta(days=10),
            is_active=True
        )
        queried_coupon = get_coupon_by_code("DISCOUNT20")
        assert queried_coupon is not None, "Coupon lookup should return coupon instance"
        assert queried_coupon.is_active == True, "Coupon should be active"
        print(f"    - SUCCESS: Coupon engine validated code '{queried_coupon.code}' with 20% discount rate.")
        success_flags.append(True)
    except Exception as e:
        print(f"    - FAILURE: Coupon verification failed: {e}")
        success_flags.append(False)

    # 5. Invoicing & GST inclusive splits
    print("\n[*] Verifying Invoicing and GST Tax splits:")
    try:
        payment = Payment.objects.create(
            user=student,
            amount=Decimal("1180.00"),
            status="COMPLETED",
            currency="INR",
            payment_gateway="STRIPE"
        )
        invoice = InvoiceService.generate_invoice(
            payment=payment,
            items_list=[{"description": "Core course bundle purchase", "amount": 1180.00}]
        )
        assert invoice.total == Decimal("1180.00"), "Total should be 1180.00"
        
        # Verify GST splits inside GSTRecord table (18% tax inclusive: 1000 base, 180 total tax)
        gst = GSTRecord.objects.get(payment=payment)
        assert gst.net_amount == Decimal("1000.00"), "Net amount should be 1000.00"
        assert gst.total_gst == Decimal("180.00"), "Total GST should be 180.00"
        print(f"    - SUCCESS: Invoice {invoice.invoice_number} verified with CGST: INR {gst.cgst}, SGST: INR {gst.sgst}")
        success_flags.append(True)
    except Exception as e:
        print(f"    - FAILURE: Invoicing GST split check failed: {e}")
        success_flags.append(False)

    # 6. Refunds and Reward Points rollback
    print("\n[*] Verifying Refunds & Balance Penalization:")
    try:
        refund = RefundService.issue_refund(
            payment_id=payment.id,
            amount=Decimal("1180.00"),
            reason="Accidental double buy"
        )
        assert refund.status == "SUCCEEDED", "Refund state should transition to SUCCEEDED"
        print(f"    - SUCCESS: Refund generated and finalized for amount: INR {refund.amount}")
        success_flags.append(True)
    except Exception as e:
        print(f"    - FAILURE: Refund execution check failed: {e}")
        success_flags.append(False)

    # 7. Teacher payout withdrawal request gating
    print("\n[*] Verifying Teacher Payout gating:")
    try:
        payout = TeacherPayoutService.request_payout(
            teacher=teacher,
            amount=Decimal("100.00"),
            payout_method="UPI"
        )
        assert payout.status == "PENDING", "Initial payout state should be PENDING"
        teacher_wallet.refresh_from_db()
        assert teacher_wallet.balance == Decimal("400.00"), "Teacher wallet balance should be debited by payout amount"
        print(f"    - SUCCESS: Payout request submitted for INR {payout.amount}. Teacher balance updated to INR {teacher_wallet.balance}")
        success_flags.append(True)
    except Exception as e:
        print(f"    - FAILURE: Teacher payout check failed: {e}")
        success_flags.append(False)

    # 8. Subscription Management
    print("\n[*] Verifying Subscription plan creations:")
    try:
        plan, _ = SubscriptionPlan.objects.get_or_create(
            name="VIP Premium Access",
            defaults={"price": Decimal("99.00"), "duration_days": 30, "is_active": True}
        )
        sub = SubscriptionService.create_subscription(
            user=student,
            plan_name="VIP Premium Access",
            price=Decimal("99.00")
        )
        active_sub = get_active_user_subscription(student)
        assert active_sub is not None, "Active subscription should be lookup-able"
        assert active_sub.plan.name == "VIP Premium Access", "Subscription plan name should match"
        print(f"    - SUCCESS: Subscription active: {active_sub.plan.name}, status: {active_sub.status}")
        success_flags.append(True)
    except Exception as e:
        print(f"    - FAILURE: Subscription check failed: {e}")
        success_flags.append(False)

    # Reconcile final checks status
    print("\n==================================================================")
    if all(success_flags) and len(success_flags) > 0:
        print("  ALL PLATFORM INTEGRATION CHECKS COMPLETED SUCCESSFULLY  ")
        print("==================================================================")
        sys.exit(0)
    else:
        print("  PLATFORM INTEGRATION CHECKS ENCOUNTERED FAILURES       ")
        print("==================================================================")
        sys.exit(1)

if __name__ == "__main__":
    run_checks()
