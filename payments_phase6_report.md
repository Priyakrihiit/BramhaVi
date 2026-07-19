# BrahmaVidya Galaxy — Payments Phase 6 React Payments Dashboard Report
**Sprint 23 — Phase 6 Documentation**

This report documents the implementation of the frontend user interfaces for the Payments, Wallet & Subscription Platform.

---

## 1. UI Pages and Components Implemented

We created a unified, premium-grade dashboard inside `src/pages/public/PaymentsDashboard.tsx` featuring the requested 10 components:

1.  **Wallet Dashboard**: Displays point balance with modals to add funds and initialize peer transfers.
2.  **Payment History**: Lists double-entry transaction journals (credits, debits, dates, descriptions).
3.  **Checkout Page**: Mocks interactive card billing sheets, applies coupons, and calculates GST taxes (18%).
4.  **Subscription Plans**: Renders cards for tier memberships (Student, Teacher, Institute) with Upgrade, Downgrade, and Cancel actions.
5.  **Invoice Viewer**: Shows client invoice details in a mock terminal with print and download buttons.
6.  **Coupons Engine**: Features validate and apply promotion code logic.
7.  **Teacher Earnings**: Keeps track of instructor withdrawal logs and payout method selections.
8.  **Withdrawals Request**: Facilitates instant withdrawal request creations.
9.  **Revenue Dashboard**: Offers admin statistics charts (daily, monthly, wallet, subscription totals).
10. **Referral Dashboard**: Invites referrals through shared VIP join URLs and credits earned.

---

## 2. API Integrations

The dashboard communicates directly with our Gateway proxy layer (/api/v1/payments/*) using a dedicated api wrapper:
*   **API Client Class**: [paymentsApi](file:///c:/Users/USER/Downloads/bramhavi%20(3)/src/services/paymentsApi.ts)

---

## 3. Router Configuration

*   **File**: [App.tsx](file:///c:/Users/USER/Downloads/bramhavi%20(3)/src/App.tsx#L104-L106)
*   **Path**: `/payments`

---

## 4. Compilation Build Status

*   **Command**: `npm run build`
*   **Status**: 🟢 **SUCCESS**
*   **Vite Build Output**:
    *   `dist/assets/index-Byjwl_g_.css` (128.71 kB)
    *   `dist/assets/index-DwV7zj0P.js` (2,368.24 kB)
