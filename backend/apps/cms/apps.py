from django.apps import AppConfig

class CmsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.cms"

    def ready(self):
        try:
            import apps.cms.signals
        except ImportError:
            pass
