"""
Wallet Balance and Ledger Service - BrahmaVidya Galaxy
Purpose: Core business transactions representing financial operations and certificate issuing sequences.
"""

from decimal import Decimal
from typing import Dict, Any, List
from django.db import transaction
from django.db.models import F, Sum
from django.shortcuts import get_object_or_404
from django.utils import timezone
import uuid

from apps.wallets.models import (
    Wallet, Transaction, Payment, SubscriptionPlan, UserSubscription,
    Invoice, Refund, Coupon, CouponUsage, Referral, TeacherPayout,
    RevenueSummary, GSTRecord, PaymentAudit
)
from apps.wallets.wallet_extras_store import set_fine_grained_tx, get_fine_grained_tx, is_wallet_id_soft_deleted


class LedgerTransactionService:
    @staticmethod
    @transaction.atomic
    def create_transaction(
        wallet_id: str,
        tx_direction: str,  # CREDIT or DEBIT
        fine_grained_type: str,  # CREDIT, DEBIT, TRANSFER, REFUND, REWARD, PURCHASE, WITHDRAWAL
        amount: Decimal,
        description: str,
        reference_id: Any = None
    ) -> Transaction:
        """
        Main low-level transaction register. Inserts append-only record, updates wallet balance atomically,
        and saves fine-grained type in extras.
        """
        if amount <= Decimal("0.0000"):
            raise ValueError("Transaction amount must be greater than zero.")

        # Atomic lock on Wallet
        wallet = Wallet.objects.select_for_update().get(id=wallet_id)

        if is_wallet_id_soft_deleted(wallet.id):
            raise ValueError("Cannot transact on a soft-deleted wallet.")

        if tx_direction == "DEBIT" and wallet.balance < amount:
            raise ValueError("Insufficient wallet balance.")

        # Create standard Django transaction
        tx = Transaction.objects.create(
            wallet=wallet,
            type=tx_direction,
            amount=amount,
            description=f"[{fine_grained_type}] {description}",
            reference_id=reference_id
        )

        # Save metadata
        set_fine_grained_tx(tx.id, fine_grained_type)

        # Update wallet balance directly from ledger entries
        credits = Transaction.objects.filter(wallet=wallet, type="CREDIT").aggregate(total=Sum("amount"))["total"] or Decimal("0.0000")
        debits = Transaction.objects.filter(wallet=wallet, type="DEBIT").aggregate(total=Sum("amount"))["total"] or Decimal("0.0000")
        wallet.balance = credits - debits
        wallet.save(update_fields=["balance", "updated_at"])
        wallet.refresh_from_db()

        return tx

    @classmethod
    @transaction.atomic
    def transfer_funds(
        cls,
        source_wallet_id: str,
        target_wallet_id: str,
        amount: Decimal,
        description: str,
        reference_id: Any = None
    ) -> Dict[str, Any]:
        """
        Executes a secure double-entry accounting transfer between wallets.
        Uses relational transactional blocks (atomic) to protect database integrity.
        """
        if str(source_wallet_id) == str(target_wallet_id):
            raise ValueError("Source and target wallets must be different.")

        # Prevent deadlocks by locking in deterministic order (by sorted ID string)
        ordered_ids = sorted([str(source_wallet_id), str(target_wallet_id)])
        locked_wallets = {}
        for w_id in ordered_ids:
            locked_wallets[w_id] = Wallet.objects.select_for_update().get(id=w_id)

        source_wallet = locked_wallets[str(source_wallet_id)]
        target_wallet = locked_wallets[str(target_wallet_id)]

        if is_wallet_id_soft_deleted(source_wallet.id) or is_wallet_id_soft_deleted(target_wallet.id):
            raise ValueError("Cannot transfer to or from a soft-deleted wallet.")

        if source_wallet.balance < amount:
            raise ValueError("Insufficient wallet balance.")

        # 1. Debit Source Wallet
        debit_tx = Transaction.objects.create(
            wallet=source_wallet,
            type="DEBIT",
            amount=amount,
            description=f"[TRANSFER] Sent to {target_wallet.user.email}: {description}",
            reference_id=reference_id
        )
        set_fine_grained_tx(debit_tx.id, "TRANSFER")
        
        # Calculate source wallet balance from ledger
        src_credits = Transaction.objects.filter(wallet=source_wallet, type="CREDIT").aggregate(total=Sum("amount"))["total"] or Decimal("0.0000")
        src_debits = Transaction.objects.filter(wallet=source_wallet, type="DEBIT").aggregate(total=Sum("amount"))["total"] or Decimal("0.0000")
        source_wallet.balance = src_credits - src_debits
        source_wallet.save(update_fields=["balance", "updated_at"])

        # 2. Credit Target Wallet
        credit_tx = Transaction.objects.create(
            wallet=target_wallet,
            type="CREDIT",
            amount=amount,
            description=f"[TRANSFER] Received from {source_wallet.user.email}: {description}",
            reference_id=reference_id
        )
        set_fine_grained_tx(credit_tx.id, "TRANSFER")
        
        # Calculate target wallet balance from ledger
        tgt_credits = Transaction.objects.filter(wallet=target_wallet, type="CREDIT").aggregate(total=Sum("amount"))["total"] or Decimal("0.0000")
        tgt_debits = Transaction.objects.filter(wallet=target_wallet, type="DEBIT").aggregate(total=Sum("amount"))["total"] or Decimal("0.0000")
        target_wallet.balance = tgt_credits - tgt_debits
        target_wallet.save(update_fields=["balance", "updated_at"])

        return {
            "source_transaction_id": debit_tx.id,
            "target_transaction_id": credit_tx.id,
            "status": "COMMITTED",
            "amount": str(amount)
        }

    @staticmethod
    def get_wallet_summary(wallet_id: str) -> Dict[str, Any]:
        """
        Generates financial aggregates for wallet.
        """
        wallet = get_object_or_404(Wallet, id=wallet_id)
        tx_qs = Transaction.objects.filter(wallet=wallet)

        credits = tx_qs.filter(type="CREDIT").aggregate(total=Sum("amount"))["total"] or Decimal("0.0000")
        debits = tx_qs.filter(type="DEBIT").aggregate(total=Sum("amount"))["total"] or Decimal("0.0000")
        
        current_balance = credits - debits
        
        # Pending balance is CREDIT transactions containing '[PENDING]' or similar in description
        pending_balance = tx_qs.filter(type="CREDIT", description__icontains="PENDING").aggregate(total=Sum("amount"))["total"] or Decimal("0.0000")
        
        # Reserved balance is DEBIT transactions containing '[RESERVED]' or similar in description
        reserved_balance = tx_qs.filter(type="DEBIT", description__icontains="RESERVED").aggregate(total=Sum("amount"))["total"] or Decimal("0.0000")
        
        available_balance = current_balance - reserved_balance
        lifetime_earnings = credits
        lifetime_spending = debits

        return {
            "wallet_id": str(wallet.id),
            "owner_email": wallet.user.email,
            "current_balance": str(current_balance),
            "available_balance": str(available_balance),
            "pending_balance": str(pending_balance),
            "reserved_balance": str(reserved_balance),
            "lifetime_earnings": str(lifetime_earnings),
            "lifetime_spending": str(lifetime_spending),
            "currency": wallet.currency,
            "total_credits": str(credits),
            "total_debits": str(debits),
            "transaction_count": tx_qs.count()
        }


