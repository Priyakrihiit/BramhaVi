# Security Architecture Review — Payments, Wallet & Subscription Platform
**Sprint 23 — BrahmaVidya Galaxy**

## 1. Authentication and Access Controls
1.  **JWT Validation Checkouts**: All gateway path proxies mapping to `/api/v1/payments/*` enforce JWT validation. Invalid or expired token requests are terminated.
2.  **Role-Based Access Control (RBAC)**: Fine-grained permissions are checked before processing requests:
    *   `payments:admin` permission is required for actions like creating/deleting coupons or approving payouts.
    *   `payments:checkout` permission allows students to validate promo codes, process checkouts, or subscribe to membership plans.
    *   `sys:analytics:read` is required for administrative summaries.

## 2. Fraud Mitigation & Financial Safeguards
1.  **Payout Request Gating**: Withdrawal cashouts verify the caller's active wallet balance inside an atomic database lock transaction block to prevent race conditions or double-spend exploits.
2.  **Point Reward Rollback**: Refunding a transaction automatically triggers a corresponding debit transaction against the target student's wallet to reverse reward points.
3.  **High-Value Transactions Monitoring**: Any credit/debit transaction whose amount is greater than 1000 INR triggers a warning post-save signal, automatically logging an immutable audit record in the `PaymentAudit` database table.

## 3. Database Vulnerabilities Protections
*   All queries utilize standard Django ORM methods, guarding backend databases from SQL injection risks.
*   Data migrations are versioned and signed off, preventing manual schema changes.
