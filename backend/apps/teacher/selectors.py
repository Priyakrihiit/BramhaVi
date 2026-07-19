"""
Teacher Portal Selectors — BrahmaVidya Galaxy
Sprint 21: High-performance database selectors, aggregates, and caching layers.
"""

from __future__ import annotations

import datetime
from decimal import Decimal
from django.db.models import Sum, Avg, Count, Q
from django.utils import timezone
from django.core.cache import cache
from django.contrib.auth import get_user_model

from apps.teacher.models import (
    TeacherProfile, TeacherAnalytics, TeachingSession, Batch, Attendance,
    TeacherAnnouncement, TeacherSchedule, TeachingGoal, TeacherEarning,
    TeacherWallet, TeacherCertificate, TeacherActivityLog
)
from apps.lms.models import (
    CourseStructure, Assignment, AssignmentSubmission, Exam, ExamAttempt, LiveClass, StudentEnrollment
)

User = get_user_model()


class TeacherDashboardSelector:
    """
    Selectors compiling consolidated views of teacher portal statistics, alerts, and schedules.
    """

    @staticmethod
    def get_dashboard_summary(teacher) -> dict:
        """
        Gathers primary dashboard indicators, caching results in Redis to reduce database hits.
        """
        cache_key = f"teacher_dashboard_summary_{teacher.id}"
        try:
            cached_data = cache.get(cache_key)
            if cached_data is not None:
                return cached_data
        except Exception:
            pass

        now = timezone.now()
        today = now.date()

        # 1. Total Courses Instructing (Active)
        # Find courses where teacher has an active class entry
        active_course_ids = CourseStructure.objects.filter(
            teacher_classes__teacher=teacher,
            teacher_classes__is_active=True,
            node_type="COURSE"
        ).values_list("id", flat=True)
        total_active_courses = len(active_course_ids)

        # 2. Total Enrolled Students (Distinct across assigned courses)
        total_students = StudentEnrollment.objects.filter(
            course_id__in=active_course_ids,
            status="ACTIVE"
        ).values("student").distinct().count()

        # 3. Pending Evaluations Count (Submissions without grades for assigned courses)
        pending_evaluations = AssignmentSubmission.objects.filter(
            assignment__lesson__parent__parent__id__in=active_course_ids,  # Hierarchy check: Lesson -> Chapter -> Course
            grade__isnull=True
        ).count()

        # 4. Net Revenue Share Earnings (Current month MTD)
        start_of_month = today.replace(day=1)
        mtd_revenue = TeacherEarning.objects.filter(
            teacher=teacher,
            earning_type="REVENUE_SHARE",
            recorded_at__date__gte=start_of_month
        ).aggregate(total=Sum("amount"))["total"] or Decimal("0.00")

        # 5. Up-next Live Stream Lectures & General Sessions (Combined timeline)
        upcoming_streams = LiveClass.objects.filter(
            teacher=teacher,
            scheduled_at__gte=now
        ).order_by("scheduled_at")[:3]

        upcoming_sessions = TeachingSession.objects.filter(
            teacher=teacher,
            start_time__gte=now
        ).order_by("start_time")[:3]

        schedule_timeline = []
        for s in upcoming_streams:
            schedule_timeline.append({
                "type": "LIVE_CLASS",
                "id": str(s.id),
                "title": s.title,
                "course_title": s.course.title,
                "time": s.scheduled_at.isoformat(),
                "duration": s.duration_minutes,
                "link": s.stream_url or ""
            })
        for s in upcoming_sessions:
            schedule_timeline.append({
                "type": "TUTORING",
                "id": str(s.id),
                "title": s.title,
                "course_title": s.get_session_type_display(),
                "time": s.start_time.isoformat(),
                "duration": int((s.end_time - s.start_time).total_seconds() // 60),
                "link": s.meeting_link or ""
            })
        schedule_timeline = sorted(schedule_timeline, key=lambda x: x["time"])[:5]

        # 6. Performance Indicators (Rating metrics from profile)
        profile = TeacherProfile.objects.filter(user=teacher).first()
        rating = profile.rating if profile else Decimal("5.00")

        # Compile final dictionary payload
        summary_payload = {
            "metrics": {
                "total_active_courses": total_active_courses,
                "total_students": total_students,
                "pending_evaluations": pending_evaluations,
                "mtd_earnings": float(mtd_revenue),
                "average_rating": float(rating),
            },
            "schedule_timeline": schedule_timeline,
            "last_cached_at": now.isoformat()
        }

        try:
            cache.set(cache_key, summary_payload, timeout=300)  # Cache for 5 minutes
        except Exception:
            pass

        return summary_payload


class TeacherAnalyticsSelector:
    """
    Selectors executing complex math aggregation formulas for instructional indicators.
    """

    @staticmethod
    def get_course_performance_report(teacher, course_id: int) -> dict:
        """
        Compiles structural performance metrics of students registered under a course.
        """
        # Validate that the course belongs to the teacher
        if not CourseStructure.objects.filter(id=course_id, teacher_classes__teacher=teacher).exists():
            return {}

        # Fetch enrollments
        enrollments = StudentEnrollment.objects.filter(course_id=course_id)
        total_students = enrollments.count()
        active_students = enrollments.filter(status="ACTIVE").count()
        completed_students = enrollments.filter(status="COMPLETED").count()

        # Fetch Average Scores for Exams under this course
        exams = Exam.objects.filter(course_id=course_id)
        attempts = ExamAttempt.objects.filter(exam__in=exams, status="SUBMITTED")
        avg_score = attempts.aggregate(avg=Avg("score"))["avg"] or 0.0

        # Fetch Assignment submissions grading details
        assignments = Assignment.objects.filter(lesson__parent__parent__id=course_id)
        submissions = AssignmentSubmission.objects.filter(assignment__in=assignments)
        graded_submissions = submissions.filter(grade__isnull=False)
        avg_grade = graded_submissions.aggregate(avg=Avg("grade"))["avg"] or 0.0

        total_submissions = submissions.count()
        pending_submissions = submissions.filter(grade__isnull=True).count()

        completion_rate = (completed_students / total_students * 100) if total_students > 0 else 0.0

        return {
            "course_id": course_id,
            "enrollment_stats": {
                "total_students": total_students,
                "active_students": active_students,
                "completed_students": completed_students,
                "completion_percentage": round(completion_rate, 2)
            },
            "performance_stats": {
                "average_exam_score": round(float(avg_score), 2),
                "average_assignment_grade": round(float(avg_grade), 2),
                "total_assignment_submissions": total_submissions,
                "pending_evaluations": pending_submissions
            }
        }


class TeacherEarningSelector:
    """
    Selectors detailing payout history and points ledgers for teacher dashboards.
    """

    @staticmethod
    def get_earnings_summary(teacher) -> dict:
        """
        Compiles balance reserves, transaction breakdown list, and month-over-month summaries.
        """
        wallet = TeacherWallet.objects.filter(teacher=teacher).first()
        balance_amount = wallet.balance_amount if wallet else Decimal("0.00")
        balance_points = wallet.balance_points if wallet else 0

        # Earnings category breakdown
        earnings_by_type = TeacherEarning.objects.filter(teacher=teacher).values("earning_type").annotate(
            total=Sum("amount"),
            count=Count("id")
        )

        category_distribution = {
            item["earning_type"]: {
                "total": float(item["total"]),
                "count": item["count"]
            }
            for item in earnings_by_type
        }

        # Last 10 ledger transactions
        recent_earnings = TeacherEarning.objects.filter(teacher=teacher).order_by("-recorded_at")[:10]
        recent_transactions = [
            {
                "id": str(e.id),
                "amount": float(e.amount),
                "points": e.points,
                "earning_type": e.earning_type,
                "description": e.description or "",
                "recorded_at": e.recorded_at.isoformat()
            }
            for e in recent_earnings
        ]

        return {
            "balances": {
                "withdrawable_amount": float(balance_amount),
                "withdrawable_points": balance_points,
                "payout_method": wallet.payout_method if wallet else "STRIPE",
                "payout_address": wallet.payout_address if wallet else ""
            },
            "categories": category_distribution,
            "recent_transactions": recent_transactions
        }
