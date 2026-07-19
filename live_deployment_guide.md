# Live Classes Platform — Deployment Guide
**Sprint 22 — Phase 9 Documentation**

## 1. Prerequisites
*   Python 3.12+ / Node.js 20+
*   Running Redis instance (`redis://127.0.0.1:6379`)

## 2. Backend Deployment Steps
1.  Navigate to workspace backend root.
2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3.  Execute migrations:
    ```bash
    python manage.py migrate
    ```
4.  Run Celery background workers:
    ```bash
    celery -A django_project worker --loglevel=info
    ```

## 3. Gateway & Frontend Deployment
1.  Compile frontend bundle assets:
    ```bash
    npm run build
    ```
2.  Start the Express central gateway server:
    ```bash
    node dist/server.cjs
    ```
