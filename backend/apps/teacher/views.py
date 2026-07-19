"""
Teacher Portal Views — BrahmaVidya Galaxy
Sprint 21: Comprehensive viewsets and API endpoints for all Teacher Portal operations.
"""

from __future__ import annotations

import logging
from uuid import UUID
from decimal import Decimal
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

from rest_framework import viewsets, status, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination

# Imports from apps.teacher
from apps.teacher.models import (
    TeacherProfile, TeacherAnalytics, TeachingSession, Batch, Attendance,
    QuestionCategory, QuestionDifficulty, TeachingCalendar, TeacherAnnouncement,
    TeacherSchedule, TeachingGoal, TeacherEarning, TeacherWallet,
    TeacherCertificate, TeacherAchievement, TeacherNotificationPreference,
    TeacherActivityLog
)
from apps.teacher.serializers import (
    TeacherProfileSerializer, TeacherProfileReadSerializer, TeacherProfileWriteSerializer,
    TeacherWalletSerializer, TeacherEarningSerializer, TeachingSessionSerializer,
    TeachingCalendarSerializer, TeacherScheduleSerializer, BatchSerializer,
    TeacherAnnouncementSerializer, CourseStructureLessonSerializer, AssignmentSerializer,
    AssignmentSubmissionSerializer, QuestionCategorySerializer, QuestionDifficultySerializer,
    AttendanceSerializer, TeacherAnalyticsSerializer, CoursePerformanceReportSerializer,
    TeacherCertificateSerializer, TeacherAchievementSerializer, TeachingGoalSerializer,
    TeacherActivityLogSerializer, TeacherNotificationPreferenceSerializer,
    TeacherDashboardSummarySerializer
)
from apps.teacher.permissions import (
    IsTeacher, IsTeacherOwner, IsTeacherOrAdmin, TeacherDashboardPermission,
    CoursePermission, AssignmentPermission
)
from apps.teacher.selectors import (
    TeacherDashboardSelector, TeacherAnalyticsSelector, TeacherEarningSelector
)
from apps.teacher.services import (
    TeacherService, DashboardService, CourseService, LessonService,
    AssignmentService, QuizService, AttendanceService, AnalyticsService,
    CertificateService, WalletService
)
from apps.teacher.filters import (
    BatchFilter, AttendanceFilter, TeacherAnnouncementFilter, TeacherScheduleFilter,
    TeachingGoalFilter, TeacherEarningFilter, TeacherCertificateFilter, TeacherActivityLogFilter
)

# Imports from other apps
from apps.lms.models import CourseStructure, Assignment, AssignmentSubmission, LiveClass

logger = logging.getLogger("teacher.views")
User = get_user_model()


class TeacherPagination(PageNumberPagination):
    """Standard paginator for Teacher Portal index resources."""
    page_size = 15
    page_size_query_param = "page_size"
    max_page_size = 100


# ─── BASE VIEWSETS ────────────────────────────────────────────────────────────

class BaseTeacherViewSet(viewsets.ModelViewSet):
    """
    Standard base viewset enforcing authentications, tenancy isolation (based on 'teacher' field),
    pagination, and standard filter backends.
    """
    permission_classes = [IsTeacher, IsTeacherOwner]
    pagination_class = TeacherPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]

    def get_queryset(self):
        user = self.request.user
        if not user or not user.is_authenticated:
            return self.queryset.none()
        if user.is_superuser or (hasattr(user, "role") and user.role and user.role.name in ["SUPERADMIN", "ADMIN"]):
            return self.queryset.all()
        return self.queryset.filter(teacher=user)

    def perform_create(self, serializer):
        serializer.save(teacher=self.request.user)


# ─── DASHBOARD & SUMMARY ──────────────────────────────────────────────────────

class TeacherDashboardSummaryView(APIView):
    """
    API View supplying consolidated dashboard summaries of teacher statistics and agenda events.
    """
    permission_classes = [IsTeacher, TeacherDashboardPermission]

    def get(self, request, *args, **kwargs):
        summary = TeacherDashboardSelector.get_dashboard_summary(request.user)
        serializer = TeacherDashboardSummarySerializer(data=summary)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# ─── PROFILE & PREFERENCES ────────────────────────────────────────────────────

class TeacherProfileViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing, updating, and certifying Teacher Profiles.
    """
    queryset = TeacherProfile.objects.select_related("user").all()
    permission_classes = [IsTeacher, IsTeacherOwner]
    pagination_class = TeacherPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["bio", "user__email"]

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return TeacherProfileWriteSerializer
        return TeacherProfileReadSerializer

    def get_queryset(self):
        user = self.request.user
        if not user or not user.is_authenticated:
            return self.queryset.none()
        if user.is_superuser or (hasattr(user, "role") and user.role and user.role.name in ["SUPERADMIN", "ADMIN"]):
            return self.queryset.all()
        return self.queryset.filter(user=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=["get", "patch", "put"], url_path="me")
    def me(self, request) -> Response:
        """Endpoint to query or modify the logged-in teacher's profile."""
        profile, _ = TeacherProfile.objects.get_or_create(user=request.user)
        if request.method == "GET":
            serializer = TeacherProfileReadSerializer(profile)
            return Response(serializer.data)
        
        serializer = TeacherProfileWriteSerializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        # Update via Service
        updated_profile = TeacherService.update_profile(
            user=request.user,
            bio=serializer.validated_data.get("bio"),
            qualifications=serializer.validated_data.get("qualifications"),
            specialties=serializer.validated_data.get("specialties"),
            experience_years=serializer.validated_data.get("experience_years")
        )
        read_serializer = TeacherProfileReadSerializer(updated_profile)
        return Response(read_serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="verify", permission_classes=[permissions.IsAdminUser])
    def verify(self, request, pk=None) -> Response:
        """Administrative action to certify instructor credentials."""
        profile = self.get_object()
        updated = TeacherService.verify_teacher(teacher_user=profile.user, admin_user=request.user)
        return Response(TeacherProfileReadSerializer(updated).data, status=status.HTTP_200_OK)


class TeacherNotificationPreferenceViewSet(viewsets.ModelViewSet):
    """
    ViewSet managing customized channel alert triggers.
    """
    queryset = TeacherNotificationPreference.objects.select_related("teacher").all()
    serializer_class = TeacherNotificationPreferenceSerializer
    permission_classes = [IsTeacher, IsTeacherOwner]
    pagination_class = TeacherPagination

    def get_queryset(self):
        user = self.request.user
        if not user or not user.is_authenticated:
            return self.queryset.none()
        return self.queryset.filter(teacher=user)

    def perform_create(self, serializer):
        serializer.save(teacher=self.request.user)


# ─── WALLET & PAYOUT LEDGER ───────────────────────────────────────────────────

class TeacherWalletViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ReadOnly ViewSet serving balances and offering withdraw and configure configurations.
    """
    queryset = TeacherWallet.objects.select_related("teacher").all()
    serializer_class = TeacherWalletSerializer
    permission_classes = [IsTeacher, IsTeacherOwner]

    def get_queryset(self):
        user = self.request.user
        if not user or not user.is_authenticated:
            return self.queryset.none()
        return self.queryset.filter(teacher=user)

    @action(detail=False, methods=["get"])
    def summary(self, request) -> Response:
        """Returns consolidated financial reports and balances."""
        data = TeacherEarningSelector.get_earnings_summary(request.user)
        return Response(data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"], url_path="configure")
    def configure(self, request) -> Response:
        """Configures connected Stripe/PayPal destination accounts."""
        serializer = TeacherWalletSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        
        payout_method = serializer.validated_data.get("payout_method")
        payout_address = serializer.validated_data.get("payout_address")
        
        if not payout_method or not payout_address:
            return Response(
                {"error": "Both 'payout_method' and 'payout_address' fields are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        wallet = WalletService.configure_payout_details(
            teacher=request.user,
            payout_method=payout_method,
            payout_address=payout_address
        )
        return Response(TeacherWalletSerializer(wallet).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"], url_path="withdraw")
    def withdraw(self, request) -> Response:
        """Submits a payout withdrawal claim against balance pools."""
        amount_str = request.data.get("amount")
        if not amount_str:
            return Response({"error": "The withdrawal 'amount' is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            amount = Decimal(str(amount_str))
        except Exception:
            return Response({"error": "Invalid numerical format for withdrawal amount."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            new_balance = WalletService.request_withdrawal(teacher=request.user, withdraw_amount=amount)
            return Response({
                "status": "success",
                "withdrawn_amount": float(amount),
                "remaining_balance": float(new_balance),
                "message": "Payout requested successfully."
            }, status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class TeacherEarningViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ReadOnly ViewSet allowing teachers to query historical itemized earnings transactions.
    """
    queryset = TeacherEarning.objects.select_related("teacher", "course").all()
    serializer_class = TeacherEarningSerializer
    permission_classes = [IsTeacher, IsTeacherOwner]
    pagination_class = TeacherPagination
    filterset_class = TeacherEarningFilter
    ordering_fields = ["recorded_at", "amount", "points"]
    ordering = ["-recorded_at"]

    def get_queryset(self):
        user = self.request.user
        if not user or not user.is_authenticated:
            return self.queryset.none()
        return self.queryset.filter(teacher=user)


