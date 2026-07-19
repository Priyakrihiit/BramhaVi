from django.apps import AppConfig


class StudentConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.student"

    def ready(self):
        try:
            import apps.student.signals  # noqa: F401
        except ImportError:
            pass
