"""
Teacher Portal Endpoints Router — BrahmaVidya Galaxy
Sprint 21: Register and namespace all Teacher ViewSets and Dashboard views.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.teacher.views import (
    TeacherDashboardSummaryView, TeacherProfileViewSet,
    TeacherNotificationPreferenceViewSet, TeacherWalletViewSet,
    TeacherEarningViewSet, TeachingSessionViewSet,
    TeachingCalendarViewSet, TeacherScheduleViewSet,
    CourseViewSet, LessonViewSet, BatchViewSet,
    AssignmentViewSet, AssignmentSubmissionViewSet,
    QuestionCategoryViewSet, QuestionDifficultyViewSet,
    AttendanceViewSet, TeacherAnalyticsViewSet,
    TeacherCertificateViewSet, TeacherAchievementViewSet,
    TeachingGoalViewSet, TeacherAnnouncementViewSet,
    TeacherActivityLogViewSet
)

router = DefaultRouter()
router.register("profiles", TeacherProfileViewSet, basename="profile")
router.register("preferences", TeacherNotificationPreferenceViewSet, basename="preference")
router.register("wallet", TeacherWalletViewSet, basename="wallet")
router.register("earnings", TeacherEarningViewSet, basename="earning")
router.register("sessions", TeachingSessionViewSet, basename="session")
router.register("calendar", TeachingCalendarViewSet, basename="calendar")
router.register("schedule", TeacherScheduleViewSet, basename="schedule")
router.register("courses", CourseViewSet, basename="course")
router.register("lessons", LessonViewSet, basename="lesson")
router.register("batches", BatchViewSet, basename="batch")
router.register("assignments", AssignmentViewSet, basename="assignment")
router.register("submissions", AssignmentSubmissionViewSet, basename="submission")
router.register("quiz/categories", QuestionCategoryViewSet, basename="quiz-category")
router.register("quiz/difficulties", QuestionDifficultyViewSet, basename="quiz-difficulty")
router.register("attendance", AttendanceViewSet, basename="attendance")
router.register("analytics", TeacherAnalyticsViewSet, basename="analytics")
router.register("certificates", TeacherCertificateViewSet, basename="certificate")
router.register("achievements", TeacherAchievementViewSet, basename="achievement")
router.register("goals", TeachingGoalViewSet, basename="goal")
router.register("announcements", TeacherAnnouncementViewSet, basename="announcement")
router.register("activity-logs", TeacherActivityLogViewSet, basename="activity-log")

app_name = "teacher"

urlpatterns = [
    path("dashboard/summary/", TeacherDashboardSummaryView.as_view(), name="dashboard-summary"),
    path("", include(router.urls)),
]
