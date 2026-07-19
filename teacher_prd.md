# BrahmaVidya Galaxy — Teacher Portal Product Requirements Document (PRD)

This document details the product requirements for the **Teacher Portal** of the BrahmaVidya Galaxy platform.

---

## 1. Product Vision & Goals

The Teacher Portal is designed to provide certified instructors with a comprehensive dashboard and workspace to curate curricula, schedule classes, evaluate student work, track performance, and manage payment options.

---

## 2. Target Audience & Roles

*   **Instructors / Teachers**: Primary users who curate courses, deliver live stream sessions, grade assignments, and track wallet balances.
*   **Admins**: Verify teacher applications and process payout splits.
*   **Students**: View teacher announcements, participate in streams, and receive grades.

---

## 3. Core Functional Requirements

### 3.1. Instructor Dashboard
*   **Metric Strips**: Display total students enrolled, average pass rate %, active courses, and net revenue share points.
*   **Cues Panel**: Alert instructors of pending assignments requiring grading.
*   **Schedule Feed**: Display upcoming live lectures and calendars.

### 3.2. Curriculum Curation (Course Builder)
*   **Nested Syllabus Hierarchy**: Add, update, draft, or delete chapters, topics, subtopics, and lessons.
*   **Lesson Management**: Support markdown resources, drip-delay durations, and video URLs.

### 3.3. Student Evaluation (Grading Hub)
*   **Submissions Review**: Side-by-side reading of student text or attachments.
*   **Grading Action**: Apply grades, text feedback commentaries, and digital marks.

### 3.4. Live Classroom Management
*   **Live Sessions**: Schedule live streaming slots and populate WebRTC stream endpoints.

### 3.5. Wallet & Financial Payouts
*   **Balance Ledger**: Track earned points and request payout transfers to PayPal/Stripe accounts.

---

## 4. Technical Quality Attributes
*   **Least-Privilege Authorization**: Ensure teachers can only edit or view grades for courses they are assigned to instruct.
*   **Performance Cache**: Implement 5-minute Redis caches for dashboard views.
*   **Audit Integrity**: Log all grading actions, profile modifications, and announcements in audit databases.
