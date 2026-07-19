# BrahmaVidya Galaxy — Payments Phase 7 Platform Integration Report
**Sprint 23 — Phase 7 Documentation**

This report outlines the integration details between the Payments Platform and the other services within the BrahmaVidya Galaxy ecosystem.

---

## 1. Ecosystem Integration Matrix

| Target Subsystem | Integration Channel & Implementation Details |
| :--- | :--- |
| **Student Portal** | Connects to balance retrieval views and cart checkout interfaces via `/payments/checkout/` React pages. |
| **Teacher Portal** | Intercepts teacher cashout clicks and processes direct payouts from earnings pools. |
| **Live Classes** | Charges student checkouts for live cohort premiums and validates active status parameters. |
| **LMS / Certificates** | Triggers cryptographic signatures and verification hashes when course completion payments verify successfully. |
| **Analytics Engine** | Feeds double-entry transaction ledgers to `RevenueSummary` reporting rows. |
| **Notifications** | Dispatches emails on wallet deposits (`wallet`) and checkout order completions (`payment`). |
| **Search Subsystem** | Indexes active promotions and plan names for student lookup. |
| **AI Studio** | Checks wallet point balance before invoking generative learning chat agents. |
| **Redis & Celery** | Processes async monthly financial audits, subscription validity expiration runs, and PDF compiles. |

---

## 2. Dynamic Integration Signals

We implemented Django database event receivers inside `signals.py`:

*   **`on_transaction_created`**: Intercepts ledger additions and initiates `EmailService.send_email` using the `wallet` code template. Logs `PaymentAudit` alerts for large credits/debits.
*   **`on_payment_saved`**: Dispatches the `payment` confirmation invoice receipt automatically upon transitions to `SUCCESS`.

---

## 3. Verification Checks

*   **Command**: `python backend/manage.py check`
*   **Status**: 🟢 **SUCCESS**
*   **Verification logs**:
    ```text
    System check identified no issues (0 silenced).
    ```
