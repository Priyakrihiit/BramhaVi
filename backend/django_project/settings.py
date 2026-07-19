"""
Django Settings Configuration - BrahmaVidya Galaxy
Purpose: Production-hardened settings with environment-driven security controls.
Sprint 18.1: Full security hardening, caching, throttling, connection pooling.
"""

import os
import logging
from pathlib import Path

# ─── Paths ────────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent

# ─── Security ─────────────────────────────────────────────────────────────────
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "django-insecure-fallback-secret-key-for-development")
DEBUG = os.getenv("DJANGO_DEBUG", "True").lower() == "true"
ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS", "*").split(",")

# Production security headers — all controlled via env vars so dev works without them
# In production: set DJANGO_PRODUCTION=True in environment.
_IS_PRODUCTION = os.getenv("DJANGO_PRODUCTION", "False").lower() == "true"

SECURE_SSL_REDIRECT              = _IS_PRODUCTION and os.getenv("SECURE_SSL_REDIRECT", "True").lower() == "true"
SECURE_HSTS_SECONDS              = int(os.getenv("SECURE_HSTS_SECONDS", "31536000")) if _IS_PRODUCTION else 0
SECURE_HSTS_INCLUDE_SUBDOMAINS   = _IS_PRODUCTION
SECURE_HSTS_PRELOAD              = _IS_PRODUCTION
SECURE_CONTENT_TYPE_NOSNIFF      = True
SECURE_BROWSER_XSS_FILTER        = True
SESSION_COOKIE_SECURE            = _IS_PRODUCTION
SESSION_COOKIE_HTTPONLY          = True
SESSION_COOKIE_SAMESITE          = "Lax"
CSRF_COOKIE_SECURE               = _IS_PRODUCTION
CSRF_COOKIE_HTTPONLY             = True
CSRF_COOKIE_SAMESITE             = "Lax"
X_FRAME_OPTIONS                  = "DENY"
SECURE_REFERRER_POLICY           = "strict-origin-when-cross-origin"
SECURE_PROXY_SSL_HEADER          = ("HTTP_X_FORWARDED_PROTO", "https") if _IS_PRODUCTION else None

# ─── Application Definition ───────────────────────────────────────────────────
INSTALLED_APPS = [
    # Core Django System
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Third-Party Frameworks
    "rest_framework",
    "corsheaders",
    "rest_framework_simplejwt.token_blacklist",
    "django_filters",

    # Custom BrahmaVidya Modular Django Apps
    "apps.users.apps.UsersConfig",
    "apps.cms.apps.CmsConfig",
    "apps.lms.apps.LmsConfig",
    "apps.wallets.apps.WalletsConfig",
    "apps.control_center.apps.ControlCenterConfig",
    "apps.ai.apps.AiConfig",
    "apps.portfolio.apps.PortfolioConfig",
    "apps.publishing.apps.PublishingConfig",
    "apps.services.apps.ServicesConfig",
    "apps.seo.apps.SeoConfig",
    "apps.notifications.apps.NotificationsConfig",
    "apps.search.apps.SearchConfig",
    "apps.analytics.apps.AnalyticsConfig",
    # Sprint 20 — Student Portal
    "apps.student.apps.StudentConfig",
    # Sprint 21 — Teacher Portal
    "apps.teacher.apps.TeacherConfig",
]

MIDDLEWARE = [
    "middleware.request_id.RequestIDMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    # Custom Structural Auditing and Security Middleware
    "middleware.audit.AuditLogMiddleware",
    "middleware.security.SecurityHardeningMiddleware",
]

ROOT_URLCONF = "django_project.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "django_project.wsgi.application"
ASGI_APPLICATION = "django_project.asgi.application"

# ─── Database ─────────────────────────────────────────────────────────────────
# CONN_MAX_AGE: Persistent connections — reuse DB connections for 60s (improves throughput)
if os.getenv("USE_SQLITE", "True").lower() == "true":
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
            # SQLite doesn't support persistent connections — keep at 0
            "CONN_MAX_AGE": 0,
            "OPTIONS": {
                "timeout": 20,
            },
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.getenv("DB_NAME", "brahmavidya"),
            "USER": os.getenv("DB_USER", "postgres"),
            "PASSWORD": os.getenv("DB_PASSWORD", ""),
            "HOST": os.getenv("DB_HOST", "localhost"),
            "PORT": os.getenv("DB_PORT", "5432"),
            # Persistent connections — avoids new TCP connection per request
            "CONN_MAX_AGE": int(os.getenv("DB_CONN_MAX_AGE", "60")),
            "OPTIONS": {
                "connect_timeout": 10,
                "options": "-c statement_timeout=30000",  # 30s query timeout
            },
        }
    }

