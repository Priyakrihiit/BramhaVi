# Product Requirements Document (PRD): BrahmaVidya Student Portal

**Document Version**: 1.0.0  
**Date**: July 13, 2026  
**Status**: APPROVED  
**Target Sprint**: Sprint 20  

---

## 1. Executive Summary & Product Vision
BrahmaVidya is an advanced, personalized learning experience platform designed to blend ancient philosophical wisdom with modern educational methodologies. The **Student Portal** is the central learning space for students. It empowers them to consume rich media lessons, manage notes, track personal study goals, schedule reminders, collect rewards, and interact with the AI-driven **Vidya Learning Companion**.

The primary objective of Sprint 20 is to fully integrate the Student Dashboard backend so that learner progression, bookmarking activity, note taking, and achievement metrics are cached efficiently via Redis, synchronized in search indexes via Celery, and grounded into the Vidya AI Conversation memory in real-time.

---

## 2. Key Target Audience & User Personas
*   **Modern Seekers (Learners)**: Highly motivated individuals trying to balance contemporary daily routines with spiritual, mindfulness, and philosophical studies. They require interactive tools like progress trackers, bookmarks, and reminders to remain consistent.
*   **System Mentors (Admins)**: Educators and content administrators who publish syllabi, curate recommended lists, and monitor overall community performance metrics.

---

## 3. Detailed Feature Requirements

### 3.1 Personal Learning Bookmarks
*   **FR-1.1**: Users must be able to bookmark course lessons, tutorials, articles, or meditations.
*   **FR-1.2**: Deletion of a bookmark must instantly remove it from the student's personal bookmarks list.
*   **FR-1.3**: Saving/Deleting bookmarks must trigger an automatic refresh of the student dashboard context and log telemetry event metrics.

### 3.2 Personal Learning Notes (Rich-Text Capture)
*   **FR-2.1**: Students must be able to capture, edit, and delete rich-text learning notes attached to specific lesson nodes.
*   **FR-2.2**: Personal notes must be indexed asynchronously via Celery search tasks, allowing users to find notes through global search query patterns.

### 3.3 Dynamic Study Goals & Streak Tracking
*   **FR-3.1**: Students can define, modify, and track custom Study Goals with specific milestones.
*   **FR-3.2**: System must automatically increment active daily learning streaks on consecutive study sessions.
*   **FR-3.3**: Upon completing a Study Goal (100% progress), the platform must dispatch a celebrate notification and fire a telemetry goal-achieved event.

### 3.4 Gamified Achievements & Badges
*   **FR-4.1**: Students earn badges (Achievements) based on milestone events (e.g., "First Bookmarked Lesson", "10-Day Streak", "Goal Crusher").
*   **FR-4.2**: Earning an achievement must dispatch email and in-app milestone notifications and ground the Vidya AI context.

### 3.5 Learning Reminders & Notifications
*   **FR-5.1**: Students can set specific automated Learning Reminders for courses.
*   **FR-5.2**: Celery periodic tasks must scan active reminders and dispatch push/in-app/email alerts via the centralized notification engine, updating the reminder status cleanly.

---

## 4. Technical Non-Functional Requirements (NFRs)

*   **NFR-1 (Performance)**: Dashboard data queries must execute within < 50ms under heavy loads by utilizing a fast caching layer (e.g., Redis).
*   **NFR-2 (Search Latency)**: Notes search indexing must complete asynchronously within 2 seconds of document save.
*   **NFR-3 (Context Synchronization)**: AI Tutor conversation grounding context must be updated immediately upon any core learning event so that the student has continuous real-time contextual tutor assistance.
