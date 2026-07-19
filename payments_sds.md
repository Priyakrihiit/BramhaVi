# Software Design Specification (SDS) — Payments, Wallet & Subscription Platform
**Sprint 23 — BrahmaVidya Galaxy**

## 1. Architectural Overview
The Payments Platform utilizes a service-oriented architectural layer mapped inside the Django `apps.wallets` application:

```
[React Client] <---> [Express Gateway Server] <---> [Django Backend] <---> [PostgreSQL DB]
                             |                            |
                     [Rate Limiter Stack]         [Celery Background]
                                                          |
                                                    [Redis Cache]
```

## 2. Database Model Schema
1.  **Wallet**: Stores point currency totals (`balance`, `currency`, `user`).
2.  **Transaction**: Append-only ledgers (`wallet`, `type`, `amount`, `description`).
3.  **Payment**: Invoicing card logs (`user`, `amount`, `payment_gateway`, `status`).
4.  **SubscriptionPlan**: Plan tiers (`name`, `price`, `duration_days`, `is_active`).
5.  **UserSubscription**: Membership records (`user`, `plan`, `status`, `expires_at`).
6.  **Invoice**: Compliant invoice rows (`payment`, `user`, `amount`, `tax`, `total`, `gst_number`).
7.  **GSTRecord**: Detailed tax split entries (`payment`, `net_amount`, `cgst`, `sgst`, `igst`).
8.  **Refund**: Reimbursement journals (`payment`, `amount`, `status`).
9.  **Coupon**: Promo definitions (`code`, `type`, `value`, `usage_limit`, `usage_count`, `expiry_date`).
10. **TeacherPayout**: Withdrawals tracking (`teacher`, `amount`, `status`, `payout_method`).
11. **PaymentAudit**: Immutable logging entries (`action`, `actor_email`, `details`).

## 3. Key Design Patterns
*   **Double-Entry Reconciliations**: Wallet balance updates are calculated dynamically via database SUM aggregates to guarantee zero credit leaks.
*   **Decoupled Events signals**: Transaction notifications and audits are dispatched asynchronously through Django post-save signals.
