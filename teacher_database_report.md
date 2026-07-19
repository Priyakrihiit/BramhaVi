# BrahmaVidya Galaxy LMS Platform — Teacher Portal Database Report
**Sprint 21 — Phase 2: Database Extension & Schema Certification**

**Date**: July 13, 2026  
**Lead Architect**: BrahmaVidya Core Database Engineering Team  
**Status**: 🟢 **Database Schema Fully Implemented, Migrated, and Checked (100% Pass)**

---

## 1. Executive Summary

This report documents the successful design and physical implementation of the database extensions supporting the newly introduced **Teacher Portal** for the BrahmaVidya Galaxy platform. In alignment with our architectural specifications (detailed in `teacher_portal_analysis.md`), a modular Django application called `apps.teacher` was initialized.

A complete suite of 17 database models has been declared, resolving schema gaps for instructor profiles, analytics logs, scheduling calendars, attendance tracking, revenue ledger entries, performance indicators, and audit trails.

All database migrations have been generated, successfully applied to the persistent storage layer, and verified through Django's native system diagnostics, resulting in zero syntax warnings, schema conflicts, or relationship errors.

---

## 2. Implemented Database Schema Specifications

The following relational models have been successfully created inside the `apps.teacher` application (`/backend/apps/teacher/models.py`), leveraging our robust base classes (`BaseModel` and `SoftDeleteModel`):

### 2.1. Profiles & Core Identity
*   **`TeacherProfile`** *(SoftDeleteModel)*
    *   *Purpose*: Extends the system-wide User model with instructor-specific identity credentials and details.
    *   *Schema*:
        *   `user` (OneToOneField -> `users.User`): Unique link mapping the core account to this profile.
        *   `bio` (TextField): Professional biography and academic introduction.
        *   `qualifications` (JSONField): Serialized array of academic degrees, certifications, and credentials.
        *   `specialties` (JSONField): List of primary academic subjects and expertise.
        *   `experience_years` (IntegerField): Total years of professional teaching experience.
        *   `is_verified` (BooleanField): Status flag confirming verified credentials by system admins.
        *   `rating` (DecimalField): Normalized course evaluation score (1.00 to 5.00).

### 2.2. Scheduling, Calendar, & Events
*   **`TeachingSession`** *(SoftDeleteModel)*
    *   *Purpose*: Schedules tutoring, mentoring, and office hour events outside the core curriculum classes.
    *   *Schema*:
        *   `teacher` (ForeignKey -> `users.User`): Instructor hosting the session.
        *   `title` (CharField): Session topic or purpose.
        *   `session_type` (CharField): Type of tutorial (e.g., `OFFICE_HOURS`, `MENTORING`, `GROUP_REVIEW`).
        *   `start_time` / `end_time` (DateTimeField): Scheduled time block bounds.
        *   `meeting_link` (CharField): Virtual meeting URL (Google Meet, Zoom, etc.).
        *   `notes` (TextField): Pre-meeting syllabus context.

*   **`TeachingCalendar`** *(BaseModel)*
    *   *Purpose*: Manages recurring availability slots for instructors.
    *   *Schema*:
        *   `teacher` (ForeignKey -> `users.User`): Associated teacher.
        *   `day_of_week` (IntegerField): Day index (1 to 7 corresponding to Monday to Sunday).
        *   `start_time` / `end_time` (TimeField): Operational availability window.
        *   `recurrence_rule` (CharField): Cron-style or standard recurrence keyword (e.g., `WEEKLY`).

*   **`TeacherSchedule`** *(BaseModel)*
    *   *Purpose*: Tracks individual administrative tasks and events scheduled by the teacher.
    *   *Schema*:
        *   `teacher` (ForeignKey -> `users.User`): Associated teacher.
        *   `title` (CharField) / `description` (TextField): Scheduled action.
        *   `start_time` / `end_time` (DateTimeField): Schedule timestamps.
        *   `status` (CharField): Event lifecycle state (`PENDING`, `IN_PROGRESS`, `COMPLETED`, `CANCELLED`).