# ─── SCHEDULE & CALENDAR DYNAMICS ─────────────────────────────────────────────

class TeachingSessionViewSet(BaseTeacherViewSet):
    """
    ViewSet managing individual scheduled mentoring, Office Hours, or Tutoring events.
    """
    queryset = TeachingSession.objects.select_related("teacher").all()
    serializer_class = TeachingSessionSerializer
    ordering_fields = ["start_time", "created_at"]
    ordering = ["start_time"]


class TeachingCalendarViewSet(BaseTeacherViewSet):
    """
    ViewSet curating general weekly recurring operational availability slots.
    """
    queryset = TeachingCalendar.objects.select_related("teacher").all()
    serializer_class = TeachingCalendarSerializer
    ordering_fields = ["day_of_week", "start_time"]
    ordering = ["day_of_week", "start_time"]


class TeacherScheduleViewSet(BaseTeacherViewSet):
    """
    ViewSet tracking Consolidated Instructor tasks and schedule activities.
    """
    queryset = TeacherSchedule.objects.select_related("teacher").all()
    serializer_class = TeacherScheduleSerializer
    filterset_class = TeacherScheduleFilter
    ordering_fields = ["start_time", "end_time"]
    ordering = ["start_time"]

    @action(detail=True, methods=["post"], url_path="transition")
    def transition(self, request, pk=None) -> Response:
        """Transitions status of scheduled events."""
        status_val = request.data.get("status")
        if not status_val:
            return Response({"error": "The 'status' parameter is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        item = DashboardService.update_schedule_status(
            teacher=request.user,
            item_id=pk,
            status=status_val
        )
        return Response(TeacherScheduleSerializer(item).data, status=status.HTTP_200_OK)


# ─── COURSE & LESSON APIS ─────────────────────────────────────────────────────

class CourseViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ReadOnly ViewSet allowing instructors to list courses they are assigned to teach.
    """
    queryset = CourseStructure.objects.filter(node_type="COURSE").prefetch_related("teacher_classes")
    serializer_class = CourseStructureLessonSerializer  # Uses lesson/course node representation
    permission_classes = [IsTeacher, CoursePermission]
    pagination_class = TeacherPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["title", "description"]

    def get_queryset(self):
        user = self.request.user
        if not user or not user.is_authenticated:
            return self.queryset.none()
        if user.is_superuser or (hasattr(user, "role") and user.role and user.role.name in ["SUPERADMIN", "ADMIN"]):
            return self.queryset.all()
        return self.queryset.filter(teacher_classes__teacher=user, teacher_classes__is_active=True)


class LessonViewSet(viewsets.ModelViewSet):
    """
    ViewSet allowing teachers to manage syllabus chapters and create lessons under assigned courses.
    """
    queryset = CourseStructure.objects.filter(node_type="LESSON").select_related("parent__parent")
    serializer_class = CourseStructureLessonSerializer
    permission_classes = [IsTeacher, CoursePermission]
    pagination_class = TeacherPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["title", "description"]
    ordering_fields = ["display_order", "created_at"]
    ordering = ["display_order"]

    def get_queryset(self):
        user = self.request.user
        if not user or not user.is_authenticated:
            return self.queryset.none()
        if user.is_superuser or (hasattr(user, "role") and user.role and user.role.name in ["SUPERADMIN", "ADMIN"]):
            return self.queryset.all()
        # Lesson -> Parent Chapter -> Parent Course
        return self.queryset.filter(parent__parent__teacher_classes__teacher=user, parent__parent__teacher_classes__is_active=True)

    def create(self, request, *args, **kwargs) -> Response:
        """Creates a syllabus Lesson node via LessonService."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        parent_id = request.data.get("parent")
        title = serializer.validated_data.get("title")
        description = serializer.validated_data.get("description")
        
        metadata = request.data.get("metadata", {})
        drip_delay = metadata.get("drip_delay_days", 0) if isinstance(metadata, dict) else 0
        video_url = metadata.get("video_url") if isinstance(metadata, dict) else None

        if not parent_id:
            return Response({"error": "The parent Chapter ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            lesson = LessonService.create_lesson_node(
                teacher=request.user,
                parent_chapter_id=parent_id,
                title=title,
                description=description,
                drip_delay_days=drip_delay,
                video_url=video_url
            )
            return Response(self.get_serializer(lesson).data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class BatchViewSet(viewsets.ModelViewSet):
    """
    ViewSet managing student Cohorts/Batches.
    """
    queryset = Batch.objects.prefetch_related("instructors").select_related("course").all()
    serializer_class = BatchSerializer
    permission_classes = [IsTeacher, IsTeacherOwner]
    pagination_class = TeacherPagination
    filterset_class = BatchFilter
    ordering_fields = ["start_date", "created_at"]
    ordering = ["-start_date"]

    def get_queryset(self):
        user = self.request.user
        if not user or not user.is_authenticated:
            return self.queryset.none()
        if user.is_superuser or (hasattr(user, "role") and user.role and user.role.name in ["SUPERADMIN", "ADMIN"]):
            return self.queryset.all()
        return self.queryset.filter(instructors=user)

    def create(self, request, *args, **kwargs) -> Response:
        """Creates a Batch Cohort atomically."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        course_id = request.data.get("course")
        name = serializer.validated_data.get("name")
        start_date = serializer.validated_data.get("start_date")
        end_date = serializer.validated_data.get("end_date")
        instructor_ids = request.data.get("instructors", [request.user.id])

        if not course_id:
            return Response({"error": "The course ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        instructors = list(User.objects.filter(id__in=instructor_ids))

        try:
            batch = CourseService.create_cohort_batch(
                course_id=course_id,
                name=name,
                start_date=start_date,
                end_date=end_date,
                instructors=instructors
            )
            return Response(self.get_serializer(batch).data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# ─── ASSIGNMENTS & EVALUATIONS ────────────────────────────────────────────────

class AssignmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet curating lesson Assignment assessment briefs.
    """
    queryset = Assignment.objects.select_related("lesson").all()
    serializer_class = AssignmentSerializer
    permission_classes = [IsTeacher, AssignmentPermission]
    pagination_class = TeacherPagination
    ordering_fields = ["max_points", "created_at"]
    ordering = ["-created_at"]

    def get_queryset(self):
        user = self.request.user
        if not user or not user.is_authenticated:
            return self.queryset.none()
        if user.is_superuser or (hasattr(user, "role") and user.role and user.role.name in ["SUPERADMIN", "ADMIN"]):
            return self.queryset.all()
        return self.queryset.filter(lesson__parent__parent__teacher_classes__teacher=user, lesson__parent__parent__teacher_classes__is_active=True)


class AssignmentSubmissionViewSet(viewsets.ModelViewSet):
    """
    ViewSet handling student homework reviews and grading evaluation matrices.
    """
    queryset = AssignmentSubmission.objects.select_related("assignment", "student", "graded_by").all()
    serializer_class = AssignmentSubmissionSerializer
    permission_classes = [IsTeacher, AssignmentPermission]
    pagination_class = TeacherPagination
    ordering_fields = ["submitted_at", "grade", "created_at"]
    ordering = ["-submitted_at"]

    def get_queryset(self):
        user = self.request.user
        if not user or not user.is_authenticated:
            return self.queryset.none()
        if user.is_superuser or (hasattr(user, "role") and user.role and user.role.name in ["SUPERADMIN", "ADMIN"]):
            return self.queryset.all()
        return self.queryset.filter(assignment__lesson__parent__parent__teacher_classes__teacher=user, assignment__lesson__parent__parent__teacher_classes__is_active=True)

    @action(detail=True, methods=["post"], url_path="grade")
    def grade(self, request, pk=None) -> Response:
        """Executes student evaluation grades and delivers rewards points."""
        grade_val = request.data.get("grade")
        feedback = request.data.get("feedback", "")

        if grade_val is None:
            return Response({"error": "The numerical score 'grade' is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            score = float(grade_val)
        except Exception:
            return Response({"error": "Invalid numerical format for grade score."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            sub = AssignmentService.grade_student_submission(
                teacher=request.user,
                submission_id=pk,
                grade=score,
                feedback=feedback
            )
            return Response(AssignmentSubmissionSerializer(sub).data, status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# ─── QUIZ ASSESSMENT BANK ─────────────────────────────────────────────────────

class QuestionCategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet organizing custom taxonomy category items.
    """
    queryset = QuestionCategory.objects.all()
    serializer_class = QuestionCategorySerializer
    permission_classes = [IsTeacher]
    pagination_class = TeacherPagination

    def create(self, request, *args, **kwargs) -> Response:
        name = request.data.get("name")
        description = request.data.get("description", "")
        if not name:
            return Response({"error": "Category name is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        category = QuizService.create_question_category(name, description)
        return Response(self.get_serializer(category).data, status=status.HTTP_201_CREATED)


class QuestionDifficultyViewSet(viewsets.ModelViewSet):
    """
    ViewSet managing quiz challenge level multipliers.
    """
    queryset = QuestionDifficulty.objects.all()
    serializer_class = QuestionDifficultySerializer
    permission_classes = [IsTeacher]
    pagination_class = TeacherPagination

    def create(self, request, *args, **kwargs) -> Response:
        level = request.data.get("level")
        multiplier_str = request.data.get("multiplier")
        if not level or not multiplier_str:
            return Response({"error": "Both 'level' and 'multiplier' are required."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            mult = float(multiplier_str)
        except Exception:
            return Response({"error": "Multiplier must be a valid float."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            diff = QuizService.create_difficulty_tier(level, mult)
            return Response(self.get_serializer(diff).data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# ─── ATTENDANCE LOGGING ───────────────────────────────────────────────────────

class AttendanceViewSet(viewsets.ModelViewSet):
    """
    ViewSet monitoring and logging student seminar/stream attendance records.
    """
    queryset = Attendance.objects.select_related("session", "live_class", "student").all()
    serializer_class = AttendanceSerializer
    permission_classes = [IsTeacher, IsTeacherOwner]
    pagination_class = TeacherPagination
    filterset_class = AttendanceFilter
    ordering_fields = ["joined_at", "created_at"]
    ordering = ["-joined_at"]

    def get_queryset(self):
        user = self.request.user
        if not user or not user.is_authenticated:
            return self.queryset.none()
        if user.is_superuser or (hasattr(user, "role") and user.role and user.role.name in ["SUPERADMIN", "ADMIN"]):
            return self.queryset.all()
        # Filter where session hosted by teacher or live class hosted by teacher
        return self.queryset.filter(Q(session__teacher=user) | Q(live_class__teacher=user))

    def create(self, request, *args, **kwargs) -> Response:
        """Logs student attendance levels."""
        live_class_id_str = request.data.get("live_class")
        student_id = request.data.get("student")
        status_val = request.data.get("status", "PRESENT")
        joined_at_str = request.data.get("joined_at")
        left_at_str = request.data.get("left_at")

        if not live_class_id_str or not student_id:
            return Response({"error": "Both 'live_class' UUID and 'student' ID are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            lc_id = UUID(str(live_class_id_str))
        except Exception:
            return Response({"error": "Invalid UUID format for 'live_class'."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            att = AttendanceService.log_live_class_attendance(
                live_class_id=lc_id,
                student_id=student_id,
                status=status_val,
                joined_at=joined_at_str,
                left_at=left_at_str
            )
            return Response(self.get_serializer(att).data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# ─── ANALYTICS AND PERFORMANCE ────────────────────────────────────────────────

class TeacherAnalyticsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ReadOnly ViewSet showcasing instructor analytics records.
    """
    queryset = TeacherAnalytics.objects.select_related("teacher").all()
    serializer_class = TeacherAnalyticsSerializer
    permission_classes = [IsTeacher, IsTeacherOwner]

    def get_queryset(self):
        user = self.request.user
        if not user or not user.is_authenticated:
            return self.queryset.none()
        return self.queryset.filter(teacher=user)

    @action(detail=False, methods=["post"], url_path="recompute")
    def recompute(self, request) -> Response:
        """Updates teacher performance aggregations on-demand."""
        analytics = AnalyticsService.recompute_teacher_aggregates(request.user)
        return Response(TeacherAnalyticsSerializer(analytics).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], url_path="course-performance")
    def course_performance(self, request) -> Response:
        """Compiles analytics reports for a specific course assigned to the instructor."""
        course_id_str = request.query_params.get("course_id")
        if not course_id_str:
            return Response({"error": "Query parameter 'course_id' is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            course_id = int(course_id_str)
        except Exception:
            return Response({"error": "Query parameter 'course_id' must be an integer."}, status=status.HTTP_400_BAD_REQUEST)

        report = TeacherAnalyticsSelector.get_course_performance_report(request.user, course_id)
        if not report:
            return Response(
                {"error": "Performance report not available or unauthorized course query."},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = CoursePerformanceReportSerializer(data=report)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# ─── CERTIFICATES & GOALS ─────────────────────────────────────────────────────

class TeacherCertificateViewSet(viewsets.ModelViewSet):
    """
    ViewSet supporting verification credentials registration.
    """
    queryset = TeacherCertificate.objects.select_related("teacher").all()
    serializer_class = TeacherCertificateSerializer
    permission_classes = [IsTeacher, IsTeacherOwner]
    pagination_class = TeacherPagination
    filterset_class = TeacherCertificateFilter
    ordering_fields = ["issued_date", "created_at"]
    ordering = ["-issued_date"]

    def get_queryset(self):
        user = self.request.user
        if not user or not user.is_authenticated:
            return self.queryset.none()
        return self.queryset.filter(teacher=user)

    def create(self, request, *args, **kwargs) -> Response:
        """Logs external instructor credential verification attributes."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            cert = CertificateService.issue_teacher_credential(
                teacher=request.user,
                title=serializer.validated_data.get("title"),
                issuer=serializer.validated_data.get("issuer"),
                issued_date=serializer.validated_data.get("issued_date"),
                expiry_date=serializer.validated_data.get("expiry_date"),
                verification_url=serializer.validated_data.get("verification_url")
            )
            return Response(self.get_serializer(cert).data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class TeacherAchievementViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ReadOnly ViewSet detailing systems-wide internal gamification achievement medals.
    """
    queryset = TeacherAchievement.objects.select_related("teacher").all()
    serializer_class = TeacherAchievementSerializer
    permission_classes = [IsTeacher, IsTeacherOwner]
    pagination_class = TeacherPagination

    def get_queryset(self):
        user = self.request.user
        if not user or not user.is_authenticated:
            return self.queryset.none()
        return self.queryset.filter(teacher=user)


class TeachingGoalViewSet(BaseTeacherViewSet):
    """
    ViewSet supporting KPI Target/Goal definitions.
    """
    queryset = TeachingGoal.objects.select_related("teacher").all()
    serializer_class = TeachingGoalSerializer
    filterset_class = TeachingGoalFilter
    ordering_fields = ["deadline", "created_at"]
    ordering = ["deadline"]


# ─── AUDIT ACTIVITIES ─────────────────────────────────────────────────────────

class TeacherAnnouncementViewSet(BaseTeacherViewSet):
    """
    ViewSet supporting bulletin board broadcasts.
    """
    queryset = TeacherAnnouncement.objects.select_related("teacher", "course").all()
    serializer_class = TeacherAnnouncementSerializer
    filterset_class = TeacherAnnouncementFilter
    ordering_fields = ["published_at", "created_at"]
    ordering = ["-published_at"]

    def perform_create(self, serializer):
        serializer.save(teacher=self.request.user, published_at=timezone.now())


class TeacherActivityLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ReadOnly ViewSet supporting audit security logs.
    """
    queryset = TeacherActivityLog.objects.select_related("teacher").all()
    serializer_class = TeacherActivityLogSerializer
    permission_classes = [IsTeacher, IsTeacherOwner]
    pagination_class = TeacherPagination
    filterset_class = TeacherActivityLogFilter
    ordering_fields = ["timestamp", "created_at"]
    ordering = ["-timestamp"]

    def get_queryset(self):
        user = self.request.user
        if not user or not user.is_authenticated:
            return self.queryset.none()
        return self.queryset.filter(teacher=user)
