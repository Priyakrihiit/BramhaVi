# Deployment Guide: Enterprise Analytics Platform

This guide outlines the steps required to configure, migrate, build, and deploy the analytics platform to staging and production environments.

---

## 1. Environment Requirements

### Python & Celery
Ensure all dependencies are installed:
```bash
pip install -r backend/requirements.txt
```

### Redis Server
A running Redis server is required to handle the Celery task queue and rate-limiter backend:
```bash
redis-server --daemonize yes
```

---

## 2. Deploy Steps

### 1. Database Migrations
Apply the database migrations to create the analytics tables schemas:
```bash
python backend/manage.py migrate analytics
```

### 2. Populate Metrics Definitions Catalog
To seed the initial metric parameters and KPI targets in the database, run the seed script:
```bash
python backend/manage.py shell -c "from apps.analytics.models import Metric; Metric.objects.get_or_create(key='user_activity', defaults={'name': 'User Login Success', 'category': 'general', 'unit': 'count'})"
```

### 3. Start Celery worker & Beat Scheduler
Run the Celery worker and periodic scheduler process to start background tasks and aggregations:
```bash
celery -A django_project worker --loglevel=info
celery -A django_project beat --loglevel=info
```

---

## 3. Frontend & Gateway Bundle

### 1. Gateway Server Build
Compile and bundle the Node API gateway:
```bash
npx esbuild server.ts --bundle --platform=node --format=cjs --packages=external --outfile=dist/server.cjs
```

### 2. React Production Build
Vite compiles React client assets into the `dist/` folder:
```bash
npm run build
```
