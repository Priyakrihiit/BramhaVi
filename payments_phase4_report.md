# BrahmaVidya Galaxy — Payments Phase 4 Serializers, Views & URLs Report
**Sprint 23 — Phase 4 Documentation**

This report documents the implementation of the serializers, permission settings, ViewSets, and URL patterns exposing REST APIs for the Payments, Wallet & Subscription Platform.

---

## 1. REST API Endpoints Exposed

We exposed fully database-backed endpoints inside the `apps.wallets` application mapping the requested features:

### 1.1. Wallet & Ledger Transactions
*   **ViewSet**: [WalletViewSet](file:///c:/Users/USER/Downloads/bramhavi%20(3)/backend/apps/wallets/views.py#L39)
    *   `GET /api/v1/wallets/wallets/{id}/balance/`: Retrieves wallet balances.
    *   `POST /api/v1/wallets/wallets/{id}/add-funds/`: Credits funds (finance/admin restricted).
    *   `POST /api/v1/wallets/wallets/settle-purchase/`: Debits student wallets and handles royalty splits.
*   **ViewSet**: [TransactionViewSet](file:///c:/Users/USER/Downloads/bramhavi%20(3)/backend/apps/wallets/views.py#L213)
    *   `POST /api/v1/wallets/transactions/credit/`: Creates credits.
    *   `POST /api/v1/wallets/transactions/debit/`: Creates debits.
    *   `POST /api/v1/wallets/transactions/transfer/`: Transfers points between wallets.

### 1.2. Payments & Gateway Webhooks
*   **ViewSet**: [PaymentViewSet](file:///c:/Users/USER/Downloads/bramhavi%20(3)/backend/apps/wallets/views.py#L466)
    *   `POST /api/v1/wallets/payments/`: Submits gateway payments.
    *   `POST /api/v1/wallets/payments/{id}/verify/`: Verifies checkout signatures and issues certificates.

### 1.3. Subscription Plans & User Subscriptions
*   **ViewSet**: [SubscriptionViewSet](file:///c:/Users/USER/Downloads/bramhavi%20(3)/backend/apps/wallets/views.py#L640)
    *   `GET /api/v1/wallets/subscriptions/current-plan/`: Gets current subscription.
    *   `POST /api/v1/wallets/subscriptions/subscribe/`: Subscribes to plan.
    *   `POST /api/v1/wallets/subscriptions/{id}/cancel/`: Cancels user subscriptions.
    *   `POST /api/v1/wallets/subscriptions/{id}/renew/`: Renews plans.

### 1.4. Invoices & Receipts
*   **ViewSet**: [InvoiceViewSet](file:///c:/Users/USER/Downloads/bramhavi%20(3)/backend/apps/wallets/views.py#L910)
    *   `GET /api/v1/wallets/invoices/`: Lists invoices.
    *   `GET /api/v1/wallets/invoices/{id}/download/`: Outputs text invoice file attachments with GST calculations.
    *   `GET /api/v1/wallets/invoices/{id}/receipt/`: Generates payment confirmations.

### 1.5. Refunds
*   **ViewSet**: [RefundViewSet](file:///c:/Users/USER/Downloads/bramhavi%20(3)/backend/apps/wallets/views.py#L1014)
    *   `POST /api/v1/wallets/refunds/`: Issues Stripe/Razorpay refunds and reverses reward points.

### 1.6. Coupons & Vouchers
*   **ViewSet**: [CouponViewSet](file:///c:/Users/USER/Downloads/bramhavi%20(3)/backend/apps/wallets/views.py#L754)
    *   `POST /api/v1/wallets/coupons/validate-coupon/`: Evaluates discount limits and rates.
    *   `POST /api/v1/wallets/coupons/apply-coupon/`: Decreases voucher limits and applies cart deductions.

### 1.7. Teacher Earnings & Withdrawals
*   **ViewSet**: [TeacherPayoutViewSet](file:///c:/Users/USER/Downloads/bramhavi%20(3)/backend/apps/wallets/views.py#L980)
    *   `POST /api/v1/wallets/payouts/`: Requests payout cashouts.
    *   `POST /api/v1/wallets/payouts/{id}/approve/`: Approves payout disbursement.

### 1.8. Revenue Analytics
*   **ViewSet**: [RevenueAnalyticsViewSet](file:///c:/Users/USER/Downloads/bramhavi%20(3)/backend/apps/wallets/views.py#L1015)
    *   `GET /api/v1/wallets/revenue-analytics/summary/`: Provides dynamic aggregates of daily, monthly, subscription, and wallet revenues.

---

## 2. Integrity Verification

*   **Command**: `python backend/manage.py check`
*   **Status**: 🟢 **SUCCESS**
*   **Logs**: `System check identified no issues (0 silenced)`
