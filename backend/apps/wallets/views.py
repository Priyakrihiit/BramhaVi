import uuid
import datetime
from decimal import Decimal
from django.db import transaction
from django.db.models import F, Q, Sum, Count
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from rest_framework import viewsets, status, mixins, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination

from apps.wallets.models import (
    Wallet, Transaction, Payment, SubscriptionPlan, UserSubscription,
    Invoice, Refund, Coupon, CouponUsage, Referral, TeacherPayout,
    RevenueSummary, GSTRecord, PaymentAudit
)
from apps.wallets.permissions import IsWalletOwnerOrAdmin, IsFinanceOrAdmin
from apps.users.permissions import HasRBACPermission
from apps.wallets.serializers import (
    WalletSerializer, TransactionSerializer, PaymentSerializer, AddFundsSerializer,
    TransferSerializer, CouponSerializer, CouponValidateSerializer, SubscriptionSerializer,
    InvoiceSerializer, SubscriptionPlanSerializer, UserSubscriptionSerializer,
    InvoiceModelSerializer, RefundModelSerializer, CouponModelSerializer,
    TeacherPayoutSerializer, RevenueSummarySerializer, GSTRecordSerializer
)
from apps.wallets.services import (
    LedgerTransactionService, SubscriptionService, InvoiceService,
    RefundService, TeacherPayoutService
)
from apps.wallets.selectors import (
    get_active_user_subscription, get_user_invoices, get_coupon_by_code,
    get_teacher_payouts, get_revenue_summaries, get_payment_refunds
)
from apps.wallets.wallet_extras_store import (
    soft_delete_wallet_id, restore_wallet_id, is_wallet_id_soft_deleted
)


class EnterprisePagination(PageNumberPagination):
    """
    Standard enterprise pagination class specifying default page size and size override parameter.
    """
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


class WalletViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling Wallet queries, updates, balance checks, soft deletion, and fund modifications.
    """
    queryset = Wallet.objects.select_related("user").all()
    serializer_class = WalletSerializer
    permission_classes = [HasRBACPermission]
    lookup_field = "id"
    pagination_class = EnterprisePagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["user__email", "currency"]
    ordering_fields = ["balance", "created_at", "updated_at"]
    ordering = ["-created_at"]

    required_permissions = {
        "list": "wallets:ledgers:read",
        "retrieve": "wallets:ledgers:read",
        "create": "wallets:ledgers:debit",
        "update": "wallets:ledgers:debit",
        "partial_update": "wallets:ledgers:debit",
        "destroy": "wallets:ledgers:debit",
        "balance": "wallets:ledgers:read",
        "summary": "wallets:ledgers:read",
        "transactions": "wallets:ledgers:read",
        "restore": "wallets:ledgers:debit",
        "add_funds": "wallets:ledgers:debit",
        "settle_purchase": "wallets:ledgers:debit",
    }

    def get_queryset(self):
        user = self.request.user
        if not user or not user.is_authenticated:
            return Wallet.objects.none()

        is_privileged = user.is_superuser or (
            hasattr(user, "role") and user.role and user.role.name in ["SUPERADMIN", "ADMIN", "FINANCE"]
        )

        include_deleted = self.request.query_params.get("include_deleted", "false").lower() == "true"

        if is_privileged:
            qs = self.queryset
        else:
            qs = self.queryset.filter(user=user)

        # Handle soft deleted filtration manually on-the-fly
        filtered_wallets = []
        for wallet in qs:
            deleted = is_wallet_id_soft_deleted(wallet.id)
            if deleted:
                if include_deleted and is_privileged:
                    filtered_wallets.append(wallet.id)
            else:
                filtered_wallets.append(wallet.id)

        return self.queryset.filter(id__in=filtered_wallets)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def destroy(self, request, *args, **kwargs):
        """
        Soft deletes the wallet.
        """
        wallet = self.get_object()
        soft_delete_wallet_id(wallet.id)
        return Response({"detail": "Wallet soft-deleted successfully.", "is_deleted": True}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="restore")
    def restore(self, request, id=None):
        """
        Restores a soft-deleted wallet.
        """
        # Read the raw wallet object without checking get_object restrictions
        wallet = get_object_or_404(Wallet, id=id)
        restore_wallet_id(wallet.id)
        return Response({"detail": "Wallet restored successfully.", "is_deleted": False}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get"], url_path="balance")
    def balance(self, request, id=None):
        """
        GET /wallets/{id}/balance/
        """
        wallet = self.get_object()
        return Response({
            "wallet_id": wallet.id,
            "balance": wallet.balance,
            "currency": wallet.currency,
        }, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get"], url_path="summary")
    def summary(self, request, id=None):
        """
        GET /wallets/{id}/summary/
        """
        wallet = self.get_object()
        summary_data = LedgerTransactionService.get_wallet_summary(wallet.id)
        return Response(summary_data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get"], url_path="transactions")
    def transactions(self, request, id=None):
        """
        GET /wallets/{id}/transactions/
        """
        wallet = self.get_object()
        transactions = wallet.transactions.all().order_by("-created_at")

        page = self.paginate_queryset(transactions)
        if page is not None:
            serializer = TransactionSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = TransactionSerializer(transactions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="add-funds")
    def add_funds(self, request, id=None):
        """
        POST /wallets/{id}/add-funds/
        """
        wallet = self.get_object()
        serializer = AddFundsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        amount = serializer.validated_data["amount"]
        description = serializer.validated_data.get("description") or "Admin credit adjustment"
        reference_id = serializer.validated_data.get("reference_id")

        try:
            tx = LedgerTransactionService.create_transaction(
                wallet_id=wallet.id,
                tx_direction="CREDIT",
                fine_grained_type="CREDIT",
                amount=amount,
                description=description,
                reference_id=reference_id
            )
            return Response({
                "detail": "Funds successfully credited.",
                "wallet_id": wallet.id,
                "balance": str(wallet.balance),
                "transaction_id": tx.id
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["post"], url_path="settle-purchase")
    def settle_purchase(self, request):
        """
        POST /wallets/settle-purchase/
        """
        buyer_user_id = request.data.get("buyer_user_id")
        price = request.data.get("price")
        product_type = request.data.get("product_type")
        product_id = request.data.get("product_id")
        platform_wallet_id = request.data.get("platform_wallet_id")
        
        if not buyer_user_id or not price or not product_type or not product_id or not platform_wallet_id:
            return Response({"detail": "buyer_user_id, price, product_type, product_id, platform_wallet_id are required."}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            from apps.wallets.services import SettlementEngineService
            summary = SettlementEngineService.process_purchase_settlement(
                buyer_user_id=buyer_user_id,
                price=Decimal(str(price)),
                product_type=product_type,
                product_id=product_id,
                platform_wallet_id=platform_wallet_id
            )
            return Response(summary, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class TransactionViewSet(mixins.CreateModelMixin,
                         mixins.RetrieveModelMixin,
                         mixins.ListModelMixin,
                         viewsets.GenericViewSet):
    """
    ViewSet for transactions. Supports fine-grained creation (debit, credit, transfer, refund, reward, purchase, withdrawal).
    Completely immutable: Update, partial_update, and destroy operations are structurally disabled.
    """
    queryset = Transaction.objects.select_related("wallet", "wallet__user").all().order_by("-created_at")
    serializer_class = TransactionSerializer
    permission_classes = [HasRBACPermission]
    lookup_field = "id"
    pagination_class = EnterprisePagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["description", "wallet__user__email"]
    ordering_fields = ["amount", "created_at"]
    ordering = ["-created_at"]

    required_permissions = {
        "list": "wallets:ledgers:read",
        "retrieve": "wallets:ledgers:read",
        "credit": "wallets:ledgers:debit",
        "debit": "wallets:ledgers:debit",
        "transfer": "wallets:ledgers:debit",
        "refund": "wallets:ledgers:debit",
        "reward": "wallets:ledgers:debit",
        "purchase": "wallets:ledgers:debit",
        "withdrawal": "wallets:ledgers:debit",
    }

    def get_queryset(self):
        user = self.request.user
        if not user or not user.is_authenticated:
            return Transaction.objects.none()

        is_privileged = user.is_superuser or (
            hasattr(user, "role") and user.role and user.role.name in ["SUPERADMIN", "ADMIN", "FINANCE"]
        )

        qs = self.queryset
        if not is_privileged:
            qs = qs.filter(wallet__user=user)

        # Filters
        tx_type = self.request.query_params.get("type")
        if tx_type:
            qs = qs.filter(type=tx_type.upper())

        wallet_id = self.request.query_params.get("wallet")
        if wallet_id:
            qs = qs.filter(wallet_id=wallet_id)

        return qs

    @action(detail=False, methods=["post"])
    def credit(self, request):
        """
        POST /transactions/credit/
        """
        wallet_id = request.data.get("wallet_id")
        amount = request.data.get("amount")
        description = request.data.get("description", "Credit Adjustment")
        reference_id = request.data.get("reference_id")

        if not wallet_id or not amount:
            return Response({"detail": "wallet_id and amount are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            tx = LedgerTransactionService.create_transaction(
                wallet_id=wallet_id,
                tx_direction="CREDIT",
                fine_grained_type="CREDIT",
                amount=Decimal(str(amount)),
                description=description,
                reference_id=reference_id
            )
            return Response(TransactionSerializer(tx).data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["post"])
    def debit(self, request):
        """
        POST /transactions/debit/
        """
        wallet_id = request.data.get("wallet_id")
        amount = request.data.get("amount")
        description = request.data.get("description", "Debit Adjustment")
        reference_id = request.data.get("reference_id")

        if not wallet_id or not amount:
            return Response({"detail": "wallet_id and amount are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            tx = LedgerTransactionService.create_transaction(
                wallet_id=wallet_id,
                tx_direction="DEBIT",
                fine_grained_type="DEBIT",
                amount=Decimal(str(amount)),
                description=description,
                reference_id=reference_id
            )
            return Response(TransactionSerializer(tx).data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["post"])
    def transfer(self, request):
        """
        POST /transactions/transfer/
        """
        serializer = TransferSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        target_wallet_id = serializer.validated_data["target_wallet_id"]
        amount = serializer.validated_data["amount"]
        description = serializer.validated_data["description"]

        user = request.user
        is_privileged = user.is_superuser or (
            hasattr(user, "role") and user.role and user.role.name in ["SUPERADMIN", "ADMIN", "FINANCE"]
        )

        source_wallet_id = request.data.get("source_wallet_id")
        if not source_wallet_id:
            # Student transferring from their own wallet
            wallet_qs = Wallet.objects.filter(user=user)
            if not wallet_qs.exists():
                return Response({"detail": "Caller does not possess a wallet."}, status=status.HTTP_400_BAD_REQUEST)
            source_wallet_id = wallet_qs.first().id
        else:
            if not is_privileged:
                # Enforce owner match if not privileged
                wallet_qs = Wallet.objects.filter(user=user, id=source_wallet_id)
                if not wallet_qs.exists():
                    return Response({"detail": "Permission denied for this source wallet."}, status=status.HTTP_403_FORBIDDEN)

        try:
            res = LedgerTransactionService.transfer_funds(
                source_wallet_id=source_wallet_id,
                target_wallet_id=target_wallet_id,
                amount=amount,
                description=description
            )
            return Response(res, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["post"])
    def refund(self, request):
        """
        POST /transactions/refund/
        """
        wallet_id = request.data.get("wallet_id")
        amount = request.data.get("amount")
        description = request.data.get("description", "Refund Transaction")
        reference_id = request.data.get("reference_id")

        if not wallet_id or not amount:
            return Response({"detail": "wallet_id and amount are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            tx = LedgerTransactionService.create_transaction(
                wallet_id=wallet_id,
                tx_direction="CREDIT",
                fine_grained_type="REFUND",
                amount=Decimal(str(amount)),
                description=description,
                reference_id=reference_id
            )
            return Response(TransactionSerializer(tx).data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["post"])
    def reward(self, request):
        """
        POST /transactions/reward/
        """
        wallet_id = request.data.get("wallet_id")
        amount = request.data.get("amount")
        description = request.data.get("description", "Reward Points Earned")
        reference_id = request.data.get("reference_id")

        if not wallet_id or not amount:
            return Response({"detail": "wallet_id and amount are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            tx = LedgerTransactionService.create_transaction(
                wallet_id=wallet_id,
                tx_direction="CREDIT",
                fine_grained_type="REWARD",
                amount=Decimal(str(amount)),
                description=description,
                reference_id=reference_id
            )
            return Response(TransactionSerializer(tx).data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["post"])
    def purchase(self, request):
        """
        POST /transactions/purchase/
        """
        wallet_id = request.data.get("wallet_id")
        amount = request.data.get("amount")
        description = request.data.get("description", "Store Purchase")
        reference_id = request.data.get("reference_id")

        if not wallet_id or not amount:
            return Response({"detail": "wallet_id and amount are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            tx = LedgerTransactionService.create_transaction(
                wallet_id=wallet_id,
                tx_direction="DEBIT",
                fine_grained_type="PURCHASE",
                amount=Decimal(str(amount)),
                description=description,
                reference_id=reference_id
            )
            return Response(TransactionSerializer(tx).data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["post"])
    def withdrawal(self, request):
        """
        POST /transactions/withdrawal/
        """
        wallet_id = request.data.get("wallet_id")
        amount = request.data.get("amount")
        description = request.data.get("description", "Fund Withdrawal")
        reference_id = request.data.get("reference_id")

        if not wallet_id or not amount:
            return Response({"detail": "wallet_id and amount are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            tx = LedgerTransactionService.create_transaction(
                wallet_id=wallet_id,
                tx_direction="DEBIT",
                fine_grained_type="WITHDRAWAL",
                amount=Decimal(str(amount)),
                description=description,
                reference_id=reference_id
            )
            return Response(TransactionSerializer(tx).data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class PaymentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling payment operations and tracking invoice payments with gateway integrations.
    """
    queryset = Payment.objects.select_related("user", "enrollment").all().order_by("-created_at")
    serializer_class = PaymentSerializer
    permission_classes = [HasRBACPermission]
    lookup_field = "id"
    pagination_class = EnterprisePagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["gateway_transaction_id", "user__email", "currency"]
    ordering_fields = ["amount", "created_at"]
    ordering = ["-created_at"]

    required_permissions = {
        "list": "wallets:ledgers:read",
        "retrieve": "wallets:ledgers:read",
        "create": "payments:checkout",
        "update": "payments:checkout",
        "partial_update": "payments:checkout",
        "destroy": "payments:admin",
        "verify": "payments:checkout",
        "retry": "payments:checkout",
        "cancel": "payments:checkout",
        "refund": "payments:admin",
    }

    def get_queryset(self):
        user = self.request.user
        if not user or not user.is_authenticated:
            return Payment.objects.none()

        is_privileged = user.is_superuser or (
            hasattr(user, "role") and user.role and user.role.name in ["SUPERADMIN", "ADMIN", "SUPPORT", "FINANCE"]
        )

        qs = self.queryset
        if not is_privileged:
            qs = qs.filter(user=user)

        status_param = self.request.query_params.get("status")
        if status_param:
            qs = qs.filter(status=status_param.upper())

        return qs

    def perform_create(self, serializer):
        serializer.save(user=self.request.user, status="PENDING")

    @action(detail=True, methods=["post"], url_path="verify")
    def verify(self, request, id=None):
        """
        POST /payments/{id}/verify/
        Verifies and transitions payment to SUCCESS status, crediting the user reward tokens.
        """
        payment = self.get_object()
        if payment.status in ["SUCCESS", "COMPLETED"]:
            return Response({"detail": "Payment is already finalized as successful."}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            payment.status = "SUCCESS"
            tx_id = request.data.get("gateway_transaction_id") or f"TXN-{uuid.uuid4().hex[:12].upper()}"
            payment.gateway_transaction_id = tx_id
            payment.save(update_fields=["status", "gateway_transaction_id"])

            # Automatic reward token issuance (e.g. 10 VIDYA per currency unit)
            wallet, created = Wallet.objects.get_or_create(user=payment.user)
            reward_amount = Decimal(str(payment.amount)) * Decimal("10.0000")

            LedgerTransactionService.create_transaction(
                wallet_id=wallet.id,
                tx_direction="CREDIT",
                fine_grained_type="REWARD",
                amount=reward_amount,
                description=f"Reward for successful payment transaction: {payment.id}",
                reference_id=payment.id
            )

            # Generate default invoice for successful payment
            invoice_id = str(uuid.uuid4())
            subtotal = Decimal(str(payment.amount)) / Decimal("1.18")
            tax = Decimal(str(payment.amount)) - subtotal
            invoice_data = {
                "id": invoice_id,
                "invoice_number": f"INV-{timezone.now().strftime('%Y%m%d')}-{invoice_id[:8].upper()}",
                "user_id": str(payment.user.id),
                "user_email": payment.user.email,
                "amount": float(subtotal.quantize(Decimal("0.01"))),
                "tax": float(tax.quantize(Decimal("0.01"))),
                "total": float(payment.amount),
                "status": "PAID",
                "items": [{"description": f"Payment Invoice for Tx: {payment.id}", "amount": float(payment.amount)}],
                "gst_number": "27AAAAA1111A1Z1",
                "created_at": timezone.now().isoformat()
            }
            set_invoice(invoice_id, invoice_data)

        return Response({
            "detail": "Payment successfully verified and completed.",
            "payment": PaymentSerializer(payment).data,
            "invoice_id": invoice_id
        }, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="retry")
    def retry(self, request, id=None):
        """
        POST /payments/{id}/retry/
        Resets failed/cancelled payment back to PENDING.
        """
        payment = self.get_object()
        if payment.status not in ["FAILED", "CANCELLED"]:
            return Response({"detail": "Only failed or cancelled payments can be retried."}, status=status.HTTP_400_BAD_REQUEST)

        payment.status = "PENDING"
        payment.save(update_fields=["status"])
        return Response(PaymentSerializer(payment).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="cancel")
    def cancel(self, request, id=None):
        """
        POST /payments/{id}/cancel/
        Cancels a pending payment.
        """
        payment = self.get_object()
        if payment.status not in ["PENDING", "PROCESSING"]:
            return Response({"detail": "Only pending or processing payments can be cancelled."}, status=status.HTTP_400_BAD_REQUEST)

        payment.status = "CANCELLED"
        payment.save(update_fields=["status"])
        return Response(PaymentSerializer(payment).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="refund")
    def refund(self, request, id=None):
        """
        POST /payments/{id}/refund/
        Refunds a successful payment, with balance deduction.
        """
        payment = self.get_object()
        if payment.status not in ["SUCCESS", "COMPLETED"]:
            return Response({"detail": "Only successful payments can be refunded."}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            payment.status = "REFUNDED"
            payment.save(update_fields=["status"])

            # Reverse reward point token issuance
            wallet, created = Wallet.objects.get_or_create(user=payment.user)
            deduct_amount = Decimal(str(payment.amount)) * Decimal("10.0000")

            # Try to debit from wallet. If balance is short, allow anyway but reflect deficit (balance can go negative on refund)
            tx = Transaction.objects.create(
                wallet=wallet,
                type="DEBIT",
                amount=deduct_amount,
                description=f"[REFUND] Revoked point reward for payment refund: {payment.id}",
                reference_id=payment.id
            )
            wallet.balance = F("balance") - deduct_amount
            wallet.save(update_fields=["balance"])

        return Response(PaymentSerializer(payment).data, status=status.HTTP_200_OK)


class SubscriptionViewSet(viewsets.ModelViewSet):
    """
    ModelViewSet handling subscriber services (Subscribe, Upgrade, Downgrade, Cancel, Renew, Current Plan).
    """
    queryset = UserSubscription.objects.select_related("user", "plan").all()
    serializer_class = UserSubscriptionSerializer
    permission_classes = [HasRBACPermission]
    lookup_field = "id"
    pagination_class = EnterprisePagination

    required_permissions = {
        "list": "payments:admin",
        "retrieve": "payments:admin",
        "create": "payments:checkout",
        "update": "payments:admin",
        "partial_update": "payments:admin",
        "destroy": "payments:admin",
        "current_plan": "payments:checkout",
        "subscribe": "payments:checkout",
        "cancel": "payments:checkout",
        "renew": "payments:checkout",
    }

    def get_queryset(self):
        user = self.request.user
        if not user or not user.is_authenticated:
            return UserSubscription.objects.none()
        if user.is_superuser or (hasattr(user, "role") and user.role and user.role.name in ["SUPERADMIN", "ADMIN"]):
            return self.queryset
        return self.queryset.filter(user=user)

    @action(detail=False, methods=["get"], url_path="current-plan")
    def current_plan(self, request):
        sub = get_active_user_subscription(request.user)
        if not sub:
            return Response({"plan_name": "Free", "status": "ACTIVE"}, status=status.HTTP_200_OK)
        return Response(UserSubscriptionSerializer(sub).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"])
    def subscribe(self, request):
        plan_name = request.data.get("plan_name", "Student Premium")
        price = Decimal(request.data.get("price", "99.00"))
        sub = SubscriptionService.create_subscription(request.user, plan_name, price)
        return Response(UserSubscriptionSerializer(sub).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"], url_path="cancel")
    def cancel(self, request, id=None):
        sub = self.get_object()
        sub.status = "CANCELLED"
        sub.save(update_fields=["status"])
        return Response(UserSubscriptionSerializer(sub).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="renew")
    def renew(self, request, id=None):
        sub = self.get_object()
        sub.status = "ACTIVE"
        sub.expires_at = max(sub.expires_at, timezone.now()) + timezone.timedelta(days=30)
        sub.save(update_fields=["status", "expires_at"])
        return Response(UserSubscriptionSerializer(sub).data, status=status.HTTP_200_OK)


class CouponViewSet(viewsets.ModelViewSet):
    """
    ModelViewSet for administrative and student operations on Coupon codes.
    """
    queryset = Coupon.objects.all()
    serializer_class = CouponModelSerializer
    permission_classes = [HasRBACPermission]
    lookup_field = "id"
    pagination_class = EnterprisePagination

    required_permissions = {
        "list": "payments:admin",
        "retrieve": "payments:admin",
        "create": "payments:admin",
        "update": "payments:admin",
        "partial_update": "payments:admin",
        "destroy": "payments:admin",
        "validate_coupon": "payments:checkout",
        "apply_coupon": "payments:checkout",
    }

    @action(detail=False, methods=["post"], url_path="validate-coupon")
    def validate_coupon(self, request):
        code = request.data.get("code")
        cart_amount = Decimal(str(request.data.get("cart_amount", "0.00")))
        coupon = get_coupon_by_code(code)
        if not coupon:
            return Response({"detail": "Invalid or expired coupon code."}, status=status.HTTP_400_BAD_REQUEST)
        if coupon.usage_count >= coupon.usage_limit:
            return Response({"detail": "Coupon limit reached."}, status=status.HTTP_400_BAD_REQUEST)
        if cart_amount < coupon.minimum_purchase:
            return Response({"detail": f"Cart total must exceed ${coupon.minimum_purchase}."}, status=status.HTTP_400_BAD_REQUEST)

        discount = coupon.value if coupon.type == "FIXED" else cart_amount * (coupon.value / Decimal("100.00"))
        discount = min(discount, cart_amount)

        return Response({
            "code": coupon.code,
            "valid": True,
            "calculated_discount": str(discount.quantize(Decimal("0.01"))),
            "final_amount": str((cart_amount - discount).quantize(Decimal("0.01")))
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"], url_path="apply-coupon")
    def apply_coupon(self, request):
        code = request.data.get("code")
        cart_amount = Decimal(str(request.data.get("cart_amount", "0.00")))
        coupon = get_coupon_by_code(code)
        if not coupon or coupon.usage_count >= coupon.usage_limit or cart_amount < coupon.minimum_purchase:
            return Response({"detail": "Voucher is invalid or expired."}, status=status.HTTP_400_BAD_REQUEST)
        
        coupon.usage_count += 1
        coupon.save(update_fields=["usage_count"])
        
        discount = coupon.value if coupon.type == "FIXED" else cart_amount * (coupon.value / Decimal("100.00"))
        discount = min(discount, cart_amount)
        
        return Response({
            "code": coupon.code,
            "calculated_discount": str(discount.quantize(Decimal("0.01"))),
            "final_amount": str((cart_amount - discount).quantize(Decimal("0.01")))
        }, status=status.HTTP_200_OK)


class InvoiceViewSet(viewsets.ModelViewSet):
    """
    ModelViewSet for rendering customer invoices and payment receipts (GST-Ready).
    """
    queryset = Invoice.objects.select_related("payment", "user").all().order_by("-created_at")
    serializer_class = InvoiceModelSerializer
    permission_classes = [HasRBACPermission]
    lookup_field = "id"
    pagination_class = EnterprisePagination

    required_permissions = {
        "list": "payments:checkout",
        "retrieve": "payments:checkout",
        "create": "payments:admin",
        "update": "payments:admin",
        "partial_update": "payments:admin",
        "destroy": "payments:admin",
        "download": "payments:checkout",
        "receipt": "payments:checkout",
    }

    def get_queryset(self):
        user = self.request.user
        if not user or not user.is_authenticated:
            return Invoice.objects.none()
        if user.is_superuser or (hasattr(user, "role") and user.role and user.role.name in ["SUPERADMIN", "ADMIN", "FINANCE"]):
            return self.queryset
        return self.queryset.filter(user=user)

    @action(detail=True, methods=["get"], url_path="download")
    def download(self, request, id=None):
        inv = self.get_object()
        items_lines = ""
        for item in inv.items:
            items_lines += f"| {item.get('description', 'Purchase Item'):<40} | ₹{float(item.get('amount', 0.00)):>10.2f} |\n"

        invoice_content = f"""
============================================================
             INVOICE: {inv.invoice_number}
============================================================
BrahmaVidya Galaxy Portal Ltd.
GSTIN: {inv.gst_number}
Date: {inv.created_at.strftime('%Y-%m-%d')}
Client Email: {inv.user.email}
------------------------------------------------------------
Items Breakdown:
| Description                              |     Amount |
------------------------------------------------------------
{items_lines}------------------------------------------------------------
Subtotal (Excl. GST @ 18%):                   ₹{float(inv.amount):>10.2f}
IGST tax (18%):                               ₹{float(inv.tax):>10.2f}
============================================================
TOTAL DUE / PAID:                             ₹{float(inv.total):>10.2f}
============================================================
Thank you for learning with BrahmaVidya Galaxy!
"""
        response = HttpResponse(invoice_content, content_type="text/plain")
        response["Content-Disposition"] = f'attachment; filename="Invoice-{inv.invoice_number}.txt"'
        return response

    @action(detail=True, methods=["get"], url_path="receipt")
    def receipt(self, request, id=None):
        inv = self.get_object()
        receipt_content = f"""
============================================================
                  OFFICIAL PAYMENT RECEIPT
============================================================
Receipt ID: RCPT-{str(inv.id)[:8].upper()}
Invoice Reference: {inv.invoice_number}
Date issued: {inv.created_at.strftime('%Y-%m-%d')}
Customer: {inv.user.email}
------------------------------------------------------------
Transaction Total Received:                 ₹{float(inv.total):.2f}
Payment Gateway Confirmation:               SUCCESS (PAID)
============================================================
"""
        response = HttpResponse(receipt_content, content_type="text/plain")
        response["Content-Disposition"] = f'attachment; filename="Receipt-{str(inv.id)[:8]}.txt"'
        return response


class TeacherPayoutViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling teacher payout requests and approvals.
    """
    queryset = TeacherPayout.objects.select_related("teacher").all().order_by("-created_at")
    serializer_class = TeacherPayoutSerializer
    permission_classes = [HasRBACPermission]
    lookup_field = "id"
    pagination_class = EnterprisePagination

    required_permissions = {
        "list": "payments:admin",
        "retrieve": "payments:admin",
        "create": "payments:checkout",
        "update": "payments:admin",
        "partial_update": "payments:admin",
        "destroy": "payments:admin",
        "approve": "payments:admin",
    }

    def get_queryset(self):
        user = self.request.user
        if not user or not user.is_authenticated:
            return TeacherPayout.objects.none()
        if user.is_superuser or (hasattr(user, "role") and user.role and user.role.name in ["SUPERADMIN", "ADMIN", "FINANCE"]):
            return self.queryset
        return self.queryset.filter(teacher=user)

    def perform_create(self, serializer):
        TeacherPayoutService.request_payout(self.request.user, serializer.validated_data["amount"], serializer.validated_data.get("payout_method", "BANK_TRANSFER"))

    @action(detail=True, methods=["post"], url_path="approve")
    def approve(self, request, id=None):
        payout = self.get_object()
        payout.status = "APPROVED"
        payout.reference_id = request.data.get("reference_id", f"PAY-{uuid.uuid4().hex[:10].upper()}")
        payout.save(update_fields=["status", "reference_id"])
        return Response(TeacherPayoutSerializer(payout).data, status=status.HTTP_200_OK)


class RefundViewSet(viewsets.ModelViewSet):
    """
    ViewSet for tracking and executing refunds.
    """
    queryset = Refund.objects.select_related("payment").all().order_by("-created_at")
    serializer_class = RefundModelSerializer
    permission_classes = [HasRBACPermission]
    lookup_field = "id"
    pagination_class = EnterprisePagination

    required_permissions = {
        "list": "payments:admin",
        "retrieve": "payments:admin",
        "create": "payments:admin",
        "update": "payments:admin",
        "partial_update": "payments:admin",
        "destroy": "payments:admin",
    }

    def perform_create(self, serializer):
        RefundService.issue_refund(serializer.validated_data["payment"].id, serializer.validated_data["amount"], serializer.validated_data.get("reason", "Administrative Refund"))


class RevenueAnalyticsViewSet(viewsets.ViewSet):
    """
    ViewSet for computing and plotting system-wide revenue statistics and metrics.
    """
    permission_classes = [HasRBACPermission]
    required_permissions = {
        "summary": "sys:analytics:read",
    }

    @action(detail=False, methods=["get"], url_path="summary")
    def summary(self, request):
        now = timezone.now()
        one_day_ago = now - timezone.timedelta(days=1)
        one_month_ago = now - timezone.timedelta(days=30)

        daily_pmts = Payment.objects.filter(status__in=["SUCCESS", "COMPLETED"], created_at__gte=one_day_ago)
        daily_rev = daily_pmts.aggregate(total=Sum("amount"))["total"] or Decimal("0.00")

        monthly_pmts = Payment.objects.filter(status__in=["SUCCESS", "COMPLETED"], created_at__gte=one_month_ago)
        monthly_rev = monthly_pmts.aggregate(total=Sum("amount"))["total"] or Decimal("0.00")

        wallet_purchase_txs = Transaction.objects.filter(type="DEBIT")
        wallet_rev = wallet_purchase_txs.aggregate(total=Sum("amount"))["total"] or Decimal("0.00")

        # Database backed Subscription plans totals
        active_subs_count = UserSubscription.objects.filter(status="ACTIVE").count()
        sub_rev = Decimal(str(active_subs_count)) * Decimal("99.00")

        total_payments = Payment.objects.count()
        success_payments = Payment.objects.filter(status__in=["SUCCESS", "COMPLETED"]).count()
        refund_payments = Payment.objects.filter(status="REFUNDED").count()

        success_rate = (success_payments / total_payments * 100) if total_payments > 0 else 100.0
        refund_rate = (refund_payments / total_payments * 100) if total_payments > 0 else 0.0

        return Response({
            "daily_revenue": str(daily_rev),
            "monthly_revenue": str(monthly_rev),
            "wallet_revenue": str(wallet_rev),
            "subscription_revenue": str(sub_rev),
            "payment_success_rate": round(success_rate, 2),
            "refund_rate": round(refund_rate, 2),
            "total_payment_count": total_payments
        }, status=status.HTTP_200_OK)
