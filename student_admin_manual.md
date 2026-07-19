# Administrator Management Manual: BrahmaVidya Portal

**Audience**: System Operators, Curators, Mentors, and Administrators  

---

## 1. Monitoring Learner Engagement

As a BrahmaVidya Administrator, you can monitor student engagement through the Central Telemetry Hub:
*   **Activity Logging**: Core learning events (including bookmarks, note creation, and study goals) are recorded as telemetry events. Use these logs to identify high-performing content and track active study times.
*   **Engagement Audits**: Track learning streak distributions to measure user retention across different cohorts.

---

## 2. Managing System Badges & Achievements
You can manage the gamified achievements awarded to students:
1.  Log in to the **BrahmaVidya Admin Console**.
2.  Navigate to **Student** -> **Achievements**.
3.  Click **Add New Achievement**.
4.  Specify a unique name, descriptive prompt (e.g., *"Unlocked after completing a 7-day study streak"*), and attach a custom badge graphic.
5.  Save the achievement. The background engine will automatically evaluate eligibility and award the new badge to qualified students.

---

## 3. Reviewing Automated Communication Dispatches
Automated learner reminders are dispatched automatically by background worker processes.
*   **Dispatch Verification**: Check **Notification Logs** in the admin dashboard to verify that reminder emails and in-app alerts are being successfully delivered.
*   **Delivery Metrics**: Track delivery rates to identify any issues with email configurations or push delivery networks.
*   **System Integrity**: Use the health logs to ensure Celery workers are processing scheduled reminder queues successfully.
