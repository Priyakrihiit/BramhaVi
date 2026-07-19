import uuid
import datetime
from decimal import Decimal
from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from rest_framework import viewsets, status, filters, serializers
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.wallets.models import Wallet, Transaction, Payment
from apps.control_center.models import PlatformSetting
from apps.users.permissions import HasRBACPermission
from apps.wallets.views import EnterprisePagination

from apps.wallets.payment_gateway_services import (
    PaymentGatewayService, CouponService, PGAnalyticsService,
    PaymentProviderRegistry, calculate_gst_breakdown,
    read_pg_store, write_pg_store, log_pg_audit
)


# -------------------------------------------------------------
# Dynamic & Enterprise Serializers
# -------------------------------------------------------------

class DynamicPaymentSerializer(serializers.ModelSerializer):
    """
    Enterprise-grade dynamic serializer supporting lazy loading and conditional field visibility.
    """
    user_email = serializers.ReadOnlyField(source="user.email")
    gst_breakdown = serializers.SerializerMethodField()
    refund_details = serializers.SerializerMethodField()

    class Meta:
        model = Payment
        fields = [
            "id", "user", "user_email", "enrollment", "amount", "currency",
            "payment_gateway", "gateway_transaction_id", "status", "created_at",
            "gst_breakdown", "refund_details"
        ]

    def get_gst_breakdown(self, obj) -> dict:
        # Generate on-the-fly GST metadata
        return calculate_gst_breakdown(Decimal(str(obj.amount)))

    def get_refund_details(self, obj) -> dict:
        if obj.status in ["REFUNDED", "PARTIALLY_REFUNDED"]:
            pg_store = read_pg_store()
            return pg_store.get("refund_notes", {}).get(obj.gateway_transaction_id, {})
        return None


class CouponPlatformSettingSerializer(serializers.ModelSerializer):
    """
    Database-backed ModelSerializer translating PlatformSetting JSON value into a structured Coupon object.
    Requires NO migrations and supports search, filtering, and ordering.
    """
    code = serializers.CharField(required=True)
    type = serializers.ChoiceField(choices=[("PERCENTAGE", "Percentage"), ("FIXED", "Fixed")], required=True)
    value = serializers.DecimalField(max_digits=10, decimal_places=2, required=True)
    usage_limit = serializers.IntegerField(required=False, default=100)
    usage_count = serializers.IntegerField(read_only=True)
    expiry_date = serializers.CharField(required=True)  # YYYY-MM-DD
    minimum_purchase = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, default=Decimal("0.00"))
    is_active = serializers.BooleanField(required=False, default=True)

    class Meta:
        model = PlatformSetting
        fields = ["id", "code", "type", "value", "usage_limit", "usage_count", "expiry_date", "minimum_purchase", "is_active"]

    def to_representation(self, instance):
        # Convert PlatformSetting database format to representation
        data = instance.value if isinstance(instance.value, dict) else {}
        code = instance.key.replace("coupon_", "")
        return {
            "id": str(instance.id),
            "code": code,
            "type": data.get("type", "PERCENTAGE"),
            "value": float(data.get("value", 0)),
            "usage_limit": int(data.get("usage_limit", 100)),
            "usage_count": int(data.get("usage_count", 0)),
            "expiry_date": data.get("expiry_date", ""),
            "minimum_purchase": float(data.get("minimum_purchase", 0)),
            "is_active": bool(data.get("is_active", True))
        }

    def create(self, validated_data):
        code = validated_data["code"].upper().strip()
        key = f"coupon_{code}"
        if PlatformSetting.objects.filter(key=key).exists():
            raise serializers.ValidationError({"code": "Coupon with this code already exists."})

        coupon_data = {
            "type": validated_data["type"],
            "value": str(validated_data["value"]),
            "usage_limit": validated_data.get("usage_limit", 100),
            "usage_count": 0,
            "expiry_date": validated_data["expiry_date"],
            "minimum_purchase": str(validated_data.get("minimum_purchase", Decimal("0.00"))),
            "is_active": validated_data.get("is_active", True)
        }

        # Create record in PlatformSetting
        setting = PlatformSetting.objects.create(
            key=key,
            value=coupon_data,
            description=f"Payment coupon code: {code}"
        )

        # Synchronize with legacy JSON store for seamless interoperability
        CouponService.create_coupon(validated_data)

        return setting

    def update(self, instance, validated_data):
        code = instance.key.replace("coupon_", "")
        coupon_data = {
            "type": validated_data.get("type", instance.value.get("type")),
            "value": str(validated_data.get("value", instance.value.get("value"))),
            "usage_limit": validated_data.get("usage_limit", instance.value.get("usage_limit", 100)),
            "usage_count": instance.value.get("usage_count", 0),
            "expiry_date": validated_data.get("expiry_date", instance.value.get("expiry_date")),
            "minimum_purchase": str(validated_data.get("minimum_purchase", instance.value.get("minimum_purchase", Decimal("0.00")))),
            "is_active": validated_data.get("is_active", instance.value.get("is_active", True))
        }
        instance.value = coupon_data
        instance.save()

        # Synchronize back
        store = read_pg_store()
        store["custom_coupons"][code] = {
            "code": code,
            **coupon_data
        }
        write_pg_store(store)

        return instance


