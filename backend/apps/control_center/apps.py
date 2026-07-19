from django.apps import AppConfig


class ControlCenterConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.control_center"
    verbose_name = "BrahmaVidya Control Center"

    def ready(self):
        import apps.control_center.integration_hub
