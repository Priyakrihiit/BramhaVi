from decimal import Decimal
from rest_framework import serializers
from apps.wallets.models import (
    Wallet, Transaction, Payment, SubscriptionPlan, UserSubscription,
    Invoice, Refund, Coupon, CouponUsage, Referral, TeacherPayout,
    RevenueSummary, GSTRecord, PaymentAudit
)
from apps.wallets.wallet_extras_store import is_wallet_id_soft_deleted, get_fine_grained_tx


class WalletSerializer(serializers.ModelSerializer):
    user_email = serializers.ReadOnlyField(source="user.email")
    is_deleted = serializers.SerializerMethodField()

    class Meta:
        model = Wallet
        fields = [
            "id", "user", "user_email", "balance", "currency", 
            "is_deleted", "created_at", "updated_at"
        ]
        read_only_fields = ["balance", "is_deleted"]

    def get_is_deleted(self, obj) -> bool:
        return is_wallet_id_soft_deleted(obj.id)


class TransactionSerializer(serializers.ModelSerializer):
    user_email = serializers.ReadOnlyField(source="wallet.user.email")
    fine_grained_type = serializers.SerializerMethodField()

    class Meta:
        model = Transaction
        fields = [
            "id", "wallet", "user_email", "type", "fine_grained_type", 
            "amount", "description", "reference_id", "created_at"
        ]

    def get_fine_grained_type(self, obj) -> str:
        # Get fine grained classification from store or extract from description
        fine_grained = get_fine_grained_tx(obj.id)
        if fine_grained == "UNKNOWN" and obj.description and obj.description.startswith("["):
            # e.g., "[TRANSFER] Received from ..."
            end_idx = obj.description.find("]")
            if end_idx != -1:
                return obj.description[1:end_idx]
        return fine_grained if fine_grained != "UNKNOWN" else obj.type


class PaymentSerializer(serializers.ModelSerializer):
    user_email = serializers.ReadOnlyField(source="user.email")

    class Meta:
        model = Payment
        fields = [
            "id", "user", "user_email", "enrollment", "amount", "currency", 
            "payment_gateway", "gateway_transaction_id", "status", "created_at"
        ]


class AddFundsSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=15, decimal_places=4, min_value=Decimal("0.0001"))
    description = serializers.CharField(max_length=255, required=False, allow_blank=True, allow_null=True)
    reference_id = serializers.UUIDField(required=False, allow_null=True)


class TransferSerializer(serializers.Serializer):
    target_wallet_id = serializers.UUIDField()
    amount = serializers.DecimalField(max_digits=15, decimal_places=4, min_value=Decimal("0.0001"))
    description = serializers.CharField(max_length=255, default="Wallet Transfer")


class CouponSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=50)
    type = serializers.ChoiceField(choices=[("PERCENTAGE", "Percentage"), ("FLAT", "Flat")])
    value = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=Decimal("0.01"))
    usage_limit = serializers.IntegerField(min_value=1, default=100)
    usage_count = serializers.IntegerField(read_only=True)
    expiry_date = serializers.DateField()
    is_active = serializers.BooleanField(default=True)


class CouponValidateSerializer(serializers.Serializer):
    code = serializers.CharField()
    cart_amount = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=Decimal("0.01"))


class SubscriptionSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    plan_name = serializers.ChoiceField(choices=[
        ("Free", "Free"),
        ("Student Premium", "Student Premium"),
        ("Teacher Premium", "Teacher Premium"),
        ("Institute", "Institute"),
        ("Portfolio Builder (₹99/month)", "Portfolio Builder (₹99/month)"),
        ("Business Website", "Business Website"),
        ("Enterprise", "Enterprise")
    ])
    status = serializers.CharField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    expires_at = serializers.DateTimeField(read_only=True)


class InvoiceItemSerializer(serializers.Serializer):
    description = serializers.CharField(max_length=255)
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)


class InvoiceSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    invoice_number = serializers.CharField(read_only=True)
    user_id = serializers.UUIDField()
    user_email = serializers.EmailField(read_only=True)
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    tax = serializers.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    status = serializers.ChoiceField(choices=[("PAID", "Paid"), ("UNPAID", "Unpaid"), ("CANCELLED", "Cancelled")])
    items = InvoiceItemSerializer(many=True)
    gst_number = serializers.CharField(max_length=15, required=False, allow_blank=True, default="27AAAAA1111A1Z1")
    created_at = serializers.DateTimeField(read_only=True)


class SubscriptionPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPlan
        fields = ["id", "name", "price", "duration_days", "is_active", "created_at", "updated_at"]


class UserSubscriptionSerializer(serializers.ModelSerializer):
    user_email = serializers.ReadOnlyField(source="user.email")
    plan_name = serializers.ReadOnlyField(source="plan.name")
    price = serializers.ReadOnlyField(source="plan.price")

    class Meta:
        model = UserSubscription
        fields = ["id", "user", "user_email", "plan", "plan_name", "price", "status", "starts_at", "expires_at", "created_at"]


class InvoiceModelSerializer(serializers.ModelSerializer):
    user_email = serializers.ReadOnlyField(source="user.email")

    class Meta:
        model = Invoice
        fields = ["id", "invoice_number", "payment", "user", "user_email", "amount", "tax", "total", "status", "gst_number", "items", "created_at"]


class RefundModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Refund
        fields = ["id", "payment", "amount", "reason", "gateway_refund_id", "status", "created_at"]


class CouponModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = ["id", "code", "type", "value", "usage_limit", "usage_count", "minimum_purchase", "expiry_date", "is_active", "created_at"]


class TeacherPayoutSerializer(serializers.ModelSerializer):
    teacher_email = serializers.ReadOnlyField(source="teacher.email")

    class Meta:
        model = TeacherPayout
        fields = ["id", "teacher", "teacher_email", "amount", "status", "payout_method", "reference_id", "created_at", "updated_at"]


class RevenueSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = RevenueSummary
        fields = ["id", "date", "total_revenue", "total_tax", "total_commission", "total_payouts", "created_at"]


class GSTRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = GSTRecord
        fields = ["id", "payment", "invoice_number", "net_amount", "cgst", "sgst", "igst", "total_gst", "created_at"]
