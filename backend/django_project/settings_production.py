"""
Django Production Settings — BrahmaVidya Galaxy
Sprint 18.1: Full production-safe overrides for security and performance.
Usage: DJANGO_SETTINGS_MODULE=django_project.settings_production gunicorn ...
"""
from .settings import *  # noqa: F401,F403
import os

# ── Core Security ──────────────────────────────────────────────────────────────
DEBUG = False
SECRET_KEY = os.environ["DJANGO_SECRET_KEY"]   # Must be explicitly set — no fallback
ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", "").split(",")

# ── HTTPS / HSTS ──────────────────────────────────────────────────────────────
SECURE_SSL_REDIRECT              = True
SECURE_HSTS_SECONDS              = 31536000      # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS   = True
SECURE_HSTS_PRELOAD              = True
SECURE_CONTENT_TYPE_NOSNIFF      = True
SECURE_BROWSER_XSS_FILTER        = True
SECURE_REFERRER_POLICY           = "strict-origin-when-cross-origin"
SECURE_PROXY_SSL_HEADER          = ("HTTP_X_FORWARDED_PROTO", "https")

# ── Cookie Security ────────────────────────────────────────────────────────────
SESSION_COOKIE_SECURE    = True
SESSION_COOKIE_HTTPONLY  = True
SESSION_COOKIE_SAMESITE  = "Lax"
CSRF_COOKIE_SECURE       = True
CSRF_COOKIE_HTTPONLY     = True
CSRF_COOKIE_SAMESITE     = "Lax"
X_FRAME_OPTIONS          = "DENY"

# ── Database ─────────────────────────────────────────────────────────────────
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("DB_NAME", "brahmavidya"),
        "USER": os.environ.get("DB_USER", "postgres"),
        "PASSWORD": os.environ["DB_PASSWORD"],
        "HOST": os.environ.get("DB_HOST", "localhost"),
        "PORT": os.environ.get("DB_PORT", "5432"),
        "CONN_MAX_AGE": int(os.environ.get("DB_CONN_MAX_AGE", "60")),
        "OPTIONS": {
            "connect_timeout": 10,
            "options": "-c statement_timeout=30000",
        },
    }
}

# ── DRF — disable BrowsableAPI in production ─────────────────────────────────
REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"] = [  # noqa: F405
    "rest_framework.renderers.JSONRenderer",
]

# ── Celery — no eager execution in production ─────────────────────────────────
CELERY_TASK_ALWAYS_EAGER = False
CELERY_BROKER_URL     = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND = os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")

# ── Logging — quiet console, file-first ───────────────────────────────────────
LOGGING["loggers"]["django"]["handlers"] = ["app_file", "error_file"]  # noqa: F405
LOGGING["loggers"]["django"]["level"] = "WARNING"  # noqa: F405