# ─── Caching ──────────────────────────────────────────────────────────────────
_REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/1")

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": _REDIS_URL,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "IGNORE_EXCEPTIONS": True,   # Graceful fallback if Redis is down
            "CONNECTION_POOL_KWARGS": {
                "max_connections": 50,
                "retry_on_timeout": True,
            },
        },
        "KEY_PREFIX": "bvg",
        "TIMEOUT": 300,    # 5-minute default cache TTL
        "VERSION": 1,
    },
    # Separate cache for long-lived analytics summaries (1 hour TTL)
    "analytics": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": os.getenv("REDIS_ANALYTICS_URL", "redis://localhost:6379/2"),
        "OPTIONS": {
            "IGNORE_EXCEPTIONS": True,
            "CONNECTION_POOL_KWARGS": {"max_connections": 20},
        },
        "KEY_PREFIX": "bvg_analytics",
        "TIMEOUT": 3600,    # 1-hour TTL for pre-computed aggregations
        "VERSION": 1,
    },
    # Fallback in-memory cache for local/test environments without Redis
    "locmem": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "brahmavidya-local",
    },
}

# Session engine — use cached sessions for speed in production
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"

# ─── Password Validation ──────────────────────────────────────────────────────
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", "OPTIONS": {"min_length": 10}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ─── Regionalization ──────────────────────────────────────────────────────────
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# ─── Static & Media Assets ────────────────────────────────────────────────────
STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")    # Required for collectstatic
STATICFILES_DIRS = []
MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

# ─── Default Primary Key Field Policy ────────────────────────────────────────
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
AUTH_USER_MODEL = "users.User"

# ─── Django REST Framework ────────────────────────────────────────────────────
REST_FRAMEWORK = {
    "DEFAULT_VERSIONING_CLASS": "rest_framework.versioning.NamespaceVersioning",
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
    # ── Throttling — rate limits at DRF layer ──
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon":           "60/minute",      # Unauthenticated API calls
        "user":           "300/minute",     # Authenticated user calls
        "analytics":      "100/minute",     # Analytics event collector
        "exports":        "10/minute",      # Export job creation
        "report_create":  "20/minute",      # Report schedule creation
    },
    # ── Performance ──
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",   # Remove BrowsableAPIRenderer in prod
    ] if _IS_PRODUCTION else [
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
    ],
    "EXCEPTION_HANDLER": "rest_framework.views.exception_handler",
    "NUM_PROXIES": int(os.getenv("NUM_PROXIES", "1")),   # For throttling behind proxy
}

# ─── Celery Task Broker ───────────────────────────────────────────────────────
CELERY_BROKER_URL              = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND          = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")
CELERY_TASK_ALWAYS_EAGER       = False    # FIXED: was True — tasks run async now
CELERY_TASK_EAGER_PROPAGATES   = False
CELERY_ACCEPT_CONTENT          = ["json"]
CELERY_TASK_SERIALIZER         = "json"
CELERY_RESULT_SERIALIZER       = "json"
CELERY_TIMEZONE                = "UTC"
CELERY_RESULT_EXPIRES          = 60 * 60 * 24     # 24 hours
CELERY_TASK_SOFT_TIME_LIMIT    = 300              # 5-min soft limit
CELERY_TASK_TIME_LIMIT         = 600             # 10-min hard kill
CELERY_WORKER_CONCURRENCY      = int(os.getenv("CELERY_CONCURRENCY", "4"))
CELERY_WORKER_PREFETCH_MULTIPLIER = 1            # Prevent starvation on long tasks
CELERY_TASK_MAX_RETRIES        = 3
CELERY_TASK_DEFAULT_RETRY_DELAY = 60
CELERY_WORKER_MAX_TASKS_PER_CHILD = 1000        # Recycle worker after 1000 tasks — prevents memory leaks
CELERY_TASK_ACKS_LATE          = True            # Ack after task completes (safer)
CELERY_TASK_REJECT_ON_WORKER_LOST = True        # Requeue if worker crashes mid-task
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True

