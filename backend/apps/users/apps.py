from django.apps import AppConfig

class UsersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.users"

    def ready(self):
        # Establish event signal connections when Django is fully initialized
        try:
            import apps.users.signals
        except ImportError:
            pass
