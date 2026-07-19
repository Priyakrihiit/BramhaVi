# Transaction Sequence Diagrams — Payments, Wallet & Subscription Platform
**Sprint 23 — BrahmaVidya Galaxy**

## 1. Purchase Checkout & GST Invoice Sequence

```mermaid
sequence_diagram
    autonumber
    actor Student
    participant Gateway as API Gateway (server.ts)
    participant Django as Django Backend (views/services)
    participant DB as PostgreSQL Database

    Student->>Gateway: POST /api/v1/payments/ (amount, plan/course)
    Note over Gateway: Verify JWT & Correlation ID
    Gateway->>Django: Proxy POST /api/v1/wallets/payments/
    Django->>DB: INSERT Payment record (status=PENDING)
    Django-->>Student: Return Payment ID

    Student->>Gateway: POST /api/v1/payments/{id}/verify/ (gateway_tx_id)
    Gateway->>Django: Proxy POST /api/v1/wallets/payments/{id}/verify/
    opt transaction.atomic
        Django->>DB: UPDATE Payment status to COMPLETED
        Django->>Django: Calculate GST tax split (18% inclusive)
        Django->>DB: INSERT Invoice & GSTRecord
        Django->>DB: UPDATE Student Wallet (add reward points)
        Django->>DB: INSERT Transaction (Reward credits)
    end
    Django-->>Student: Return Success Response & Invoice ID
```

## 2. Teacher Withdrawal Payout Gating Sequence

```mermaid
sequence_diagram
    autonumber
    actor Teacher
    participant Gateway as API Gateway (server.ts)
    participant Django as Django Backend (views/services)
    participant DB as PostgreSQL Database

    Teacher->>Gateway: POST /api/v1/payments/payouts/ (amount, method)
    Gateway->>Django: Proxy POST /api/v1/wallets/payouts/
    Django->>DB: Query Teacher Wallet Balance
    alt Balance >= Amount
        Django->>DB: INSERT Transaction (DEBIT withdrawal amount)
        Django->>DB: UPDATE Wallet balance (atomic debit)
        Django->>DB: INSERT TeacherPayout record (status=PENDING)
        Django-->>Teacher: Return Payout Request ID
    else Balance < Amount
        Django-->>Teacher: Return 400 Insufficient Wallet Balance
    end
```
