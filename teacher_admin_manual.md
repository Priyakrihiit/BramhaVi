# BrahmaVidya Galaxy — Teacher Portal Administrative Manual

This manual provides guides for platform administrators to manage teacher accounts, verify applications, and audit activities.

---

## 1. Verifying Teacher Applications

1.  Log in to the Admin Dashboard.
2.  Navigate to **Teacher Applications**.
3.  Review the candidates' resumes, specialties, and experience descriptions.
4.  To approve: Change the application status to **APPROVED**. This automatically spawns the `TeacherProfile` and initializes default wallets and alerts.

---

## 2. Managing Teacher Verification Status

1.  Navigate to **Instructor Profiles**.
2.  Click on the teacher's profile.
3.  Verify their academic certificates.
4.  Toggle the `is_verified` flag to `True` to enable publishing permissions for the teacher.

---

## 3. Auditing Activity & Wallet Adjustments

### 3.1. Activity Logs
*   Navigate to **Activity Logs** inside the Control Center.
*   Filter by model `TeacherActivityLog` to view action histories (e.g. initializations, grading updates, payout setups).

### 3.2. Wallet Ledger Adjustments
*   Navigate to **Earning Ledgers**.
*   Verify revenue share calculations on completed courses.
*   Manual adjustments (deductions or bonuses) can be applied by adding a `TeacherEarning` ledger record with the target amount and type.