# ─── Celery Task Routing ──────────────────────────────────────────────────────
CELERY_TASK_ROUTES = {
    # CMS Critical — scheduled publish/unpublish — must not be delayed
    "apps.cms.tasks.execute_scheduled_publish_task":   {"queue": "cms-critical"},
    "apps.cms.tasks.execute_scheduled_unpublish_task": {"queue": "cms-critical"},
    # CMS Default — search index, SEO, notifications
    "apps.cms.tasks.rebuild_search_index_task":        {"queue": "cms-default"},
    "apps.cms.tasks.regenerate_seo_records_task":      {"queue": "cms-default"},
    "apps.cms.tasks.send_cms_notification_task":       {"queue": "cms-default"},
    "apps.cms.tasks.refresh_cms_cache_task":           {"queue": "cms-default"},
    # CMS Bulk — cleanup, analytics — run off-peak
    "apps.cms.tasks.cleanup_old_revisions_task":       {"queue": "cms-bulk"},
    "apps.cms.tasks.cleanup_orphaned_media_task":      {"queue": "cms-bulk"},
    "apps.cms.tasks.refresh_analytics_task":           {"queue": "cms-bulk"},
    "apps.cms.tasks.rebuild_public_sitemap_task":      {"queue": "cms-bulk"},
    "apps.cms.tasks.purge_orphaned_revisions_task":    {"queue": "cms-bulk"},
    "apps.cms.tasks.process_dead_letter_queue_task":   {"queue": "cms-dlq"},
    # Analytics — event ingestion and aggregation
    "apps.analytics.tasks.track_event_task":               {"queue": "analytics"},
    "apps.analytics.tasks.aggregate_daily_metrics_task":   {"queue": "analytics-bulk"},
    "apps.analytics.tasks.run_export_job_task":            {"queue": "analytics-bulk"},
    "apps.analytics.tasks.process_scheduled_reports_task": {"queue": "analytics-bulk"},
}

CELERY_TASK_DEFAULT_QUEUE = "cms-default"

# ─── Celery Beat Schedule ─────────────────────────────────────────────────────
CELERY_BEAT_SCHEDULE = {
    "cms-scheduled-publish": {
        "task": "apps.cms.tasks.execute_scheduled_publish_task",
        "schedule": 60.0,
        "options": {"queue": "cms-critical"},
    },
    "cms-scheduled-unpublish": {
        "task": "apps.cms.tasks.execute_scheduled_unpublish_task",
        "schedule": 300.0,
        "options": {"queue": "cms-critical"},
    },
    "cms-search-index-rebuild": {
        "task": "apps.cms.tasks.rebuild_search_index_task",
        "schedule": 86400.0,
        "options": {"queue": "cms-bulk"},
    },
    "cms-analytics-refresh": {
        "task": "apps.cms.tasks.refresh_analytics_task",
        "schedule": 21600.0,
        "options": {"queue": "cms-bulk"},
    },
    "cms-revision-cleanup": {
        "task": "apps.cms.tasks.cleanup_old_revisions_task",
        "schedule": 86400.0,
        "kwargs": {"days_threshold": 90},
        "options": {"queue": "cms-bulk"},
    },
    "cms-media-cleanup": {
        "task": "apps.cms.tasks.cleanup_orphaned_media_task",
        "schedule": 604800.0,
        "options": {"queue": "cms-bulk"},
    },
    "cms-dlq-processor": {
        "task": "apps.cms.tasks.process_dead_letter_queue_task",
        "schedule": 900.0,
        "options": {"queue": "cms-dlq"},
    },
    # Analytics periodic tasks
    "analytics-daily-aggregation": {
        "task": "apps.analytics.tasks.aggregate_daily_metrics_task",
        "schedule": 86400.0,    # Midnight daily
        "options": {"queue": "analytics-bulk"},
    },
    "analytics-scheduled-reports": {
        "task": "apps.analytics.tasks.process_scheduled_reports_task",
        "schedule": 3600.0,     # Hourly check
        "options": {"queue": "analytics-bulk"},
    },
}

# ─── Structured Logging ───────────────────────────────────────────────────────
class StructuredFormatter(logging.Formatter):
    def format(self, record):
        try:
            from middleware.request_id import get_current_request_id
            record.request_id = get_current_request_id()
        except Exception:
            record.request_id = "-"
        return super().format(record)


