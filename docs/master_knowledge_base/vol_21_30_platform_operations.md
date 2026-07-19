# BrahmaVidya Galaxy - Master Knowledge Base V2.0
## Volumes 21 to 30: Platform Systems, Finance ledgers, & DevOps Orchestration

---

## Volume 21 - Community

### 21.1 Forum & Moderation Schemas
```sql
CREATE TABLE community_flags (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    post_id UUID NOT NULL,
    flagged_by UUID REFERENCES users(id) ON DELETE CASCADE,
    reason TEXT NOT NULL,
    status VARCHAR(50) DEFAULT 'PENDING' CHECK (status IN ('PENDING', 'RESOLVED', 'DISMISSED')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

---

## Volume 22 - Finance Galaxy

### 22.1 Double-Entry Transaction Ledger Schema
To prevent race conditions, the balance of a wallet is calculated by summing the ledger entries. Direct updates to the `balance` field are protected by row locks:
```sql
-- Wallets Ledger entries table
CREATE TABLE wallet_ledger_entries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    from_wallet_id UUID REFERENCES wallets(id) ON DELETE PROTECT,
    to_wallet_id UUID REFERENCES wallets(id) ON DELETE PROTECT,
    amount DECIMAL(12, 2) NOT NULL CHECK (amount > 0),
    transaction_type VARCHAR(50) NOT NULL CHECK (transaction_type IN ('PURCHASE', 'PAYOUT', 'REFUND', 'TRANSFER', 'WITHDRAWAL')),
    gst_collected DECIMAL(12, 2) DEFAULT 0.00,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

### 22.2 Payment Webhook Processing API
* **Stripe Webhook Receiver**:
  * `POST /api/v1/payments/webhooks/stripe/`
  * Payload: Envelops standard Stripe JSON structure verifying `"type": "checkout.session.completed"`.
  * Validation: Decodes signature header using webhook secrets before adjusting ledger balances.

---

## Volume 23 - AI Recommendation Engine

### 23.1 Vector Similarity Recommendation Logic
* **Cross-Module Recommendations**: Matches target user profiles with vectors representing courses, jobs, or books:
$$\text{Score} = \frac{\mathbf{u} \cdot \mathbf{v}}{\|\mathbf{u}\| \|\mathbf{v}\|}$$
Where $\mathbf{u}$ represents the user profile embedding and $\mathbf{v}$ represents the course/job/book metadata embedding vector.

---

## Volume 24 - Notifications

### 24.1 Delivery Router Rules
The pipeline dynamically chooses delivery protocols:
* Verification Codes -> TWILIO SMS or WHATSAPP API.
* Course Completed Updates -> SENDGRID Email.
* Daily Streaks Reminder -> FIREBASE Push Notifications.

---

## Volume 25 - Analytics

### 25.1 Clickstream Analytics
```sql
CREATE TABLE clickstream_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID,
    event_type VARCHAR(100) NOT NULL, -- e.g., 'VIDEO_PLAY', 'BUTTON_CLICK'
    payload JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
) PARTITION BY RANGE (created_at);
```

---

## Volume 26 - Administration

### 26.1 System Audits Logging
Administrative adjustments (e.g. updating platform fee cuts, editing user permissions) are logged immutably:
```sql
CREATE TABLE system_audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    action_by UUID REFERENCES users(id) ON DELETE RESTRICT,
    action_type VARCHAR(100) NOT NULL, -- 'RBAC_CHANGE', 'FEE_UPDATE'
    previous_state JSONB,
    current_state JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

---

## Volume 27 - DevOps

### 27.1 Containerization Layout
The production architecture is dockerized using separate containers:
* `web-client`: Serves React / Flutter web assets.
* `api-gateway`: Node.js Express proxy router.
* `backend-api`: Django WSGI app container.
* `db`: PostgreSQL cluster database.
* `cache`: Redis cluster caching scopes.

---

## Volume 28 - Security

### 28.1 TOTP & Encryption Rules
All credentials and client configuration secrets (e.g., Stripe private keys, Gemini tokens) are loaded as environment variables and decrypted at runtime.

---

## Volume 29 - Testing

### 29.1 Playwright E2E Pathway Configuration
```javascript
// Sample Playwright User Checkout Flow Test
import { test, expect } from '@playwright/test';

test('Verify successful student course purchase splits ledger', async ({ page }) => {
  await page.goto('https://brahmavidya.galaxy/login');
  await page.fill('#email', 'student@brahmavidya.edu');
  await page.fill('#password', 'studentpassword123');
  await page.click('#submit-btn');
  await page.goto('https://brahmavidya.galaxy/courses/quantum-metaphorics');
  await page.click('#buy-now-btn');
  await expect(page.locator('#checkout-modal')).toBeVisible();
});
```

---

## Volume 30 - Release Roadmap

### 30.1 Sprint Pipeline Milestones
* **Sprint 1-2**: Migration corrections and custom permission filters validation on Django.
* **Sprint 3-4**: Deploy Flutter responsive layout shell interfaces.
* **Sprint 5-6**: Stripe checkout webhook balance splits reconciliation.
