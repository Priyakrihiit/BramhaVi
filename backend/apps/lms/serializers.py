from rest_framework import serializers
from apps.lms.models import (
    CourseStructure, LearningProgress, Assignment, AssignmentSubmission, PracticeSession,
    Project, Exam, QuestionBank, ExamQuestion, ExamAttempt, Certificate, Badge, UserBadge,
    TeacherApplication, TeacherClass, StudentEnrollment, ProjectSubmission, LiveClass
)



class CourseStructureSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseStructure
        fields = ["id", "parent", "node_type", "title", "slug", "description", "display_order", "metadata", "created_at", "updated_at"]


class LearningProgressSerializer(serializers.ModelSerializer):
    student_email = serializers.ReadOnlyField(source="student.email")
    node_title = serializers.ReadOnlyField(source="node.title")

    class Meta:
        model = LearningProgress
        fields = ["id", "student", "student_email", "node", "node_title", "progress_percentage", "is_completed", "last_accessed_at", "completed_at"]


class AssignmentSerializer(serializers.ModelSerializer):
    """
    Standard serializer for Assignment instances, used primarily for creation and updates.
    """
    lesson_title = serializers.ReadOnlyField(source="lesson.title")

    class Meta:
        model = Assignment
        fields = ["id", "lesson", "lesson_title", "title", "instructions", "max_points", "created_at"]
        read_only_fields = ["id", "created_at"]


class AssignmentListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer optimized for listing multiple Assignment records.
    """
    lesson_title = serializers.ReadOnlyField(source="lesson.title")

    class Meta:
        model = Assignment
        fields = ["id", "lesson", "lesson_title", "title", "instructions", "max_points", "created_at"]
        read_only_fields = ["id", "created_at"]


class AssignmentDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for a single Assignment instance.
    """
    lesson_title = serializers.ReadOnlyField(source="lesson.title")

    class Meta:
        model = Assignment
        fields = ["id", "lesson", "lesson_title", "title", "instructions", "max_points", "created_at"]
        read_only_fields = ["id", "created_at"]


class AssignmentSubmissionSerializer(serializers.ModelSerializer):
    """
    Standard serializer for AssignmentSubmission instances, used primarily for creation and updates.
    """
    student_email = serializers.ReadOnlyField(source="student.email")
    assignment_title = serializers.ReadOnlyField(source="assignment.title")
    graded_by_email = serializers.ReadOnlyField(source="graded_by.email")

    class Meta:
        model = AssignmentSubmission
        fields = [
            "id", "assignment", "assignment_title", "student", "student_email", 
            "submission_payload", "grade", "feedback", "graded_by", "graded_by_email", 
            "submitted_at", "graded_at"
        ]
        read_only_fields = ["id", "student", "submitted_at", "graded_by", "graded_at"]


class AssignmentSubmissionListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer optimized for listing multiple AssignmentSubmission records.
    """
    student_email = serializers.ReadOnlyField(source="student.email")
    assignment_title = serializers.ReadOnlyField(source="assignment.title")
    graded_by_email = serializers.ReadOnlyField(source="graded_by.email")

    class Meta:
        model = AssignmentSubmission
        fields = [
            "id", "assignment", "assignment_title", "student", "student_email", 
            "submission_payload", "grade", "feedback", "graded_by", "graded_by_email", 
            "submitted_at", "graded_at"
        ]
        read_only_fields = ["id", "student", "submitted_at", "graded_by", "graded_at"]


class AssignmentSubmissionDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for a single AssignmentSubmission instance.
    """
    student_email = serializers.ReadOnlyField(source="student.email")
    assignment_title = serializers.ReadOnlyField(source="assignment.title")
    graded_by_email = serializers.ReadOnlyField(source="graded_by.email")

    class Meta:
        model = AssignmentSubmission
        fields = [
            "id", "assignment", "assignment_title", "student", "student_email", 
            "submission_payload", "grade", "feedback", "graded_by", "graded_by_email", 
            "submitted_at", "graded_at"
        ]
        read_only_fields = ["id", "student", "submitted_at", "graded_by", "graded_at"]