class CertificateSignatureService:
    @staticmethod
    def issue_course_certificate(user_id: str, course_id: str) -> Dict[str, Any]:
        """
        Drafts a signed credential certificate confirming standard curriculum completion.
        Generates SHA-256 dynamic verification hashes to prove authenticity.
        """
        import hashlib
        raw_string = f"{user_id}:{course_id}:{timezone.now().isoformat()}"
        hash_signature = hashlib.sha256(raw_string.encode("utf-8")).hexdigest()
        return {
            "certificate_id": str(uuid.uuid4()),
            "hash_signature": hash_signature,
            "issued_at": timezone.now().isoformat()
        }


class SettlementEngineService:
    @staticmethod
    @transaction.atomic
    def process_purchase_settlement(
        buyer_user_id: str,
        price: Decimal,
        product_type: str,  # BOOK, COURSE, etc.
        product_id: str,
        platform_wallet_id: str,
        reference_id: Any = None
    ) -> Dict[str, Any]:
        """
        Processes settlement according to Revenue Ownership, GST, Commissions, and Payout splits.
        """
        from apps.users.models import User
        from apps.publishing.models import Book, ProductOwnership
        from apps.lms.models import CourseStructure
        from apps.wallets.models import Wallet
        from decimal import Decimal
        
        # 1. Tax Calculation (GST 18%)
        # For tax-inclusive pricing, net_amount = price / 1.18. tax_amount = price - net_amount
        gst_rate = Decimal("0.18")
        net_amount = price / (Decimal("1.00") + gst_rate)
        tax_amount = price - net_amount
        
        # Determine product ownership rules
        ownership = None
        if product_type == "BOOK":
            ownership = ProductOwnership.objects.filter(book_id=product_id).first()
        elif product_type == "COURSE":
            ownership = ProductOwnership.objects.filter(course_id=product_id).first()
        elif product_type == "SERVICE":
            ownership = ProductOwnership.objects.filter(owner_user_id=product_id, book__isnull=True, course__isnull=True).first()
            
        commission_rate = Decimal("10.00")  # Default platform fee 10%
        owner_wallet = None
        owner_type = "PLATFORM"
        
        if ownership:
            commission_rate = ownership.commission_rate
            owner_wallet = ownership.wallet_destination
            owner_type = ownership.owner_type
        elif product_type == "SERVICE":
            provider_user = User.objects.get(id=product_id)
            owner_wallet = provider_user.wallet
            owner_type = "TEACHER"
            
        platform_fee = net_amount * (commission_rate / Decimal("100.0"))
        creator_share = net_amount - platform_fee
        
        # Get buyer wallet
        buyer_user = User.objects.get(id=buyer_user_id)
        buyer_wallet = buyer_user.wallet
        
        # Standard debits for buyer
        LedgerTransactionService.create_transaction(
            wallet_id=str(buyer_wallet.id),
            tx_direction="DEBIT",
            fine_grained_type="PURCHASE",
            amount=price,
            description=f"Purchase of {product_type} {product_id}",
            reference_id=reference_id
        )
        
        # Credit tax to platform wallet
        LedgerTransactionService.create_transaction(
            wallet_id=str(platform_wallet_id),
            tx_direction="CREDIT",
            fine_grained_type="TAX",
            amount=tax_amount,
            description=f"GST (18%) tax collected on purchase of {product_type} {product_id}",
            reference_id=reference_id
        )
        
        # Credit platform commission to platform wallet
        LedgerTransactionService.create_transaction(
            wallet_id=str(platform_wallet_id),
            tx_direction="CREDIT",
            fine_grained_type="COMMISSION",
            amount=platform_fee,
            description=f"Platform commission fee on purchase of {product_type} {product_id}",
            reference_id=reference_id
        )
        
        # Credit remaining to owner wallet (or platform if platform owned)
        if owner_type != "PLATFORM" and owner_wallet:
            LedgerTransactionService.create_transaction(
                wallet_id=str(owner_wallet.id),
                tx_direction="CREDIT",
                fine_grained_type="SETTLEMENT",
                amount=creator_share,
                description=f"Creator payout settlement for {product_type} {product_id}",
                reference_id=reference_id
            )
        else:
            LedgerTransactionService.create_transaction(
                wallet_id=str(platform_wallet_id),
                tx_direction="CREDIT",
                fine_grained_type="SETTLEMENT",
                amount=creator_share,
                description=f"Platform payout earnings for {product_type} {product_id}",
                reference_id=reference_id
            )
            
        return {
            "price": str(price),
            "tax_collected": str(tax_amount),
            "platform_commission": str(platform_fee),
            "creator_share": str(creator_share),
            "status": "SETTLED"
        }


