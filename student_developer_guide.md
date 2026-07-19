# Backend Developer Integration Guide: BrahmaVidya Portal

**Audience**: Backend Engineers, Platform Developers, and Integrators  

---

## 1. Local Development Sandbox Setup

### 1.1 Prerequisites
*   Python 3.11+
*   Node.js 18+
*   Redis Server (running locally, or mock settings enabled)

### 1.2 Initial Database Setup
To initialize your local SQLite development database, run the following commands:
```bash
# Touch initial migration markers inside the apps
for dir in backend/apps/*/migrations; do touch "$dir/__init__.py"; done

# Generate database migrations for the Student app
python3 backend/manage.py makemigrations student

# Run all migrations
python3 backend/manage.py migrate
```

---

## 2. Working with the Student Signals System
The Student app relies on Django Signals to decouple core events. To add new custom hooks:
1.  Open `/backend/apps/student/signals.py`.
2.  Register your handler using the standard Django receiver decorators:
```python
from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.student.models import Bookmark

@receiver(post_save, sender=Bookmark)
def on_custom_bookmark_event(sender, instance, created, **kwargs):
    if created:
        # Implement your custom integration logic here
        pass
```
3.  Ensure your signal is registered inside `/backend/apps/student/apps.py` within the `ready()` execution override:
```python
class StudentConfig(AppConfig):
    name = "apps.student"

    def ready(self):
        import apps.student.signals  # noqa
```

---

## 3. Verifying Your Changes Locally
We have created a custom verification script `verify_sprint20.py` to help you verify your changes. You can run it locally to verify caching, database integrations, and signal responses in seconds:
```bash
python3 verify_sprint20.py
```
Make sure all dynamic integration checks pass successfully before submitting code reviews.
