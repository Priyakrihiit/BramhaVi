"""
Teacher Portal Services — BrahmaVidya Galaxy
Sprint 21: High-performance business logic, transactional services, and caching integrations.
"""

from __future__ import annotations

import uuid
import datetime
from decimal import Decimal
from django.db import transaction
from django.db.models import Sum
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.core.cache import cache
from django.contrib.auth import get_user_model

from apps.teacher.models import (
    TeacherProfile, TeacherAnalytics, TeachingSession, Batch, Attendance,
    QuestionCategory, QuestionDifficulty, TeachingCalendar, TeacherAnnouncement,
    TeacherSchedule, TeachingGoal, TeacherEarning, TeacherWallet,
    TeacherCertificate, TeacherAchievement, TeacherNotificationPreference,
    TeacherActivityLog
)
from apps.lms.models import (
    CourseStructure, CourseNodeType, Assignment, AssignmentSubmission, Exam, ExamAttempt, LiveClass, StudentEnrollment
)
from apps.teacher.validators import (
    validate_teacher_rating, validate_positive_experience, validate_batch_dates,
    validate_payout_amount, validate_payout_address, validate_multiplier, validate_grade_score
)
from apps.control_center.integration_hub import CentralNotificationEngine, CentralAnalyticsTracker

User = get_user_model()


def invalidate_teacher_dashboard_cache(teacher_id) -> None:
    """Clears cached entries in Redis for this teacher."""
    cache_keys = [
        f"teacher_dashboard_summary_{teacher_id}",
    ]
    for key in cache_keys:
        try:
            cache.delete(key)
        except Exception:
            pass


class TeacherService:
    """Manages teacher profiles, verification states, and administrative logs."""

    @staticmethod
    @transaction.atomic
    def update_profile(
        user,
        bio: str | None = None,
        qualifications: list | None = None,
        specialties: list | None = None,
        experience_years: int | None = None
    ) -> TeacherProfile:
        if experience_years is not None:
            validate_positive_experience(experience_years)

        profile, _ = TeacherProfile.objects.get_or_create(user=user)

        if bio is not None:
            profile.bio = bio
        if qualifications is not None:
            profile.qualifications = qualifications
        if specialties is not None:
            profile.specialties = specialties
        if experience_years is not None:
            profile.experience_years = experience_years

        profile.save()

        # Audit activity
        TeacherActivityLog.objects.create(
            teacher=user,
            action="UPDATE_PROFILE",
            details=f"Updated bio or teaching specialties: {specialties}"
        )

        invalidate_teacher_dashboard_cache(user.id)
        return profile

    @staticmethod
    @transaction.atomic
    def verify_teacher(teacher_user, admin_user) -> TeacherProfile:
        """Admins certify credentials of an instructor."""
        profile, _ = TeacherProfile.objects.get_or_create(user=teacher_user)
        profile.is_verified = True
        profile.save()

        # Unlock system achievement for onboarding completion
        TeacherAchievement.objects.get_or_create(
            teacher=teacher_user,
            title="Verified Guru Badge",
            defaults={
                "description": "Successfully completed credential verification with BrahmaVidya Board.",
                "badge_icon": "award"
            }
        )

        return profile


class DashboardService:
    """Manages schedules, calendar rules, and announcements."""

    @staticmethod
    @transaction.atomic
    def create_schedule_item(
        teacher,
        title: str,
        description: str | None = None,
        start_time: datetime.datetime | None = None,
        end_time: datetime.datetime | None = None,
    ) -> TeacherSchedule:
        if start_time and end_time and start_time >= end_time:
            raise ValidationError("Schedule event start time must precede end time.")

        item = TeacherSchedule.objects.create(
            teacher=teacher,
            title=title,
            description=description,
            start_time=start_time or timezone.now(),
            end_time=end_time or (timezone.now() + datetime.timedelta(hours=1)),
            status="PENDING"
        )

        invalidate_teacher_dashboard_cache(teacher.id)
        return item

    @staticmethod
    @transaction.atomic
    def update_schedule_status(teacher, item_id: int, status: str) -> TeacherSchedule:
        item = TeacherSchedule.objects.get(id=item_id, teacher=teacher)
        item.status = status
        item.save()

        invalidate_teacher_dashboard_cache(teacher.id)
        return item


class CourseService:
    """Manages course node assignments, cohort batches, and structural settings."""

    @staticmethod
    @transaction.atomic
    def create_cohort_batch(
        course_id: int,
        name: str,
        start_date: datetime.date,
        end_date: datetime.date,
        instructors: list[User]
    ) -> Batch:
        course = CourseStructure.objects.get(id=course_id, node_type="COURSE")
        validate_batch_dates(start_date, end_date)

        batch = Batch.objects.create(
            course=course,
            name=name,
            start_date=start_date,
            end_date=end_date,
            is_active=True
        )
        if instructors:
            batch.instructors.set(instructors)

        for instructor in instructors:
            invalidate_teacher_dashboard_cache(instructor.id)

        return batch


