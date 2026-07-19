from django.apps import AppConfig

class SeoConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.seo"

    def ready(self):
        try:
            import apps.seo.signals
        except ImportError:
            pass
