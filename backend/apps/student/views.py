"""
Student Dashboard Views — BrahmaVidya Galaxy
Sprint 20: ViewSets and API views for all Student Portal models.
"""

from __future__ import annotations

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination

from permissions.roles import IsStudent
from apps.student.permissions import IsStudentOwner, IsEnrolledInCourse

from apps.student.models import (
    LearningHistory, ContinueLearning, Bookmark,
    StudentNote, StudyGoal, StudySession,
    StudyCalendarEvent, DailyProgress, WeeklyProgress,
    MonthlyProgress, LearningStreak, Achievement,
    StudentAchievement, StudentPreference, RecentlyViewedLesson,
    LearningReminder
)

from apps.student.serializers import (
    LearningHistorySerializer, ContinueLearningSerializer, BookmarkSerializer,
    StudentNoteSerializer, StudyGoalSerializer, StudySessionSerializer,
    StudyCalendarEventSerializer, DailyProgressSerializer, WeeklyProgressSerializer,
    MonthlyProgressSerializer, LearningStreakSerializer, AchievementSerializer,
    StudentAchievementSerializer, StudentPreferenceSerializer, RecentlyViewedLessonSerializer,
    LearningReminderSerializer
)

from apps.student.filters import (
    BookmarkFilter, StudentNoteFilter, StudyGoalFilter,
    StudySessionFilter, StudyCalendarEventFilter, LearningReminderFilter
)


class StudentDashboardPagination(PageNumberPagination):
    """
    Standard pagination for student dashboard resources.
    """
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


class BaseStudentViewSet(viewsets.ModelViewSet):
    """
    Abstract Base ViewSet enforcing tenancy isolation so that students
    can only access and mutate their own records.
    """
    permission_classes = [IsStudent, IsStudentOwner]
    pagination_class = StudentDashboardPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]

    def get_queryset(self):
        user = self.request.user
        if not user or not user.is_authenticated:
            return self.queryset.none()
        if user.is_superuser or (hasattr(user, "role") and user.role and user.role.name in ["SUPERADMIN", "ADMIN"]):
            return self.queryset.all()
        return self.queryset.filter(student=user)


class LearningHistoryViewSet(BaseStudentViewSet):
    """
    ViewSet for tracking student course/lesson access history.
    """
    queryset = LearningHistory.objects.select_related("student", "node", "enrollment").all()
    serializer_class = LearningHistorySerializer
    permission_classes = [IsStudent, IsStudentOwner, IsEnrolledInCourse]
    ordering_fields = ["accessed_at", "created_at"]
    ordering = ["-accessed_at"]


class ContinueLearningViewSet(BaseStudentViewSet):
    """
    ViewSet for resuming learning progress on enrolled courses.
    """
    queryset = ContinueLearning.objects.select_related("student", "enrollment__course", "last_node").all()
    serializer_class = ContinueLearningSerializer
    ordering_fields = ["last_accessed_at", "created_at"]
    ordering = ["-last_accessed_at"]


class BookmarkViewSet(BaseStudentViewSet):
    """
    ViewSet for resource bookmarking.
    """
    queryset = Bookmark.objects.select_related("student").all()
    serializer_class = BookmarkSerializer
    filterset_class = BookmarkFilter
    search_fields = ["title", "source_name", "note"]
    ordering_fields = ["created_at"]
    ordering = ["-created_at"]

    @action(detail=False, methods=["POST"])
    def toggle(self, request):
        """
        Atomically toggles a resource bookmark (creates if missing, deletes if exists).
        """
        student = request.user
        content_type = request.data.get("content_type")
        content_id = request.data.get("content_id")
        title = request.data.get("title")
        source_name = request.data.get("source_name")
        url_path = request.data.get("url_path")
        note = request.data.get("note")

        if not content_type or not content_id or not title:
            return Response(
                {"error": "content_type, content_id, and title are required fields."},
                status=status.HTTP_400_BAD_REQUEST
            )

        from apps.student.services import BookmarkService
        bookmark, created = BookmarkService.toggle_bookmark(
            student=student,
            content_type=content_type,
            content_id=content_id,
            title=title,
            source_name=source_name,
            url_path=url_path,
            note=note
        )

        if bookmark:
            serializer = self.get_serializer(bookmark)
            return Response({"created": True, "bookmark": serializer.data}, status=status.HTTP_201_CREATED)
        return Response({"created": False, "message": "Bookmark removed"}, status=status.HTTP_200_OK)


