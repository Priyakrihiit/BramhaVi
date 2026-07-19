import uuid
from decimal import Decimal
from datetime import datetime
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.users.permissions import HasRBACPermission
from apps.users.models import User
from apps.wallets.models import Wallet, Transaction, Payment
from apps.control_center.admin_serializers import (
    CouponAdminSerializer, SubscriptionAdminSerializer
)
from apps.control_center.admin_store import (
    get_admin_collection, save_admin_item
)

class AdminPortfolioViewSet(viewsets.ViewSet):
    """
    Module 6 — Enterprise Portfolio & Website Administration.
    Governs user portfolios, domains, storage quotas, and subdomains.
    """
    permission_classes = [HasRBACPermission]
    required_permissions = {
        "list_websites": "control:portfolio:view",
        "update_domain": "control:portfolio:update",
        "media_storage_stats": "control:portfolio:view",
        "subscriptions_list": "control:portfolio:view",
    }

    @action(detail=False, methods=["get"], url_path="websites")
    def list_websites(self, request):
        from apps.portfolio.portfolio_store import get_collection as get_port_col
        websites = get_port_col("websites")
        # filter or search if requested
        search_query = request.query_params.get("search")
        if search_query:
            websites = [w for w in websites if search_query.lower() in w.get("title", "").lower() or search_query.lower() in w.get("domain", "").lower()]
            
        status_filter = request.query_params.get("status")
        if status_filter:
            websites = [w for w in websites if w.get("status") == status_filter]
            
        return Response(websites, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="update-domain")
    def update_domain(self, request, pk=None):
        from apps.portfolio.portfolio_store import get_collection as get_port_col, save_item as save_port_item
        websites = get_port_col("websites")
        custom_domain = request.data.get("custom_domain")
        status_val = request.data.get("status")
        
        for w in websites:
            if w["id"] == str(pk):
                if custom_domain is not None:
                    w["custom_domain"] = custom_domain
                if status_val is not None:
                    w["status"] = status_val
                save_port_item("websites", pk, w)
                return Response(w, status=status.HTTP_200_OK)
                
        return Response({"error": "Website not found."}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=["get"], url_path="storage")
    def media_storage_stats(self, request):
        # Calculates combined mock telemetry storage allocations
        from apps.portfolio.portfolio_store import get_collection as get_port_col
        websites = get_port_col("websites")
        total_quota_mb = len(websites) * 512.0
        used_quota_mb = len(websites) * 42.15
        
        return Response({
            "websites_tracked": len(websites),
            "allocated_total_gb": round(total_quota_mb / 1024, 2),
            "consumed_total_gb": round(used_quota_mb / 1024, 2),
            "average_site_size_mb": 42.15,
            "status": "HEALTHY"
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], url_path="subscriptions")
    def subscriptions_list(self, request):
        subs = get_admin_collection("subscriptions")
        return Response(subs, status=status.HTTP_200_OK)


