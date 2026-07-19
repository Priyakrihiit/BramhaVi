# Developer Guide — Payments, Wallet & Subscription Platform
**Sprint 23 — BrahmaVidya Galaxy**

## 1. Directory Layout & Key Modules
The Payments engine is contained inside `backend/apps/wallets/`:
*   `models.py`: Declares the database structure including wallets, transactions, plans, invoices, and payouts.
*   `services.py`: Implements transactional service layers (e.g. `SubscriptionService`, `InvoiceService`, `RefundService`).
*   `selectors.py`: Houses reusable lookup queries.
*   `filters.py`: Standardizes filtering criteria for search, pagination, and sorting.
*   `tasks.py`: Declares async Celery jobs.
*   `signals.py`: Listens to post-save events.

## 2. Extending Services Layer
When adding new business operations, construct methods inside `services.py` inside an atomic transaction block:

```python
from django.db import transaction

class CustomBillingService:
    @staticmethod
    @transaction.atomic
    def process_custom_billing(user, price):
        # 1. Lock wallet balance
        # 2. Add ledger transaction entries
        # 3. Save records
        pass
```

## 3. Local Verification Testing
To run the automated checkouts validation locally:
1.  Execute `python verify_sprint23.py` inside the project root folder.
2.  Review output statements to check if wallet deposits, transfers, GST invoice splits, and payouts request gating complete successfully.
