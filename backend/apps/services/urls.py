from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.services.views import (
    ProfessionalServiceViewSet, ServiceLeadViewSet, ServiceProjectViewSet, ProjectMilestoneViewSet
)

router = DefaultRouter()
router.register("catalog", ProfessionalServiceViewSet, basename="service-catalog")
router.register("leads", ServiceLeadViewSet, basename="service-lead")
router.register("projects", ServiceProjectViewSet, basename="service-project")
router.register("milestones", ProjectMilestoneViewSet, basename="project-milestone")

app_name = "services"

urlpatterns = [
    path("", include(router.urls)),
]