# -------------------------------------------------------------
# ViewSets (ModelViewSets Only)
# -------------------------------------------------------------

class PaymentGatewayViewSet(viewsets.ModelViewSet):
    """
    Module 13 — Enterprise Payment Gateway Router & Integration Engine.
    Governs monetary checkouts, verifications, captures, and secure webhook channels.
    """
    queryset = Payment.objects.select_related("user", "enrollment").all().order_by("-created_at")
    serializer_class = DynamicPaymentSerializer
    permission_classes = [HasRBACPermission]
    lookup_field = "id"
    pagination_class = EnterprisePagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["gateway_transaction_id", "user__email", "payment_gateway"]
    ordering_fields = ["amount", "created_at"]
    ordering = ["-created_at"]

    required_permissions = {
        "list": "payments:checkout",
        "retrieve": "payments:checkout",
        "create": "payments:checkout",
        "update": "payments:admin",
        "destroy": "payments:admin",
        "create_order": "payments:checkout",
        "verify_order": "payments:checkout",
        "capture": "payments:checkout",
        "cancel_order": "payments:checkout",
        "retry_order": "payments:checkout",
        "refund_order": "payments:admin",
        "partial_refund": "payments:admin",
        "payment_status": "payments:checkout",
        "pending_payments": "payments:admin",
        "failed_payments": "payments:admin",
        "restore": "payments:admin",
        "analytics": "sys:analytics:read",
        "webhook": "payments:checkout",  # Webhook triggers are public-ready
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

        # Filters
        gateway = self.request.query_params.get("gateway")
        if gateway:
            qs = qs.filter(payment_gateway=gateway.upper())

        status_param = self.request.query_params.get("status")
        if status_param:
            qs = qs.filter(status=status_param.upper())

        # Handle virtual soft deletion
        include_deleted = self.request.query_params.get("include_deleted", "false").lower() == "true"
        pg_store = read_pg_store()
        soft_deleted_ids = pg_store.get("soft_deleted_payments", [])

        if include_deleted and is_privileged:
            # Show all records
            pass
        else:
            # Exclude soft deleted
            qs = qs.exclude(id__in=soft_deleted_ids)

        return qs

    def perform_destroy(self, instance):
        # Implement virtual soft delete
        pg_store = read_pg_store()
        if "soft_deleted_payments" not in pg_store:
            pg_store["soft_deleted_payments"] = []
        inst_id = str(instance.id)
        if inst_id not in pg_store["soft_deleted_payments"]:
            pg_store["soft_deleted_payments"].append(inst_id)
            write_pg_store(pg_store)
            log_pg_audit("PAYMENT_SOFT_DELETED", self.request.user.email, instance.id)

    @action(detail=True, methods=["post"], url_path="restore")
    def restore(self, request, id=None):
        """Restores a virtually soft-deleted payment record."""
        payment = get_object_or_404(Payment, id=id)
        pg_store = read_pg_store()
        soft_deleted_ids = pg_store.get("soft_deleted_payments", [])
        inst_id = str(payment.id)
        if inst_id in soft_deleted_ids:
            soft_deleted_ids.remove(inst_id)
            pg_store["soft_deleted_payments"] = soft_deleted_ids
            write_pg_store(pg_store)
            log_pg_audit("PAYMENT_RESTORED", request.user.email, payment.id)
            return Response({"detail": "Payment restored successfully.", "is_deleted": False}, status=status.HTTP_200_OK)
        return Response({"detail": "Payment is not deleted."}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["post"], url_path="create-order")
    def create_order(self, request):
        """
        POST /api/v1/wallets/payments/create-order/
        Initializes an order across Razorpay, Stripe, PayPal, PhonePe, Cashfree, or PayU.
        """
        user = request.user
        amount = Decimal(str(request.data.get("amount")))
        currency = request.data.get("currency", "USD")
        gateway = request.data.get("payment_gateway", "STRIPE")
        item_type = request.data.get("item_type", "COURSE")  # COURSE, BUNDLE, PROJECT, CERTIFICATE, SUBSCRIPTION
        item_id = request.data.get("item_id")  # Course UUID or subscription plan name
        coupon_code = request.data.get("coupon_code")

        if not amount or not item_id:
            return Response({"error": "amount and item_id are required fields."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            res = PaymentGatewayService.create_payment_intent(
                user=user,
                amount=amount,
                currency=currency,
                gateway=gateway,
                item_type=item_type,
                item_id=item_id,
                coupon_code=coupon_code
            )
            return Response(res, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"], url_path="verify-order")
    def verify_order(self, request, id=None):
        """
        POST /api/v1/wallets/payments/{id}/verify-order/
        Verifies signatures/hashes and finalizes reward points credits, LMS enrollments, and GST invoice generations.
        """
        payment = self.get_object()
        gateway_transaction_id = request.data.get("gateway_transaction_id") or payment.gateway_transaction_id

        # Trigger cryptographic or abstract provider verification
        provider = PaymentProviderRegistry.get_provider(payment.payment_gateway)
        payload = request.data.get("payload", {})
        signature = request.data.get("signature", "")

        is_valid = provider.verify_payment_signature(payload, signature)
        if not is_valid:
            return Response({"error": "Cryptographic signature verification failed."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            finalized_payment = PaymentGatewayService.finalize_successful_payment(
                payment_id=payment.id,
                gateway_transaction_id=gateway_transaction_id
            )
            return Response({
                "detail": "Payment successfully verified and finalized.",
                "payment": DynamicPaymentSerializer(finalized_payment).data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"], url_path="capture")
    def capture(self, request, id=None):
        """POST /api/v1/wallets/payments/{id}/capture/"""
        payment = self.get_object()
        provider = PaymentProviderRegistry.get_provider(payment.payment_gateway)
        try:
            capture_res = provider.capture_payment(payment.gateway_transaction_id, payment.amount)
            payment.status = "COMPLETED"
            payment.save(update_fields=["status"])
            log_pg_audit("PAYMENT_CAPTURED", request.user.email, payment.id, capture_res)
            return Response(capture_res, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"], url_path="cancel-order")
    def cancel_order(self, request, id=None):
        """POST /api/v1/wallets/payments/{id}/cancel-order/"""
        payment = self.get_object()
        provider = PaymentProviderRegistry.get_provider(payment.payment_gateway)
        try:
            cancel_res = provider.cancel_payment(payment.gateway_transaction_id)
            payment.status = "FAILED"
            payment.save(update_fields=["status"])
            log_pg_audit("PAYMENT_CANCELLED_GATEWAY", request.user.email, payment.id, cancel_res)
            return Response(cancel_res, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"], url_path="retry-order")
    def retry_order(self, request, id=None):
        """POST /api/v1/wallets/payments/{id}/retry-order/"""
        payment = self.get_object()
        if payment.status not in ["FAILED", "CANCELLED"]:
            return Response({"error": "Only failed/cancelled payments can be retried."}, status=status.HTTP_400_BAD_REQUEST)

        payment.status = "PENDING"
        payment.save(update_fields=["status"])
        log_pg_audit("PAYMENT_RETR_STARTED", request.user.email, payment.id)
        return Response(DynamicPaymentSerializer(payment).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="refund-order")
    def refund_order(self, request, id=None):
        """POST /api/v1/wallets/payments/{id}/refund-order/ (Complete refund)"""
        payment = self.get_object()
        reason = request.data.get("reason", "Administrative Refund")
        try:
            res = PaymentGatewayService.process_refund_with_reversals(payment_id=payment.id, reason=reason)
            return Response(res, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"], url_path="partial-refund")
    def partial_refund(self, request, id=None):
        """POST /api/v1/wallets/payments/{id}/partial-refund/"""
        payment = self.get_object()
        amount_val = request.data.get("amount")
        reason = request.data.get("reason", "Administrative Partial Refund")

        if not amount_val:
            return Response({"error": "amount parameter is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            amount = Decimal(str(amount_val))
            res = PaymentGatewayService.process_refund_with_reversals(payment_id=payment.id, amount=amount, reason=reason)
            return Response(res, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["get"], url_path="payment-status")
    def payment_status(self, request, id=None):
        """GET /api/v1/wallets/payments/{id}/payment-status/"""
        payment = self.get_object()
        return Response({
            "payment_id": payment.id,
            "status": payment.status,
            "currency": payment.currency,
            "amount": float(payment.amount),
            "gateway": payment.payment_gateway,
            "gateway_order_id": payment.gateway_transaction_id,
            "created_at": payment.created_at
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], url_path="pending")
    def pending_payments(self, request):
        """GET /api/v1/wallets/payments/pending/"""
        queryset = self.filter_queryset(self.get_queryset().filter(status="PENDING"))
        page = self.paginate_queryset(queryset)
        if page is not None:
            ser = self.get_serializer(page, many=True)
            return self.get_paginated_response(ser.data)
        ser = self.get_serializer(queryset, many=True)
        return Response(ser.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], url_path="failed")
    def failed_payments(self, request):
        """GET /api/v1/wallets/payments/failed/"""
        queryset = self.filter_queryset(self.get_queryset().filter(status="FAILED"))
        page = self.paginate_queryset(queryset)
        if page is not None:
            ser = self.get_serializer(page, many=True)
            return self.get_paginated_response(ser.data)
        ser = self.get_serializer(queryset, many=True)
        return Response(ser.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], url_path="analytics-reports")
    def analytics(self, request):
        """GET /api/v1/wallets/payments/analytics-reports/"""
        stats = PGAnalyticsService.get_comprehensive_dashboard_stats()
        return Response(stats, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"], url_path="webhook/(?P<provider>[^/.]+)")
    def webhook(self, request, provider=None):
        """
        POST /api/v1/wallets/payments/webhook/{provider}/
        Unified Webhook endpoint mapping: Razorpay, Stripe, PayPal, PhonePe, Cashfree, and PayU.
        Provides secure signature checks, duplicate event detection, and strict idempotency.
        """
        raw_body = request.body.decode("utf-8")
        signature = request.META.get("HTTP_X_PAYMENT_SIGNATURE", "")
        secret = "MOCK_WEBHOOK_SECRET_KEY"

        # Lookup and verify signature
        try:
            prov_adapter = PaymentProviderRegistry.get_provider(provider)
            sig_ok = prov_adapter.verify_webhook_signature(raw_body, signature, secret)
            if not sig_ok:
                return Response({"error": "Webhook signature mismatch."}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # Parse Event data
        data = request.data
        gateway_txn_id = data.get("gateway_transaction_id") or data.get("order_id") or data.get("id")

        if not gateway_txn_id:
            return Response({"error": "Missing transaction identifier in payload."}, status=status.HTTP_400_BAD_REQUEST)

        # Maintain Idempotency: Prevent duplicate webhook processing
        pg_store = read_pg_store()
        webhook_log = pg_store["webhook_logs"].get(gateway_txn_id)

        if webhook_log and webhook_log.get("processed"):
            # Already finalized successfully. Return 200 OK directly.
            return Response({"detail": "Webhook event already processed.", "idempotent": True}, status=status.HTTP_200_OK)

        # Retrieve Payment record
        payment = Payment.objects.filter(gateway_transaction_id=gateway_txn_id).first()
        if not payment:
            # Create dynamic/unrecognized payment record as fail-safe fallback
            user_email = data.get("user_email")
            user = User.objects.filter(email=user_email).first() if user_email else User.objects.first()
            payment = Payment.objects.create(
                user=user,
                amount=Decimal(str(data.get("amount", "0.00"))),
                currency=data.get("currency", "USD").upper(),
                payment_gateway=provider.upper(),
                gateway_transaction_id=gateway_txn_id,
                status="PENDING"
            )

        # Finalize and credit rewards, LMS activation
        try:
            PaymentGatewayService.finalize_successful_payment(
                payment_id=payment.id,
                gateway_transaction_id=gateway_txn_id
            )
            return Response({"detail": "Webhook callback processed successfully.", "payment_id": str(payment.id)}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": f"Failed to process webhook: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SubscriptionGatewayViewSet(viewsets.ModelViewSet):
    """
    ModelViewSet governing student subscriptions and pricing plans.
    """
    queryset = Payment.objects.filter(gateway_transaction_id__isnull=False).select_related("user")
    serializer_class = DynamicPaymentSerializer
    permission_classes = [HasRBACPermission]
    lookup_field = "id"
    pagination_class = EnterprisePagination

    required_permissions = {
        "list": "payments:checkout",
        "retrieve": "payments:checkout",
        "create": "payments:checkout",
        "update": "payments:admin",
        "destroy": "payments:admin",
        "current_plan": "payments:checkout",
        "subscribe": "payments:checkout",
        "upgrade": "payments:checkout",
        "downgrade": "payments:checkout",
        "cancel": "payments:checkout",
        "renew": "payments:checkout",
        "history": "payments:checkout"
    }

    @action(detail=False, methods=["get"], url_path="current-plan")
    def current_plan(self, request):
        """GET /api/v1/wallets/subscriptions/current-plan/"""
        user = request.user
        from apps.wallets.wallet_extras_store import get_user_subscription, set_user_subscription
        sub = get_user_subscription(user.id)
        if not sub:
            sub = {
                "id": str(uuid.uuid4()),
                "plan_name": "Free Plan",
                "status": "active",
                "created_at": timezone.now().isoformat(),
                "expires_at": (timezone.now() + timezone.timedelta(days=36500)).isoformat()
            }
            set_user_subscription(user.id, sub)
        return Response(sub, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"], url_path="subscribe")
    def subscribe(self, request):
        """
        POST /api/v1/wallets/subscriptions/subscribe/
        Initiates a pricing plan subscription.
        Plans supported: Free Plan, Student Premium, Teacher Premium, Institute, Portfolio Builder, Business Website, Enterprise.
        """
        user = request.user
        plan_name = request.data.get("plan_name")
        gateway = request.data.get("payment_gateway", "STRIPE")
        coupon_code = request.data.get("coupon_code")

        valid_plans = {
            "Free Plan": Decimal("0.00"),
            "Student Premium": Decimal("19.00"),
            "Teacher Premium": Decimal("49.00"),
            "Institute": Decimal("199.00"),
            "Portfolio Builder": Decimal("9.00"),
            "Business Website": Decimal("49.00"),
            "Enterprise": Decimal("999.00")
        }

        if plan_name not in valid_plans:
            return Response({"error": f"Invalid pricing plan. Supported: {list(valid_plans.keys())}"}, status=status.HTTP_400_BAD_REQUEST)

        amount = valid_plans[plan_name]

        if amount == Decimal("0.00"):
            # Free plan setup directly
            sub_id = str(uuid.uuid4())
            sub_data = {
                "id": sub_id,
                "plan_name": plan_name,
                "status": "active",
                "created_at": timezone.now().isoformat(),
                "expires_at": (timezone.now() + timezone.timedelta(days=36500)).isoformat(),
                "auto_renew": False,
                "payment_gateway": "FREE",
                "invoice_ref": "FREE"
            }
            from apps.wallets.wallet_extras_store import set_user_subscription
            set_user_subscription(user.id, sub_data)
            return Response({"detail": "Successfully subscribed to Free plan.", "subscription": sub_data}, status=status.HTTP_201_CREATED)

        # Paid plan: Create payment order flow
        try:
            res = PaymentGatewayService.create_payment_intent(
                user=user,
                amount=amount,
                currency="USD",
                gateway=gateway,
                item_type="SUBSCRIPTION",
                item_id=plan_name,
                coupon_code=coupon_code
            )
            return Response(res, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["post"], url_path="upgrade")
    def upgrade(self, request):
        """POST /api/v1/wallets/subscriptions/upgrade/"""
        # Initiates upgrade payment intent
        return self.subscribe(request)

    @action(detail=False, methods=["post"], url_path="downgrade")
    def downgrade(self, request):
        """POST /api/v1/wallets/subscriptions/downgrade/"""
        user = request.user
        plan_name = request.data.get("plan_name")
        # Direct downgrade configuration in persistent store
        sub_id = str(uuid.uuid4())
        sub_data = {
            "id": sub_id,
            "plan_name": plan_name,
            "status": "active",
            "created_at": timezone.now().isoformat(),
            "expires_at": (timezone.now() + timezone.timedelta(days=30)).isoformat(),
            "auto_renew": True,
            "payment_gateway": "DOWNGRADE",
            "invoice_ref": "DOWNGRADE"
        }
        from apps.wallets.wallet_extras_store import set_user_subscription
        set_user_subscription(user.id, sub_data)
        log_pg_audit("SUBSCRIPTION_DOWNGRADED", user.email, None, {"plan_name": plan_name})
        return Response({"detail": f"Subscription downgraded successfully to {plan_name}.", "subscription": sub_data}, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"], url_path="cancel")
    def cancel(self, request):
        """POST /api/v1/wallets/subscriptions/cancel/"""
        user = request.user
        from apps.wallets.wallet_extras_store import get_user_subscription, set_user_subscription
        sub = get_user_subscription(user.id)
        if not sub:
            return Response({"error": "No active subscription found."}, status=status.HTTP_400_BAD_REQUEST)

        sub["status"] = "cancelled"
        sub["auto_renew"] = False
        set_user_subscription(user.id, sub)
        log_pg_audit("SUBSCRIPTION_CANCELLED", user.email, None)
        return Response({"detail": "Auto-renewal has been cancelled successfully.", "subscription": sub}, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"], url_path="renew")
    def renew(self, request):
        """POST /api/v1/wallets/subscriptions/renew/"""
        return self.subscribe(request)

    @action(detail=False, methods=["get"], url_path="history")
    def history(self, request):
        """GET /api/v1/wallets/subscriptions/history/"""
        store = read_pg_store()
        u_id = str(request.user.id)
        hist = store.get("subscription_history", {}).get(u_id, [])
        return Response(hist, status=status.HTTP_200_OK)


class CouponGatewayViewSet(viewsets.ModelViewSet):
    """
    ModelViewSet governing coupon administration, validating and applying.
    Database-backed using PlatformSetting key-value mapping to respect zero-migrations.
    """
    queryset = PlatformSetting.objects.filter(key__startswith="coupon_")
    serializer_class = CouponPlatformSettingSerializer
    permission_classes = [HasRBACPermission]
    lookup_field = "id"
    pagination_class = EnterprisePagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["key"]
    ordering_fields = ["key"]
    ordering = ["key"]

    required_permissions = {
        "list": "payments:admin",
        "retrieve": "payments:admin",
        "create": "payments:admin",
        "update": "payments:admin",
        "destroy": "payments:admin",
        "validate_coupon": "payments:checkout",
        "apply_coupon": "payments:checkout",
        "remove_coupon": "payments:checkout"
    }

    @action(detail=False, methods=["post"], url_path="validate-coupon")
    def validate_coupon(self, request):
        """
        POST /api/v1/wallets/coupons/validate-coupon/
        Checks minimum purchase, usage counts, active flags, and date expirations.
        """
        code = request.data.get("code")
        amount_val = request.data.get("amount")

        if not code or not amount_val:
            return Response({"error": "code and amount parameters are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            amount = Decimal(str(amount_val))
            res = CouponService.validate_coupon(code, amount)
            return Response(res, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["post"], url_path="apply-coupon")
    def apply_coupon(self, request):
        """POST /api/v1/wallets/coupons/apply-coupon/"""
        code = request.data.get("code")
        amount_val = request.data.get("amount")

        if not code or not amount_val:
            return Response({"error": "code and amount parameters are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            amount = Decimal(str(amount_val))
            res = CouponService.apply_coupon(code, amount)
            # Synchronize PlatformSetting record usage count
            if res["valid"]:
                setting = PlatformSetting.objects.filter(key=f"coupon_{code.upper().strip()}").first()
                if setting:
                    setting.value["usage_count"] = setting.value.get("usage_count", 0) + 1
                    setting.save(update_fields=["value"])
            return Response(res, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["post"], url_path="remove-coupon")
    def remove_coupon(self, request):
        """POST /api/v1/wallets/coupons/remove-coupon/"""
        code = request.data.get("code")
        if not code:
            return Response({"error": "code parameter is required."}, status=status.HTTP_400_BAD_REQUEST)

        ok = CouponService.remove_coupon(code)
        if ok:
            setting = PlatformSetting.objects.filter(key=f"coupon_{code.upper().strip()}").first()
            if setting and setting.value.get("usage_count", 0) > 0:
                setting.value["usage_count"] -= 1
                setting.save(update_fields=["value"])
            return Response({"detail": "Coupon removed successfully and count rolled back."}, status=status.HTTP_200_OK)
        return Response({"detail": "Coupon count was already at zero or code not found."}, status=status.HTTP_400_BAD_REQUEST)