class StudentNoteViewSet(BaseStudentViewSet):
    """
    ViewSet for student rich text Markdown learning notes.
    """
    queryset = StudentNote.objects.select_related("student", "node").all()
    serializer_class = StudentNoteSerializer
    permission_classes = [IsStudent, IsStudentOwner, IsEnrolledInCourse]
    filterset_class = StudentNoteFilter
    search_fields = ["title", "content"]
    ordering_fields = ["created_at", "updated_at", "is_pinned"]
    ordering = ["-is_pinned", "-updated_at"]

    @action(detail=True, methods=["POST"])
    def pin(self, request, pk=None):
        """
        Toggles the pin status on a student note.
        """
        note = self.get_object()
        note.is_pinned = not note.is_pinned
        note.save()
        return Response({"is_pinned": note.is_pinned}, status=status.HTTP_200_OK)


class StudyGoalViewSet(BaseStudentViewSet):
    """
    ViewSet for setting and tracking learning milestones.
    """
    queryset = StudyGoal.objects.select_related("student", "enrollment__course").all()
    serializer_class = StudyGoalSerializer
    filterset_class = StudyGoalFilter
    search_fields = ["title", "description"]
    ordering_fields = ["target_date", "created_at"]
    ordering = ["target_date"]

    @action(detail=True, methods=["POST"])
    def update_progress(self, request, pk=None):
        """
        Updates study goal progress percentage and evaluates completion states.
        """
        goal = self.get_object()
        progress_percentage = request.data.get("progress_percentage")
        if progress_percentage is None:
            return Response({"error": "progress_percentage is required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            progress_percentage = float(progress_percentage)
        except ValueError:
            return Response({"error": "progress_percentage must be a valid number"}, status=status.HTTP_400_BAD_REQUEST)

        from apps.student.services import GoalService
        goal = GoalService.update_goal_progress(
            student=request.user,
            goal_id=goal.id,
            progress_percentage=progress_percentage,
            status=request.data.get("status")
        )
        serializer = self.get_serializer(goal)
        return Response(serializer.data, status=status.HTTP_200_OK)


class StudySessionViewSet(BaseStudentViewSet):
    """
    ViewSet for starting and stopping timed study sessions.
    """
    queryset = StudySession.objects.select_related("student", "node").all()
    serializer_class = StudySessionSerializer
    filterset_class = StudySessionFilter
    ordering_fields = ["started_at", "ended_at", "duration_seconds"]
    ordering = ["-started_at"]

    @action(detail=False, methods=["POST"])
    def start_session(self, request):
        """
        Atomically shuts down any lingering session and starts a new session.
        """
        node_id = request.data.get("node_id") or request.data.get("node")
        from apps.student.services import SessionService
        session = SessionService.start_study_session(student=request.user, node_id=node_id)
        serializer = self.get_serializer(session)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["POST"])
    def end_session(self, request, pk=None):
        """
        Concludes a timed session and awards gamification XP.
        """
        session = self.get_object()
        from apps.student.services import SessionService
        session = SessionService.end_study_session(student=request.user, session_id=session.id)
        serializer = self.get_serializer(session)
        return Response(serializer.data, status=status.HTTP_200_OK)


class StudyCalendarEventViewSet(BaseStudentViewSet):
    """
    ViewSet for student calendar scheduling.
    """
    queryset = StudyCalendarEvent.objects.select_related("student", "node").all()
    serializer_class = StudyCalendarEventSerializer
    filterset_class = StudyCalendarEventFilter
    search_fields = ["title", "description"]
    ordering_fields = ["starts_at", "ends_at"]
    ordering = ["starts_at"]


class DailyProgressViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ReadOnly ViewSet for inspecting daily learning progress.
    """
    queryset = DailyProgress.objects.select_related("student").all()
    serializer_class = DailyProgressSerializer
    permission_classes = [IsStudent, IsStudentOwner]
    pagination_class = StudentDashboardPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    ordering_fields = ["date"]
    ordering = ["-date"]

    def get_queryset(self):
        user = self.request.user
        if not user or not user.is_authenticated:
            return self.queryset.none()
        if user.is_superuser or (hasattr(user, "role") and user.role and user.role.name in ["SUPERADMIN", "ADMIN"]):
            return self.queryset.all()
        return self.queryset.filter(student=user)


class WeeklyProgressViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ReadOnly ViewSet for inspecting weekly learning aggregates.
    """
    queryset = WeeklyProgress.objects.select_related("student").all()
    serializer_class = WeeklyProgressSerializer
    permission_classes = [IsStudent, IsStudentOwner]
    pagination_class = StudentDashboardPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    ordering_fields = ["week_start"]
    ordering = ["-week_start"]

    def get_queryset(self):
        user = self.request.user
        if not user or not user.is_authenticated:
            return self.queryset.none()
        if user.is_superuser or (hasattr(user, "role") and user.role and user.role.name in ["SUPERADMIN", "ADMIN"]):
            return self.queryset.all()
        return self.queryset.filter(student=user)


class MonthlyProgressViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ReadOnly ViewSet for inspecting monthly learning aggregates.
    """
    queryset = MonthlyProgress.objects.select_related("student").all()
    serializer_class = MonthlyProgressSerializer
    permission_classes = [IsStudent, IsStudentOwner]
    pagination_class = StudentDashboardPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    ordering_fields = ["year", "month"]
    ordering = ["-year", "-month"]

    def get_queryset(self):
        user = self.request.user
        if not user or not user.is_authenticated:
            return self.queryset.none()
        if user.is_superuser or (hasattr(user, "role") and user.role and user.role.name in ["SUPERADMIN", "ADMIN"]):
            return self.queryset.all()
        return self.queryset.filter(student=user)


class LearningStreakViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ReadOnly ViewSet for reading lifetime gamified progress, points (XP), and active streaks.
    """
    queryset = LearningStreak.objects.select_related("student").all()
    serializer_class = LearningStreakSerializer
    permission_classes = [IsStudent, IsStudentOwner]
    pagination_class = StudentDashboardPagination
    filter_backends = [DjangoFilterBackend]

    def get_queryset(self):
        user = self.request.user
        if not user or not user.is_authenticated:
            return self.queryset.none()
        if user.is_superuser or (hasattr(user, "role") and user.role and user.role.name in ["SUPERADMIN", "ADMIN"]):
            return self.queryset.all()
        return self.queryset.filter(student=user)


class AchievementViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ReadOnly ViewSet for browsing gamification metadata templates.
    """
    queryset = Achievement.objects.all()
    serializer_class = AchievementSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StudentDashboardPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["title", "description", "category"]
    ordering_fields = ["code", "xp_reward"]
    ordering = ["code"]


class StudentAchievementViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ReadOnly ViewSet for auditing individual student achievement records.
    """
    queryset = StudentAchievement.objects.select_related("student", "achievement").all()
    serializer_class = StudentAchievementSerializer
    permission_classes = [IsStudent, IsStudentOwner]
    pagination_class = StudentDashboardPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    ordering_fields = ["unlocked_at", "created_at"]
    ordering = ["-unlocked_at"]

    def get_queryset(self):
        user = self.request.user
        if not user or not user.is_authenticated:
            return self.queryset.none()
        if user.is_superuser or (hasattr(user, "role") and user.role and user.role.name in ["SUPERADMIN", "ADMIN"]):
            return self.queryset.all()
        return self.queryset.filter(student=user)


class StudentPreferenceViewSet(BaseStudentViewSet):
    """
    ViewSet for managing individual layout settings and daily targets.
    """
    queryset = StudentPreference.objects.select_related("student").all()
    serializer_class = StudentPreferenceSerializer


class RecentlyViewedLessonViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ReadOnly ViewSet displaying recently viewed course lesson buffers.
    """
    queryset = RecentlyViewedLesson.objects.select_related("student", "node").all()
    serializer_class = RecentlyViewedLessonSerializer
    permission_classes = [IsStudent, IsStudentOwner]
    pagination_class = StudentDashboardPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    ordering_fields = ["viewed_at"]
    ordering = ["-viewed_at"]

    def get_queryset(self):
        user = self.request.user
        if not user or not user.is_authenticated:
            return self.queryset.none()
        if user.is_superuser or (hasattr(user, "role") and user.role and user.role.name in ["SUPERADMIN", "ADMIN"]):
            return self.queryset.all()
        return self.queryset.filter(student=user)


class LearningReminderViewSet(BaseStudentViewSet):
    """
    ViewSet for managing study calendar notification alarms.
    """
    queryset = LearningReminder.objects.select_related("student", "node").all()
    serializer_class = LearningReminderSerializer
    filterset_class = LearningReminderFilter
    search_fields = ["title", "message"]
    ordering_fields = ["remind_at", "created_at"]
    ordering = ["remind_at"]


class StudentDashboardSummaryView(APIView):
    """
    API View supplying nested aggregated summaries of student streaks,
    daily/weekly statistics, bookmarks, and active learning positions in a single call.
    """
    permission_classes = [IsStudent]

    def get(self, request, *args, **kwargs):
        from apps.student.selectors import DashboardSelector
        context = DashboardSelector.get_student_dashboard_context(request.user)
        return Response(context, status=status.HTTP_200_OK)
