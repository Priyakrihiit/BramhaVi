# Enterprise DAM Deployment Guide

## 1. Prerequisites
- Python 3.10+
- Node.js 18+
- SQLite / PostgreSQL

## 2. Server Deployment Steps

### A. Backend Setup
1. Navigate to the project root.
2. Install Python dependencies:
   ```bash
   pip install -r backend/requirements.txt
   ```
3. Run migrations:
   ```bash
   python backend/manage.py migrate
   ```
4. Collect static files:
   ```bash
   python backend/manage.py collectstatic --noinput
   ```

### B. Frontend Setup
1. Install Node modules:
   ```bash
   npm install
   ```
2. Build assets:
   ```bash
   npm run build
   ```

### C. Run Application
Run the proxy gateway node server:
```bash
npm start
```
This runs Node.js to serve compiled HTML assets and proxies API calls directly to the background Django WSGI/ASGI service on port 8000.
