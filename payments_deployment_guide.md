# Deployment Guide — Payments, Wallet & Subscription Platform
**Sprint 23 — BrahmaVidya Galaxy**

## 1. Migration Runbook
Follow this sequence to roll out database schemas safely:

```bash
# 1. Pull latest master commits and compile static packages
git pull origin main
npm run build

# 2. Run django checks to verify codebase syntax integrity
python backend/manage.py check

# 3. View pending migration files
python backend/manage.py showmigrations

# 4. Apply new tables (Wallet, Payments, SubscriptionPlan, Coupon, UserSubscription, Invoice, GSTRecord)
python backend/manage.py migrate wallets
```

## 2. Environment Configurations
Add the following keys to your deployment environment (e.g. `.env` file):

```text
# External Payment Gateway Credentials
STRIPE_SECRET_KEY=sk_live_...
RAZORPAY_KEY_ID=rzp_live_...
RAZORPAY_KEY_SECRET=...

# GST Parameter Configs
GST_PERCENTAGE=18
COMPANY_GSTIN=27AAAAA1111A1Z1

# Celery Broker Configurations
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

## 3. Rollback Runbook
If schema exceptions trigger during deployments:
1.  Revert migrations to previous stable state:
    `python backend/manage.py migrate wallets 0001_initial`
2.  Revert code changes in git to the tag prior to release.
