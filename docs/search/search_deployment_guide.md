# Deployment Guide: Unified Enterprise Search Platform

This guide outlines the steps required to migrate, configure, build, and deploy the search platform to staging and production environments.

---

## 1. Prerequisites & Dependencies

### Python Requirements
Ensure all Django and Celery dependencies are installed:
```bash
pip install -r backend/requirements.txt
```

### Redis Server
A running Redis server instance is required to act as the Celery task broker and the rate-limiter backend store:
```bash
redis-server --daemonize yes
```

---

## 2. Backend Deployment Mappings

### 1. Database Migrations
Apply the database migrations to create the search indices schemas:
```bash
python backend/manage.py migrate search
```

### 2. Populate / Rebuild Search Indices
Initialize search document records by running the re-indexing command:
```bash
python backend/manage.py shell -c "from apps.search.services import IndexService; IndexService.reindex_all()"
```

### 3. Celery Worker Execution
Run the Celery worker process to start the asynchronous indexing tasks:
```bash
celery -A django_project worker --loglevel=info
```

---

## 3. Frontend & Gateway Build

### 1. Gateway Server Bundle
Build the Node gateway server:
```bash
npx esbuild server.ts --bundle --platform=node --format=cjs --packages=external --outfile=dist/server.cjs
```

### 2. React Client Compilation
Compile and build the Vite React client bundle:
```bash
npm run build
```
This writes the static assets to the `dist` directory, which is served automatically by the Node gateway in production.