class PracticeSessionSerializer(serializers.ModelSerializer):
    student_email = serializers.ReadOnlyField(source="student.email")
    course_title = serializers.ReadOnlyField(source="course.title")

    class Meta:
        model = PracticeSession
        fields = ["id", "student", "student_email", "course", "course_title", "score", "session_data", "created_at"]


class PracticeSerializer(serializers.ModelSerializer):
    """
    Standard serializer for CourseStructure nodes serving as Practice resources.
    """
    parent_title = serializers.ReadOnlyField(source="parent.title")
    practice_type = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    difficulty = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    status = serializers.CharField(required=False, allow_null=True, allow_blank=True)

    class Meta:
        model = CourseStructure
        fields = [
            "id", "parent", "parent_title", "node_type", "title", "slug", 
            "description", "display_order", "metadata", "practice_type", 
            "difficulty", "status", "created_at"
        ]
        read_only_fields = ["id", "created_at"]

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        metadata = instance.metadata or {}
        ret["practice_type"] = metadata.get("practice_type")
        ret["difficulty"] = metadata.get("difficulty")
        ret["status"] = metadata.get("status")
        return ret

    def create(self, validated_data):
        practice_type = validated_data.pop("practice_type", None)
        difficulty = validated_data.pop("difficulty", None)
        status = validated_data.pop("status", None)
        
        metadata = validated_data.get("metadata", {}) or {}
        if practice_type is not None:
            metadata["practice_type"] = practice_type
        if difficulty is not None:
            metadata["difficulty"] = difficulty
        if status is not None:
            metadata["status"] = status
        validated_data["metadata"] = metadata
        
        if "node_type" not in validated_data:
            validated_data["node_type"] = "LESSON"
            
        return super().create(validated_data)

    def update(self, instance, validated_data):
        practice_type = validated_data.pop("practice_type", None)
        difficulty = validated_data.pop("difficulty", None)
        status = validated_data.pop("status", None)
        
        metadata = validated_data.get("metadata", instance.metadata or {}) or {}
        if practice_type is not None:
            metadata["practice_type"] = practice_type
        if difficulty is not None:
            metadata["difficulty"] = difficulty
        if status is not None:
            metadata["status"] = status
        validated_data["metadata"] = metadata
        
        return super().update(instance, validated_data)


class PracticeListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer optimized for listing multiple Practice records.
    """
    parent_title = serializers.ReadOnlyField(source="parent.title")
    practice_type = serializers.CharField(source="metadata.practice_type", read_only=True)
    difficulty = serializers.CharField(source="metadata.difficulty", read_only=True)
    status = serializers.CharField(source="metadata.status", read_only=True)

    class Meta:
        model = CourseStructure
        fields = [
            "id", "parent", "parent_title", "node_type", "title", "slug", 
            "description", "display_order", "practice_type", "difficulty", "status", "created_at"
        ]
        read_only_fields = ["id", "created_at"]


class PracticeDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for a single Practice instance.
    """
    parent_title = serializers.ReadOnlyField(source="parent.title")
    practice_type = serializers.CharField(source="metadata.practice_type", read_only=True)
    difficulty = serializers.CharField(source="metadata.difficulty", read_only=True)
    status = serializers.CharField(source="metadata.status", read_only=True)

    class Meta:
        model = CourseStructure
        fields = [
            "id", "parent", "parent_title", "node_type", "title", "slug", 
            "description", "display_order", "metadata", "practice_type", 
            "difficulty", "status", "created_at"
        ]
        read_only_fields = ["id", "created_at"]


class PracticeAttemptSerializer(serializers.ModelSerializer):
    """
    Standard serializer for PracticeAttempt records.
    """
    student_email = serializers.ReadOnlyField(source="student.email")
    practice = serializers.PrimaryKeyRelatedField(queryset=CourseStructure.objects.all(), source="course")
    practice_title = serializers.ReadOnlyField(source="course.title")

    class Meta:
        model = PracticeSession
        fields = [
            "id", "student", "student_email", "practice", "practice_title", 
            "score", "session_data", "created_at"
        ]
        read_only_fields = ["id", "student", "created_at"]


class PracticeAttemptListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer optimized for listing PracticeAttempts.
    """
    student_email = serializers.ReadOnlyField(source="student.email")
    practice = serializers.PrimaryKeyRelatedField(queryset=CourseStructure.objects.all(), source="course")
    practice_title = serializers.ReadOnlyField(source="course.title")

    class Meta:
        model = PracticeSession
        fields = [
            "id", "student", "student_email", "practice", "practice_title", 
            "score", "created_at"
        ]
        read_only_fields = ["id", "student", "created_at"]


class PracticeAttemptDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for a single PracticeAttempt instance.
    """
    student_email = serializers.ReadOnlyField(source="student.email")
    practice = serializers.PrimaryKeyRelatedField(queryset=CourseStructure.objects.all(), source="course")
    practice_title = serializers.ReadOnlyField(source="course.title")

    class Meta:
        model = PracticeSession
        fields = [
            "id", "student", "student_email", "practice", "practice_title", 
            "score", "session_data", "created_at"
        ]
        read_only_fields = ["id", "student", "created_at"]


class ProjectSerializer(serializers.ModelSerializer):
    course_title = serializers.ReadOnlyField(source="course.title")

    class Meta:
        model = Project
        fields = ["id", "course", "course_title", "title", "description", "requirements", "created_at"]
        read_only_fields = ["id", "created_at"]


class ProjectListSerializer(serializers.ModelSerializer):
    course_title = serializers.ReadOnlyField(source="course.title")

    class Meta:
        model = Project
        fields = ["id", "course", "course_title", "title", "description", "requirements", "created_at"]
        read_only_fields = ["id", "created_at"]


class ProjectDetailSerializer(serializers.ModelSerializer):
    course_title = serializers.ReadOnlyField(source="course.title")

    class Meta:
        model = Project
        fields = ["id", "course", "course_title", "title", "description", "requirements", "created_at"]
        read_only_fields = ["id", "created_at"]


class ProjectSubmissionSerializer(serializers.ModelSerializer):
    student_email = serializers.ReadOnlyField(source="student.email")
    project_title = serializers.ReadOnlyField(source="project.title")

    class Meta:
        model = ProjectSubmission
        fields = ["id", "project", "project_title", "student", "student_email", "submission_payload", "created_at", "updated_at"]
        read_only_fields = ["id", "student", "created_at", "updated_at"]


class ProjectSubmissionListSerializer(serializers.ModelSerializer):
    student_email = serializers.ReadOnlyField(source="student.email")
    project_title = serializers.ReadOnlyField(source="project.title")

    class Meta:
        model = ProjectSubmission
        fields = ["id", "project", "project_title", "student", "student_email", "submission_payload", "created_at", "updated_at"]
        read_only_fields = ["id", "student", "created_at", "updated_at"]


class ProjectSubmissionDetailSerializer(serializers.ModelSerializer):
    student_email = serializers.ReadOnlyField(source="student.email")
    project_title = serializers.ReadOnlyField(source="project.title")

    class Meta:
        model = ProjectSubmission
        fields = ["id", "project", "project_title", "student", "student_email", "submission_payload", "created_at", "updated_at"]
        read_only_fields = ["id", "student", "created_at", "updated_at"]


class ExamSerializer(serializers.ModelSerializer):
    course_title = serializers.ReadOnlyField(source="course.title")

    class Meta:
        model = Exam
        fields = ["id", "course", "course_title", "title", "passing_score", "duration_minutes", "created_at"]


class QuestionBankSerializer(serializers.ModelSerializer):
    course_title = serializers.ReadOnlyField(source="course.title")

    class Meta:
        model = QuestionBank
        fields = [
            "id", "course", "course_title", "question_text", 
            "question_type", "options", "correct_answers", "created_at"
        ]
        read_only_fields = ["id", "created_at"]

    def validate_question_type(self, value):
        allowed_types = [
            "MULTIPLE_CHOICE", "MULTIPLE_SELECT", "TRUE_FALSE", 
            "SHORT_ANSWER", "LONG_ANSWER", "FILL_IN_THE_BLANK", 
            "MATCHING", "NUMERICAL"
        ]
        if value.upper() not in allowed_types:
            raise serializers.ValidationError(
                f"Question type '{value}' is not supported. "
                f"Must be one of: {', '.join(allowed_types)}"
            )
        return value.upper()


