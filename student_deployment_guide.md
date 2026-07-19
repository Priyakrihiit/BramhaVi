# Deployment Operations Guide: BrahmaVidya Student Portal

**Target Runtime Platform**: Google Cloud Run, GCP Cloud SQL PostgreSQL, GCP Memorystore Redis  

---

## 1. System Environment Configuration
Before deploying the full-stack BrahmaVidya system to production, define the following variables within your cloud container environments:

```env
# ─── Environment Core ────────────────────────────────────────────────────────
DJANGO_DEBUG=False
DJANGO_SECRET_KEY=yoursecretkeyhere-ensurethisislongerthan50characters
ALLOWED_HOSTS=brahmavidya.example.com

# ─── Database Connections ────────────────────────────────────────────────────
DB_NAME=brahmavidya
DB_USER=brahmavidya_admin
DB_PASSWORD=secure_postgres_password_here
DB_HOST=/cloudsql/project:region:instance-connection-name
DB_PORT=5432
DB_CONN_MAX_AGE=60

# ─── Cache & Caching Infrastructure ──────────────────────────────────────────
REDIS_URL=redis://10.0.0.3:6379/1
```

---

## 2. Docker & Container Multi-Stage Builds
The standard build command compiles assets and bundle files cleanly:
`npm run build`

The pipeline:
1.  **Frontend Compile**: Uses Vite to compile the client-side single-page application inside the `/dist/` folder.
2.  **Server Bundle**: Bundles the `server.ts` Express/Vite proxy file into a standalone, optimized ES module at `/dist/server.cjs` via esbuild.

---

## 3. Database Migration Procedures
Upon launching a container release, run the database migration script before redirecting production traffic:

```bash
# Apply all Django database schema migrations
python3 backend/manage.py migrate
```

---

## 4. Launching the App
Run the following start command to spin up the Node runtime:
```bash
npm run start
```
This serves compiled client assets and proxies API endpoint requests directly into Django's WSGI server.
