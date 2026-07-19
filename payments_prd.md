# Product Requirements Document (PRD) — Payments, Wallet & Subscription Platform
**Sprint 23 — BrahmaVidya Galaxy**

## 1. Goal & Objectives
To build a secure, transactional, and audit-ready payments, billing, and subscription management system inside the BrahmaVidya learning platform. The platform handles student credit deposits, peer-to-peer transfers, membership renewals, promotional coupons, GST tax splits, and instructor payouts.

## 2. Core Functional Requirements
1.  **Wallet Management**:
    *   Virtual credit ledger for students.
    *   Add funds mock checkouts.
    *   Instant peer-to-peer point transfers.
2.  **Monetary Transactions**:
    *   Stripe and Razorpay billing gateway checkouts.
    *   Payment status transitions (PENDING -> COMPLETED/FAILED).
3.  **Promotional Engine**:
    *   Fixed-value or percentage-based discount codes.
    *   Redemption usage count limits and expiration dates.
4.  **Invoicing & Taxes**:
    *   18% GST calculation (CGST and SGST shares split).
    *   Dynamic text invoice downloads and payment receipts.
5.  **Subscriptions**:
    *   Plan memberships tier grids (Free, Student, Teacher, Institute).
    *   Cron checks to expire subscriptions whose validity has lapsed.
6.  **Teacher Payouts**:
    *   Request withdrawal gating based on teacher wallet balance.
    *   Admin approval transitions.
7.  **Platform Audit logs**:
    *   Security events auditing for high-value transactions (> 1000 INR).

## 3. Non-Functional Requirements
1.  **Data Consistency**: Ledger balances must equal the sum of Credits minus Debits (double-entry accounting).
2.  **Auditability**: PaymentAudit records are write-once and immutable.
3.  **Observability**: Correlation IDs mapped to gateway proxy requests.
