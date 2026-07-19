"""
Student Dashboard Endpoints Router - BrahmaVidya Galaxy
Sprint 20: Maps routing paths to Student Dashboard views.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.student.views import (
    LearningHistoryViewSet, ContinueLearningViewSet, BookmarkViewSet,
    StudentNoteViewSet, StudyGoalViewSet, StudySessionViewSet,
    StudyCalendarEventViewSet, DailyProgressViewSet, WeeklyProgressViewSet,
    MonthlyProgressViewSet, LearningStreakViewSet, AchievementViewSet,
    StudentAchievementViewSet, StudentPreferenceViewSet, RecentlyViewedLessonViewSet,
    LearningReminderViewSet, StudentDashboardSummaryView
)

router = DefaultRouter()
router.register("history", LearningHistoryViewSet, basename="history")
router.register("continue-learning", ContinueLearningViewSet, basename="continue-learning")
router.register("bookmarks", BookmarkViewSet, basename="bookmark")
router.register("notes", StudentNoteViewSet, basename="note")
router.register("goals", StudyGoalViewSet, basename="goal")
router.register("sessions", StudySessionViewSet, basename="session")
router.register("calendar-events", StudyCalendarEventViewSet, basename="calendarevent")
router.register("progress/daily", DailyProgressViewSet, basename="dailyprogress")
router.register("progress/weekly", WeeklyProgressViewSet, basename="weeklyprogress")
router.register("progress/monthly", MonthlyProgressViewSet, basename="monthlyprogress")
router.register("streaks", LearningStreakViewSet, basename="learningstreak")
router.register("achievements", AchievementViewSet, basename="achievement")
router.register("student-achievements", StudentAchievementViewSet, basename="studentachievement")
router.register("preferences", StudentPreferenceViewSet, basename="studentpreference")
router.register("recently-viewed", RecentlyViewedLessonViewSet, basename="recentlyviewed")
router.register("reminders", LearningReminderViewSet, basename="reminder")

app_name = "student"

urlpatterns = [
    path("dashboard/summary/", StudentDashboardSummaryView.as_view(), name="dashboard-summary"),
    path("", include(router.urls)),
]
