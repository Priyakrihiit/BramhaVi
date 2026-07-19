# Payments Walkthrough — Sprint 23 — BrahmaVidya Galaxy

This document provides a walkthrough of the Payments, Wallet & Subscription Platform features.

---

## 1. Database Migrations Setup
Ensure database schemas compile and migrate successfully:
```bash
python backend/manage.py makemigrations
python backend/manage.py migrate
```

## 2. Walkthrough Features Checklist

### A. Student Wallet Operations
1.  Navigate to the `/payments` route.
2.  Deposit ₹500 using the **Deposit Funds** input form.
3.  The wallet balance instantly reflects `₹500.00`.
4.  Initialize a peer-to-peer transfer to another student user. Source wallet balance is debited, and the target wallet is credited.

### B. Promo Coupon Codes
1.  Verify voucher creation in the coupon engine.
2.  Input promo code `DISCOUNT20` on checkout.
3.  The final price reflects the 20% discount.

### C. Invoicing and GST Split Calculations
1.  Process a checkout transaction.
2.  The resulting invoice splits the total price intoCGST/SGST shares based on an 18% inclusive tax rate.
3.  Download the compiled text file attachment invoice.

### D. Subscriptions
1.  Review premium membership tier grids.
2.  Subscribe to the "VIP Premium Access" tier.
3.  The active plan is set to ACTIVE and displays the correct expiration dates.