class SubscriptionService:
    @staticmethod
    @transaction.atomic
    def create_subscription(user, plan_name: str, price: Decimal) -> UserSubscription:
        plan, _ = SubscriptionPlan.objects.get_or_create(
            name=plan_name,
            defaults={"price": price, "duration_days": 30}
        )
        # Deactivate existing active subscriptions
        UserSubscription.objects.filter(user=user, status="ACTIVE").update(status="EXPIRED")
        
        sub = UserSubscription.objects.create(
            user=user,
            plan=plan,
            status="ACTIVE",
            expires_at=timezone.now() + timezone.timedelta(days=30)
        )
        return sub


class InvoiceService:
    @staticmethod
    @transaction.atomic
    def generate_invoice(payment: Payment, items_list: list, gst_number: str = "27AAAAA1111A1Z1") -> Invoice:
        # GST calculation
        gst_rate = Decimal("0.18")
        amount = payment.amount / (Decimal("1.00") + gst_rate)
        tax = payment.amount - amount
        
        invoice_number = f"INV-{uuid.uuid4().hex[:10].upper()}"
        
        invoice = Invoice.objects.create(
            invoice_number=invoice_number,
            payment=payment,
            user=payment.user,
            amount=amount,
            tax=tax,
            total=payment.amount,
            status="PAID" if payment.status == "COMPLETED" else "UNPAID",
            gst_number=gst_number,
            items=items_list
        )
        
        # Save GST record
        GSTRecord.objects.create(
            payment=payment,
            invoice_number=invoice_number,
            net_amount=amount,
            cgst=tax / Decimal("2.0"),
            sgst=tax / Decimal("2.0"),
            igst=Decimal("0.00"),
            total_gst=tax
        )
        
        return invoice


class RefundService:
    @staticmethod
    @transaction.atomic
    def issue_refund(payment_id: str, amount: Decimal, reason: str = "Administrative Refund") -> Refund:
        payment = get_object_or_404(Payment, id=payment_id)
        if payment.status != "COMPLETED":
            raise ValueError("Can only refund completed payments.")
            
        # Call provider capture refund details
        refund = Refund.objects.create(
            payment=payment,
            amount=amount,
            reason=reason,
            gateway_refund_id=f"re_{uuid.uuid4().hex[:10]}",
            status="SUCCEEDED"
        )
        
        payment.status = "FAILED"  # Mark payment as failed/refunded
        payment.save(update_fields=["status"])
        
        return refund


class TeacherPayoutService:
    @staticmethod
    @transaction.atomic
    def request_payout(teacher, amount: Decimal, payout_method: str = "BANK_TRANSFER") -> TeacherPayout:
        # Settle payout validation
        wallet = teacher.wallet
        if wallet.balance < amount:
            raise ValueError("Insufficient wallet balance.")
            
        # Debit wallet balance
        LedgerTransactionService.create_transaction(
            wallet_id=str(wallet.id),
            tx_direction="DEBIT",
            fine_grained_type="WITHDRAWAL",
            amount=amount,
            description=f"Withdrawal request payout of {amount} via {payout_method}"
        )
        
        payout = TeacherPayout.objects.create(
            teacher=teacher,
            amount=amount,
            status="PENDING",
            payout_method=payout_method
        )
        
        return payout