class QuestionBankListSerializer(serializers.ModelSerializer):
    course_title = serializers.ReadOnlyField(source="course.title")

    class Meta:
        model = QuestionBank
        fields = [
            "id", "course", "course_title", "question_text", 
            "question_type", "options", "correct_answers", "created_at"
        ]
        read_only_fields = ["id", "created_at"]


class QuestionBankDetailSerializer(serializers.ModelSerializer):
    course_title = serializers.ReadOnlyField(source="course.title")

    class Meta:
        model = QuestionBank
        fields = [
            "id", "course", "course_title", "question_text", 
            "question_type", "options", "correct_answers", "created_at"
        ]
        read_only_fields = ["id", "created_at"]


class ExamQuestionSerializer(serializers.ModelSerializer):
    exam_title = serializers.ReadOnlyField(source="exam.title")

    class Meta:
        model = ExamQuestion
        fields = ["id", "exam", "exam_title", "question", "created_at"]


class CertificateSerializer(serializers.ModelSerializer):
    user_email = serializers.ReadOnlyField(source="user.email")
    course_title = serializers.ReadOnlyField(source="course.title")

    class Meta:
        model = Certificate
        fields = ["id", "user", "user_email", "course", "course_title", "certificate_url", "signature_hash", "issued_at"]


class BadgeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Badge
        fields = ["id", "title", "description", "icon_url", "criteria", "created_at"]


class UserBadgeSerializer(serializers.ModelSerializer):
    user_email = serializers.ReadOnlyField(source="user.email")
    badge_title = serializers.ReadOnlyField(source="badge.title")

    class Meta:
        model = UserBadge
        fields = ["id", "user", "user_email", "badge", "badge_title", "unlocked_at"]


class TeacherApplicationSerializer(serializers.ModelSerializer):
    user_email = serializers.ReadOnlyField(source="user.email")
    reviewed_by_email = serializers.ReadOnlyField(source="reviewed_by.email")

    class Meta:
        model = TeacherApplication
        fields = [
            "id", "user", "user_email", "resume_url", "experience_summary", 
            "subjects_requested", "status", "reviewed_by", "reviewed_by_email", 
            "created_at", "updated_at"
        ]


class TeacherClassSerializer(serializers.ModelSerializer):
    teacher_email = serializers.ReadOnlyField(source="teacher.email")
    course_title = serializers.ReadOnlyField(source="course.title")

    class Meta:
        model = TeacherClass
        fields = ["id", "teacher", "teacher_email", "course", "course_title", "schedule_info", "is_active", "created_at", "updated_at"]


class StudentEnrollmentSerializer(serializers.ModelSerializer):
    student_email = serializers.ReadOnlyField(source="student.email")
    course_title = serializers.ReadOnlyField(source="course.title")

    class Meta:
        model = StudentEnrollment
        fields = ["id", "student", "student_email", "course", "course_title", "status", "enrolled_at", "created_at", "updated_at"]


class CourseSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and updating Course instances.
    Forces and preserves node_type as CourseNodeType.COURSE.
    """
    class Meta:
        model = CourseStructure
        fields = [
            "id",
            "parent",
            "node_type",
            "title",
            "slug",
            "description",
            "display_order",
            "metadata",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["node_type", "created_at", "updated_at"]

    def create(self, validated_data):
        """
        Create a new Course node and explicitly set node_type to COURSE.
        """
        validated_data["node_type"] = "COURSE"
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """
        Update an existing Course node, ensuring node_type remains COURSE.
        """
        validated_data["node_type"] = "COURSE"
        return super().update(instance, validated_data)


class CourseStructureNodeSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = CourseStructure
        fields = [
            "id", "parent", "node_type", "title", "slug", "description", 
            "display_order", "metadata", "children"
        ]

    def get_children(self, obj):
        children = obj.children.filter(deleted_at__isnull=True).order_by("display_order")
        return CourseStructureNodeSerializer(children, many=True, context=self.context).data


class ChapterSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and updating Chapter instances.
    Forces and preserves node_type as CourseNodeType.CHAPTER.
    """
    class Meta:
        model = CourseStructure
        fields = [
            "id",
            "parent",
            "node_type",
            "title",
            "slug",
            "description",
            "display_order",
            "metadata",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["node_type", "created_at", "updated_at"]

    def create(self, validated_data):
        """
        Create a new Chapter node and explicitly set node_type to CHAPTER.
        """
        validated_data["node_type"] = "CHAPTER"
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """
        Update an existing Chapter node, ensuring node_type remains CHAPTER.
        """
        validated_data["node_type"] = "CHAPTER"
        return super().update(instance, validated_data)


class LessonSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and updating Lesson instances (node_type="LESSON").
    """
    class Meta:
        model = CourseStructure
        fields = [
            "id",
            "parent",
            "node_type",
            "title",
            "slug",
            "description",
            "display_order",
            "metadata",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["node_type", "created_at", "updated_at"]

    def create(self, validated_data):
        """
        Create a new Lesson node and explicitly set node_type to LESSON.
        """
        validated_data["node_type"] = "LESSON"
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """
        Update an existing Lesson node, ensuring node_type remains LESSON.
        """
        validated_data["node_type"] = "LESSON"
        return super().update(instance, validated_data)


class ProgramSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and updating Program instances.
    Forces and preserves node_type as CourseNodeType.PROGRAM.
    """
    class Meta:
        model = CourseStructure
        fields = [
            "id",
            "parent",
            "node_type",
            "title",
            "slug",
            "description",
            "display_order",
            "metadata",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["node_type", "created_at", "updated_at"]

    def create(self, validated_data):
        """
        Create a new Program node and explicitly set node_type to PROGRAM.
        """
        validated_data["node_type"] = "PROGRAM"
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """
        Update an existing Program node, ensuring node_type remains PROGRAM.
        """
        validated_data["node_type"] = "PROGRAM"
        return super().update(instance, validated_data)


class ProgramListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer optimized for listing Program nodes.
    Includes count of child nodes (e.g. subjects).
    """
    children_count = serializers.SerializerMethodField(
        help_text="The count of active, non-deleted child nodes associated with this program."
    )

    class Meta:
        model = CourseStructure
        fields = [
            "id",
            "parent",
            "node_type",
            "title",
            "slug",
            "description",
            "display_order",
            "metadata",
            "children_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["node_type", "created_at", "updated_at"]

    def get_children_count(self, obj) -> int:
        """
        Retrieves the count of active child nodes.
        """
        return obj.children.filter(deleted_at__isnull=True).count()


class ProgramDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for Program nodes.
    Provides complete nested child nodes hierarchy (e.g. nested CourseStructures).
    """
    children = serializers.SerializerMethodField(
        help_text="Fully nested tree structure of active child nodes (e.g., Subjects, Courses, Chapters)."
    )

    class Meta:
        model = CourseStructure
        fields = [
            "id",
            "parent",
            "node_type",
            "title",
            "slug",
            "description",
            "display_order",
            "metadata",
            "children",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["node_type", "created_at", "updated_at"]

    def get_children(self, obj) -> list:
        """
        Recursively serializes nested child structure using CourseStructureNodeSerializer.
        """
        children = obj.children.filter(deleted_at__isnull=True).order_by("display_order")
        # Reuse existing CourseStructureNodeSerializer to get full recursive tree.
        return CourseStructureNodeSerializer(children, many=True, context=self.context).data


class SubjectSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and updating Subject instances.
    Forces and preserves node_type as CourseNodeType.SUBJECT.
    """
    class Meta:
        model = CourseStructure
        fields = [
            "id",
            "parent",
            "node_type",
            "title",
            "slug",
            "description",
            "display_order",
            "metadata",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["node_type", "created_at", "updated_at"]

    def create(self, validated_data):
        """
        Create a new Subject node and explicitly set node_type to SUBJECT.
        """
        validated_data["node_type"] = "SUBJECT"
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """
        Update an existing Subject node, ensuring node_type remains SUBJECT.
        """
        validated_data["node_type"] = "SUBJECT"
        return super().update(instance, validated_data)


class SubjectListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer optimized for listing Subject nodes.
    Includes count of child nodes (e.g. courses).
    """
    courses_count = serializers.SerializerMethodField(
        help_text="The count of active, non-deleted courses associated with this subject."
    )

    class Meta:
        model = CourseStructure
        fields = [
            "id",
            "parent",
            "node_type",
            "title",
            "slug",
            "description",
            "display_order",
            "metadata",
            "courses_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["node_type", "created_at", "updated_at"]

    def get_courses_count(self, obj) -> int:
        """
        Retrieves the count of active child course nodes.
        """
        return obj.children.filter(node_type="COURSE", deleted_at__isnull=True).count()


class SubjectDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for Subject nodes.
    Provides nested courses under this subject.
    """
    courses = serializers.SerializerMethodField(
        help_text="Active courses associated under this subject."
    )

    class Meta:
        model = CourseStructure
        fields = [
            "id",
            "parent",
            "node_type",
            "title",
            "slug",
            "description",
            "display_order",
            "metadata",
            "courses",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["node_type", "created_at", "updated_at"]

    def get_courses(self, obj) -> list:
        """
        Retrieves the active, non-deleted course child nodes.
        """
        courses = obj.children.filter(node_type="COURSE", deleted_at__isnull=True).order_by("display_order")
        return CourseSerializer(courses, many=True, context=self.context).data


class CourseListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer optimized for listing Course nodes.
    Includes count of child chapters.
    """
    chapters_count = serializers.SerializerMethodField(
        help_text="The count of active, non-deleted chapters associated with this course."
    )

    class Meta:
        model = CourseStructure
        fields = [
            "id",
            "parent",
            "node_type",
            "title",
            "slug",
            "description",
            "display_order",
            "metadata",
            "chapters_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["node_type", "created_at", "updated_at"]

    def get_chapters_count(self, obj) -> int:
        """
        Retrieves the count of active child chapter nodes.
        """
        return obj.children.filter(node_type="CHAPTER", deleted_at__isnull=True).count()


class CourseDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for Course nodes.
    Provides nested chapters under this course.
    """
    chapters = serializers.SerializerMethodField(
        help_text="Active chapters associated under this course."
    )

    class Meta:
        model = CourseStructure
        fields = [
            "id",
            "parent",
            "node_type",
            "title",
            "slug",
            "description",
            "display_order",
            "metadata",
            "chapters",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["node_type", "created_at", "updated_at"]

    def get_chapters(self, obj) -> list:
        """
        Retrieves the active, non-deleted chapter child nodes.
        """
        chapters = obj.children.filter(node_type="CHAPTER", deleted_at__isnull=True).order_by("display_order")
        return ChapterSerializer(chapters, many=True, context=self.context).data


class TopicSerializer(serializers.ModelSerializer):
    """
    Serializer for Topic instances (node_type="TOPIC").
    """
    class Meta:
        model = CourseStructure
        fields = [
            "id",
            "parent",
            "node_type",
            "title",
            "slug",
            "description",
            "display_order",
            "metadata",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["node_type", "created_at", "updated_at"]

    def create(self, validated_data):
        """
        Create a new Topic node and explicitly set node_type to TOPIC.
        """
        validated_data["node_type"] = "TOPIC"
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """
        Update an existing Topic node, ensuring node_type remains TOPIC.
        """
        validated_data["node_type"] = "TOPIC"
        return super().update(instance, validated_data)


class ChapterListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer optimized for listing Chapter nodes.
    Includes count of child topics.
    """
    topics_count = serializers.SerializerMethodField(
        help_text="The count of active, non-deleted topics associated with this chapter."
    )

    class Meta:
        model = CourseStructure
        fields = [
            "id",
            "parent",
            "node_type",
            "title",
            "slug",
            "description",
            "display_order",
            "metadata",
            "topics_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["node_type", "created_at", "updated_at"]

    def get_topics_count(self, obj) -> int:
        """
        Retrieves the count of active child topic nodes.
        """
        return obj.children.filter(node_type="TOPIC", deleted_at__isnull=True).count()


class ChapterDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for Chapter nodes.
    Provides nested topics under this chapter.
    """
    topics = serializers.SerializerMethodField(
        help_text="Active topics associated under this chapter."
    )

    class Meta:
        model = CourseStructure
        fields = [
            "id",
            "parent",
            "node_type",
            "title",
            "slug",
            "description",
            "display_order",
            "metadata",
            "topics",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["node_type", "created_at", "updated_at"]

    def get_topics(self, obj) -> list:
        """
        Retrieves the active, non-deleted topic child nodes.
        """
        topics = obj.children.filter(node_type="TOPIC", deleted_at__isnull=True).order_by("display_order")
        return TopicSerializer(topics, many=True, context=self.context).data


class SubtopicSerializer(serializers.ModelSerializer):
    """
    Serializer for Subtopic instances (node_type="SUBTOPIC").
    """
    class Meta:
        model = CourseStructure
        fields = [
            "id",
            "parent",
            "node_type",
            "title",
            "slug",
            "description",
            "display_order",
            "metadata",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["node_type", "created_at", "updated_at"]

    def create(self, validated_data):
        """
        Create a new Subtopic node and explicitly set node_type to SUBTOPIC.
        """
        validated_data["node_type"] = "SUBTOPIC"
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """
        Update an existing Subtopic node, ensuring node_type remains SUBTOPIC.
        """
        validated_data["node_type"] = "SUBTOPIC"
        return super().update(instance, validated_data)


class TopicListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer optimized for listing Topic nodes.
    Includes count of child subtopics.
    """
    subtopics_count = serializers.SerializerMethodField(
        help_text="The count of active, non-deleted subtopics associated with this topic."
    )

    class Meta:
        model = CourseStructure
        fields = [
            "id",
            "parent",
            "node_type",
            "title",
            "slug",
            "description",
            "display_order",
            "metadata",
            "subtopics_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["node_type", "created_at", "updated_at"]

    def get_subtopics_count(self, obj) -> int:
        """
        Retrieves the count of active child subtopic nodes.
        """
        return obj.children.filter(node_type="SUBTOPIC", deleted_at__isnull=True).count()


class TopicDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for Topic nodes.
    Provides nested subtopics under this topic.
    """
    subtopics = serializers.SerializerMethodField(
        help_text="Active subtopics associated under this topic."
    )

    class Meta:
        model = CourseStructure
        fields = [
            "id",
            "parent",
            "node_type",
            "title",
            "slug",
            "description",
            "display_order",
            "metadata",
            "subtopics",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["node_type", "created_at", "updated_at"]

    def get_subtopics(self, obj) -> list:
        """
        Retrieves the active, non-deleted subtopic child nodes.
        """
        subtopics = obj.children.filter(node_type="SUBTOPIC", deleted_at__isnull=True).order_by("display_order")
        return SubtopicSerializer(subtopics, many=True, context=self.context).data


class SubtopicListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer optimized for listing Subtopic nodes.
    Includes count of child lessons.
    """
    lessons_count = serializers.SerializerMethodField(
        help_text="The count of active, non-deleted lessons associated with this subtopic."
    )

    class Meta:
        model = CourseStructure
        fields = [
            "id",
            "parent",
            "node_type",
            "title",
            "slug",
            "description",
            "display_order",
            "metadata",
            "lessons_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["node_type", "created_at", "updated_at"]

    def get_lessons_count(self, obj) -> int:
        """
        Retrieves the count of active child lesson nodes.
        """
        return obj.children.filter(node_type="LESSON", deleted_at__isnull=True).count()


class SubtopicDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for Subtopic nodes.
    Provides nested lessons under this subtopic.
    """
    lessons = serializers.SerializerMethodField(
        help_text="Active lessons associated under this subtopic."
    )

    class Meta:
        model = CourseStructure
        fields = [
            "id",
            "parent",
            "node_type",
            "title",
            "slug",
            "description",
            "display_order",
            "metadata",
            "lessons",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["node_type", "created_at", "updated_at"]

    def get_lessons(self, obj) -> list:
        """
        Retrieves the active, non-deleted lesson child nodes.
        """
        lessons = obj.children.filter(node_type="LESSON", deleted_at__isnull=True).order_by("display_order")
        return LessonSerializer(lessons, many=True, context=self.context).data


class LessonListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer optimized for listing Lesson nodes.
    """
    class Meta:
        model = CourseStructure
        fields = [
            "id",
            "parent",
            "node_type",
            "title",
            "slug",
            "description",
            "display_order",
            "metadata",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["node_type", "created_at", "updated_at"]


class LessonDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for Lesson nodes.
    """
    class Meta:
        model = CourseStructure
        fields = [
            "id",
            "parent",
            "node_type",
            "title",
            "slug",
            "description",
            "display_order",
            "metadata",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["node_type", "created_at", "updated_at"]


from apps.lms.models import (
    LiveClass, LiveSession, MeetingParticipant, Recording, Whiteboard, ChatMessage,
    Poll, PollOption, PollVote, BreakoutRoom, CalendarEvent, Reminder, MeetingAnalytics
)

class LiveClassSerializer(serializers.ModelSerializer):
    teacher_email = serializers.ReadOnlyField(source="teacher.email")
    course_title = serializers.ReadOnlyField(source="course.title")

    class Meta:
        model = LiveClass
        fields = [
            "id", "course", "course_title", "teacher", "teacher_email", "title",
            "scheduled_at", "duration_minutes", "stream_url", "status", "meeting_id",
            "created_at", "updated_at"
        ]
        read_only_fields = ["id", "teacher", "created_at", "updated_at"]


class LiveSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = LiveSession
        fields = ["id", "live_class", "started_at", "ended_at", "is_active", "created_at", "updated_at"]
        read_only_fields = ["id", "started_at", "created_at", "updated_at"]


class MeetingParticipantSerializer(serializers.ModelSerializer):
    user_email = serializers.ReadOnlyField(source="user.email")

    class Meta:
        model = MeetingParticipant
        fields = ["id", "live_class", "user", "user_email", "role", "joined_at", "left_at", "created_at", "updated_at"]
        read_only_fields = ["id", "joined_at", "created_at", "updated_at"]


class RecordingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recording
        fields = ["id", "live_class", "video_url", "file_size_bytes", "duration_seconds", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class WhiteboardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Whiteboard
        fields = ["id", "live_class", "canvas_data", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class ChatMessageSerializer(serializers.ModelSerializer):
    sender_email = serializers.ReadOnlyField(source="sender.email")

    class Meta:
        model = ChatMessage
        fields = ["id", "live_class", "sender", "sender_email", "message", "timestamp", "created_at", "updated_at"]
        read_only_fields = ["id", "sender", "timestamp", "created_at", "updated_at"]


class PollOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PollOption
        fields = ["id", "poll", "option_text", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class PollSerializer(serializers.ModelSerializer):
    options = PollOptionSerializer(many=True, read_only=True)
    creator_email = serializers.ReadOnlyField(source="creator.email")

    class Meta:
        model = Poll
        fields = ["id", "live_class", "creator", "creator_email", "question", "is_anonymous", "is_active", "options", "created_at", "updated_at"]
        read_only_fields = ["id", "creator", "created_at", "updated_at"]


class PollVoteSerializer(serializers.ModelSerializer):
    voter_email = serializers.ReadOnlyField(source="voter.email")

    class Meta:
        model = PollVote
        fields = ["id", "poll", "option", "voter", "voter_email", "created_at", "updated_at"]
        read_only_fields = ["id", "voter", "created_at", "updated_at"]


class BreakoutRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = BreakoutRoom
        fields = ["id", "live_class", "name", "meeting_id", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class CalendarEventSerializer(serializers.ModelSerializer):
    user_email = serializers.ReadOnlyField(source="user.email")

    class Meta:
        model = CalendarEvent
        fields = ["id", "user", "user_email", "live_class", "event_title", "start_time", "end_time", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class ReminderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reminder
        fields = ["id", "user", "live_class", "remind_at", "is_sent", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class MeetingAnalyticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = MeetingAnalytics
        fields = ["id", "live_class", "total_participants", "average_engagement_score", "peak_concurrent_users", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class ExamAttemptSerializer(serializers.ModelSerializer):
    student_email = serializers.ReadOnlyField(source="student.email")
    exam_title = serializers.ReadOnlyField(source="exam.title")

    class Meta:
        model = ExamAttempt
        fields = [
            "id", "student", "student_email", "exam", "exam_title", 
            "answers", "score", "passed", "started_at", "submitted_at", "status"
        ]
        read_only_fields = ["id", "student", "score", "passed", "started_at", "submitted_at", "status"]

