# Payments, Wallet & Subscription Platform — Repository Audit & Analysis
**Sprint 23 — Phase 0 Analysis**

This document details the complete repository audit of the financial ledger, transaction tracking, billing, and subscription features across the BrahmaVidya Galaxy codebase.

---

## 1. Database Entity Audit

We analyzed the current database schemas and JSON extra stores to verify the persistence layer for the Payments & Subscriptions platform:

| Entity | Status | Implementation Details / File References |
| :--- | :--- | :--- |
| **Wallet** | Existing | Defined as a Django model `Wallet` in [models.py](file:///c:/Users/USER/Downloads/bramhavi%20(3)/backend/apps/wallets/models.py#L6-L38). Tracks balance using `DecimalField` in currency type `"VIDYA"`. |
| **Transaction** | Existing | Defined as a Django model `Transaction` in [models.py](file:///c:/Users/USER/Downloads/bramhavi%20(3)/backend/apps/wallets/models.py#L40-L78). Implements double-entry accounting with type `CREDIT` or `DEBIT` and references specific wallets. |
| **Subscription** | Needs Extension | Missing database table; currently simulated dynamically and stored in JSON format via [wallet_extras_store.py](file:///c:/Users/USER/Downloads/bramhavi%20(3)/backend/apps/wallets/wallet_extras_store.py#L71-L82). Needs a proper Django model table. |
| **Payment** | Existing | Defined as a Django model `Payment` in [models.py](file:///c:/Users/USER/Downloads/bramhavi%20(3)/backend/apps/wallets/models.py#L80-L128). Integrates Stripe and Razorpay external transactions. |
| **Invoice** | Needs Extension | Missing database table; currently simulated dynamically and stored in JSON format via [wallet_extras_store.py](file:///c:/Users/USER/Downloads/bramhavi%20(3)/backend/apps/wallets/wallet_extras_store.py#L106-L119). Needs a proper database-backed model table. |
| **Certificate** | Existing | Mapped via Django model `Certificate` in [backend/apps/lms/models.py](file:///c:/Users/USER/Downloads/bramhavi%20(3)/backend/apps/lms/models.py#L362). Validated and signed using dynamic hashes in [services.py](file:///c:/Users/USER/Downloads/bramhavi%20(3)/backend/apps/wallets/services.py#L176-L192). |
| **Teacher Earnings** | Existing | Split rules, GST calculation, and platform commission shares are handled via `SettlementEngineService` in [services.py](file:///c:/Users/USER/Downloads/bramhavi%20(3)/backend/apps/wallets/services.py#L193-L305). Withdrawal requests are managed in `TeacherWallet.tsx`. |
| **Student Purchases** | Existing | Tracked as standard `DEBIT` transactions with a fine-grained type of `PURCHASE` under the double-entry point transaction ledger. |

---

## 2. Platform Architecture Breakdown

### 2.1. Existing Functionality & Modules
1.  **Wallet Functionality**: Implemented via [WalletViewSet](file:///c:/Users/USER/Downloads/bramhavi%20(3)/backend/apps/wallets/views.py#L39-L184) and `LedgerTransactionService` in [services.py](file:///c:/Users/USER/Downloads/bramhavi%20(3)/backend/apps/wallets/services.py#L18-L175). Supports balance inquiries, fund transfers, credits, debits, soft deletes, and restores.
2.  **Payment Processing**: Implements Stripe and Razorpay provider modules in [payment_gateway_services.py](file:///c:/Users/USER/Downloads/bramhavi%20(3)/backend/apps/wallets/payment_gateway_services.py#L90-L200) with signature checkouts, secure captures, and audit logging. Mapped to client APIs in [payment_gateway_views.py](file:///c:/Users/USER/Downloads/bramhavi%20(3)/backend/apps/wallets/payment_gateway_views.py#L147-L200).
3.  **Subscription Processing**: Endpoints mapped via `SubscriptionViewSet` and `SubscriptionGatewayViewSet` in [urls.py](file:///c:/Users/USER/Downloads/bramhavi%20(3)/backend/apps/wallets/urls.py#L20-L28). Plans are stored as serialized strings (e.g. Free, Student Premium, Teacher Premium, Institute).
4.  **Transaction Ledger**: Persists transaction registers (`CREDIT`/`DEBIT`), linked to unique transaction UUIDs, with a fine-grained metadata store in `wallet_extras.json`.
5.  **Invoices & GST Receipts**: Auto-calculates tax-inclusive pricing, deducting 18% GST and splitting remaining earnings. Managed dynamically via JSON invoice schemas in [wallet_extras_store.py](file:///c:/Users/USER/Downloads/bramhavi%20(3)/backend/apps/wallets/wallet_extras_store.py#L106-L119).
6.  **Coupons Engine**: Fully dynamic validation engine in [payment_gateway_views.py](file:///c:/Users/USER/Downloads/bramhavi%20(3)/backend/apps/wallets/payment_gateway_views.py#L56-L142) translating `PlatformSetting` configurations into percentage or flat discount models.
7.  **Refunds**: Handled directly in Stripe and Razorpay provider blocks using `process_refund` captures.
8.  **APIs**: Exposes `/api/v1/wallets/` routers proxying requests from gateway `server.ts` to Django rest endpoints.
9.  **React Interfaces**:
    *   `TeacherWallet.tsx`: Handles balances KPI metrics, earnings histories, and withdrawal forms.
    *   `MarketplaceView.tsx`: Processes checkout validations, purchase settlements, and GST invoicing overlays.
    *   `Module4Affiliate.tsx`: Handles affiliate referral programs and commission wallets.
10. **Permissions & Security**: Defined in [permissions.py](file:///c:/Users/USER/Downloads/bramhavi%20(3)/backend/apps/wallets/permissions.py). Restricts wallet ownership to the user/admins, and restricts modifications to the `FINANCE` or `ADMIN` roles.
11. **Analytics & Notifications**: Telemetry tracking in `RevenueAnalyticsViewSet` and `PGAnalyticsService`. Background notification jobs are dispatched via Celery tasks.

### 2.2. Component Audit Checklist

*   **Existing**:
    *   Wallet balances, transfers, and ledger registries.
    *   Stripe & Razorpay payment providers.
    *   Coupons engine mapped to database-backed settings.
    *   Refund capture routines.
    *   Teacher royalty splits and payouts tracking.
    *   LMS Certificate model integrations.
    *   Reverse proxy gateway configurations for wallets and checkouts in [server.ts](file:///c:/Users/USER/Downloads/bramhavi%20(3)/server.ts#L84-L110).
*   **Missing**:
    *   Subscriptions table in the relational database.
    *   Invoices table in the relational database.
*   **Needs Extension**:
    *   `Subscription` JSON fields need migration to structured SQL tables to support relational tracking of plans, expirations, and renewals.
    *   `Invoice` JSON fields need migration to SQL tables to allow financial reporting and cross-referencing with `Payment` transactions.
*   **Needs Replacement**:
    *   **NONE**. The existing architecture is clean, highly modular, and fully integrated with core LMS and user structures.

---

## 3. Architectural Recommendation

We recommend **extending the existing `wallets` app** instead of creating a new `apps/payments` application for the following reasons:

1.  **Avoid Ledger Duplication**: Core payment models (`Payment`, `Transaction`, `Wallet`) are already fully implemented inside `wallets`. Introducing a separate `payments` app would split the double-entry point transaction registers, resulting in complex cross-app joins and transaction synchronization issues.
2.  **Decoupled Gateway Schemas**: The Express proxy config in `server.ts` maps all checkout, gateway, subscription, and invoice endpoints directly to the `/api/v1/wallets/` namespace. Maintaining these in a single Django application preserves the existing API routing structure.
3.  **Interoperable Extras Migration**: Migrating simulated JSON stores (`subscriptions`, `invoices`) to database models can be performed surgically within `apps/wallets` via Django migrations without breaking existing signal layers.