class LessonService:
    """Curates lesson structures, metadata settings, and drip locks."""

    @staticmethod
    @transaction.atomic
    def create_lesson_node(
        teacher,
        parent_chapter_id: int,
        title: str,
        description: str | None = None,
        drip_delay_days: int = 0,
        video_url: str | None = None
    ) -> CourseStructure:
        parent = CourseStructure.objects.get(id=parent_chapter_id, node_type="CHAPTER")

        # Determine display order index under parent
        existing_count = CourseStructure.objects.filter(parent=parent).count()

        # Build metadata structure
        meta = {
            "drip_delay_days": drip_delay_days,
            "video_url": video_url or "",
            "is_draft": True
        }

        # Generate custom unique url slug
        slug = f"lesson-{uuid.uuid4().hex[:8]}"

        lesson = CourseStructure.objects.create(
            parent=parent,
            node_type="LESSON",
            title=title,
            slug=slug,
            description=description,
            display_order=existing_count + 1,
            metadata=meta
        )

        TeacherActivityLog.objects.create(
            teacher=teacher,
            action="CREATE_LESSON",
            details=f"Created lesson '{title}' under Chapter {parent_chapter_id}"
        )

        invalidate_teacher_dashboard_cache(teacher.id)
        return lesson


class AssignmentService:
    """Handles curriculum assessment releases and evaluations."""

    @staticmethod
    @transaction.atomic
    def grade_student_submission(
        teacher,
        submission_id: int,
        grade: float,
        feedback: str | None = None
    ) -> AssignmentSubmission:
        submission = AssignmentSubmission.objects.select_related("assignment", "student").get(id=submission_id)
        validate_grade_score(grade, submission.assignment.max_points)

        submission.grade = Decimal(str(grade))
        submission.feedback = feedback or ""
        submission.graded_by = teacher
        submission.graded_at = timezone.now()
        submission.save()

        # Trigger dynamic alerts to student
        CentralNotificationEngine.send_notification(
            user=submission.student,
            event_type="ASSIGNMENT_GRADED",
            title="Assignment Graded!",
            message=f"Your submission for {submission.assignment.title} was evaluated: {grade}/{submission.assignment.max_points}.",
            channels=["IN_APP"]
        )

        # Award points for grading completion to the teacher
        WalletService.credit_points_and_funds(
            teacher=teacher,
            amount=Decimal("5.00"),  # $5 grading incentive
            points=10,  # 10 performance points
            earning_type="GRADING_BONUS",
            description=f"Award for reviewing Assignment Submission ID: {submission.id} (Student: {submission.student.email})"
        )

        TeacherActivityLog.objects.create(
            teacher=teacher,
            action="GRADE_ASSIGNMENT",
            details=f"Graded submission {submission_id} with score {grade}"
        )

        invalidate_teacher_dashboard_cache(teacher.id)
        return submission


class QuizService:
    """Curates quiz assessments and structures Question Bank items."""

    @staticmethod
    @transaction.atomic
    def create_question_category(name: str, description: str | None = None) -> QuestionCategory:
        category, _ = QuestionCategory.objects.get_or_create(
            name=name,
            defaults={"description": description or ""}
        )
        return category

    @staticmethod
    @transaction.atomic
    def create_difficulty_tier(level: str, multiplier: float) -> QuestionDifficulty:
        validate_multiplier(multiplier)
        difficulty, _ = QuestionDifficulty.objects.get_or_create(
            level=level,
            defaults={"multiplier": Decimal(str(multiplier))}
        )
        return difficulty


class AttendanceService:
    """Logs class student stream attendance levels."""

    @staticmethod
    @transaction.atomic
    def log_live_class_attendance(
        live_class_id: uuid.UUID,
        student_id: int,
        status: str = "PRESENT",
        joined_at: datetime.datetime | None = None,
        left_at: datetime.datetime | None = None
    ) -> Attendance:
        live_class = LiveClass.objects.get(id=live_class_id)
        student = User.objects.get(id=student_id)

        attendance, _ = Attendance.objects.update_or_create(
            live_class=live_class,
            student=student,
            defaults={
                "status": status,
                "joined_at": joined_at,
                "left_at": left_at
            }
        )

        return attendance


