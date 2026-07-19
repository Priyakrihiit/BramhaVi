# Performance Review — Payments, Wallet & Subscription Platform
**Sprint 23 — BrahmaVidya Galaxy**

## 1. Database Query Optimizations
To maintain sub-second response times on transactional endpoints, we implemented the following ORM optimizations:
*   **Selective Preloading**: ViewSets utilize `.select_related()` (e.g. preloading `user` and `plan` on subscriptions) to collapse SQL N+1 queries.
*   **Database Indexing**:
    *   Index added on Transaction's `wallet` field: `idx_transactions_wallet` to speed up ledger balances aggregations.
    *   Unique constraint index on Coupon's `code` to enable constant time promotion lookups.

## 2. Dynamic Ledgers vs. Cached Balances
*   Instead of storing mutable balance numbers susceptible to write anomalies, wallet balances are re-computed via aggregate SUM functions across Transaction records.
*   To minimize compute load, balance calculations are processed inside atomic database transactions and updated directly.

## 3. Background Task Processing
*   **Eager/Delay Queues**: Asynchronous jobs (like rendering PDF invoices or verifying completion hashes) are delegated to Celery workers, keeping request-response times minimal.
*   **Cache Buffers**: Daily scanning of expired subscription memberships is handled as a nightly Celery beat task, reducing traffic spikes.
