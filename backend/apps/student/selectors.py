"""
Student Dashboard Selectors — BrahmaVidya Galaxy
Sprint 20: Aggregate query abstraction and database query logic.
"""

from __future__ import annotations

import datetime
from django.db.models import QuerySet, Sum, Q
from django.utils import timezone
from django.core.cache import cache

from apps.student.models import (
    Bookmark, StudentNote, StudyGoal,
    StudySession, StudyCalendarEvent, DailyProgress,
    WeeklyProgress, MonthlyProgress, LearningStreak,
    RecentlyViewedLesson, LearningReminder,
)
from apps.lms.models import CourseStructure, StudentEnrollment, LiveClass


class DashboardSelector:
    """
    Selectors for consolidating student portal dashboard widgets.
    """

    @staticmethod
    def get_student_dashboard_context(user) -> dict:
        """
        Compiles the primary dashboard data payload in a single nested dict.
        """
        cache_key = f"dashboard_context_{user.id}"
        try:
            cached_data = cache.get(cache_key)
            if cached_data:
                return cached_data
        except Exception:
            pass

        today = timezone.now().date()
        week_start = today - datetime.timedelta(days=today.weekday())  # Monday

        # 1. Fetch Streak
        streak_record = LearningStreak.objects.filter(student=user).first()
        streak_data = {
            "current_streak": streak_record.current_streak if streak_record else 0,
            "longest_streak": streak_record.longest_streak if streak_record else 0,
            "total_study_days": streak_record.total_study_days if streak_record else 0,
            "total_xp": streak_record.total_xp if streak_record else 0,
        }

        # 2. Fetch Daily Progress (Today)
        daily_record = DailyProgress.objects.filter(student=user, date=today).first()
        today_stats = {
            "study_minutes": daily_record.study_minutes if daily_record else 0,
            "lessons_completed": daily_record.lessons_completed if daily_record else 0,
            "xp_earned": daily_record.xp_earned if daily_record else 0,
            "lessons_accessed": daily_record.lessons_accessed if daily_record else 0,
        }

        # 3. Fetch Weekly Progress (Current Week)
        weekly_record = WeeklyProgress.objects.filter(student=user, week_start=week_start).first()
        weekly_stats = {
            "study_minutes": weekly_record.study_minutes if weekly_record else 0,
            "lessons_completed": weekly_record.lessons_completed if weekly_record else 0,
            "xp_earned": weekly_record.xp_earned if weekly_record else 0,
            "goal_minutes": weekly_record.goal_minutes if weekly_record else 0,
        }

        # 4. Fetch Goals summary
        active_goals_count = StudyGoal.objects.filter(
            student=user,
            status=StudyGoal.GoalStatus.ACTIVE
        ).count()

        # 5. Bookmarks summary (top 5 recent)
        recent_bookmarks = Bookmark.objects.filter(student=user).order_by("-created_at")[:5]
        bookmarks_data = [
            {
                "id": str(b.id),
                "content_type": b.content_type,
                "content_id": str(b.content_id),
                "title": b.title,
                "source_name": b.source_name,
                "url_path": b.url_path,
                "created_at": b.created_at.isoformat(),
            }
            for b in recent_bookmarks
        ]

        # 6. Recently Viewed Lessons
        recent_views = RecentlyViewedLesson.objects.filter(student=user).select_related("node").order_by("-viewed_at")[:5]
        recently_viewed_data = [
            {
                "id": rv.id,
                "node_id": rv.node.id,
                "title": rv.node.title,
                "node_type": rv.node.node_type,
                "viewed_at": rv.viewed_at.isoformat(),
            }
            for rv in recent_views
        ]

        # 7. Active Study Session
        active_session = StudySession.objects.filter(student=user, is_active=True).first()
        active_session_data = None
        if active_session:
            active_session_data = {
                "id": str(active_session.id),
                "node_id": active_session.node.id if active_session.node else None,
                "node_title": active_session.node.title if active_session.node else None,
                "started_at": active_session.started_at.isoformat(),
            }

        context_data = {
            "streak": streak_data,
            "today_stats": today_stats,
            "weekly_stats": weekly_stats,
            "active_goals_count": active_goals_count,
            "bookmarks": bookmarks_data,
            "recently_viewed": recently_viewed_data,
            "active_session": active_session_data,
        }
        try:
            cache.set(cache_key, context_data, timeout=300)
        except Exception:
            pass
        return context_data


