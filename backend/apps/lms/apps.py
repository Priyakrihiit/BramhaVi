from django.apps import AppConfig

class LmsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.lms"

    def ready(self):
        try:
            import apps.lms.signals
        except ImportError:
            pass
