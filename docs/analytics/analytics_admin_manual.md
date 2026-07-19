# Administrator Manual: Enterprise Analytics Platform

**BrahmaVidya Galaxy — Analytics Module**
**Version:** 1.0 | **Audience:** Platform Administrators, Institute Managers, Teachers

---

## 1. Overview

Administrators have full access to the analytics platform, including global platform metrics, revenue dashboards, export tools, and report scheduling. This manual describes the operations available to administrative users.

---

## 2. Control Dashboard

### 2.1 Widget Grid
The dashboard loads all configured widgets automatically. Widgets are populated dynamically based on your role. Admin-role widgets include:

| Widget | Source Metric | Description |
|---|---|---|
| Total Students | `users.User` count | Registered learner count |
| Platform Revenue | `wallets.Payment` sum | Total completed payment amounts |
| Active Sessions | `analytics.UserSession` active count | Live concurrent users |
| AI Token Usage | `control_center.AIMessage` count | Tokens consumed this month |
| Certificates Issued | `lms.Certificate` count | Verified completions |
| Media Files | `control_center.MediaFile` count | DAM library size |

### 2.2 KPI Indicators Panel
Each KPI displays:
- **Current Value** vs. **Target Value** with a progress bar.
- A status badge: `ACHIEVED` (green) or `IN PROGRESS` (amber).

To update a KPI target, navigate to the **KPI Configurations** tab and edit the target value.

---

## 3. Module Analytics

Click **Module Analytics** and select a module from the selector row:

| Module | Key Metrics Tracked |
|---|---|
| User | Login success rate, geographic distribution |
| Course | Completion rate, assignment scores |
| Revenue | MRR, payment success rate |
| Search | Query volumes, click-through rates |
| SEO | Page update frequency, sitemap coverage |
| Notifications | Delivery success, open rate |
| CMS | Article publication rate, comment volume |
| Wallet | Transaction count, refund rate |
| Marketplace | Listing count, purchase conversions |
| AI | Token consumption, model usage split |

---

## 4. Report Exporter Tab

### 4.1 Quick Export
Click **Create CSV Export**, **Create Excel Export**, or **Create PDF Export** to trigger a background export job. The job table updates automatically when the file is ready.

### 4.2 Scheduling Automated Reports
1. Enter a **Report Title** (e.g., `Weekly Revenue Summary`).
2. Select **Frequency**: Daily, Weekly, or Monthly.
3. Enter **Recipients** as comma-separated email addresses.
4. Click **Add Report Schedule**.

The platform will dispatch the report via email at the configured frequency.

To delete a schedule, click the trash icon next to the schedule row.

---

## 5. KPI Configurations Tab

Lists all tracked KPIs with their metric keys, current values, and defined targets. Use the backend admin panel at `/admin/analytics/kpi/` to create or modify KPI entries.

---

## 6. Backend Admin Panel

Access the Django admin at `/admin/` for full control:
- `Analytics > Analytics Events` — Browse raw telemetry log records.
- `Analytics > Daily Summaries` — View aggregated summary counts.
- `Analytics > Export Jobs` — Monitor export job status and download links.
- `Analytics > KPIs` — Create, edit, or delete KPI definitions.
- `Analytics > Report Schedules` — Manage automated report triggers.
- `Analytics > Dashboard Widgets` — Configure widget cards ordering and display.