### 2.3. Cohort & Group Management
*   **`Batch`** *(SoftDeleteModel)*
    *   *Purpose*: Segments course enrollments into distinct schedule cohorts.
    *   *Schema*:
        *   `course` (ForeignKey -> `lms.CourseStructure` where `node_type = 'COURSE'`): Associated course curriculum node.
        *   `name` (CharField): Cohort label (e.g., "Fall 2026 Batch Alpha").
        *   `start_date` / `end_date` (DateField): Batch boundaries.
        *   `instructors` (ManyToManyField -> `users.User`): Teachers authorized to instruct this cohort.
        *   `is_active` (BooleanField): Status flag indicating if the cohort is active.

*   **`Attendance`** *(BaseModel)*
    *   *Purpose*: Records student attendance for synchronous events and stream lectures.
    *   *Schema*:
        *   `session` (ForeignKey -> `TeachingSession`): Associated tutoring session, if applicable.
        *   `live_class` (ForeignKey -> `lms.LiveClass`): Associated Live Class stream, if applicable.
        *   `student` (ForeignKey -> `users.User`): Student user.
        *   `joined_at` / `left_at` (DateTimeField): Stream interaction logs.
        *   `status` (CharField): Attendance status (`PRESENT`, `ABSENT`, `LATE`, `EXCUSED`).

### 2.4. Financial Ledger & Wallet
*   **`TeacherEarning`** *(BaseModel)*
    *   *Purpose*: Logs split revenues, evaluation bonuses, and pay ledger entries for instructors.
    *   *Schema*:
        *   `teacher` (ForeignKey -> `users.User`): Earning instructor recipient.
        *   `course` (ForeignKey -> `lms.CourseStructure`): Source course yielding the transaction, if applicable.
        *   `amount` (DecimalField): Financial amount credited.
        *   `points` (IntegerField): Gamified points credited.
        *   `earning_type` (CharField): Earning category (`REVENUE_SHARE`, `GRADING_BONUS`, `LECTURE_PAYMENT`, `SYSTEM_AWARD`).
        *   `description` (TextField): Descriptive metadata notes.
        *   `recorded_at` (DateTimeField): Automated ledger timestamp.

*   **`TeacherWallet`** *(BaseModel)*
    *   *Purpose*: Stores configuration for withdrawable balances and payout parameters.
    *   *Schema*:
        *   `teacher` (OneToOneField -> `users.User`): Connected user.
        *   `payout_method` (CharField): Selected payment processor (`STRIPE`, `PAYPAL`, `BANK`).
        *   `payout_address` (CharField): Routing bank details, cards, or PayPal address.
        *   `balance_points` (IntegerField) / `balance_amount` (DecimalField): Withdrawable balances.
        *   `last_payout_at` (DateTimeField): Timestamp of the last completed withdrawal.

### 2.5. Question Bank Taxonomy
*   **`QuestionCategory`** *(BaseModel)*
    *   *Purpose*: Custom organizational tags for question items.
    *   *Schema*:
        *   `name` (CharField): Unique taxonomic category name (e.g., "Sanskrit", "Ethics").
        *   `description` (TextField): Explanatory topic notes.

*   **`QuestionDifficulty`** *(BaseModel)*
    *   *Purpose*: Complexity weights for exam evaluations.
    *   *Schema*:
        *   `level` (CharField): Tier identifier (e.g., "EASY", "MEDIUM", "HARD").
        *   `multiplier` (DecimalField): Grading multiplier.

### 2.6. Performance, Gamification, & Preferences
*   **`TeacherAnalytics`** *(BaseModel)*
    *   *Purpose*: Aggregates teacher instructional metrics over time.
    *   *Schema*:
        *   `teacher` (ForeignKey -> `users.User`): Associated teacher.
        *   `total_students_taught` (IntegerField): Total students.
        *   `average_course_rating` (DecimalField): Aggregated ratings.
        *   `total_teaching_hours` (DecimalField): Sum of live hours.
        *   `assignment_completion_rate` (DecimalField): Grading turnaround pace.

