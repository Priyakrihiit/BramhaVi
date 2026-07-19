# Administrative Manual — Payments, Wallet & Subscription Platform
**Sprint 23 — BrahmaVidya Galaxy**

This guide provides instructives for administrators managing financial configurations and payouts.

## 1. Creating Promotional Coupons
*   Coupons are managed via the Django admin console or administrative REST endpoints.
*   Required parameters when creating coupons:
    *   `code`: Uppercase alphanumeric code string (e.g. `WELCOME50`).
    *   `type`: PERCENTAGE or FIXED.
    *   `value`: Numerical value representation (e.g. 50.00 for percentage or absolute credits).
    *   `usage_limit`: Maximum allowed redemptions.
    *   `expiry_date`: Date limit.

## 2. Reviewing and Approving Teacher Payouts
*   Instructors submit cashout withdrawal requests when their wallet balance accumulates funds.
*   To process payouts:
    1.  Navigate to the Django admin panel or `/api/v1/payments/payouts/`.
    2.  Filter request items by `status = PENDING`.
    3.  Verify the teacher's wallet balance.
    4.  Authorize bank transfers.
    5.  Post a confirmation to `/api/v1/payments/payouts/{id}/approve/` with the transaction `reference_id` to finalize state transitions to `APPROVED`/`PAID`.

## 3. Financial Auditing
*   Execute the auditing task via Celery to reconcile database double-entry accounts:
    *   Calculates sum(credits) - sum(debits) for each wallet.
    *   Flags mismatch errors in transaction ledger outputs.
