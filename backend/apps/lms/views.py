from rest_framework import viewsets, status, filters, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.utils import timezone
from django.db import models

from apps.lms.models import (
    CourseStructure, LearningProgress, Assignment, AssignmentSubmission, PracticeSession,
    Project, Exam, QuestionBank, ExamQuestion, ExamAttempt, Certificate, Badge, UserBadge,
    TeacherApplication, TeacherClass, StudentEnrollment, LiveClass
)
from apps.lms.serializers import LiveClassSerializer
from apps.users.permissions import HasRBACPermission
from apps.lms.permissions import IsTeacherOrAdminOrReadOnly
from apps.lms.serializers import (
    CourseStructureSerializer, LearningProgressSerializer, AssignmentSerializer,
    AssignmentListSerializer, AssignmentDetailSerializer,
    AssignmentSubmissionSerializer, AssignmentSubmissionListSerializer, AssignmentSubmissionDetailSerializer,
    PracticeSessionSerializer, ProjectSerializer,
    ExamSerializer, QuestionBankSerializer, QuestionBankListSerializer, QuestionBankDetailSerializer, ExamQuestionSerializer, CertificateSerializer,
    ExamAttemptSerializer,
    BadgeSerializer, UserBadgeSerializer, TeacherApplicationSerializer, TeacherClassSerializer,
    StudentEnrollmentSerializer, CourseSerializer, CourseStructureNodeSerializer,
    ChapterSerializer, LessonSerializer, LessonListSerializer, LessonDetailSerializer,
    ProgramSerializer, ProgramListSerializer,
    ProgramDetailSerializer, SubjectSerializer, SubjectListSerializer, SubjectDetailSerializer,
    CourseListSerializer, CourseDetailSerializer, ChapterListSerializer, ChapterDetailSerializer,
    TopicSerializer, TopicListSerializer, TopicDetailSerializer,
    SubtopicSerializer, SubtopicListSerializer, SubtopicDetailSerializer,
    PracticeSerializer, PracticeListSerializer, PracticeDetailSerializer,
    PracticeAttemptSerializer, PracticeAttemptListSerializer, PracticeAttemptDetailSerializer,
    ProjectSubmission, ProjectListSerializer, ProjectDetailSerializer,
    ProjectSubmissionSerializer, ProjectSubmissionListSerializer, ProjectSubmissionDetailSerializer
)

try:
    from django_filters.rest_framework import DjangoFilterBackend
except ImportError:
    DjangoFilterBackend = None


from django.core.cache import cache

def get_deleted_assignments():
    return cache.get("deleted_assignment_ids", set())

def add_deleted_assignment(assignment_id):
    deleted = get_deleted_assignments()
    deleted.add(str(assignment_id))
    cache.set("deleted_assignment_ids", deleted)

def remove_deleted_assignment(assignment_id):
    deleted = get_deleted_assignments()
    deleted.discard(str(assignment_id))
    cache.set("deleted_assignment_ids", deleted)

def get_deleted_submissions():
    return cache.get("deleted_submission_ids", set())

def add_deleted_submission(submission_id):
    deleted = get_deleted_submissions()
    deleted.add(str(submission_id))
    cache.set("deleted_submission_ids", deleted)

def remove_deleted_submission(submission_id):
    deleted = get_deleted_submissions()
    deleted.discard(str(submission_id))
    cache.set("deleted_submission_ids", deleted)


def get_deleted_practice_attempts():
    return cache.get("deleted_practice_attempt_ids", set())


def add_deleted_practice_attempt(attempt_id):
    deleted = get_deleted_practice_attempts()
    deleted.add(str(attempt_id))
    cache.set("deleted_practice_attempt_ids", deleted)


def remove_deleted_practice_attempt(attempt_id):
    deleted = get_deleted_practice_attempts()
    deleted.discard(str(attempt_id))
    cache.set("deleted_practice_attempt_ids", deleted)



class EnterprisePagination(PageNumberPagination):
    """
    Standard Enterprise-grade pagination class with configurable page sizes and limits.
    """
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


class CourseStructureViewSet(viewsets.ModelViewSet):
    queryset = CourseStructure.objects.select_related("parent").all().order_by("display_order")
    serializer_class = CourseStructureSerializer
    permission_classes = [HasRBACPermission]
    lookup_field = "id"
    required_permissions = {
        "list": "lms:course_structure:view",
        "retrieve": "lms:course_structure:view",
        "create": "lms:course_structure:create",
        "update": "lms:course_structure:update",
        "partial_update": "lms:course_structure:update",
        "destroy": "lms:course_structure:delete",
    }


class LearningProgressViewSet(viewsets.ModelViewSet):
    queryset = LearningProgress.objects.select_related("student", "node").all()
    serializer_class = LearningProgressSerializer
    permission_classes = [HasRBACPermission]
    pagination_class = EnterprisePagination
    lookup_field = "id"
    
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    if DjangoFilterBackend is not None:
        filter_backends.append(DjangoFilterBackend)
        
    search_fields = ["student__email", "node__title"]
    ordering_fields = ["progress_percentage", "last_accessed_at", "completed_at"]
    ordering = ["-last_accessed_at"]

    required_permissions = {
        "list": "lms:progress:view",
        "retrieve": "lms:progress:view",
        "create": "lms:progress:create",
        "update": "lms:progress:update",
        "partial_update": "lms:progress:update",
        "destroy": "lms:progress:delete",
        "restore": "lms:progress:update",
    }

    def get_queryset(self):
        user = self.request.user
        include_deleted = self.request.query_params.get("include_deleted", "false").lower() == "true"
        is_privileged = user.is_authenticated and (
            user.is_superuser or (
                user.is_teacher_cbac
            )
        )
        manager = LearningProgress.all_objects if (include_deleted and is_privileged) else LearningProgress.objects
        queryset = manager.select_related("student", "node").all()
        
        if not is_privileged:
            queryset = queryset.filter(student=user)
            
        node_id = self.request.query_params.get("node") or self.request.query_params.get("node_id")
        if node_id:
            queryset = queryset.filter(node_id=node_id)
            
        return queryset.order_by("-last_accessed_at")

    def perform_create(self, serializer):
        serializer.save(student=self.request.user)

    @action(detail=True, methods=["post"], url_path="restore")
    def restore(self, request, id=None):
        """
        POST /learning-progress/{id}/restore/
        Restores a soft-deleted progress record.
        """
        user = self.request.user
        is_privileged = user.is_superuser or (
            user.is_teacher_cbac
        )
        if not is_privileged:
            return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)
            
        progress = LearningProgress.all_objects.filter(id=id, deleted_at__isnull=False).first()
        if not progress:
            return Response({"detail": "Progress record not found or not soft-deleted."}, status=status.HTTP_404_NOT_FOUND)
            
        progress.restore()
        return Response(LearningProgressSerializer(progress).data, status=status.HTTP_200_OK)


class AssignmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling full CRUD operations on Assignments.
    Supports soft delete, restore endpoints, optimized querysets, custom filters, and search/ordering.
    """
    queryset = Assignment.objects.select_related(
        "lesson",
        "lesson__parent",
        "lesson__parent__parent",
        "lesson__parent__parent__parent",
        "lesson__parent__parent__parent__parent",
        "lesson__parent__parent__parent__parent__parent",
        "lesson__parent__parent__parent__parent__parent__parent"
    ).all().order_by("-created_at")
    serializer_class = AssignmentSerializer
    permission_classes = [HasRBACPermission]
    pagination_class = EnterprisePagination
    lookup_field = "id"

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    if DjangoFilterBackend is not None:
        filter_backends.append(DjangoFilterBackend)

    search_fields = ["title", "instructions"]
    ordering_fields = ["created_at", "title", "max_points"]
    ordering = ["-created_at"]

    required_permissions = {
        "list": "lms:assignment:view",
        "retrieve": "lms:assignment:view",
        "create": "lms:assignment:create",
        "update": "lms:assignment:update",
        "partial_update": "lms:assignment:update",
        "destroy": "lms:assignment:delete",
        "restore": "lms:assignment:update",
        "submissions": "lms:assignment:view",
    }

    def get_queryset(self):
        user = self.request.user
        include_deleted = self.request.query_params.get("include_deleted", "false").lower() == "true"
        is_privileged = user.is_authenticated and (
            user.is_superuser or (
                user.is_teacher_cbac
            )
        )

        if include_deleted and is_privileged:
            queryset = self.queryset
        else:
            deleted_ids = get_deleted_assignments()
            queryset = self.queryset.exclude(id__in=deleted_ids)

        # Filtering by direct fields
        lesson_id = self.request.query_params.get("lesson") or self.request.query_params.get("lesson_id")
        if lesson_id:
            queryset = queryset.filter(lesson_id=lesson_id)

        # Filtering by hierarchical parents
        subtopic_id = self.request.query_params.get("subtopic") or self.request.query_params.get("subtopic_id")
        if subtopic_id:
            queryset = queryset.filter(lesson__parent_id=subtopic_id)

        topic_id = self.request.query_params.get("topic") or self.request.query_params.get("topic_id")
        if topic_id:
            queryset = queryset.filter(lesson__parent__parent_id=topic_id)

        chapter_id = self.request.query_params.get("chapter") or self.request.query_params.get("chapter_id")
        if chapter_id:
            queryset = queryset.filter(lesson__parent__parent__parent_id=chapter_id)

        course_id = self.request.query_params.get("course") or self.request.query_params.get("course_id")
        if course_id:
            queryset = queryset.filter(lesson__parent__parent__parent__parent_id=course_id)

        subject_id = self.request.query_params.get("subject") or self.request.query_params.get("subject_id")
        if subject_id:
            queryset = queryset.filter(lesson__parent__parent__parent__parent__parent_id=subject_id)

        program_id = self.request.query_params.get("program") or self.request.query_params.get("program_id")
        if program_id:
            queryset = queryset.filter(lesson__parent__parent__parent__parent__parent__parent_id=program_id)

        # Safe dynamic filtering for non-direct fields
        assignment_type = self.request.query_params.get("assignment_type")
        if assignment_type:
            if hasattr(Assignment, "assignment_type"):
                queryset = queryset.filter(assignment_type=assignment_type)
            else:
                queryset = queryset.filter(models.Q(title__icontains=assignment_type) | models.Q(instructions__icontains=assignment_type))

        difficulty = self.request.query_params.get("difficulty")
        if difficulty:
            if hasattr(Assignment, "difficulty"):
                queryset = queryset.filter(difficulty=difficulty)

        status_val = self.request.query_params.get("status")
        if status_val:
            if hasattr(Assignment, "status"):
                queryset = queryset.filter(status=status_val)

        created_by = self.request.query_params.get("created_by") or self.request.query_params.get("created_by_id")
        if created_by:
            if hasattr(Assignment, "created_by"):
                queryset = queryset.filter(created_by_id=created_by)

        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return AssignmentListSerializer
        elif self.action == "retrieve":
            return AssignmentDetailSerializer
        return AssignmentSerializer

    def perform_destroy(self, instance):
        add_deleted_assignment(instance.id)

    @action(detail=True, methods=["post"], url_path="restore")
    def restore(self, request, id=None):
        """
        POST /assignments/{id}/restore/
        Allows restoring a soft-deleted assignment. Restricted to admins/teachers.
        """
        user = self.request.user
        is_privileged = user.is_authenticated and (
            user.is_superuser or (
                user.is_teacher_cbac
            )
        )
        if not is_privileged:
            return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

        deleted_ids = get_deleted_assignments()
        if str(id) not in deleted_ids:
            return Response({"detail": "Assignment not found or not soft-deleted."}, status=status.HTTP_404_NOT_FOUND)

        remove_deleted_assignment(id)
        return Response({"detail": "Assignment restored successfully."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get"], url_path="submissions")
    def submissions(self, request, id=None):
        """
        GET /assignments/{id}/submissions/
        Returns submissions associated with this specific assignment.
        Students can only see their own submissions. Teachers/Admins can see all.
        """
        assignment = self.get_object()
        user = self.request.user
        include_deleted = self.request.query_params.get("include_deleted", "false").lower() == "true"
        is_privileged = user.is_authenticated and (
            user.is_superuser or (
                user.is_teacher_cbac
            )
        )

        if include_deleted and is_privileged:
            submissions = AssignmentSubmission.objects.filter(assignment=assignment)
        else:
            deleted_ids = get_deleted_submissions()
            submissions = AssignmentSubmission.objects.filter(assignment=assignment).exclude(id__in=deleted_ids)

        if not is_privileged:
            submissions = submissions.filter(student=user)

        # Optimize
        submissions = submissions.select_related("assignment", "student", "graded_by")

        # Search / Order
        search = request.query_params.get("search")
        if search:
            submissions = submissions.filter(
                models.Q(student__email__icontains=search) |
                models.Q(feedback__icontains=search)
            )

        ordering = request.query_params.get("ordering", "-submitted_at")
        if ordering in ["submitted_at", "-submitted_at", "grade", "-grade"]:
            submissions = submissions.order_by(ordering)
        else:
            submissions = submissions.order_by("-submitted_at")

        page = self.paginate_queryset(submissions)
        if page is not None:
            serializer = AssignmentSubmissionListSerializer(page, many=True, context={"request": request})
            return self.get_paginated_response(serializer.data)

        serializer = AssignmentSubmissionListSerializer(submissions, many=True, context={"request": request})
        return Response(serializer.data)


class AssignmentSubmissionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling student submissions, grading records, and feedback loops.
    Supports soft delete, restore endpoints, optimized querysets, custom filters, and search/ordering.
    """
    queryset = AssignmentSubmission.objects.select_related(
        "assignment",
        "student",
        "graded_by",
        "assignment__lesson"
    ).all().order_by("-submitted_at")
    serializer_class = AssignmentSubmissionSerializer
    permission_classes = [HasRBACPermission]
    pagination_class = EnterprisePagination
    lookup_field = "id"

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    if DjangoFilterBackend is not None:
        filter_backends.append(DjangoFilterBackend)

    search_fields = ["feedback", "student__email", "assignment__title"]
    ordering_fields = ["submitted_at", "grade"]
    ordering = ["-submitted_at"]

    required_permissions = {
        "list": "lms:submission:view",
        "retrieve": "lms:submission:view",
        "create": "lms:submission:create",
        "update": "lms:submission:update",
        "partial_update": "lms:submission:update",
        "destroy": "lms:submission:delete",
        "restore": "lms:submission:update",
        "grade_submission": "lms:submission:update",
    }

    def get_queryset(self):
        user = self.request.user
        if not user or not user.is_authenticated:
            return AssignmentSubmission.objects.none()

        include_deleted = self.request.query_params.get("include_deleted", "false").lower() == "true"
        is_privileged = user.is_superuser or (
            user.is_teacher_cbac
        )

        manager = AssignmentSubmission.all_objects if (include_deleted and is_privileged) else AssignmentSubmission.objects
        queryset = manager.select_related(
            "assignment",
            "student",
            "graded_by",
            "assignment__lesson"
        ).all().order_by("-submitted_at")

        # Students can only access their own submissions
        if not is_privileged:
            queryset = queryset.filter(student=user)

        # Filtering by direct fields
        assignment_id = self.request.query_params.get("assignment") or self.request.query_params.get("assignment_id")
        if assignment_id:
            queryset = queryset.filter(assignment_id=assignment_id)

        student_id = self.request.query_params.get("student") or self.request.query_params.get("student_id")
        if student_id and is_privileged:
            queryset = queryset.filter(student_id=student_id)

        lesson_id = self.request.query_params.get("lesson") or self.request.query_params.get("lesson_id")
        if lesson_id:
            queryset = queryset.filter(assignment__lesson_id=lesson_id)

        # Filtering by hierarchical parents
        subtopic_id = self.request.query_params.get("subtopic") or self.request.query_params.get("subtopic_id")
        if subtopic_id:
            queryset = queryset.filter(assignment__lesson__parent_id=subtopic_id)

        topic_id = self.request.query_params.get("topic") or self.request.query_params.get("topic_id")
        if topic_id:
            queryset = queryset.filter(assignment__lesson__parent__parent_id=topic_id)

        chapter_id = self.request.query_params.get("chapter") or self.request.query_params.get("chapter_id")
        if chapter_id:
            queryset = queryset.filter(assignment__lesson__parent__parent__parent_id=chapter_id)

        course_id = self.request.query_params.get("course") or self.request.query_params.get("course_id")
        if course_id:
            queryset = queryset.filter(assignment__lesson__parent__parent__parent__parent_id=course_id)

        subject_id = self.request.query_params.get("subject") or self.request.query_params.get("subject_id")
        if subject_id:
            queryset = queryset.filter(assignment__lesson__parent__parent__parent__parent__parent_id=subject_id)

        program_id = self.request.query_params.get("program") or self.request.query_params.get("program_id")
        if program_id:
            queryset = queryset.filter(assignment__lesson__parent__parent__parent__parent__parent__parent_id=program_id)

        # Filtering by status
        status_val = self.request.query_params.get("status")
        if status_val:
            if status_val.upper() == "GRADED":
                queryset = queryset.filter(grade__isnull=False)
            elif status_val.upper() == "PENDING":
                queryset = queryset.filter(grade__isnull=True)

        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return AssignmentSubmissionListSerializer
        elif self.action == "retrieve":
            return AssignmentSubmissionDetailSerializer
        return AssignmentSubmissionSerializer

    def perform_create(self, serializer):
        serializer.save(student=self.request.user)

    def perform_update(self, serializer):
        from rest_framework.exceptions import PermissionDenied
        user = self.request.user
        is_privileged = user.is_superuser or (
            user.is_teacher_cbac
        )
        instance = self.get_object()
        if not is_privileged and instance.student != user:
            raise PermissionDenied("You cannot modify another student's submission.")
        serializer.save()

    def perform_destroy(self, instance):
        instance.delete()

    @action(detail=True, methods=["post"], url_path="restore")
    def restore(self, request, id=None):
        """
        POST /assignment-submissions/{id}/restore/
        Allows restoring a soft-deleted submission. Restricted to admins/teachers.
        """
        user = self.request.user
        is_privileged = user.is_authenticated and (
            user.is_superuser or (
                user.is_teacher_cbac
            )
        )
        if not is_privileged:
            return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

        try:
            instance = AssignmentSubmission.all_objects.get(id=id)
        except AssignmentSubmission.DoesNotExist:
            return Response({"detail": "Assignment submission not found."}, status=status.HTTP_404_NOT_FOUND)

        if instance.deleted_at is None:
            return Response({"detail": "Assignment submission is not soft-deleted."}, status=status.HTTP_404_NOT_FOUND)

        instance.restore()
        return Response({"detail": "Assignment submission restored successfully."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"])
    def grade_submission(self, request, id=None):
        """
        POST /assignment-submissions/{id}/grade_submission/
        Grades a student's submission. Restricted to teachers and admins.
        """
        user = self.request.user
        is_privileged = user.is_authenticated and (
            user.is_superuser or (
                user.is_teacher_cbac
            )
        )
        if not is_privileged:
            return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

        submission = self.get_object()
        grade = request.data.get("grade")
        feedback = request.data.get("feedback")
        
        submission.grade = grade
        submission.feedback = feedback
        submission.graded_by = request.user
        submission.graded_at = timezone.now()
        submission.save()
        
        return Response(AssignmentSubmissionSerializer(submission).data)


class PracticeViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling full CRUD operations on Practices (backed by CourseStructure).
    Supports soft delete, restore endpoints, optimized querysets, custom filters, and search/ordering.
    """
    queryset = CourseStructure.objects.select_related(
        "parent",
        "parent__parent",
        "parent__parent__parent",
        "parent__parent__parent__parent",
        "parent__parent__parent__parent__parent",
        "parent__parent__parent__parent__parent__parent"
    ).all().order_by("-created_at")
    serializer_class = PracticeSerializer
    permission_classes = [HasRBACPermission]
    pagination_class = EnterprisePagination
    lookup_field = "id"

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    if DjangoFilterBackend is not None:
        filter_backends.append(DjangoFilterBackend)

    search_fields = ["title", "description"]
    ordering_fields = ["created_at", "title", "display_order"]
    ordering = ["-created_at"]

    required_permissions = {
        "list": "lms:practice:view",
        "retrieve": "lms:practice:view",
        "create": "lms:practice:create",
        "update": "lms:practice:update",
        "partial_update": "lms:practice:update",
        "destroy": "lms:practice:delete",
        "restore": "lms:practice:update",
        "attempts": "lms:practice:view",
    }

    def get_queryset(self):
        user = self.request.user
        include_deleted = self.request.query_params.get("include_deleted", "false").lower() == "true"
        is_privileged = user.is_authenticated and (
            user.is_superuser or (
                user.is_teacher_cbac
            )
        )

        manager = CourseStructure.all_objects if (include_deleted and is_privileged) else CourseStructure.objects
        queryset = manager.select_related(
            "parent",
            "parent__parent",
            "parent__parent__parent",
            "parent__parent__parent__parent",
            "parent__parent__parent__parent__parent",
            "parent__parent__parent__parent__parent__parent"
        ).all().order_by("-created_at")

        # Filtering by direct fields
        lesson_id = self.request.query_params.get("lesson") or self.request.query_params.get("lesson_id")
        if lesson_id:
            queryset = queryset.filter(parent_id=lesson_id)

        # Filtering by hierarchical parents
        subtopic_id = self.request.query_params.get("subtopic") or self.request.query_params.get("subtopic_id")
        if subtopic_id:
            queryset = queryset.filter(parent__parent_id=subtopic_id)

        topic_id = self.request.query_params.get("topic") or self.request.query_params.get("topic_id")
        if topic_id:
            queryset = queryset.filter(parent__parent__parent_id=topic_id)

        chapter_id = self.request.query_params.get("chapter") or self.request.query_params.get("chapter_id")
        if chapter_id:
            queryset = queryset.filter(parent__parent__parent__parent_id=chapter_id)

        course_id = self.request.query_params.get("course") or self.request.query_params.get("course_id")
        if course_id:
            queryset = queryset.filter(parent__parent__parent__parent__parent_id=course_id)

        subject_id = self.request.query_params.get("subject") or self.request.query_params.get("subject_id")
        if subject_id:
            queryset = queryset.filter(parent__parent__parent__parent__parent__parent_id=subject_id)

        program_id = self.request.query_params.get("program") or self.request.query_params.get("program_id")
        if program_id:
            queryset = queryset.filter(parent__parent__parent__parent__parent__parent__parent_id=program_id)

        # Filtering metadata fields
        practice_type = self.request.query_params.get("practice_type")
        if practice_type:
            queryset = queryset.filter(metadata__practice_type=practice_type)

        difficulty = self.request.query_params.get("difficulty")
        if difficulty:
            queryset = queryset.filter(metadata__difficulty=difficulty)

        status_val = self.request.query_params.get("status")
        if status_val:
            queryset = queryset.filter(metadata__status=status_val)

        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return PracticeListSerializer
        elif self.action == "retrieve":
            return PracticeDetailSerializer
        return PracticeSerializer

    def perform_destroy(self, instance):
        instance.delete()

    @action(detail=True, methods=["post"], url_path="restore")
    def restore(self, request, id=None):
        """
        POST /practice/{id}/restore/
        Allows restoring a soft-deleted practice. Restricted to admins/teachers.
        """
        user = self.request.user
        is_privileged = user.is_authenticated and (
            user.is_superuser or (
                user.is_teacher_cbac
            )
        )
        if not is_privileged:
            return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

        try:
            instance = CourseStructure.all_objects.get(id=id)
        except CourseStructure.DoesNotExist:
            return Response({"detail": "Practice not found."}, status=status.HTTP_404_NOT_FOUND)

        if instance.deleted_at is None:
            return Response({"detail": "Practice is not deleted."}, status=status.HTTP_400_BAD_REQUEST)

        instance.restore()
        return Response({"detail": "Practice restored successfully."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get"], url_path="attempts")
    def attempts(self, request, id=None):
        """
        GET /practice/{id}/attempts/
        Returns practice attempts (sessions) associated with this practice.
        """
        practice = self.get_object()
        user = self.request.user
        is_privileged = user.is_authenticated and (
            user.is_superuser or (
                user.is_teacher_cbac
            )
        )

        queryset = PracticeSession.objects.filter(course=practice).order_by("-created_at")
        if not is_privileged:
            queryset = queryset.filter(student=user)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = PracticeAttemptListSerializer(page, many=True, context={"request": request})
            return self.get_paginated_response(serializer.data)

        serializer = PracticeAttemptListSerializer(queryset, many=True, context={"request": request})
        return Response(serializer.data)


class PracticeAttemptViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling CRUD operations on Practice Attempts (backed by PracticeSession).
    Supports soft delete, restore, pagination, search, filters, and ordering.
    """
    queryset = PracticeSession.objects.select_related("student", "course").all().order_by("-created_at")
    serializer_class = PracticeAttemptSerializer
    permission_classes = [HasRBACPermission]
    pagination_class = EnterprisePagination
    lookup_field = "id"

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    if DjangoFilterBackend is not None:
        filter_backends.append(DjangoFilterBackend)

    search_fields = ["course__title", "student__email"]
    ordering_fields = ["created_at", "score"]
    ordering = ["-created_at"]

    required_permissions = {
        "list": "lms:practice:view",
        "retrieve": "lms:practice:view",
        "create": "lms:practice:create",
        "update": "lms:practice:update",
        "partial_update": "lms:practice:update",
        "destroy": "lms:practice:delete",
        "restore": "lms:practice:update",
    }

    def get_queryset(self):
        user = self.request.user
        include_deleted = self.request.query_params.get("include_deleted", "false").lower() == "true"
        is_privileged = user.is_authenticated and (
            user.is_superuser or (
                user.is_teacher_cbac
            )
        )

        manager = PracticeSession.all_objects if (include_deleted and is_privileged) else PracticeSession.objects
        queryset = manager.select_related("student", "course").all().order_by("-created_at")

        if not is_privileged:
            queryset = queryset.filter(student=user)

        # Filtering by practice id
        practice_id = self.request.query_params.get("practice") or self.request.query_params.get("practice_id")
        if practice_id:
            queryset = queryset.filter(course_id=practice_id)

        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return PracticeAttemptListSerializer
        elif self.action == "retrieve":
            return PracticeAttemptDetailSerializer
        return PracticeAttemptSerializer

    def perform_create(self, serializer):
        serializer.save(student=self.request.user)

    def perform_destroy(self, instance):
        instance.delete()

    @action(detail=True, methods=["post"], url_path="restore")
    def restore(self, request, id=None):
        """
        POST /practice-attempts/{id}/restore/
        Restores a soft-deleted practice attempt. Restricted to admins/teachers.
        """
        user = self.request.user
        is_privileged = user.is_authenticated and (
            user.is_superuser or (
                user.is_teacher_cbac
            )
        )
        if not is_privileged:
            return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

        try:
            instance = PracticeSession.all_objects.get(id=id)
        except PracticeSession.DoesNotExist:
            return Response({"detail": "Practice attempt not found."}, status=status.HTTP_404_NOT_FOUND)

        if instance.deleted_at is None:
            return Response({"detail": "Practice attempt is not soft-deleted."}, status=status.HTTP_404_NOT_FOUND)

        instance.restore()
        return Response(PracticeAttemptDetailSerializer(instance).data)


class ProjectViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling CRUD operations on Projects.
    Supports soft delete, restore, pagination, search, filters, and ordering.
    """
    queryset = Project.objects.select_related(
        "course",
        "course__parent",
        "course__parent__parent",
        "course__parent__parent__parent",
        "course__parent__parent__parent__parent",
        "course__parent__parent__parent__parent__parent",
        "course__parent__parent__parent__parent__parent__parent"
    ).all().order_by("-created_at")
    serializer_class = ProjectSerializer
    permission_classes = [HasRBACPermission]
    pagination_class = EnterprisePagination
    lookup_field = "id"

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    if DjangoFilterBackend is not None:
        filter_backends.append(DjangoFilterBackend)

    search_fields = ["title", "description", "course__title"]
    ordering_fields = ["created_at", "title"]
    ordering = ["-created_at"]

    required_permissions = {
        "list": "lms:project:view",
        "retrieve": "lms:project:view",
        "create": "lms:project:create",
        "update": "lms:project:update",
        "partial_update": "lms:project:update",
        "destroy": "lms:project:delete",
        "restore": "lms:project:update",
        "submissions": "lms:submission:view",
    }

    def get_queryset(self):
        user = self.request.user
        include_deleted = self.request.query_params.get("include_deleted", "false").lower() == "true"
        is_privileged = user.is_authenticated and (
            user.is_superuser or (
                user.is_teacher_cbac
            )
        )

        manager = Project.all_objects if (include_deleted and is_privileged) else Project.objects
        queryset = manager.select_related(
            "course",
            "course__parent",
            "course__parent__parent",
            "course__parent__parent__parent",
            "course__parent__parent__parent__parent",
            "course__parent__parent__parent__parent__parent",
            "course__parent__parent__parent__parent__parent__parent"
        ).all().order_by("-created_at")

        # Hierarchical parent filters
        lesson_id = self.request.query_params.get("lesson") or self.request.query_params.get("lesson_id")
        if lesson_id:
            queryset = queryset.filter(
                models.Q(course_id=lesson_id) |
                models.Q(course__parent_id=lesson_id) |
                models.Q(course__parent__parent_id=lesson_id) |
                models.Q(course__parent__parent__parent_id=lesson_id)
            )

        subtopic_id = self.request.query_params.get("subtopic") or self.request.query_params.get("subtopic_id")
        if subtopic_id:
            queryset = queryset.filter(
                models.Q(course_id=subtopic_id) |
                models.Q(course__parent_id=subtopic_id) |
                models.Q(course__parent__parent_id=subtopic_id) |
                models.Q(course__parent__parent__parent_id=subtopic_id)
            )

        topic_id = self.request.query_params.get("topic") or self.request.query_params.get("topic_id")
        if topic_id:
            queryset = queryset.filter(
                models.Q(course_id=topic_id) |
                models.Q(course__parent_id=topic_id) |
                models.Q(course__parent__parent_id=topic_id) |
                models.Q(course__parent__parent__parent_id=topic_id)
            )

        chapter_id = self.request.query_params.get("chapter") or self.request.query_params.get("chapter_id")
        if chapter_id:
            queryset = queryset.filter(
                models.Q(course_id=chapter_id) |
                models.Q(course__parent_id=chapter_id) |
                models.Q(course__parent__parent_id=chapter_id) |
                models.Q(course__parent__parent__parent_id=chapter_id)
            )

        course_id_param = self.request.query_params.get("course") or self.request.query_params.get("course_id")
        if course_id_param:
            queryset = queryset.filter(
                models.Q(course_id=course_id_param) |
                models.Q(course__parent_id=course_id_param) |
                models.Q(course__parent__parent_id=course_id_param) |
                models.Q(course__parent__parent__parent_id=course_id_param)
            )

        subject_id = self.request.query_params.get("subject") or self.request.query_params.get("subject_id")
        if subject_id:
            queryset = queryset.filter(
                models.Q(course_id=subject_id) |
                models.Q(course__parent_id=subject_id) |
                models.Q(course__parent__parent_id=subject_id) |
                models.Q(course__parent__parent__parent_id=subject_id) |
                models.Q(course__parent__parent__parent__parent_id=subject_id) |
                models.Q(course__parent__parent__parent__parent__parent_id=subject_id)
            )

        program_id = self.request.query_params.get("program") or self.request.query_params.get("program_id")
        if program_id:
            queryset = queryset.filter(
                models.Q(course_id=program_id) |
                models.Q(course__parent_id=program_id) |
                models.Q(course__parent__parent_id=program_id) |
                models.Q(course__parent__parent__parent_id=program_id) |
                models.Q(course__parent__parent__parent__parent_id=program_id) |
                models.Q(course__parent__parent__parent__parent__parent_id=program_id) |
                models.Q(course__parent__parent__parent__parent__parent__parent_id=program_id)
            )

        # Filtering metadata fields
        project_type = self.request.query_params.get("project_type")
        if project_type:
            queryset = queryset.filter(course__metadata__project_type=project_type)

        difficulty = self.request.query_params.get("difficulty")
        if difficulty:
            queryset = queryset.filter(course__metadata__difficulty=difficulty)

        status_val = self.request.query_params.get("status")
        if status_val:
            queryset = queryset.filter(course__metadata__status=status_val)

        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return ProjectListSerializer
        elif self.action == "retrieve":
            return ProjectDetailSerializer
        return ProjectSerializer

    def perform_destroy(self, instance):
        instance.delete()

    @action(detail=True, methods=["post"], url_path="restore")
    def restore(self, request, id=None):
        """
        POST /projects/{id}/restore/
        Allows restoring a soft-deleted project. Restricted to admins/teachers.
        """
        user = self.request.user
        is_privileged = user.is_authenticated and (
            user.is_superuser or (
                user.is_teacher_cbac
            )
        )
        if not is_privileged:
            return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

        try:
            instance = Project.all_objects.get(id=id)
        except Project.DoesNotExist:
            return Response({"detail": "Project not found."}, status=status.HTTP_404_NOT_FOUND)

        if instance.deleted_at is None:
            return Response({"detail": "Project is not soft-deleted."}, status=status.HTTP_400_BAD_REQUEST)

        instance.restore()
        return Response({"detail": "Project restored successfully."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get"], url_path="submissions")
    def submissions(self, request, id=None):
        """
        GET /projects/{project_id}/submissions/
        Returns submissions associated with this specific project.
        """
        project = self.get_object()
        user = self.request.user
        include_deleted = request.query_params.get("include_deleted", "false").lower() == "true"
        is_privileged = user.is_authenticated and (
            user.is_superuser or (
                user.is_teacher_cbac
            )
        )

        manager = ProjectSubmission.all_objects if (include_deleted and is_privileged) else ProjectSubmission.objects
        queryset = manager.filter(project=project).select_related("project", "student").order_by("-created_at")

        # Student privacy boundary
        if not is_privileged:
            queryset = queryset.filter(student=user)

        # Search support
        search = request.query_params.get("search")
        if search:
            queryset = queryset.filter(
                models.Q(student__email__icontains=search)
            )

        # Order support
        ordering = request.query_params.get("ordering", "-created_at")
        if ordering in ["created_at", "-created_at"]:
            queryset = queryset.order_by(ordering)
        else:
            queryset = queryset.order_by("-created_at")

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ProjectSubmissionListSerializer(page, many=True, context={"request": request})
            return self.get_paginated_response(serializer.data)

        serializer = ProjectSubmissionListSerializer(queryset, many=True, context={"request": request})
        return Response(serializer.data)


class ProjectSubmissionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling CRUD operations on Project Submissions.
    Supports soft delete, restore, pagination, search, filters, and ordering.
    """
    queryset = ProjectSubmission.objects.select_related("project", "student").all().order_by("-created_at")
    serializer_class = ProjectSubmissionSerializer
    permission_classes = [HasRBACPermission]
    pagination_class = EnterprisePagination
    lookup_field = "id"

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    if DjangoFilterBackend is not None:
        filter_backends.append(DjangoFilterBackend)

    search_fields = ["project__title", "student__email"]
    ordering_fields = ["created_at"]
    ordering = ["-created_at"]

    required_permissions = {
        "list": "lms:submission:view",
        "retrieve": "lms:submission:view",
        "create": "lms:submission:create",
        "update": "lms:submission:update",
        "partial_update": "lms:submission:update",
        "destroy": "lms:submission:delete",
        "restore": "lms:submission:update",
    }

    def get_queryset(self):
        user = self.request.user
        if not user or not user.is_authenticated:
            return ProjectSubmission.objects.none()

        include_deleted = self.request.query_params.get("include_deleted", "false").lower() == "true"
        is_privileged = user.is_superuser or (
            user.is_teacher_cbac
        )

        manager = ProjectSubmission.all_objects if (include_deleted and is_privileged) else ProjectSubmission.objects
        queryset = manager.select_related("project", "student").all().order_by("-created_at")

        # Student privacy boundary: Students only see their own submissions
        if not is_privileged:
            queryset = queryset.filter(student=user)

        # Filtering by project_id / project
        project_id = self.request.query_params.get("project") or self.request.query_params.get("project_id")
        if project_id:
            queryset = queryset.filter(project_id=project_id)

        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return ProjectSubmissionListSerializer
        elif self.action == "retrieve":
            return ProjectSubmissionDetailSerializer
        return ProjectSubmissionSerializer

    def perform_create(self, serializer):
        serializer.save(student=self.request.user)

    def perform_destroy(self, instance):
        instance.delete()

    @action(detail=True, methods=["post"], url_path="restore")
    def restore(self, request, id=None):
        """
        POST /project-submissions/{id}/restore/
        Allows restoring a soft-deleted project submission. Restricted to admins/teachers.
        """
        user = self.request.user
        is_privileged = user.is_authenticated and (
            user.is_superuser or (
                user.is_teacher_cbac
            )
        )
        if not is_privileged:
            return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

        try:
            instance = ProjectSubmission.all_objects.get(id=id)
        except ProjectSubmission.DoesNotExist:
            return Response({"detail": "Project submission not found."}, status=status.HTTP_404_NOT_FOUND)

        if instance.deleted_at is None:
            return Response({"detail": "Project submission is not soft-deleted."}, status=status.HTTP_400_BAD_REQUEST)

        instance.restore()
        return Response({"detail": "Project submission restored successfully."}, status=status.HTTP_200_OK)


class ExamViewSet(viewsets.ModelViewSet):
    queryset = Exam.objects.select_related("course").all().order_by("-created_at")
    serializer_class = ExamSerializer
    permission_classes = [HasRBACPermission]
    lookup_field = "id"
    required_permissions = {
        "list": "lms:exam:view",
        "retrieve": "lms:exam:view",
        "create": "lms:exam:create",
        "update": "lms:exam:update",
        "partial_update": "lms:exam:update",
        "destroy": "lms:exam:delete",
        "start": "lms:progress:create",
        "submit": "lms:progress:create",
    }

    @action(detail=True, methods=["post"], url_path="start")
    def start_exam(self, request, id=None):
        """
        POST /exams/{id}/start/
        Initializes an ExamAttempt session for the logged in student.
        """
        import datetime
        exam = self.get_object()
        # Find if student has an active started session to avoid duplicates
        active_attempt = ExamAttempt.objects.filter(
            student=request.user, exam=exam, status="STARTED"
        ).first()
        if active_attempt:
            # check duration limit
            duration_limit = timezone.now() - datetime.timedelta(minutes=exam.duration_minutes)
            if active_attempt.started_at < duration_limit:
                active_attempt.status = "TIMED_OUT"
                active_attempt.save()
            else:
                return Response(
                    ExamAttemptSerializer(active_attempt).data, 
                    status=status.HTTP_200_OK
                )
        
        attempt = ExamAttempt.objects.create(
            student=request.user,
            exam=exam,
            status="STARTED",
            started_at=timezone.now()
        )
        return Response(
            ExamAttemptSerializer(attempt).data, 
            status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=["post"], url_path="submit")
    def submit_exam(self, request, id=None):
        """
        POST /exams/{id}/submit/
        Submits student answers, scores them automatically, updates state,
        awards badge milestones, and triggers certificates.
        """
        import datetime
        exam = self.get_object()
        attempt = ExamAttempt.objects.filter(
            student=request.user, exam=exam, status="STARTED"
        ).first()
        if not attempt:
            return Response(
                {"detail": "No active exam session started for this exam."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check time limit
        duration_limit = attempt.started_at + datetime.timedelta(minutes=exam.duration_minutes + 2) # add 2 mins grace period
        submitted_at = timezone.now()
        if submitted_at > duration_limit:
            attempt.status = "TIMED_OUT"
            attempt.score = 0.00
            attempt.passed = False
            attempt.submitted_at = submitted_at
            attempt.save()
            return Response(
                {"detail": "Exam attempt has timed out and was graded 0%.", "attempt": ExamAttemptSerializer(attempt).data}, 
                status=status.HTTP_200_OK
            )
            
        answers = request.data.get("answers", {}) # dict {question_id_str: list_of_selected_indices}
        
        # Grading Logic:
        # Get all exam questions linked
        exam_questions = ExamQuestion.objects.filter(exam=exam).select_related("question")
        total_questions = exam_questions.count()
        if total_questions == 0:
            # fall back if no questions configured
            attempt.score = 100.00
            attempt.passed = True
        else:
            correct_count = 0
            for eq in exam_questions:
                q = eq.question
                q_id_str = str(q.id)
                user_choices = answers.get(q_id_str, [])
                correct_choices = q.correct_answers # list of correct indexes
                
                # Check match
                if sorted(user_choices) == sorted(correct_choices):
                    correct_count += 1
            
            attempt.score = round((correct_count / total_questions) * 100, 2)
            attempt.passed = attempt.score >= exam.passing_score
            
        attempt.answers = answers
        attempt.submitted_at = submitted_at
        attempt.status = "SUBMITTED"
        attempt.save()
        
        # 1. Trigger Certificate if passed
        if attempt.passed:
            import hashlib
            from apps.lms.models import Certificate
            # Check if prior certificate exists
            cert = Certificate.objects.filter(user=request.user, course=exam.course).first()
            if not cert:
                sig = hashlib.sha256(f"{request.user.id}:{exam.course.id}:BrahmaVidyaGalaxy".encode("utf-8")).hexdigest()
                Certificate.objects.create(
                    user=request.user,
                    course=exam.course,
                    signature_hash=sig,
                    certificate_url=f"https://brahmavidya.galaxy/certs/{exam.course.slug or exam.course.id}-cert.pdf"
                )
                
            # Unlock dynamic badge: "Exam Conqueror" or "Perfect Score"
            from apps.lms.models import Badge, UserBadge
            badge_title = "Exam Conqueror"
            if attempt.score == 100.00:
                badge_title = "Perfect Sage"
                
            badge, _ = Badge.objects.get_or_create(
                title=badge_title,
                defaults={
                    "description": f"Earned by successfully passing an exam on the platform.",
                    "icon_url": f"https://brahmavidya.galaxy/badges/{badge_title.lower().replace(' ', '_')}.svg"
                }
            )
            UserBadge.objects.get_or_create(user=request.user, badge=badge)
            
        # Unlock a default badge for starting/finishing any quiz/session: "Knowledge Seeker"
        from apps.lms.models import Badge, UserBadge
        seeker_badge, _ = Badge.objects.get_or_create(
            title="Knowledge Seeker",
            defaults={
                "description": "Awarded for participating in learning evaluations.",
                "icon_url": "https://brahmavidya.galaxy/badges/knowledge_seeker.svg"
            }
        )
        UserBadge.objects.get_or_create(user=request.user, badge=seeker_badge)
        
        return Response(ExamAttemptSerializer(attempt).data, status=status.HTTP_200_OK)


class ExamAttemptViewSet(viewsets.ModelViewSet):
    queryset = ExamAttempt.objects.select_related("student", "exam").all().order_by("-started_at")
    serializer_class = ExamAttemptSerializer
    permission_classes = [HasRBACPermission]
    lookup_field = "id"
    required_permissions = {
        "list": "lms:progress:view",
        "retrieve": "lms:progress:view",
        "create": "lms:progress:create",
        "update": "lms:progress:update",
        "partial_update": "lms:progress:update",
        "destroy": "lms:progress:delete",
    }

    def get_queryset(self):
        user = self.request.user
        is_privileged = user.is_superuser or (
            user.is_teacher_cbac
        )
        queryset = ExamAttempt.objects.select_related("student", "exam").all()
        if not is_privileged:
            queryset = queryset.filter(student=user)
        return queryset.order_by("-started_at")

    def perform_create(self, serializer):
        serializer.save(student=self.request.user)


class QuestionBankViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling CRUD operations on Question Bank.
    Supports soft delete, restore, pagination, search, filters, and ordering.
    """
    queryset = QuestionBank.objects.select_related(
        "course",
        "course__parent",
        "course__parent__parent",
        "course__parent__parent__parent",
        "course__parent__parent__parent__parent",
        "course__parent__parent__parent__parent__parent",
        "course__parent__parent__parent__parent__parent__parent"
    ).all().order_by("-created_at")
    serializer_class = QuestionBankSerializer
    permission_classes = [HasRBACPermission]
    pagination_class = EnterprisePagination
    lookup_field = "id"

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    if DjangoFilterBackend is not None:
        filter_backends.append(DjangoFilterBackend)

    search_fields = ["question_text", "question_type", "course__title"]
    ordering_fields = ["created_at", "question_text"]
    ordering = ["-created_at"]

    required_permissions = {
        "list": "lms:question:view",
        "retrieve": "lms:question:view",
        "create": "lms:question:create",
        "update": "lms:question:update",
        "partial_update": "lms:question:update",
        "destroy": "lms:question:delete",
        "restore": "lms:question:update",
    }

    def get_queryset(self):
        user = self.request.user
        include_deleted = self.request.query_params.get("include_deleted", "false").lower() == "true"
        is_privileged = user.is_authenticated and (
            user.is_superuser or (
                user.is_teacher_cbac
            )
        )

        manager = QuestionBank.all_objects if (include_deleted and is_privileged) else QuestionBank.objects
        queryset = manager.select_related(
            "course",
            "course__parent",
            "course__parent__parent",
            "course__parent__parent__parent",
            "course__parent__parent__parent__parent",
            "course__parent__parent__parent__parent__parent",
            "course__parent__parent__parent__parent__parent__parent"
        ).all().order_by("-created_at")

        # Hierarchical parent filters
        for param_name in ["program", "subject", "course", "chapter", "topic", "subtopic", "lesson"]:
            val = self.request.query_params.get(param_name) or self.request.query_params.get(f"{param_name}_id")
            if val:
                queryset = queryset.filter(
                    models.Q(course_id=val) |
                    models.Q(course__parent_id=val) |
                    models.Q(course__parent__parent_id=val) |
                    models.Q(course__parent__parent__parent_id=val) |
                    models.Q(course__parent__parent__parent__parent_id=val) |
                    models.Q(course__parent__parent__parent__parent__parent_id=val) |
                    models.Q(course__parent__parent__parent__parent__parent__parent_id=val)
                )

        # Direct classification/attribute filters
        question_type = self.request.query_params.get("question_type")
        if question_type:
            queryset = queryset.filter(question_type=question_type)

        difficulty = self.request.query_params.get("difficulty")
        if difficulty:
            queryset = queryset.filter(course__metadata__difficulty=difficulty)

        status_val = self.request.query_params.get("status")
        if status_val:
            queryset = queryset.filter(course__metadata__status=status_val)

        created_by = self.request.query_params.get("created_by") or self.request.query_params.get("created_by_id")
        if created_by:
            if hasattr(QuestionBank, "created_by"):
                queryset = queryset.filter(created_by_id=created_by)
            elif hasattr(QuestionBank, "created_by_id"):
                queryset = queryset.filter(created_by_id=created_by)

        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return QuestionBankListSerializer
        elif self.action == "retrieve":
            return QuestionBankDetailSerializer
        return QuestionBankSerializer

    def perform_destroy(self, instance):
        instance.delete()

    @action(detail=True, methods=["post"], url_path="restore")
    def restore(self, request, id=None):
        """
        POST /question-banks/{id}/restore/
        Allows restoring a soft-deleted question. Restricted to admins/teachers.
        """
        user = self.request.user
        is_privileged = user.is_authenticated and (
            user.is_superuser or (
                user.is_teacher_cbac
            )
        )
        if not is_privileged:
            return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

        try:
            instance = QuestionBank.all_objects.get(id=id)
        except QuestionBank.DoesNotExist:
            return Response({"detail": "Question not found."}, status=status.HTTP_404_NOT_FOUND)

        if instance.deleted_at is None:
            return Response({"detail": "Question is not soft-deleted."}, status=status.HTTP_400_BAD_REQUEST)

        instance.restore()
        return Response({"detail": "Question restored successfully."}, status=status.HTTP_200_OK)


class ExamQuestionViewSet(viewsets.ModelViewSet):
    queryset = ExamQuestion.objects.select_related("exam", "question").all()
    serializer_class = ExamQuestionSerializer
    permission_classes = [HasRBACPermission]
    lookup_field = "id"
    required_permissions = {
        "list": "lms:exam_question:view",
        "retrieve": "lms:exam_question:view",
        "create": "lms:exam_question:create",
        "update": "lms:exam_question:update",
        "partial_update": "lms:exam_question:update",
        "destroy": "lms:exam_question:delete",
    }


class CertificateViewSet(viewsets.ModelViewSet):
    queryset = Certificate.objects.select_related("user", "course").all().order_by("-issued_at")
    serializer_class = CertificateSerializer
    permission_classes = [HasRBACPermission]
    pagination_class = EnterprisePagination
    lookup_field = "id"
    
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    if DjangoFilterBackend is not None:
        filter_backends.append(DjangoFilterBackend)
        
    search_fields = ["user__email", "course__title", "signature_hash"]
    ordering_fields = ["issued_at"]
    ordering = ["-issued_at"]

    required_permissions = {
        "list": "lms:certificate:view",
        "retrieve": "lms:certificate:view",
        "create": "lms:certificate:create",
        "update": "lms:certificate:update",
        "partial_update": "lms:certificate:update",
        "destroy": "lms:certificate:delete",
        "restore": "lms:certificate:update",
    }

    def get_queryset(self):
        user = self.request.user
        include_deleted = self.request.query_params.get("include_deleted", "false").lower() == "true"
        is_privileged = user.is_authenticated and (
            user.is_superuser or (
                user.is_teacher_cbac
            )
        )
        manager = Certificate.all_objects if (include_deleted and is_privileged) else Certificate.objects
        queryset = manager.select_related("user", "course").all()
        
        if not is_privileged:
            queryset = queryset.filter(user=user)
            
        return queryset.order_by("-issued_at")

    @action(detail=True, methods=["get"], url_path="verify")
    def verify(self, request, id=None):
        """
        GET /certificates/{id}/verify/
        Verifies certificate by UUID.
        """
        try:
            certificate = Certificate.objects.select_related("user", "course").get(id=id)
        except Certificate.DoesNotExist:
            return Response({"verified": False, "detail": "Certificate not found."}, status=status.HTTP_404_NOT_FOUND)
            
        return Response({
            "verified": True,
            "certificate_id": certificate.id,
            "student_email": certificate.user.email,
            "student_name": f"{certificate.user.first_name} {certificate.user.last_name}".strip() or certificate.user.username,
            "course_title": certificate.course.title,
            "signature_hash": certificate.signature_hash,
            "issued_at": certificate.issued_at
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], url_path="verify")
    def verify_public(self, request):
        """
        GET /certificates/verify/
        Public verification lookup via the signature_hash parameter.
        """
        signature_hash = request.query_params.get("hash") or request.query_params.get("signature_hash")
        if not signature_hash:
            return Response({"error": "Query parameter 'hash' is required."}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            certificate = Certificate.objects.select_related("user", "course").get(signature_hash=signature_hash)
        except Certificate.DoesNotExist:
            return Response({"verified": False, "detail": "Invalid signature hash. Verification failed."}, status=status.HTTP_404_NOT_FOUND)
            
        return Response({
            "verified": True,
            "certificate_id": certificate.id,
            "student_email": certificate.user.email,
            "student_name": f"{certificate.user.first_name} {certificate.user.last_name}".strip() or certificate.user.username,
            "course_title": certificate.course.title,
            "signature_hash": certificate.signature_hash,
            "issued_at": certificate.issued_at
        }, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="restore")
    def restore(self, request, id=None):
        """
        POST /certificates/{id}/restore/
        Restores a soft-deleted certificate.
        """
        user = self.request.user
        is_privileged = user.is_superuser or (
            user.is_teacher_cbac
        )
        if not is_privileged:
            return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)
            
        cert = Certificate.all_objects.filter(id=id, deleted_at__isnull=False).first()
        if not cert:
            return Response({"detail": "Certificate not found or not soft-deleted."}, status=status.HTTP_404_NOT_FOUND)
            
        cert.restore()
        return Response(CertificateSerializer(cert).data, status=status.HTTP_200_OK)


class BadgeViewSet(viewsets.ModelViewSet):
    queryset = Badge.objects.all().order_by("-created_at")
    serializer_class = BadgeSerializer
    permission_classes = [HasRBACPermission]
    pagination_class = EnterprisePagination
    lookup_field = "id"
    
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    if DjangoFilterBackend is not None:
        filter_backends.append(DjangoFilterBackend)
        
    search_fields = ["title", "description"]
    ordering_fields = ["created_at", "title"]
    ordering = ["-created_at"]

    required_permissions = {
        "list": "lms:badge:view",
        "retrieve": "lms:badge:view",
        "create": "lms:badge:create",
        "update": "lms:badge:update",
        "partial_update": "lms:badge:update",
        "destroy": "lms:badge:delete",
        "restore": "lms:badge:update",
    }

    def get_queryset(self):
        user = self.request.user
        include_deleted = self.request.query_params.get("include_deleted", "false").lower() == "true"
        is_privileged = user.is_authenticated and (
            user.is_superuser or (
                user.is_teacher_cbac
            )
        )
        manager = Badge.all_objects if (include_deleted and is_privileged) else Badge.objects
        return manager.all().order_by("-created_at")

    @action(detail=True, methods=["post"], url_path="award")
    def award(self, request, id=None):
        """
        POST /badges/{id}/award/
        Awards this badge to a student.
        """
        user = request.user
        is_privileged = user.is_superuser or (
            user.is_teacher_cbac
        )
        if not is_privileged:
            return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)
            
        try:
            badge = self.get_object()
        except Badge.DoesNotExist:
            return Response({"detail": "Badge not found."}, status=status.HTTP_404_NOT_FOUND)
            
        from apps.users.models import User
        student_id = request.data.get("student_id") or request.data.get("user_id") or request.data.get("student")
        if not student_id:
            return Response({"error": "student_id/user_id is required."}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            student = User.objects.get(id=student_id)
        except (User.DoesNotExist, ValueError, TypeError):
            return Response({"error": "Valid student user not found."}, status=status.HTTP_404_NOT_FOUND)
            
        user_badge, created = UserBadge.objects.get_or_create(user=student, badge=badge)
        if not created:
            return Response({
                "detail": "Badge already awarded.",
                "data": UserBadgeSerializer(user_badge).data
            }, status=status.HTTP_200_OK)
            
        return Response({
            "detail": "Badge awarded successfully.",
            "data": UserBadgeSerializer(user_badge).data
        }, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"], url_path="restore")
    def restore(self, request, id=None):
        """
        POST /badges/{id}/restore/
        Restores a soft-deleted badge.
        """
        user = self.request.user
        is_privileged = user.is_superuser or (
            user.is_teacher_cbac
        )
        if not is_privileged:
            return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)
            
        badge = Badge.all_objects.filter(id=id, deleted_at__isnull=False).first()
        if not badge:
            return Response({"detail": "Badge not found or not soft-deleted."}, status=status.HTTP_404_NOT_FOUND)
            
        badge.restore()
        return Response(BadgeSerializer(badge).data, status=status.HTTP_200_OK)


class UserBadgeViewSet(viewsets.ModelViewSet):
    queryset = UserBadge.objects.select_related("user", "badge").all().order_by("-unlocked_at")
    serializer_class = UserBadgeSerializer
    permission_classes = [HasRBACPermission]
    pagination_class = EnterprisePagination
    lookup_field = "id"
    
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    if DjangoFilterBackend is not None:
        filter_backends.append(DjangoFilterBackend)
        
    search_fields = ["user__email", "badge__title"]
    ordering_fields = ["unlocked_at"]
    ordering = ["-unlocked_at"]

    required_permissions = {
        "list": "lms:user_badge:view",
        "retrieve": "lms:user_badge:view",
        "create": "lms:user_badge:create",
        "update": "lms:user_badge:update",
        "partial_update": "lms:user_badge:update",
        "destroy": "lms:user_badge:delete",
        "restore": "lms:user_badge:update",
    }

    def get_queryset(self):
        user = self.request.user
        include_deleted = self.request.query_params.get("include_deleted", "false").lower() == "true"
        is_privileged = user.is_authenticated and (
            user.is_superuser or (
                user.is_teacher_cbac
            )
        )
        manager = UserBadge.all_objects if (include_deleted and is_privileged) else UserBadge.objects
        queryset = manager.select_related("user", "badge").all()
        
        if not is_privileged:
            queryset = queryset.filter(user=user)
            
        return queryset.order_by("-unlocked_at")

    @action(detail=True, methods=["post"], url_path="restore")
    def restore(self, request, id=None):
        """
        POST /user-badges/{id}/restore/
        Restores a soft-deleted user-badge relationship.
        """
        user = self.request.user
        is_privileged = user.is_superuser or (
            user.is_teacher_cbac
        )
        if not is_privileged:
            return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)
            
        ub = UserBadge.all_objects.filter(id=id, deleted_at__isnull=False).first()
        if not ub:
            return Response({"detail": "UserBadge relation not found or not soft-deleted."}, status=status.HTTP_404_NOT_FOUND)
            
        ub.restore()
        return Response(UserBadgeSerializer(ub).data, status=status.HTTP_200_OK)


class TeacherApplicationViewSet(viewsets.ModelViewSet):
    queryset = TeacherApplication.objects.select_related("user", "reviewed_by").all().order_by("-created_at")
    serializer_class = TeacherApplicationSerializer
    permission_classes = [HasRBACPermission]
    lookup_field = "id"
    required_permissions = {
        "list": "lms:teacher_application:view",
        "retrieve": "lms:teacher_application:view",
        "create": "lms:teacher_application:create",
        "update": "lms:teacher_application:update",
        "partial_update": "lms:teacher_application:update",
        "destroy": "lms:teacher_application:delete",
    }

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or (user.role and user.role.name in ["SUPERADMIN", "ADMIN"]):
            return self.queryset
        return self.queryset.filter(user=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=["post"])
    def process_application(self, request, pk=None):
        application = self.get_object()
        status_choice = request.data.get("status")
        if status_choice not in ["APPROVED", "REJECTED"]:
            return Response({"error": "Invalid status option"}, status=status.HTTP_400_BAD_REQUEST)
            
        application.status = status_choice
        application.reviewed_by = request.user
        application.updated_at = timezone.now()
        application.save()
        
        return Response(TeacherApplicationSerializer(application).data)


class TeacherClassViewSet(viewsets.ModelViewSet):
    queryset = TeacherClass.objects.select_related("teacher", "course").all().order_by("-created_at")
    serializer_class = TeacherClassSerializer
    permission_classes = [HasRBACPermission]
    lookup_field = "id"
    required_permissions = {
        "list": "lms:teacher_class:view",
        "retrieve": "lms:teacher_class:view",
        "create": "lms:teacher_class:create",
        "update": "lms:teacher_class:update",
        "partial_update": "lms:teacher_class:update",
        "destroy": "lms:teacher_class:delete",
    }

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or (user.role and user.role.name in ["SUPERADMIN", "ADMIN"]):
            return self.queryset
        return self.queryset.filter(teacher=user)


class StudentEnrollmentViewSet(viewsets.ModelViewSet):
    queryset = StudentEnrollment.objects.select_related("student", "course").all().order_by("-enrolled_at")
    serializer_class = StudentEnrollmentSerializer
    permission_classes = [HasRBACPermission]
    pagination_class = EnterprisePagination
    lookup_field = "id"
    
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    if DjangoFilterBackend is not None:
        filter_backends.append(DjangoFilterBackend)
        
    search_fields = ["student__email", "course__title", "status"]
    ordering_fields = ["enrolled_at", "status"]
    ordering = ["-enrolled_at"]

    required_permissions = {
        "list": "lms:enrollment:view",
        "retrieve": "lms:enrollment:view",
        "create": "lms:enrollment:create",
        "update": "lms:enrollment:update",
        "partial_update": "lms:enrollment:update",
        "destroy": "lms:enrollment:delete",
        "restore": "lms:enrollment:update",
    }

    def get_queryset(self):
        user = self.request.user
        include_deleted = self.request.query_params.get("include_deleted", "false").lower() == "true"
        is_privileged = user.is_authenticated and (
            user.is_superuser or (
                user.is_teacher_cbac
            )
        )
        manager = StudentEnrollment.all_objects if (include_deleted and is_privileged) else StudentEnrollment.objects
        queryset = manager.select_related("student", "course").all()
        
        if not is_privileged:
            queryset = queryset.filter(student=user)
            
        status_val = self.request.query_params.get("status")
        if status_val:
            queryset = queryset.filter(status=status_val)
            
        course_id = self.request.query_params.get("course") or self.request.query_params.get("course_id")
        if course_id:
            queryset = queryset.filter(course_id=course_id)
            
        student_id = self.request.query_params.get("student") or self.request.query_params.get("student_id")
        if student_id:
            queryset = queryset.filter(student_id=student_id)
            
        return queryset.order_by("-enrolled_at")

    def perform_create(self, serializer):
        serializer.save(student=self.request.user)

    @action(detail=True, methods=["post"], url_path="restore")
    def restore(self, request, id=None):
        """
        POST /student-enrollments/{id}/restore/
        Restores a soft-deleted enrollment.
        """
        user = self.request.user
        is_privileged = user.is_superuser or (
            user.is_teacher_cbac
        )
        if not is_privileged:
            return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)
            
        enrollment = StudentEnrollment.all_objects.filter(id=id, deleted_at__isnull=False).first()
        if not enrollment:
            return Response({"detail": "Enrollment not found or not soft-deleted."}, status=status.HTTP_404_NOT_FOUND)
            
        enrollment.restore()
        return Response(StudentEnrollmentSerializer(enrollment).data, status=status.HTTP_200_OK)


EnrollmentViewSet = StudentEnrollmentViewSet


class CourseViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling full CRUD operations on courses with UUID lookup,
    soft delete support, RBAC permissions, custom filtering, searching, ordering, pagination, and nested serializer support.
    """
    queryset = CourseStructure.objects.filter(node_type="COURSE").order_by("display_order")
    serializer_class = CourseSerializer
    permission_classes = [IsTeacherOrAdminOrReadOnly]
    pagination_class = EnterprisePagination
    lookup_field = "id"

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["title", "slug", "description"]
    ordering_fields = ["display_order", "title", "created_at", "updated_at"]
    ordering = ["display_order"]

    # RBAC configuration for HasRBACPermission
    required_permissions = {
        "list": "lms:course:view",
        "retrieve": "lms:course:view",
        "create": "lms:course:create",
        "update": "lms:course:update",
        "partial_update": "lms:course:update",
        "destroy": "lms:course:delete",
        "restore": "lms:course:update",
    }

    def get_queryset(self):
        """
        Retrieves the optimized queryset of Course nodes, optionally including soft-deleted ones for authorized roles.
        Filters by subject and program if passed in query parameters.
        """
        user = self.request.user
        include_deleted = self.request.query_params.get("include_deleted", "false").lower() == "true"
        is_privileged = user.is_authenticated and (
            user.is_superuser or (
                user.is_teacher_cbac
            )
        )

        if include_deleted and is_privileged:
            queryset = CourseStructure.all_objects.filter(node_type="COURSE")
        else:
            queryset = CourseStructure.objects.filter(node_type="COURSE")

        # Optimization: select_related parent (Subject) and parent__parent (Program)
        # prefetch_related children (Chapters) and children__children (Lessons)
        queryset = queryset.select_related("parent", "parent__parent").prefetch_related(
            "children",
            "children__children"
        )

        # Filtering by Subject (parent)
        subject_id = (
            self.request.query_params.get("subject") or 
            self.request.query_params.get("subject_id") or 
            self.request.query_params.get("parent") or 
            self.request.query_params.get("parent_id")
        )
        if subject_id:
            queryset = queryset.filter(parent_id=subject_id)

        # Filtering by Program (grandparent)
        program_id = (
            self.request.query_params.get("program") or 
            self.request.query_params.get("program_id")
        )
        if program_id:
            queryset = queryset.filter(parent__parent_id=program_id)

        # Filtering by slug
        slug = self.request.query_params.get("slug")
        if slug:
            queryset = queryset.filter(slug=slug)

        return queryset.order_by("display_order")

    def get_serializer_class(self):
        """
        Determines the appropriate serializer based on the current action.
        - 'list': CourseListSerializer (lightweight list representation with chapters count)
        - 'retrieve': CourseDetailSerializer (detailed view with nested chapters list)
        - default (create, update, etc.): CourseSerializer (input validation and flat representation)
        """
        if self.action == "list":
            return CourseListSerializer
        elif self.action == "retrieve":
            return CourseDetailSerializer
        return CourseSerializer

    @action(detail=True, methods=["get"], url_path="structure")
    def structure(self, request, id=None):
        """
        GET /courses/{id}/structure/
        Returns the full nested course hierarchy starting from this course node.
        """
        queryset = self.get_queryset()
        try:
            course = queryset.get(id=id)
        except CourseStructure.DoesNotExist:
            return Response({"detail": "Course not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = CourseStructureNodeSerializer(course, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="restore")
    def restore(self, request, id=None):
        """
        POST /courses/{id}/restore/
        Allows restoring a soft-deleted course. Restricted to admins/teachers.
        """
        user = self.request.user
        is_privileged = user.is_superuser or (
            user.is_teacher_cbac
        )
        if not is_privileged:
            return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

        course = CourseStructure.all_objects.filter(id=id, node_type="COURSE", deleted_at__isnull=False).first()
        if not course:
            return Response({"detail": "Course not found or not soft-deleted."}, status=status.HTTP_404_NOT_FOUND)

        course.restore()
        return Response({"detail": "Course restored successfully."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get"], url_path="chapters")
    def chapters(self, request, id=None):
        """
        GET /courses/{id}/chapters/
        Returns active chapters associated with this specific course.
        """
        course = self.get_object()
        user = self.request.user
        include_deleted = self.request.query_params.get("include_deleted", "false").lower() == "true"
        is_privileged = user.is_authenticated and (
            user.is_superuser or (
                user.is_teacher_cbac
            )
        )

        if include_deleted and is_privileged:
            chapters = CourseStructure.all_objects.filter(parent=course, node_type="CHAPTER")
        else:
            chapters = CourseStructure.objects.filter(parent=course, node_type="CHAPTER")

        # Filtering by slug if specified in query params
        slug = request.query_params.get("slug")
        if slug:
            chapters = chapters.filter(slug=slug)

        # Prefetch children (topics) to optimize count
        chapters = chapters.prefetch_related("children")

        # Support search and ordering if query params provided
        search = request.query_params.get("search")
        if search:
            chapters = chapters.filter(
                models.Q(title__icontains=search) |
                models.Q(slug__icontains=search) |
                models.Q(description__icontains=search)
            )

        ordering = request.query_params.get("ordering", "display_order")
        if ordering in ["display_order", "-display_order", "title", "-title", "created_at", "-created_at", "updated_at", "-updated_at"]:
            chapters = chapters.order_by(ordering)
        else:
            chapters = chapters.order_by("display_order")

        page = self.paginate_queryset(chapters)
        if page is not None:
            serializer = ChapterListSerializer(page, many=True, context={"request": request})
            return self.get_paginated_response(serializer.data)

        serializer = ChapterListSerializer(chapters, many=True, context={"request": request})
        return Response(serializer.data)

    @action(detail=True, methods=["get"], url_path="enrollments")
    def enrollments(self, request, id=None):
        """
        GET /courses/{id}/enrollments/
        Returns all enrollments for this course. Supports filtering, search, ordering, pagination.
        """
        try:
            course = CourseStructure.objects.get(id=id, node_type="COURSE")
        except CourseStructure.DoesNotExist:
            return Response({"detail": "Course not found."}, status=status.HTTP_404_NOT_FOUND)
            
        user = request.user
        include_deleted = request.query_params.get("include_deleted", "false").lower() == "true"
        is_privileged = user.is_authenticated and (
            user.is_superuser or (
                user.is_teacher_cbac
            )
        )
        
        manager = StudentEnrollment.all_objects if (include_deleted and is_privileged) else StudentEnrollment.objects
        queryset = manager.select_related("student", "course").filter(course=course).order_by("-enrolled_at")
        
        if not is_privileged:
            queryset = queryset.filter(student=user)
            
        status_val = request.query_params.get("status")
        if status_val:
            queryset = queryset.filter(status=status_val)
            
        search_query = request.query_params.get("search")
        if search_query:
            queryset = queryset.filter(
                models.Q(student__email__icontains=search_query) | 
                models.Q(status__icontains=search_query)
            )
            
        paginator = EnterprisePagination()
        page = paginator.paginate_queryset(queryset, request, view=self)
        if page is not None:
            serializer = StudentEnrollmentSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)
            
        serializer = StudentEnrollmentSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"], url_path="progress")
    def progress(self, request, id=None):
        """
        GET /courses/{id}/progress/
        Returns progress records for this course. Supports filtering, search, ordering, pagination.
        """
        try:
            course = CourseStructure.objects.get(id=id, node_type="COURSE")
        except CourseStructure.DoesNotExist:
            return Response({"detail": "Course not found."}, status=status.HTTP_404_NOT_FOUND)
            
        user = request.user
        include_deleted = request.query_params.get("include_deleted", "false").lower() == "true"
        is_privileged = user.is_authenticated and (
            user.is_superuser or (
                user.is_teacher_cbac
            )
        )
        
        manager = LearningProgress.all_objects if (include_deleted and is_privileged) else LearningProgress.objects
        
        # Filter progress for course itself and all nested chapters/lessons/topics/practices under the course structure.
        queryset = manager.select_related("student", "node").filter(
            models.Q(node=course) |
            models.Q(node__parent=course) |
            models.Q(node__parent__parent=course) |
            models.Q(node__parent__parent__parent=course) |
            models.Q(node__parent__parent__parent__parent=course)
        ).order_by("-last_accessed_at")
        
        if not is_privileged:
            queryset = queryset.filter(student=user)
            
        is_completed_val = request.query_params.get("is_completed")
        if is_completed_val:
            queryset = queryset.filter(is_completed=is_completed_val.lower() == "true")
            
        search_query = request.query_params.get("search")
        if search_query:
            queryset = queryset.filter(
                models.Q(student__email__icontains=search_query) |
                models.Q(node__title__icontains=search_query)
            )
            
        paginator = EnterprisePagination()
        page = paginator.paginate_queryset(queryset, request, view=self)
        if page is not None:
            serializer = LearningProgressSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)
            
        serializer = LearningProgressSerializer(queryset, many=True)
        return Response(serializer.data)


class ChapterViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling full CRUD operations on Chapters (node_type="CHAPTER") with UUID lookup,
    soft delete support, RBAC permissions, custom filtering, searching, ordering, pagination, and nested serializer support.
    """
    queryset = CourseStructure.objects.filter(node_type="CHAPTER").order_by("display_order")
    serializer_class = ChapterSerializer
    permission_classes = [IsTeacherOrAdminOrReadOnly]
    pagination_class = EnterprisePagination
    lookup_field = "id"

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["title", "slug", "description"]
    ordering_fields = ["display_order", "title", "created_at", "updated_at"]
    ordering = ["display_order"]

    # RBAC configuration for HasRBACPermission
    required_permissions = {
        "list": "lms:chapter:view",
        "retrieve": "lms:chapter:view",
        "create": "lms:chapter:create",
        "update": "lms:chapter:update",
        "partial_update": "lms:chapter:update",
        "destroy": "lms:chapter:delete",
        "restore": "lms:chapter:update",
    }

    def get_queryset(self):
        """
        Retrieves the optimized queryset of Chapter nodes, optionally including soft-deleted ones for authorized roles.
        Supports filtering by program, subject, course, and slug.
        """
        user = self.request.user
        include_deleted = self.request.query_params.get("include_deleted", "false").lower() == "true"
        is_privileged = user.is_authenticated and (
            user.is_superuser or (
                user.is_teacher_cbac
            )
        )

        if include_deleted and is_privileged:
            queryset = CourseStructure.all_objects.filter(node_type="CHAPTER")
        else:
            queryset = CourseStructure.objects.filter(node_type="CHAPTER")

        # Optimization: select_related parent (Course), parent__parent (Subject), parent__parent__parent (Program)
        # prefetch_related children (Topics)
        queryset = queryset.select_related("parent", "parent__parent", "parent__parent__parent").prefetch_related("children")

        # Filtering by Course (parent)
        course_id = (
            self.request.query_params.get("course") or 
            self.request.query_params.get("course_id") or 
            self.request.query_params.get("parent") or 
            self.request.query_params.get("parent_id")
        )
        if course_id:
            queryset = queryset.filter(parent_id=course_id)

        # Filtering by Subject (grandparent)
        subject_id = (
            self.request.query_params.get("subject") or 
            self.request.query_params.get("subject_id")
        )
        if subject_id:
            queryset = queryset.filter(parent__parent_id=subject_id)

        # Filtering by Program (great-grandparent)
        program_id = (
            self.request.query_params.get("program") or 
            self.request.query_params.get("program_id")
        )
        if program_id:
            queryset = queryset.filter(parent__parent__parent_id=program_id)

        # Filtering by slug
        slug = self.request.query_params.get("slug")
        if slug:
            queryset = queryset.filter(slug=slug)

        return queryset.order_by("display_order")

    def get_serializer_class(self):
        """
        Determines the appropriate serializer based on the current action.
        - 'list': ChapterListSerializer (lightweight list representation with topics count)
        - 'retrieve': ChapterDetailSerializer (detailed view with nested topics list)
        - default (create, update, etc.): ChapterSerializer (input validation and flat representation)
        """
        if self.action == "list":
            return ChapterListSerializer
        elif self.action == "retrieve":
            return ChapterDetailSerializer
        return ChapterSerializer

    @action(detail=True, methods=["post"], url_path="restore")
    def restore(self, request, id=None):
        """
        POST /chapters/{id}/restore/
        Allows restoring a soft-deleted chapter. Restricted to admins/teachers.
        """
        user = self.request.user
        is_privileged = user.is_superuser or (
            user.is_teacher_cbac
        )
        if not is_privileged:
            return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

        chapter = CourseStructure.all_objects.filter(id=id, node_type="CHAPTER", deleted_at__isnull=False).first()
        if not chapter:
            return Response({"detail": "Chapter not found or not soft-deleted."}, status=status.HTTP_404_NOT_FOUND)

        chapter.restore()
        return Response({"detail": "Chapter restored successfully."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get"], url_path="topics")
    def topics(self, request, id=None):
        """
        GET /chapters/{id}/topics/
        Returns active topics associated with this specific chapter.
        """
        chapter = self.get_object()
        user = self.request.user
        include_deleted = self.request.query_params.get("include_deleted", "false").lower() == "true"
        is_privileged = user.is_authenticated and (
            user.is_superuser or (
                user.is_teacher_cbac
            )
        )

        if include_deleted and is_privileged:
            topics = CourseStructure.all_objects.filter(parent=chapter, node_type="TOPIC")
        else:
            topics = CourseStructure.objects.filter(parent=chapter, node_type="TOPIC")

        # Filtering by slug if specified in query params
        slug = request.query_params.get("slug")
        if slug:
            topics = topics.filter(slug=slug)

        # Prefetch children (subtopics) to optimize count
        topics = topics.prefetch_related("children")

        # Support search and ordering if query params provided
        search = request.query_params.get("search")
        if search:
            topics = topics.filter(
                models.Q(title__icontains=search) |
                models.Q(slug__icontains=search) |
                models.Q(description__icontains=search)
            )

        ordering = request.query_params.get("ordering", "display_order")
        if ordering in ["display_order", "-display_order", "title", "-title", "created_at", "-created_at", "updated_at", "-updated_at"]:
            topics = topics.order_by(ordering)
        else:
            topics = topics.order_by("display_order")

        page = self.paginate_queryset(topics)
        if page is not None:
            serializer = TopicListSerializer(page, many=True, context={"request": request})
            return self.get_paginated_response(serializer.data)

        serializer = TopicListSerializer(topics, many=True, context={"request": request})
        return Response(serializer.data)



class LessonViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling full CRUD operations on Lessons (node_type="LESSON") with UUID lookup,
    soft delete support, RBAC permissions, custom filtering, searching, ordering, pagination, and nested serializer support.
    """
    queryset = CourseStructure.objects.filter(node_type="LESSON").order_by("display_order")
    serializer_class = LessonSerializer
    permission_classes = [IsTeacherOrAdminOrReadOnly]
    pagination_class = EnterprisePagination
    lookup_field = "id"

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    if DjangoFilterBackend is not None:
        filter_backends.append(DjangoFilterBackend)

    search_fields = ["title", "slug", "description"]
    ordering_fields = ["display_order", "title", "created_at", "updated_at"]
    ordering = ["display_order"]

    # RBAC configuration for HasRBACPermission
    required_permissions = {
        "list": "lms:lesson:view",
        "retrieve": "lms:lesson:view",
        "create": "lms:lesson:create",
        "update": "lms:lesson:update",
        "partial_update": "lms:lesson:update",
        "destroy": "lms:lesson:delete",
        "restore": "lms:lesson:update",
    }

    def get_queryset(self):
        """
        Retrieves the optimized queryset of Lesson nodes, optionally including soft-deleted ones for authorized roles.
        Supports filtering by program, subject, course, chapter, topic, subtopic, and slug.
        """
        user = self.request.user
        include_deleted = self.request.query_params.get("include_deleted", "false").lower() == "true"
        is_privileged = user.is_authenticated and (
            user.is_superuser or (
                user.is_teacher_cbac
            )
        )

        if include_deleted and is_privileged:
            queryset = CourseStructure.all_objects.filter(node_type="LESSON")
        else:
            queryset = CourseStructure.objects.filter(node_type="LESSON")

        # Optimization: select_related ancestors up to Program
        queryset = queryset.select_related(
            "parent",
            "parent__parent",
            "parent__parent__parent",
            "parent__parent__parent__parent",
            "parent__parent__parent__parent__parent",
            "parent__parent__parent__parent__parent__parent"
        )

        # Filtering by Subtopic (parent)
        subtopic_id = (
            self.request.query_params.get("subtopic") or 
            self.request.query_params.get("subtopic_id") or 
            self.request.query_params.get("parent") or 
            self.request.query_params.get("parent_id")
        )
        if subtopic_id:
            queryset = queryset.filter(parent_id=subtopic_id)

        # Filtering by Topic (grandparent)
        topic_id = (
            self.request.query_params.get("topic") or 
            self.request.query_params.get("topic_id")
        )
        if topic_id:
            queryset = queryset.filter(parent__parent_id=topic_id)

        # Filtering by Chapter (great-grandparent)
        chapter_id = (
            self.request.query_params.get("chapter") or 
            self.request.query_params.get("chapter_id")
        )
        if chapter_id:
            queryset = queryset.filter(parent__parent__parent_id=chapter_id)

        # Filtering by Course (great-great-grandparent)
        course_id = (
            self.request.query_params.get("course") or 
            self.request.query_params.get("course_id")
        )
        if course_id:
            queryset = queryset.filter(parent__parent__parent__parent_id=course_id)

        # Filtering by Subject (great-great-great-grandparent)
        subject_id = (
            self.request.query_params.get("subject") or 
            self.request.query_params.get("subject_id")
        )
        if subject_id:
            queryset = queryset.filter(parent__parent__parent__parent__parent_id=subject_id)

        # Filtering by Program (great-great-great-great-grandparent)
        program_id = (
            self.request.query_params.get("program") or 
            self.request.query_params.get("program_id")
        )
        if program_id:
            queryset = queryset.filter(parent__parent__parent__parent__parent__parent_id=program_id)

        # Filtering by slug
        slug = self.request.query_params.get("slug")
        if slug:
            queryset = queryset.filter(slug=slug)

        return queryset.order_by("display_order")

    def get_serializer_class(self):
        """
        Determines the appropriate serializer based on the current action.
        - 'list': LessonListSerializer (lightweight list representation)
        - 'retrieve': LessonDetailSerializer (detailed view)
        - default (create, update, etc.): LessonSerializer (input validation and flat representation)
        """
        if self.action == "list":
            return LessonListSerializer
        elif self.action == "retrieve":
            return LessonDetailSerializer
        return LessonSerializer

    @action(detail=True, methods=["post"], url_path="restore")
    def restore(self, request, id=None):
        """
        POST /lessons/{id}/restore/
        Allows restoring a soft-deleted lesson. Restricted to admins/teachers.
        """
        user = self.request.user
        is_privileged = user.is_superuser or (
            user.is_teacher_cbac
        )
        if not is_privileged:
            return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

        lesson = CourseStructure.all_objects.filter(id=id, node_type="LESSON", deleted_at__isnull=False).first()
        if not lesson:
            return Response({"detail": "Lesson not found or not soft-deleted."}, status=status.HTTP_404_NOT_FOUND)

        lesson.restore()
        return Response({"detail": "Lesson restored successfully."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get"], url_path="assignments")
    def assignments(self, request, id=None):
        """
        GET /lessons/{id}/assignments/
        Returns assignments associated with this specific lesson.
        """
        lesson = self.get_object()
        user = self.request.user
        include_deleted = self.request.query_params.get("include_deleted", "false").lower() == "true"
        is_privileged = user.is_authenticated and (
            user.is_superuser or (
                user.is_teacher_cbac
            )
        )

        if include_deleted and is_privileged:
            assignments = Assignment.objects.filter(lesson=lesson)
        else:
            deleted_ids = get_deleted_assignments()
            assignments = Assignment.objects.filter(lesson=lesson).exclude(id__in=deleted_ids)

        # Support search and ordering if query params provided
        search = request.query_params.get("search")
        if search:
            assignments = assignments.filter(
                models.Q(title__icontains=search) |
                models.Q(instructions__icontains=search)
            )

        ordering = request.query_params.get("ordering", "-created_at")
        if ordering in ["title", "-title", "created_at", "-created_at", "max_points", "-max_points"]:
            assignments = assignments.order_by(ordering)
        else:
            assignments = assignments.order_by("-created_at")

        page = self.paginate_queryset(assignments)
        if page is not None:
            serializer = AssignmentListSerializer(page, many=True, context={"request": request})
            return self.get_paginated_response(serializer.data)

        serializer = AssignmentListSerializer(assignments, many=True, context={"request": request})
        return Response(serializer.data)

    @action(detail=True, methods=["get"], url_path="practice")
    def practice(self, request, id=None):
        """
        GET /lessons/{id}/practice/
        Returns practice nodes associated with this specific lesson.
        """
        lesson = self.get_object()
        user = self.request.user
        include_deleted = request.query_params.get("include_deleted", "false").lower() == "true"
        is_privileged = user.is_authenticated and (
            user.is_superuser or (
                user.is_teacher_cbac
            )
        )
        
        manager = CourseStructure.all_objects if (include_deleted and is_privileged) else CourseStructure.objects
        queryset = manager.filter(parent=lesson).order_by("display_order")
        
        search = request.query_params.get("search")
        if search:
            queryset = queryset.filter(
                models.Q(title__icontains=search) |
                models.Q(description__icontains=search)
            )
            
        ordering = request.query_params.get("ordering", "-created_at")
        if ordering in ["title", "-title", "created_at", "-created_at", "display_order", "-display_order"]:
            queryset = queryset.order_by(ordering)
        else:
            queryset = queryset.order_by("display_order")
            
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = PracticeListSerializer(page, many=True, context={"request": request})
            return self.get_paginated_response(serializer.data)
            
        serializer = PracticeListSerializer(queryset, many=True, context={"request": request})
        return Response(serializer.data)

    @action(detail=True, methods=["get"], url_path="projects")
    def projects(self, request, id=None):
        """
        GET /lessons/{id}/projects/
        Returns projects associated with this specific lesson.
        """
        lesson = self.get_object()
        user = self.request.user
        include_deleted = request.query_params.get("include_deleted", "false").lower() == "true"
        is_privileged = user.is_authenticated and (
            user.is_superuser or (
                user.is_teacher_cbac
            )
        )
        
        manager = Project.all_objects if (include_deleted and is_privileged) else Project.objects
        queryset = manager.filter(
            models.Q(course=lesson) |
            models.Q(course__parent=lesson) |
            models.Q(course__parent__parent=lesson)
        ).order_by("-created_at")
        
        search = request.query_params.get("search")
        if search:
            queryset = queryset.filter(
                models.Q(title__icontains=search) |
                models.Q(description__icontains=search)
            )
            
        ordering = request.query_params.get("ordering", "-created_at")
        if ordering in ["title", "-title", "created_at", "-created_at"]:
            queryset = queryset.order_by(ordering)
        else:
            queryset = queryset.order_by("-created_at")
            
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ProjectListSerializer(page, many=True, context={"request": request})
            return self.get_paginated_response(serializer.data)
            
        serializer = ProjectListSerializer(queryset, many=True, context={"request": request})
        return Response(serializer.data)


class ProgramViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling full CRUD operations on Programs (node_type="PROGRAM") with UUID lookup,
    soft delete support, RBAC permissions, custom filtering, searching, ordering, pagination, and nested serializer support.
    """
    queryset = CourseStructure.objects.filter(node_type="PROGRAM").order_by("display_order")
    serializer_class = ProgramSerializer
    permission_classes = [IsTeacherOrAdminOrReadOnly]
    pagination_class = EnterprisePagination
    lookup_field = "id"

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["title", "slug", "description"]
    ordering_fields = ["display_order", "title", "created_at", "updated_at"]
    ordering = ["display_order"]

    # RBAC configuration for HasRBACPermission (if utilized as alternative or fallback)
    required_permissions = {
        "list": "lms:program:view",
        "retrieve": "lms:program:view",
        "create": "lms:program:create",
        "update": "lms:program:update",
        "partial_update": "lms:program:update",
        "destroy": "lms:program:delete",
        "restore": "lms:program:update",
    }

    def get_queryset(self):
        """
        Retrieves the optimized queryset of Program nodes, optionally including soft-deleted ones for authorized roles.
        """
        user = self.request.user
        include_deleted = self.request.query_params.get("include_deleted", "false").lower() == "true"
        is_privileged = user.is_authenticated and (
            user.is_superuser or (
                user.is_teacher_cbac
            )
        )

        if include_deleted and is_privileged:
            queryset = CourseStructure.all_objects.filter(node_type="PROGRAM")
        else:
            queryset = CourseStructure.objects.filter(node_type="PROGRAM")

        # Optimization: prefetch recursive child structures for nested serialization
        queryset = queryset.prefetch_related(
            "children",
            "children__children",
            "children__children__children"
        )

        # Filtering by parent if specified in the query params
        parent_id = self.request.query_params.get("parent") or self.request.query_params.get("parent_id")
        if parent_id:
            queryset = queryset.filter(parent_id=parent_id)

        # Filtering by slug if specified in the query params
        slug = self.request.query_params.get("slug")
        if slug:
            queryset = queryset.filter(slug=slug)

        return queryset.order_by("display_order")

    def get_serializer_class(self):
        """
        Determines the appropriate serializer based on the current action.
        - 'list': ProgramListSerializer (lightweight list representation)
        - 'retrieve': ProgramDetailSerializer (detailed view with full recursive children tree)
        - default (create, update, etc.): ProgramSerializer (input validation and flat representation)
        """
        if self.action == "list":
            return ProgramListSerializer
        elif self.action == "retrieve":
            return ProgramDetailSerializer
        return ProgramSerializer

    @action(detail=True, methods=["post"], url_path="restore")
    def restore(self, request, id=None):
        """
        POST /programs/{id}/restore/
        Allows restoring a soft-deleted program. Restricted to admins/teachers.
        """
        user = self.request.user
        is_privileged = user.is_superuser or (
            user.is_teacher_cbac
        )
        if not is_privileged:
            return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

        program = CourseStructure.all_objects.filter(id=id, node_type="PROGRAM", deleted_at__isnull=False).first()
        if not program:
            return Response({"detail": "Program not found or not soft-deleted."}, status=status.HTTP_404_NOT_FOUND)

        program.restore()
        return Response({"detail": "Program restored successfully."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get"], url_path="subjects")
    def subjects(self, request, id=None):
        """
        GET /programs/{id}/subjects/
        Returns active subjects associated with this specific program.
        """
        program = self.get_object()
        user = self.request.user
        include_deleted = self.request.query_params.get("include_deleted", "false").lower() == "true"
        is_privileged = user.is_authenticated and (
            user.is_superuser or (
                user.is_teacher_cbac
            )
        )

        if include_deleted and is_privileged:
            subjects = CourseStructure.all_objects.filter(parent=program, node_type="SUBJECT")
        else:
            subjects = CourseStructure.objects.filter(parent=program, node_type="SUBJECT")

        # Filtering by slug if specified in query params
        slug = request.query_params.get("slug")
        if slug:
            subjects = subjects.filter(slug=slug)

        # Prefetch children (courses) to optimize count
        subjects = subjects.prefetch_related("children")

        # Support search and ordering if query params provided
        search = request.query_params.get("search")
        if search:
            subjects = subjects.filter(
                models.Q(title__icontains=search) |
                models.Q(slug__icontains=search) |
                models.Q(description__icontains=search)
            )

        ordering = request.query_params.get("ordering", "display_order")
        if ordering in ["display_order", "-display_order", "title", "-title", "created_at", "-created_at", "updated_at", "-updated_at"]:
            subjects = subjects.order_by(ordering)
        else:
            subjects = subjects.order_by("display_order")

        page = self.paginate_queryset(subjects)
        if page is not None:
            serializer = SubjectListSerializer(page, many=True, context={"request": request})
            return self.get_paginated_response(serializer.data)

        serializer = SubjectListSerializer(subjects, many=True, context={"request": request})
        return Response(serializer.data)


class SubjectViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling full CRUD operations on Subjects (node_type="SUBJECT") with UUID lookup,
    soft delete support, RBAC permissions, custom filtering, searching, ordering, pagination, and nested serializer support.
    """
    queryset = CourseStructure.objects.filter(node_type="SUBJECT").order_by("display_order")
    serializer_class = SubjectSerializer
    permission_classes = [IsTeacherOrAdminOrReadOnly]
    pagination_class = EnterprisePagination
    lookup_field = "id"

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["title", "slug", "description"]
    ordering_fields = ["display_order", "title", "created_at", "updated_at"]
    ordering = ["display_order"]

    # RBAC configuration for HasRBACPermission
    required_permissions = {
        "list": "lms:subject:view",
        "retrieve": "lms:subject:view",
        "create": "lms:subject:create",
        "update": "lms:subject:update",
        "partial_update": "lms:subject:update",
        "destroy": "lms:subject:delete",
        "restore": "lms:subject:update",
    }

    def get_queryset(self):
        """
        Retrieves the optimized queryset of Subject nodes, optionally including soft-deleted ones for authorized roles.
        """
        user = self.request.user
        include_deleted = self.request.query_params.get("include_deleted", "false").lower() == "true"
        is_privileged = user.is_authenticated and (
            user.is_superuser or (
                user.is_teacher_cbac
            )
        )

        if include_deleted and is_privileged:
            queryset = CourseStructure.all_objects.filter(node_type="SUBJECT")
        else:
            queryset = CourseStructure.objects.filter(node_type="SUBJECT")

        # Optimization: prefetch child courses for nested serialization / count
        queryset = queryset.prefetch_related("children")

        # Filtering by Program (parent) if specified in query params (e.g. program, program_id, parent, parent_id)
        program_id = (
            self.request.query_params.get("program") or 
            self.request.query_params.get("program_id") or 
            self.request.query_params.get("parent") or 
            self.request.query_params.get("parent_id")
        )
        if program_id:
            queryset = queryset.filter(parent_id=program_id)

        # Filtering by slug if specified in query params
        slug = self.request.query_params.get("slug")
        if slug:
            queryset = queryset.filter(slug=slug)

        return queryset.order_by("display_order")

    def get_serializer_class(self):
        """
        Determines the appropriate serializer based on the current action.
        - 'list': SubjectListSerializer (lightweight list representation with count)
        - 'retrieve': SubjectDetailSerializer (detailed view with nested courses list)
        - default (create, update, etc.): SubjectSerializer (input validation and flat representation)
        """
        if self.action == "list":
            return SubjectListSerializer
        elif self.action == "retrieve":
            return SubjectDetailSerializer
        return SubjectSerializer

    @action(detail=True, methods=["post"], url_path="restore")
    def restore(self, request, id=None):
        """
        POST /subjects/{id}/restore/
        Allows restoring a soft-deleted subject. Restricted to admins/teachers.
        """
        user = self.request.user
        is_privileged = user.is_superuser or (
            user.is_teacher_cbac
        )
        if not is_privileged:
            return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

        subject = CourseStructure.all_objects.filter(id=id, node_type="SUBJECT", deleted_at__isnull=False).first()
        if not subject:
            return Response({"detail": "Subject not found or not soft-deleted."}, status=status.HTTP_404_NOT_FOUND)

        subject.restore()
        return Response({"detail": "Subject restored successfully."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get"], url_path="courses")
    def courses(self, request, id=None):
        """
        GET /subjects/{id}/courses/
        Returns active courses associated with this specific subject.
        """
        subject = self.get_object()
        user = self.request.user
        include_deleted = self.request.query_params.get("include_deleted", "false").lower() == "true"
        is_privileged = user.is_authenticated and (
            user.is_superuser or (
                user.is_teacher_cbac
            )
        )

        if include_deleted and is_privileged:
            courses = CourseStructure.all_objects.filter(parent=subject, node_type="COURSE")
        else:
            courses = CourseStructure.objects.filter(parent=subject, node_type="COURSE")

        # Filtering by slug if specified in query params
        slug = request.query_params.get("slug")
        if slug:
            courses = courses.filter(slug=slug)

        # Prefetch children (chapters) to optimize count
        courses = courses.prefetch_related("children")

        # Support search and ordering if query params provided
        search = request.query_params.get("search")
        if search:
            courses = courses.filter(
                models.Q(title__icontains=search) |
                models.Q(slug__icontains=search) |
                models.Q(description__icontains=search)
            )

        ordering = request.query_params.get("ordering", "display_order")
        if ordering in ["display_order", "-display_order", "title", "-title", "created_at", "-created_at", "updated_at", "-updated_at"]:
            courses = courses.order_by(ordering)
        else:
            courses = courses.order_by("display_order")

        page = self.paginate_queryset(courses)
        if page is not None:
            serializer = CourseListSerializer(page, many=True, context={"request": request})
            return self.get_paginated_response(serializer.data)

        serializer = CourseListSerializer(courses, many=True, context={"request": request})
        return Response(serializer.data)


class TopicViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling full CRUD operations on Topics (node_type="TOPIC") with UUID lookup,
    soft delete support, RBAC permissions, custom filtering, searching, ordering, pagination, and nested serializer support.
    """
    queryset = CourseStructure.objects.filter(node_type="TOPIC").order_by("display_order")
    serializer_class = TopicSerializer
    permission_classes = [IsTeacherOrAdminOrReadOnly]
    pagination_class = EnterprisePagination
    lookup_field = "id"

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    if DjangoFilterBackend is not None:
        filter_backends.append(DjangoFilterBackend)

    search_fields = ["title", "slug", "description"]
    ordering_fields = ["display_order", "title", "created_at", "updated_at"]
    ordering = ["display_order"]

    # RBAC configuration for HasRBACPermission
    required_permissions = {
        "list": "lms:topic:view",
        "retrieve": "lms:topic:view",
        "create": "lms:topic:create",
        "update": "lms:topic:update",
        "partial_update": "lms:topic:update",
        "destroy": "lms:topic:delete",
        "restore": "lms:topic:update",
    }

    def get_queryset(self):
        """
        Retrieves the optimized queryset of Topic nodes, optionally including soft-deleted ones for authorized roles.
        Supports filtering by program, subject, course, chapter, and slug.
        """
        user = self.request.user
        include_deleted = self.request.query_params.get("include_deleted", "false").lower() == "true"
        is_privileged = user.is_authenticated and (
            user.is_superuser or (
                user.is_teacher_cbac
            )
        )

        if include_deleted and is_privileged:
            queryset = CourseStructure.all_objects.filter(node_type="TOPIC")
        else:
            queryset = CourseStructure.objects.filter(node_type="TOPIC")

        # Optimization: select_related parent (Chapter), parent__parent (Course),
        # parent__parent__parent (Subject), parent__parent__parent__parent (Program)
        # prefetch_related children (Subtopics)
        queryset = queryset.select_related(
            "parent",
            "parent__parent",
            "parent__parent__parent",
            "parent__parent__parent__parent"
        ).prefetch_related("children")

        # Filtering by Chapter (parent)
        chapter_id = (
            self.request.query_params.get("chapter") or 
            self.request.query_params.get("chapter_id") or 
            self.request.query_params.get("parent") or 
            self.request.query_params.get("parent_id")
        )
        if chapter_id:
            queryset = queryset.filter(parent_id=chapter_id)

        # Filtering by Course (grandparent)
        course_id = (
            self.request.query_params.get("course") or 
            self.request.query_params.get("course_id")
        )
        if course_id:
            queryset = queryset.filter(parent__parent_id=course_id)

        # Filtering by Subject (great-grandparent)
        subject_id = (
            self.request.query_params.get("subject") or 
            self.request.query_params.get("subject_id")
        )
        if subject_id:
            queryset = queryset.filter(parent__parent__parent_id=subject_id)

        # Filtering by Program (great-great-grandparent)
        program_id = (
            self.request.query_params.get("program") or 
            self.request.query_params.get("program_id")
        )
        if program_id:
            queryset = queryset.filter(parent__parent__parent__parent_id=program_id)

        # Filtering by slug
        slug = self.request.query_params.get("slug")
        if slug:
            queryset = queryset.filter(slug=slug)

        return queryset.order_by("display_order")

    def get_serializer_class(self):
        """
        Determines the appropriate serializer based on the current action.
        - 'list': TopicListSerializer (lightweight list representation with subtopics count)
        - 'retrieve': TopicDetailSerializer (detailed view with nested subtopics list)
        - default (create, update, etc.): TopicSerializer (input validation and flat representation)
        """
        if self.action == "list":
            return TopicListSerializer
        elif self.action == "retrieve":
            return TopicDetailSerializer
        return TopicSerializer

    @action(detail=True, methods=["post"], url_path="restore")
    def restore(self, request, id=None):
        """
        POST /topics/{id}/restore/
        Allows restoring a soft-deleted topic. Restricted to admins/teachers.
        """
        user = self.request.user
        is_privileged = user.is_superuser or (
            user.is_teacher_cbac
        )
        if not is_privileged:
            return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

        topic = CourseStructure.all_objects.filter(id=id, node_type="TOPIC", deleted_at__isnull=False).first()
        if not topic:
            return Response({"detail": "Topic not found or not soft-deleted."}, status=status.HTTP_404_NOT_FOUND)

        topic.restore()
        return Response({"detail": "Topic restored successfully."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get"], url_path="subtopics")
    def subtopics(self, request, id=None):
        """
        GET /topics/{id}/subtopics/
        Returns active subtopics associated with this specific topic.
        """
        topic = self.get_object()
        user = self.request.user
        include_deleted = self.request.query_params.get("include_deleted", "false").lower() == "true"
        is_privileged = user.is_authenticated and (
            user.is_superuser or (
                user.is_teacher_cbac
            )
        )

        if include_deleted and is_privileged:
            subtopics = CourseStructure.all_objects.filter(parent=topic, node_type="SUBTOPIC")
        else:
            subtopics = CourseStructure.objects.filter(parent=topic, node_type="SUBTOPIC")

        # Filtering by slug if specified in query params
        slug = request.query_params.get("slug")
        if slug:
            subtopics = subtopics.filter(slug=slug)

        # Prefetch children (lessons) to optimize count
        subtopics = subtopics.prefetch_related("children")

        # Support search and ordering if query params provided
        search = request.query_params.get("search")
        if search:
            subtopics = subtopics.filter(
                models.Q(title__icontains=search) |
                models.Q(slug__icontains=search) |
                models.Q(description__icontains=search)
            )

        ordering = request.query_params.get("ordering", "display_order")
        if ordering in ["display_order", "-display_order", "title", "-title", "created_at", "-created_at", "updated_at", "-updated_at"]:
            subtopics = subtopics.order_by(ordering)
        else:
            subtopics = subtopics.order_by("display_order")

        page = self.paginate_queryset(subtopics)
        if page is not None:
            serializer = SubtopicListSerializer(page, many=True, context={"request": request})
            return self.get_paginated_response(serializer.data)

        serializer = SubtopicListSerializer(subtopics, many=True, context={"request": request})
        return Response(serializer.data)


class SubtopicViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling full CRUD operations on Subtopics (node_type="SUBTOPIC") with UUID lookup,
    soft delete support, RBAC permissions, custom filtering, searching, ordering, pagination, and nested serializer support.
    """
    queryset = CourseStructure.objects.filter(node_type="SUBTOPIC").order_by("display_order")
    serializer_class = SubtopicSerializer
    permission_classes = [IsTeacherOrAdminOrReadOnly]
    pagination_class = EnterprisePagination
    lookup_field = "id"

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    if DjangoFilterBackend is not None:
        filter_backends.append(DjangoFilterBackend)

    search_fields = ["title", "slug", "description"]
    ordering_fields = ["display_order", "title", "created_at", "updated_at"]
    ordering = ["display_order"]

    # RBAC configuration for HasRBACPermission
    required_permissions = {
        "list": "lms:subtopic:view",
        "retrieve": "lms:subtopic:view",
        "create": "lms:subtopic:create",
        "update": "lms:subtopic:update",
        "partial_update": "lms:subtopic:update",
        "destroy": "lms:subtopic:delete",
        "restore": "lms:subtopic:update",
    }

    def get_queryset(self):
        """
        Retrieves the optimized queryset of Subtopic nodes, optionally including soft-deleted ones for authorized roles.
        Supports filtering by program, subject, course, chapter, topic, and slug.
        """
        user = self.request.user
        include_deleted = self.request.query_params.get("include_deleted", "false").lower() == "true"
        is_privileged = user.is_authenticated and (
            user.is_superuser or (
                user.is_teacher_cbac
            )
        )

        if include_deleted and is_privileged:
            queryset = CourseStructure.all_objects.filter(node_type="SUBTOPIC")
        else:
            queryset = CourseStructure.objects.filter(node_type="SUBTOPIC")

        # Optimization: select_related parent (Topic), parent__parent (Chapter),
        # parent__parent__parent (Course), parent__parent__parent__parent (Subject),
        # parent__parent__parent__parent__parent (Program)
        # prefetch_related children (Lessons)
        queryset = queryset.select_related(
            "parent",
            "parent__parent",
            "parent__parent__parent",
            "parent__parent__parent__parent",
            "parent__parent__parent__parent__parent"
        ).prefetch_related("children")

        # Filtering by Topic (parent)
        topic_id = (
            self.request.query_params.get("topic") or 
            self.request.query_params.get("topic_id") or 
            self.request.query_params.get("parent") or 
            self.request.query_params.get("parent_id")
        )
        if topic_id:
            queryset = queryset.filter(parent_id=topic_id)

        # Filtering by Chapter (grandparent)
        chapter_id = (
            self.request.query_params.get("chapter") or 
            self.request.query_params.get("chapter_id")
        )
        if chapter_id:
            queryset = queryset.filter(parent__parent_id=chapter_id)

        # Filtering by Course (great-grandparent)
        course_id = (
            self.request.query_params.get("course") or 
            self.request.query_params.get("course_id")
        )
        if course_id:
            queryset = queryset.filter(parent__parent__parent_id=course_id)

        # Filtering by Subject (great-great-grandparent)
        subject_id = (
            self.request.query_params.get("subject") or 
            self.request.query_params.get("subject_id")
        )
        if subject_id:
            queryset = queryset.filter(parent__parent__parent__parent_id=subject_id)

        # Filtering by Program (great-great-great-grandparent)
        program_id = (
            self.request.query_params.get("program") or 
            self.request.query_params.get("program_id")
        )
        if program_id:
            queryset = queryset.filter(parent__parent__parent__parent__parent_id=program_id)

        # Filtering by slug
        slug = self.request.query_params.get("slug")
        if slug:
            queryset = queryset.filter(slug=slug)

        return queryset.order_by("display_order")

    def get_serializer_class(self):
        """
        Determines the appropriate serializer based on the current action.
        - 'list': SubtopicListSerializer (lightweight list representation with lessons count)
        - 'retrieve': SubtopicDetailSerializer (detailed view with nested lessons list)
        - default (create, update, etc.): SubtopicSerializer (input validation and flat representation)
        """
        if self.action == "list":
            return SubtopicListSerializer
        elif self.action == "retrieve":
            return SubtopicDetailSerializer
        return SubtopicSerializer

    @action(detail=True, methods=["post"], url_path="restore")
    def restore(self, request, id=None):
        """
        POST /subtopics/{id}/restore/
        Allows restoring a soft-deleted subtopic. Restricted to admins/teachers.
        """
        user = self.request.user
        is_privileged = user.is_superuser or (
            user.is_teacher_cbac
        )
        if not is_privileged:
            return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

        subtopic = CourseStructure.all_objects.filter(id=id, node_type="SUBTOPIC", deleted_at__isnull=False).first()
        if not subtopic:
            return Response({"detail": "Subtopic not found or not soft-deleted."}, status=status.HTTP_404_NOT_FOUND)

        subtopic.restore()
        return Response({"detail": "Subtopic restored successfully."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get"], url_path="lessons")
    def lessons(self, request, id=None):
        """
        GET /subtopics/{id}/lessons/
        Returns active lessons associated with this specific subtopic.
        """
        subtopic = self.get_object()
        user = self.request.user
        include_deleted = self.request.query_params.get("include_deleted", "false").lower() == "true"
        is_privileged = user.is_authenticated and (
            user.is_superuser or (
                user.is_teacher_cbac
            )
        )

        if include_deleted and is_privileged:
            lessons = CourseStructure.all_objects.filter(parent=subtopic, node_type="LESSON")
        else:
            lessons = CourseStructure.objects.filter(parent=subtopic, node_type="LESSON")

        # Filtering by slug if specified in query params
        slug = request.query_params.get("slug")
        if slug:
            lessons = lessons.filter(slug=slug)

        # Support search and ordering if query params provided
        search = request.query_params.get("search")
        if search:
            lessons = lessons.filter(
                models.Q(title__icontains=search) |
                models.Q(slug__icontains=search) |
                models.Q(description__icontains=search)
            )

        ordering = request.query_params.get("ordering", "display_order")
        if ordering in ["display_order", "-display_order", "title", "-title", "created_at", "-created_at", "updated_at", "-updated_at"]:
            lessons = lessons.order_by(ordering)
        else:
            lessons = lessons.order_by("display_order")

        page = self.paginate_queryset(lessons)
        if page is not None:
            serializer = LessonListSerializer(page, many=True, context={"request": request})
            return self.get_paginated_response(serializer.data)

        serializer = LessonListSerializer(lessons, many=True, context={"request": request})
        return Response(serializer.data)


from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

class StudentMeEnrollmentsView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """
        GET /students/me/enrollments/
        Returns active enrollments for the current logged-in student.
        """
        queryset = StudentEnrollment.objects.select_related("student", "course").filter(student=request.user).order_by("-enrolled_at")
        
        status_val = request.query_params.get("status")
        if status_val:
            queryset = queryset.filter(status=status_val)
            
        search_query = request.query_params.get("search")
        if search_query:
            queryset = queryset.filter(course__title__icontains=search_query)
            
        paginator = EnterprisePagination()
        page = paginator.paginate_queryset(queryset, request, view=self)
        if page is not None:
            serializer = StudentEnrollmentSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)
            
        serializer = StudentEnrollmentSerializer(queryset, many=True)
        return Response(serializer.data)


class StudentMeProgressView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """
        GET /students/me/progress/
        Returns learning progress for the current logged-in student.
        """
        queryset = LearningProgress.objects.select_related("student", "node").filter(student=request.user).order_by("-last_accessed_at")
        
        is_completed_val = request.query_params.get("is_completed")
        if is_completed_val:
            queryset = queryset.filter(is_completed=is_completed_val.lower() == "true")
            
        search_query = request.query_params.get("search")
        if search_query:
            queryset = queryset.filter(node__title__icontains=search_query)
            
        paginator = EnterprisePagination()
        page = paginator.paginate_queryset(queryset, request, view=self)
        if page is not None:
            serializer = LearningProgressSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)
            
        serializer = LearningProgressSerializer(queryset, many=True)
        return Response(serializer.data)


class StudentMeCertificatesView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """
        GET /students/me/certificates/
        Returns certificates achieved by the current logged-in student.
        """
        queryset = Certificate.objects.select_related("user", "course").filter(user=request.user).order_by("-issued_at")
        
        search_query = request.query_params.get("search")
        if search_query:
            queryset = queryset.filter(course__title__icontains=search_query)
            
        paginator = EnterprisePagination()
        page = paginator.paginate_queryset(queryset, request, view=self)
        if page is not None:
            serializer = CertificateSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)
            
        serializer = CertificateSerializer(queryset, many=True)
        return Response(serializer.data)


class StudentMeBadgesView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """
        GET /students/me/badges/
        Returns badges unlocked by the current logged-in student.
        """
        queryset = UserBadge.objects.select_related("user", "badge").filter(user=request.user).order_by("-unlocked_at")
        
        search_query = request.query_params.get("search")
        if search_query:
            queryset = queryset.filter(badge__title__icontains=search_query)
            
        paginator = EnterprisePagination()
        page = paginator.paginate_queryset(queryset, request, view=self)
        if page is not None:
            serializer = UserBadgeSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)
            
        serializer = UserBadgeSerializer(queryset, many=True)
        return Response(serializer.data)


class LiveClassViewSet(viewsets.ModelViewSet):
    queryset = LiveClass.objects.select_related("course", "teacher").all().order_by("scheduled_at")
    serializer_class = LiveClassSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "id"

    def perform_create(self, serializer):
        serializer.save(teacher=self.request.user)

    @action(detail=True, methods=["post"], url_path="start-session")
    def start_session(self, request, id=None) -> Response:
        from apps.lms.services import LiveClassService
        from apps.lms.serializers import LiveSessionSerializer
        session = LiveClassService.start_live_session(id)
        return Response(LiveSessionSerializer(session).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="end-session")
    def end_session(self, request, id=None) -> Response:
        from apps.lms.services import LiveClassService
        live_class = LiveClassService.end_live_session(id)
        return Response(LiveClassSerializer(live_class).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="record-attendance")
    def record_attendance(self, request, id=None) -> Response:
        from apps.lms.services import LiveClassService
        from apps.lms.serializers import MeetingParticipantSerializer
        joined_at = request.data.get("joined_at")
        left_at = request.data.get("left_at")
        participant = LiveClassService.record_attendance(id, request.user, joined_at, left_at)
        return Response(MeetingParticipantSerializer(participant).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="create-poll")
    def create_poll(self, request, id=None) -> Response:
        from apps.lms.services import LiveClassService
        from apps.lms.serializers import PollSerializer
        question = request.data.get("question")
        options_list = request.data.get("options", [])
        is_anonymous = request.data.get("is_anonymous", False)
        poll = LiveClassService.create_poll(id, request.user, question, options_list, is_anonymous)
        return Response(PollSerializer(poll).data, status=status.HTTP_200_OK)


from apps.lms.models import (
    LiveSession, MeetingParticipant, Recording, Whiteboard, ChatMessage,
    Poll, PollOption, PollVote, BreakoutRoom, CalendarEvent, Reminder, MeetingAnalytics
)
from apps.lms.serializers import (
    LiveSessionSerializer, MeetingParticipantSerializer, RecordingSerializer,
    WhiteboardSerializer, ChatMessageSerializer, PollSerializer, PollVoteSerializer,
    BreakoutRoomSerializer, CalendarEventSerializer, ReminderSerializer, MeetingAnalyticsSerializer
)

class LiveSessionViewSet(viewsets.ModelViewSet):
    queryset = LiveSession.objects.all().order_by("-started_at")
    serializer_class = LiveSessionSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "id"


class MeetingParticipantViewSet(viewsets.ModelViewSet):
    queryset = MeetingParticipant.objects.all().order_by("-joined_at")
    serializer_class = MeetingParticipantSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "id"


class RecordingViewSet(viewsets.ModelViewSet):
    queryset = Recording.objects.all().order_by("created_at")
    serializer_class = RecordingSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "id"


class WhiteboardViewSet(viewsets.ModelViewSet):
    queryset = Whiteboard.objects.all().order_by("created_at")
    serializer_class = WhiteboardSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "id"


class ChatMessageViewSet(viewsets.ModelViewSet):
    queryset = ChatMessage.objects.all().order_by("timestamp")
    serializer_class = ChatMessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "id"

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)


class PollViewSet(viewsets.ModelViewSet):
    queryset = Poll.objects.all().order_by("-created_at")
    serializer_class = PollSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "id"

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)

    @action(detail=True, methods=["post"], url_path="vote")
    def cast_vote(self, request, id=None) -> Response:
        from apps.lms.services import LiveClassService
        from apps.lms.serializers import PollVoteSerializer
        option_id = request.data.get("option_id")
        vote = LiveClassService.cast_vote(id, option_id, request.user)
        return Response(PollVoteSerializer(vote).data, status=status.HTTP_200_OK)


class PollVoteViewSet(viewsets.ModelViewSet):
    queryset = PollVote.objects.all().order_by("created_at")
    serializer_class = PollVoteSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "id"


class BreakoutRoomViewSet(viewsets.ModelViewSet):
    queryset = BreakoutRoom.objects.all().order_by("name")
    serializer_class = BreakoutRoomSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "id"


class CalendarEventViewSet(viewsets.ModelViewSet):
    queryset = CalendarEvent.objects.all().order_by("start_time")
    serializer_class = CalendarEventSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "id"


class ReminderViewSet(viewsets.ModelViewSet):
    queryset = Reminder.objects.all().order_by("remind_at")
    serializer_class = ReminderSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "id"


class MeetingAnalyticsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = MeetingAnalytics.objects.all().order_by("created_at")
    serializer_class = MeetingAnalyticsSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "id"
