"""
Celery Task Configuration - BrahmaVidya Galaxy
Purpose: Initializes Celery client mappings, reading settings directly from Django context.
"""

import os
from celery import Celery

# Set default Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_project.settings")

app = Celery("brahmavidya_galaxy")

# Retrieve broker parameters prefixed with 'CELERY_' from django config
app.config_from_object("django.conf:settings", namespace="CELERY")

# Auto-discover task routines inside registered apps (e.g., tasks.py)
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
