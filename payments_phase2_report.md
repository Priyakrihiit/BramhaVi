# BrahmaVidya Galaxy — Payments Phase 2 Database & Migrations Report
**Sprint 23 — Phase 2 Documentation**

This report documents the implementation of the database models and the successful application of migrations for the Payments, Wallet & Subscription Platform.

---

## 1. Implemented Database Models

We appended 11 missing models to [models.py](file:///c:/Users/USER/Downloads/bramhavi%20(3)/backend/apps/wallets/models.py) to replace simulated JSON storage:

1.  **`SubscriptionPlan`**: Represents available subscription tiers (Free, Premium, etc.) and prices.
2.  **`UserSubscription`**: Links users to subscriptions and tracks status and expiration dates.
3.  **`Invoice`**: Persists invoices including billing details, tax splits, GSTINs, and item list JSONs.
4.  **`Refund`**: Logs administrative refunds and gateway reference IDs.
5.  **`Coupon`**: Stores discount coupon settings (types, values, usage counts, limits, minimum amounts).
6.  **`CouponUsage`**: Tracks users who applied specific discount coupons to checkouts.
7.  **`Referral`**: Maps referring and referred users, conversion states, and commissions.
8.  **`TeacherPayout`**: Handles instructor balance withdrawals, methods, and bank reference IDs.
9.  **`RevenueSummary`**: Caches daily financial totals, platform commission summaries, and payout splits.
10. **`GSTRecord`**: Logs invoice splits (CGST, SGST, IGST, total taxes).
11. **`PaymentAudit`**: Records audit trails for security actions (webhooks, manual refunds, etc.).

---

## 2. Migrations & SQLite Sync

We generated and executed the database migrations successfully:

*   **Generation Command**: `python backend/manage.py makemigrations`
    *   **Generated File**: [0002_coupon_revenuesummary_subscriptionplan_gstrecord_and_more.py](file:///c:/Users/USER/Downloads/bramhavi%20(3)/backend/apps/wallets/migrations/0002_coupon_revenuesummary_subscriptionplan_gstrecord_and_more.py)
*   **Migration Execution**: `python backend/manage.py migrate`
    *   **Status**: `Applying wallets.0002_coupon_revenuesummary_subscriptionplan_gstrecord_and_more... OK`

---

## 3. System Integrity Checks

*   **Command**: `python backend/manage.py check`
*   **Status**: 🟢 **SUCCESS**
*   **Logs**: `System check identified no issues (0 silenced)`