class AnalyticsService:
    """Updates teaching indicators, averages, and milestones."""

    @staticmethod
    @transaction.atomic
    def recompute_teacher_aggregates(teacher) -> TeacherAnalytics:
        # Find active course IDs
        course_ids = CourseStructure.objects.filter(
            teacher_classes__teacher=teacher,
            node_type="COURSE"
        ).values_list("id", flat=True)

        total_students = StudentEnrollment.objects.filter(
            course_id__in=course_ids,
            status="ACTIVE"
        ).values("student").distinct().count()

        # Compute average rating
        profile = TeacherProfile.objects.filter(user=teacher).first()
        rating = profile.rating if profile else Decimal("5.00")

        # Sum elapsed teaching hours
        # Find all live classes by teacher
        completed_hours = LiveClass.objects.filter(
            teacher=teacher,
            scheduled_at__lt=timezone.now()
        ).aggregate(total=Sum("duration_minutes"))["total"] or 0
        hours = Decimal(str(completed_hours)) / Decimal("60.0")

        # Submission review pace
        assignments = Assignment.objects.filter(lesson__parent__parent__id__in=course_ids)
        total_sub = AssignmentSubmission.objects.filter(assignment__in=assignments).count()
        graded_sub = AssignmentSubmission.objects.filter(assignment__in=assignments, grade__isnull=False).count()
        completion_rate = (Decimal(str(graded_sub)) / Decimal(str(total_sub)) * Decimal("100.00")) if total_sub > 0 else Decimal("0.00")

        analytics, _ = TeacherAnalytics.objects.get_or_create(
            teacher=teacher,
            defaults={
                "total_students_taught": total_students,
                "average_course_rating": rating,
                "total_teaching_hours": hours,
                "assignment_completion_rate": completion_rate
            }
        )

        # Update if exists
        analytics.total_students_taught = total_students
        analytics.average_course_rating = rating
        analytics.total_teaching_hours = hours
        analytics.assignment_completion_rate = completion_rate
        analytics.save()

        # Evaluate award milestones based on analytics
        if total_students >= 100:
            TeacherAchievement.objects.get_or_create(
                teacher=teacher,
                title="Century Guru Milestone",
                defaults={
                    "description": "Shared learning knowledge with over 100 students on BrahmaVidya platform.",
                    "badge_icon": "users"
                }
            )

        return analytics


class CertificateService:
    """Authorizes professional achievement certificates."""

    @staticmethod
    @transaction.atomic
    def issue_teacher_credential(
        teacher,
        title: str,
        issuer: str,
        issued_date: datetime.date,
        expiry_date: datetime.date | None = None,
        verification_url: str | None = None
    ) -> TeacherCertificate:
        cert = TeacherCertificate.objects.create(
            teacher=teacher,
            title=title,
            issuer=issuer,
            issued_date=issued_date,
            expiry_date=expiry_date,
            verification_url=verification_url
        )

        TeacherActivityLog.objects.create(
            teacher=teacher,
            action="ISSUE_CERTIFICATE",
            details=f"Added external certificate verification credential: '{title}' from {issuer}"
        )

        return cert


class WalletService:
    """Manages withdrawable balances, connective payout methods, and ledger logs."""

    @staticmethod
    @transaction.atomic
    def credit_points_and_funds(
        teacher,
        amount: Decimal,
        points: int,
        earning_type: str,
        description: str | None = None,
        course: CourseStructure | None = None
    ) -> TeacherEarning:
        validate_payout_amount(amount)

        # 1. Update wallet balance reserves
        wallet, _ = TeacherWallet.objects.get_or_create(teacher=teacher)
        wallet.balance_amount += amount
        wallet.balance_points += points
        wallet.save()

        # 2. Record earning log entry
        earning = TeacherEarning.objects.create(
            teacher=teacher,
            course=course,
            amount=amount,
            points=points,
            earning_type=earning_type,
            description=description
        )

        invalidate_teacher_dashboard_cache(teacher.id)
        return earning

    @staticmethod
    @transaction.atomic
    def configure_payout_details(
        teacher,
        payout_method: str,
        payout_address: str
    ) -> TeacherWallet:
        validate_payout_address(payout_method, payout_address)

        wallet, _ = TeacherWallet.objects.get_or_create(teacher=teacher)
        wallet.payout_method = payout_method
        wallet.payout_address = payout_address
        wallet.save()

        TeacherActivityLog.objects.create(
            teacher=teacher,
            action="CONFIGURE_PAYOUT",
            details=f"Updated payout preference to {payout_method}."
        )

        invalidate_teacher_dashboard_cache(teacher.id)
        return wallet

    @staticmethod
    @transaction.atomic
    def request_withdrawal(teacher, withdraw_amount: Decimal) -> Decimal:
        validate_payout_amount(withdraw_amount)

        wallet = TeacherWallet.objects.get(teacher=teacher)
        if wallet.balance_amount < withdraw_amount:
            raise ValidationError("Insufficient withdrawable balance reserves in wallet.")

        wallet.balance_amount -= withdraw_amount
        wallet.last_payout_at = timezone.now()
        wallet.save()

        # Audit withdrawal activity
        TeacherActivityLog.objects.create(
            teacher=teacher,
            action="REQUEST_WITHDRAWAL",
            details=f"Withdrew ${withdraw_amount} via {wallet.payout_method}"
        )

        invalidate_teacher_dashboard_cache(teacher.id)
        return wallet.balance_amount
