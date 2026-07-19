"""
Wallets Endpoints Router - BrahmaVidya Galaxy
Purpose: Maps routing paths to Wallets, Transactions, Payments, Subscriptions, Coupons, Invoices, and Revenue views.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.wallets.views import (
    WalletViewSet, TransactionViewSet, PaymentViewSet,
    SubscriptionViewSet, CouponViewSet, InvoiceViewSet, RevenueAnalyticsViewSet,
    TeacherPayoutViewSet, RefundViewSet
)
from apps.wallets.payment_gateway_views import (
    PaymentGatewayViewSet, SubscriptionGatewayViewSet, CouponGatewayViewSet
)

router = DefaultRouter()
router.register("wallets", WalletViewSet, basename="wallet")
router.register("transactions", TransactionViewSet, basename="transaction")
router.register("payments", PaymentViewSet, basename="payment")
router.register("subscriptions", SubscriptionViewSet, basename="subscription")
router.register("coupons", CouponViewSet, basename="coupon")
router.register("invoices", InvoiceViewSet, basename="invoice")
router.register("revenue-analytics", RevenueAnalyticsViewSet, basename="revenue-analytics")
router.register("payouts", TeacherPayoutViewSet, basename="payout")
router.register("refunds", RefundViewSet, basename="refund")

# Enterprise Payment Gateway ViewSets (ModelViewSets)
router.register("payment-gateway", PaymentGatewayViewSet, basename="payment-gateway")
router.register("subscription-gateway", SubscriptionGatewayViewSet, basename="subscription-gateway")
router.register("coupon-gateway", CouponGatewayViewSet, basename="coupon-gateway")

app_name = "wallets"

urlpatterns = [
    path("", include(router.urls)),
]