*   **`TeacherCertificate`** *(SoftDeleteModel)*
    *   *Purpose*: Verification credentials earned by teachers.
    *   *Schema*:
        *   `teacher` (ForeignKey -> `users.User`): Instructor.
        *   `title` (CharField) / `issuer` (CharField): Certificate details.
        *   `issued_date` / `expiry_date` (DateField): Certification validity windows.
        *   `verification_url` (CharField): Public validator URL.

*   **`TeacherAchievement`** *(BaseModel)*
    *   *Purpose*: Rewards and milestone badges earned by instructors within the platform.
    *   *Schema*:
        *   `teacher` (ForeignKey -> `users.User`): Instructor.
        *   `title` (CharField) / `description` (TextField): Award parameters.
        *   `badge_icon` (CharField): Lucide icon tag mapping.

*   **`TeachingGoal`** *(BaseModel)*
    *   *Purpose*: Tracks professional development KPIs or progress targets.
    *   *Schema*:
        *   `teacher` (ForeignKey -> `users.User`): Associated instructor.
        *   `title` (CharField) / `description` (TextField): Goal descriptions.
        *   `target_metric` (CharField): Target metric type (`STUDENT_RATING`, `CLASSES_HELD`, `GRADED_COUNT`).
        *   `target_value` / `current_value` (DecimalField): Progress trackers.
        *   `deadline` (DateField) / `is_completed` (BooleanField): Target constraints.

*   **`TeacherNotificationPreference`** *(BaseModel)*
    *   *Purpose*: Fine-grained alert options.
    *   *Schema*:
        *   `teacher` (OneToOneField -> `users.User`): Associated teacher.
        *   `email_on_submission` (BooleanField): Immediate grading alerts.
        *   `email_on_discussion` (BooleanField): Forum discussion alerts.
        *   `push_on_live_class` (BooleanField): Live launch warnings.

### 2.7. Auditing & Bulletins
*   **`TeacherAnnouncement`** *(SoftDeleteModel)*
    *   *Purpose*: Bulletins posted by teachers to courses or cohorts.
    *   *Schema*:
        *   `teacher` (ForeignKey -> `users.User`): Associated teacher.
        *   `course` (ForeignKey -> `lms.CourseStructure`): Recipient course.
        *   `title` (CharField) / `content` (TextField): Announcement message body.

*   **`TeacherActivityLog`** *(BaseModel)*
    *   *Purpose*: Audit trails recording instructor actions.
    *   *Schema*:
        *   `teacher` (ForeignKey -> `users.User`): Associated teacher.
        *   `action` (CharField): Coded operation (e.g., "GRADED_ASSIGNMENT").
        *   `details` (TextField): Contextual details.
        *   `ip_address` (GenericIPAddressField): Operating IP.

---

## 3. Database Execution & Verification Logs

The database models have been verified through Django's migration engine and system diagnostic suite. Below are the execution logs:

### 3.1. Generating Database Migrations
```bash
python3 backend/manage.py makemigrations
```
```
Migrations for 'teacher':
  backend/apps/teacher/migrations/0001_initial.py
    - Create model QuestionCategory
    - Create model QuestionDifficulty
    - Create model Batch
    - Create model TeacherAchievement
    - Create model TeacherActivityLog
    - Create model TeacherAnalytics
    - Create model TeacherAnnouncement
    - Create model TeacherCertificate
    - Create model TeacherEarning
    - Create model TeacherNotificationPreference
    - Create model TeacherProfile
    - Create model TeacherSchedule
    - Create model TeacherWallet
    - Create model TeachingCalendar
    - Create model TeachingGoal
    - Create model TeachingSession
    - Create model Attendance
```

### 3.2. Applying Migrations
```bash
python3 backend/manage.py migrate
```
```
Operations to perform:
  Apply all migrations: admin, analytics, auth, cms, contenttypes, control_center, lms, notifications, publishing, search, seo, services, sessions, student, teacher, token_blacklist, users, wallets
Running migrations:
  Applying teacher.0001_initial... OK
```

### 3.3. Structural Integrity System Check
```bash
python3 backend/manage.py check
```
```
System check identified no issues (0 silenced).
```

---

## 4. Next Steps

With the database schemas verified and applied, Phase 2 is fully complete. The system is ready to proceed to Phase 3: **Teacher Portal API & Views Implementation**.