class ProgressSelector:
    """
    Selectors for aggregated learning logs and performance graphs.
    """

    @staticmethod
    def get_weekly_metrics(user, weeks_back: int = 4) -> list[dict]:
        """
        Compiles list of weekly stats for trend analysis.
        """
        today = timezone.now().date()
        monday = today - datetime.timedelta(days=today.weekday())

        metrics = []
        for i in range(weeks_back):
            target_monday = monday - datetime.timedelta(weeks=i)
            record = WeeklyProgress.objects.filter(student=user, week_start=target_monday).first()
            metrics.append({
                "week_start": target_monday.isoformat(),
                "study_minutes": record.study_minutes if record else 0,
                "lessons_completed": record.lessons_completed if record else 0,
                "xp_earned": record.xp_earned if record else 0,
                "goal_minutes": record.goal_minutes if record else 0,
            })
        return metrics[::-1]  # Return in chronological order

    @staticmethod
    def get_monthly_timeline(user) -> list[dict]:
        """
        Compiles monthly completion summaries.
        """
        records = MonthlyProgress.objects.filter(student=user).order_by("-year", "-month")[:12]
        return [
            {
                "year": r.year,
                "month": r.month,
                "study_minutes": r.study_minutes,
                "lessons_completed": r.lessons_completed,
                "courses_completed": r.courses_completed,
                "xp_earned": r.xp_earned,
                "badges_earned": r.badges_earned,
            }
            for r in reversed(records)
        ]


class BookmarkSelector:
    """
    Selectors for handling learner bookmarks.
    """

    @staticmethod
    def get_user_bookmarks(user, content_type: str | None = None) -> QuerySet[Bookmark]:
        """
        Retrieves user bookmarks with optional content type filtering.
        """
        qs = Bookmark.objects.filter(student=user)
        if content_type:
            qs = qs.filter(content_type=content_type)
        return qs.order_by("-created_at")


class NoteSelector:
    """
    Selectors for student notes.
    """

    @staticmethod
    def get_notes_by_course(user, course_id: int) -> QuerySet[StudentNote]:
        """
        Fetches notes created under nodes matching or belonging to the course hierarchy.
        """
        # Find all nodes under the course parent
        descendant_node_ids = CourseStructure.objects.filter(
            Q(id=course_id) | Q(parent_id=course_id) | Q(parent__parent_id=course_id)
        ).values_list("id", flat=True)

        return StudentNote.objects.filter(
            student=user,
            node_id__in=descendant_node_ids
        ).select_related("node").order_by("-is_pinned", "-updated_at")


class CalendarSelector:
    """
    Selectors to compile personalized agenda timelines.
    """

    @staticmethod
    def get_events_range(user, start_date: datetime.date, end_date: datetime.date) -> list[dict]:
        """
        Combines custom student StudyCalendarEvents and enrolled course LiveClasses.
        """
        # 1. Fetch custom events
        custom_events = StudyCalendarEvent.objects.filter(
            student=user,
            starts_at__date__gte=start_date,
            starts_at__date__lte=end_date
        ).select_related("node")

        events_payload = [
            {
                "id": str(e.id),
                "source": "CUSTOM",
                "title": e.title,
                "description": e.description,
                "event_type": e.event_type,
                "starts_at": e.starts_at.isoformat(),
                "ends_at": e.ends_at.isoformat() if e.ends_at else None,
                "all_day": e.all_day,
                "color": e.color,
                "is_completed": e.is_completed,
                "node_id": e.node.id if e.node else None,
            }
            for e in custom_events
        ]

        # 2. Fetch Live Classes for user enrollments
        enrolled_course_ids = StudentEnrollment.objects.filter(
            student=user,
            status="ACTIVE"
        ).values_list("course_id", flat=True)

        live_classes = LiveClass.objects.filter(
            course_id__in=enrolled_course_ids,
            scheduled_at__date__gte=start_date,
            scheduled_at__date__lte=end_date
        ).select_related("course")

        for lc in live_classes:
            end_time = lc.scheduled_at + datetime.timedelta(minutes=lc.duration_minutes)
            events_payload.append({
                "id": str(lc.id),
                "source": "SYSTEM_LIVE_CLASS",
                "title": f"Live Class: {lc.title}",
                "description": f"Course: {lc.course.title}",
                "event_type": "LIVE_CLASS",
                "starts_at": lc.scheduled_at.isoformat(),
                "ends_at": end_time.isoformat(),
                "all_day": False,
                "color": "rose",
                "is_completed": False,
                "node_id": lc.course.id,
            })

        return sorted(events_payload, key=lambda x: x["starts_at"])
