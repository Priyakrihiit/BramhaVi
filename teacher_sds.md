# BrahmaVidya Galaxy — Teacher Portal System Design Specification (SDS)

This document describes the technical architecture and database design for the **Teacher Portal** backend.

---

## 1. System Architecture

The Teacher Portal is built using a decoupled, multi-tier architecture:

```
[ Vite + React Client ] ➔ [ Express Gateway Proxy ] ➔ [ Django REST Backend ] ➔ [ SQLite / Cache ]
```

*   **API Gateway Routing**: Express server proxies client gateway requests from `/api/teacher/*` to DRF `/api/v1/teacher/*`.
*   **Domain App**: Backend logic resides in `backend/apps/teacher/` to separate it from the student dashboard.

---

## 2. Database Model Schema

### 2.1. TeacherProfile
*   `user` (OneToOne ➔ `users.User`): Associated teacher.
*   `bio` (TextField): Biography notes.
*   `qualifications` (JSONField): Array of verified achievements.
*   `specialties` (JSONField): Expertise topics.
*   `experience_years` (IntegerField): Teaching experience.
*   `is_verified` (BooleanField): Approval status by admins.
*   `rating` (DecimalField): Normalized rating between 1.00 and 5.00.

### 2.2. TeacherWallet
*   `teacher` (ForeignKey ➔ `users.User`)
*   `payout_method` (Stripe / PayPal)
*   `payout_address` (Stripe account ID or PayPal email)

### 2.3. TeacherEarning
*   `teacher` (ForeignKey ➔ `users.User`)
*   `course` (ForeignKey ➔ `lms.CourseStructure`)
*   `amount` (DecimalField): Earned points/dollars.
*   `earning_type` (Salary, bonus, commission)

### 2.4. Batch
*   `course` (ForeignKey ➔ `lms.CourseStructure`)
*   `instructors` (ManyToManyField ➔ `users.User`)
*   `students` (ManyToManyField ➔ `users.User`): Enrolled students.

---

## 3. API Endpoints

*   `GET /api/v1/teacher/dashboard/summary/`: Dashboard summary with Redis caching.
*   `GET /api/v1/teacher/profiles/`: Instructor details CRUD.
*   `POST /api/v1/teacher/grading/grade-submission/`: Submissions evaluation.
*   `GET /api/v1/teacher/earnings/`: Revenue audit reports.

---

## 4. Signal Handlers
*   `on_teacher_profile_saved_handler`: Auto-creates empty wallets and alert presets upon profile creation.
*   `on_teacher_earning_saved_handler`: Invalidates the cached dashboard data on change.