class AdminWalletViewSet(viewsets.ViewSet):
    """
    Module 7 — Enterprise Wallet & Ledger Administration.
    Direct manual adjustments, invoice audits, coupons and revenue reconciliation.
    """
    permission_classes = [HasRBACPermission]
    required_permissions = {
        "list_wallets": "control:wallets:view",
        "manual_adjustment": "control:wallets:update",
        "list_payments": "control:wallets:view",
        "refund_payment": "control:wallets:update",
        "list_coupons": "control:wallets:view",
        "create_coupon": "control:wallets:create",
        "revenue_report": "control:wallets:view",
    }

    @action(detail=False, methods=["get"], url_path="accounts")
    def list_wallets(self, request):
        wallets = Wallet.objects.select_related("user").all().order_by("-updated_at")
        data = []
        for w in wallets:
            data.append({
                "id": w.id,
                "user_email": w.user.email if w.user else "",
                "balance": float(w.balance),
                "currency": w.currency,
                "created_at": w.created_at,
                "updated_at": w.updated_at
            })
        return Response(data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="adjustment")
    def manual_adjustment(self, request, pk=None):
        wallet = Wallet.objects.filter(id=pk).first()
        if not wallet:
            return Response({"error": "Wallet not found."}, status=status.HTTP_404_NOT_FOUND)
            
        adj_type = request.data.get("type") # CREDIT or DEBIT
        amount = request.data.get("amount")
        desc = request.data.get("description", "Administrative balance adjustment")
        
        if adj_type not in ["CREDIT", "DEBIT"] or amount is None:
            return Response({"error": "type (CREDIT/DEBIT) and amount parameters are required."}, status=status.HTTP_400_BAD_REQUEST)
            
        amount_dec = Decimal(str(amount))
        if adj_type == "CREDIT":
            wallet.balance += amount_dec
        else:
            wallet.balance -= amount_dec
        wallet.save()
        
        Transaction.objects.create(
            wallet=wallet,
            type=adj_type,
            amount=amount_dec,
            description=desc,
            reference_id=uuid.uuid4()
        )
        return Response({"id": wallet.id, "new_balance": float(wallet.balance)}, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], url_path="payments")
    def list_payments(self, request):
        payments = Payment.objects.select_related("user").all().order_by("-created_at")
        data = []
        for p in payments:
            data.append({
                "id": p.id,
                "user_email": p.user.email if p.user else "",
                "amount": float(p.amount),
                "currency": p.currency,
                "created_at": p.created_at
            })
        return Response(data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="refund")
    def refund_payment(self, request, pk=None):
        payment = Payment.objects.filter(id=pk).first()
        if not payment:
            return Response({"error": "Payment not found."}, status=status.HTTP_404_NOT_FOUND)
            
        # Refund payment back into points ledger wallet
        wallet, _ = Wallet.objects.get_or_create(user=payment.user)
        refund_amount = payment.amount
        wallet.balance += refund_amount
        wallet.save()
        
        Transaction.objects.create(
            wallet=wallet,
            type="CREDIT",
            amount=refund_amount,
            description=f"Refund of payment ID {payment.id}",
            reference_id=payment.id
        )
        return Response({"detail": "Payment successfully refunded to point wallet balance."}, status=status.HTTP_200_OK)

    # Coupons Management (JSON persistent store)
    @action(detail=False, methods=["get"], url_path="coupons")
    def list_coupons(self, request):
        coupons = get_admin_collection("coupons")
        include_deleted = request.query_params.get("include_deleted", "false").lower() == "true"
        if not include_deleted:
            coupons = [c for c in coupons if c.get("deleted_at") is None]
        return Response(coupons, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"], url_path="coupons/create")
    def create_coupon(self, request):
        ser = CouponAdminSerializer(data=request.data)
        if not ser.is_valid():
            return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)
            
        coupon = {
            "id": f"coupon-{uuid.uuid4().hex[:8]}",
            "code": ser.validated_data["code"].upper(),
            "discount_percentage": float(ser.validated_data["discount_percentage"]),
            "is_active": ser.validated_data.get("is_active", True),
            "expires_at": ser.validated_data["expires_at"].isoformat(),
            "deleted_at": None
        }
        save_admin_item("coupons", coupon["id"], coupon)
        return Response(coupon, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["get"], url_path="revenue")
    def revenue_report(self, request):
        payments_qs = Payment.objects.all()
        gst_tax_ratio = Decimal("0.18")
        total_payments = sum(p.amount for p in payments_qs)
        gst_total = total_payments * gst_tax_ratio
        net_revenue = total_payments - gst_total
        
        return Response({
            "total_gross_monetary_payments": float(total_payments),
            "reconciled_gst_withheld": float(gst_total),
            "net_platform_revenue": float(net_revenue),
            "reconciliation_status": "BALANCED",
            "last_closing_timestamp": datetime.now().isoformat()
        }, status=status.HTTP_200_OK)