LOGS_DIR = os.path.join(BASE_DIR, "logs")
os.makedirs(LOGS_DIR, exist_ok=True)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "structured": {
            "()": "django_project.settings.StructuredFormatter",
            "format": "[%(asctime)s] [%(levelname)s] [RID:%(request_id)s] [%(name)s] %(message)s",
        },
        "json": {
            "format": '{"time": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "message": "%(message)s"}',
        },
    },
    "filters": {
        "require_debug_false": {"()": "django.utils.log.RequireDebugFalse"},
        "require_debug_true":  {"()": "django.utils.log.RequireDebugTrue"},
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "structured",
        },
        "app_file": {
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.path.join(LOGS_DIR, "application.log"),
            "maxBytes": 1024 * 1024 * 10,   # 10MB
            "backupCount": 10,
            "formatter": "structured",
            "encoding": "utf-8",
        },
        "error_file": {
            "level": "ERROR",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.path.join(LOGS_DIR, "errors.log"),
            "maxBytes": 1024 * 1024 * 10,
            "backupCount": 10,
            "formatter": "structured",
            "encoding": "utf-8",
        },
        "security_file": {
            "level": "WARNING",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.path.join(LOGS_DIR, "security.log"),
            "maxBytes": 1024 * 1024 * 5,
            "backupCount": 5,
            "formatter": "structured",
            "encoding": "utf-8",
        },
        "analytics_file": {
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.path.join(LOGS_DIR, "analytics.log"),
            "maxBytes": 1024 * 1024 * 20,   # 20MB — higher volume
            "backupCount": 10,
            "formatter": "structured",
            "encoding": "utf-8",
        },
        "performance_file": {
            "level": "WARNING",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.path.join(LOGS_DIR, "performance.log"),
            "maxBytes": 1024 * 1024 * 5,
            "backupCount": 5,
            "formatter": "structured",
            "encoding": "utf-8",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console", "app_file", "error_file"],
            "level": "INFO",
            "propagate": True,
        },
        "django.request": {
            "handlers": ["error_file"],
            "level": "ERROR",
            "propagate": False,
        },
        "django.db.backends": {
            "handlers": ["performance_file"],
            "level": "WARNING",    # Set to DEBUG locally to see all SQL
            "propagate": False,
        },
        "django.security": {
            "handlers": ["security_file", "error_file"],
            "level": "WARNING",
            "propagate": False,
        },
        "users": {
            "handlers": ["console", "app_file", "security_file"],
            "level": "INFO",
            "propagate": False,
        },
        "lms": {
            "handlers": ["console", "app_file"],
            "level": "INFO",
            "propagate": False,
        },
        "wallets": {
            "handlers": ["console", "app_file", "security_file"],
            "level": "INFO",
            "propagate": False,
        },
        "cms": {
            "handlers": ["console", "app_file"],
            "level": "INFO",
            "propagate": False,
        },
        "seo": {
            "handlers": ["console", "app_file"],
            "level": "INFO",
            "propagate": False,
        },
        "ai": {
            "handlers": ["console", "app_file"],
            "level": "INFO",
            "propagate": False,
        },
        "control_center": {
            "handlers": ["console", "app_file"],
            "level": "INFO",
            "propagate": False,
        },
        "brahmavidya.analytics": {
            "handlers": ["console", "analytics_file"],
            "level": "INFO",
            "propagate": False,
        },
        "brahmavidya.analytics.tasks": {
            "handlers": ["analytics_file", "error_file"],
            "level": "INFO",
            "propagate": False,
        },
        "brahmavidya.performance": {
            "handlers": ["performance_file"],
            "level": "WARNING",
            "propagate": False,
        },
    },
}

# ─── Email ────────────────────────────────────────────────────────────────────
EMAIL_BACKEND = os.getenv("EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend")
EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "")
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", "noreply@brahmavidya.edu")

# ─── Health Check & Monitoring ───────────────────────────────────────────────
# These settings enable the /api/health endpoint
HEALTH_CHECK_DB = True
HEALTH_CHECK_CACHE = True
HEALTH_CHECK_STORAGE = True

# ─── CORS ────────────────────────────────────────────────────────────────────
CORS_ALLOWED_ORIGINS = os.getenv(
    "CORS_ALLOWED_ORIGINS",
    "http://localhost:5173,http://localhost:3000"
).split(",")
CORS_ALLOW_CREDENTIALS = True
