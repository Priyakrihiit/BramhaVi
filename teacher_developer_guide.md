# BrahmaVidya Galaxy — Teacher Portal Developer Guide

This document is a technical guide for developers contributing to the **Teacher Portal** codebase.

---

## 1. Directory Structure & Architecture

The `apps/teacher` directory contains standard modular Django sub-components:

*   **`models.py`**: Declares models for instructor profiles, batches, schedules, and earnings.
*   **`services.py`**: Houses domain-driven transactional services (e.g. grading updates, payout initialization).
*   **`selectors.py`**: Aggregates metrics and performs cached dashboard compilations.
*   **`permissions.py`**: Custom authorization guards for endpoint access.
*   **`signals.py`**: Auto-triggers schedule synchronization, wallets creation, and cache invalidation.

---

## 2. Dev Environment Configuration

### 2.1. Celery & Redis Fallback Setup
In local development environments without a running Redis server, Celery tasks block on connection pooling retries. Enable **eager execution mode** inside your shell or test scripts:

```powershell
$env:CELERY_TASK_ALWAYS_EAGER="True"
```

---

## 3. Writing Code Conventions

### 3.1. Database Transaction Decorators
Domain-level write actions in `services.py` must be decorated with `@transaction.atomic` to prevent partial db commits on failure.

### 3.2. Caching Policies
Dashboard query aggregations use Redis cache to reduce database loads. When modifying a teacher-related model (profile, batch, earnings), ensure you call `invalidate_teacher_dashboard_cache(teacher_id)` to keep the feed synchronized.

---

## 4. Running Unit Tests

To run the unit tests suite specifically for the teacher portal application:

```powershell
$env:CELERY_TASK_ALWAYS_EAGER="True"
python backend/manage.py test apps.teacher
```
