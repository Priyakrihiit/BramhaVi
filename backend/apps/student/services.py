"""
Student Dashboard Services — BrahmaVidya Galaxy
Sprint 20: Core business services and transaction workflows.
"""

from __future__ import annotations

import datetime
from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ValidationError

from apps.student.models import (
    LearningHistory, ContinueLearning, Bookmark,
    StudentNote, StudyGoal, StudySession,
    DailyProgress, WeeklyProgress, MonthlyProgress,
    LearningStreak, RecentlyViewedLesson, Achievement,
    StudentAchievement, StudentPreference, LearningReminder,
)
from apps.student.validators import validate_goal_dates, validate_note_length, validate_reminder_time
from apps.lms.models import CourseStructure, StudentEnrollment


class LearningHistoryService:
    """
    Manages learning history logs, recently viewed leson buffers, and progress aggregations.
    """

    @staticmethod
    @transaction.atomic
    def log_lesson_visit(
        student,
        node_id: int,
        duration_seconds: int = 0,
        completed: bool = False,
        enrollment_id: int | None = None
    ) -> LearningHistory:
        node = CourseStructure.objects.get(id=node_id)
        enrollment = None
        if enrollment_id:
            enrollment = StudentEnrollment.objects.get(id=enrollment_id)
        elif node.parent_id:
            # Fallback lookup for active enrollment of the course hierarchy
            enrollment = StudentEnrollment.objects.filter(
                student=student,
                course_id=node.parent_id,
                status="ACTIVE"
            ).first()

        # 1. Create audit log
        history = LearningHistory.objects.create(
            student=student,
            node=node,
            enrollment=enrollment,
            duration_seconds=duration_seconds,
            completed=completed,
            accessed_at=timezone.now()
        )

        # 2. Update LRU recently viewed lesson buffer
        RecentlyViewedLesson.objects.update_or_create(
            student=student,
            node=node,
            defaults={"viewed_at": timezone.now()}
        )

        # Limit recent lessons count to 20
        rv_to_delete = RecentlyViewedLesson.objects.filter(student=student).order_by("-viewed_at")[20:]
        if rv_to_delete:
            RecentlyViewedLesson.objects.filter(id__in=[r.id for r in rv_to_delete]).delete()

        # 3. Update aggregations if duration > 0 or completed
        if duration_seconds > 0 or completed:
            minutes = duration_seconds // 60
            xp_earned = (duration_seconds // 60) * 2 + (50 if completed else 0)
            
            # Upsert Daily Progress
            today = timezone.now().date()
            daily, _ = DailyProgress.objects.get_or_create(student=student, date=today)
            daily.study_minutes += minutes
            if completed:
                daily.lessons_completed += 1
            daily.xp_earned += xp_earned
            daily.lessons_accessed += 1
            daily.save()

            # Upsert Weekly Progress
            week_start = today - datetime.timedelta(days=today.weekday())
            weekly, _ = WeeklyProgress.objects.get_or_create(student=student, week_start=week_start)
            weekly.study_minutes += minutes
            if completed:
                weekly.lessons_completed += 1
            weekly.xp_earned += xp_earned
            weekly.save()

            # Upsert Monthly Progress
            monthly, _ = MonthlyProgress.objects.get_or_create(student=student, year=today.year, month=today.month)
            monthly.study_minutes += minutes
            if completed:
                monthly.lessons_completed += 1
            monthly.xp_earned += xp_earned
            monthly.save()

            # Update streak lifetime XP and study days
            streak, _ = LearningStreak.objects.get_or_create(student=student)
            streak.total_xp += xp_earned
            if streak.last_studied_date != today:
                streak.total_study_days += 1
                streak.last_studied_date = today
            streak.save()

        return history


class ContinueLearningService:
    """
    Manages learner resume positions.
    """

    @staticmethod
    def update_progress_pointer(
        student,
        enrollment_id: int,
        last_node_id: int,
        position_seconds: int = 0
    ) -> ContinueLearning:
        enrollment = StudentEnrollment.objects.get(id=enrollment_id)
        last_node = CourseStructure.objects.get(id=last_node_id)

        record, _ = ContinueLearning.objects.update_or_create(
            student=student,
            enrollment=enrollment,
            defaults={
                "last_node": last_node,
                "position_seconds": position_seconds,
            }
        )
        return record


class BookmarkService:
    """
    Favorites and bookmark management.
    """

    @staticmethod
    def toggle_bookmark(
        student,
        content_type: str,
        content_id,
        title: str,
        source_name: str | None = None,
        url_path: str | None = None,
        note: str | None = None
    ) -> tuple[Bookmark | None, bool]:
        """
        Toggles bookmark: if exists, delete it. If not, create it.
        Returns (bookmark, created) tuple.
        """
        existing = Bookmark.objects.filter(
            student=student,
            content_type=content_type,
            content_id=content_id
        ).first()

        if existing:
            existing.delete()
            return None, False

        bookmark = Bookmark.objects.create(
            student=student,
            content_type=content_type,
            content_id=content_id,
            title=title,
            source_name=source_name,
            url_path=url_path,
            note=note
        )
        return bookmark, True


class NoteService:
    """
    Student learning note management.
    """

    @staticmethod
    def save_lesson_note(
        student,
        node_id: int,
        content: str,
        title: str | None = None,
        tags: list | None = None,
        is_pinned: bool = False
    ) -> StudentNote:
        validate_note_length(content)
        node = CourseStructure.objects.get(id=node_id)

        note = StudentNote.objects.create(
            student=student,
            node=node,
            title=title,
            content=content,
            tags=tags or [],
            is_pinned=is_pinned
        )
        return note

    @staticmethod
    def update_lesson_note(
        student,
        note_id,
        content: str,
        title: str | None = None,
        tags: list | None = None,
        is_pinned: bool | None = None
    ) -> StudentNote:
        validate_note_length(content)
        note = StudentNote.objects.get(id=note_id, student=student)

        note.content = content
        if title is not None:
            note.title = title
        if tags is not None:
            note.tags = tags
        if is_pinned is not None:
            note.is_pinned = is_pinned

        note.save()
        return note


class GoalService:
    """
    Manages study goals and target completion deadlines.
    """

    @staticmethod
    def create_study_goal(
        student,
        title: str,
        target_date,
        description: str | None = None,
        daily_target_minutes: int = 60,
        enrollment_id: int | None = None
    ) -> StudyGoal:
        validate_goal_dates(target_date)
        enrollment = None
        if enrollment_id:
            enrollment = StudentEnrollment.objects.get(id=enrollment_id)

        goal = StudyGoal.objects.create(
            student=student,
            enrollment=enrollment,
            title=title,
            description=description,
            target_date=target_date,
            daily_target_minutes=daily_target_minutes,
            status=StudyGoal.GoalStatus.ACTIVE
        )
        return goal

    @staticmethod
    def update_goal_progress(
        student,
        goal_id,
        progress_percentage: float,
        status: str | None = None
    ) -> StudyGoal:
        goal = StudyGoal.objects.get(id=goal_id, student=student)
        goal.progress_percentage = progress_percentage

        if progress_percentage >= 100.0:
            goal.status = StudyGoal.GoalStatus.COMPLETED
            goal.completed_at = timezone.now()
        elif status:
            goal.status = status

        goal.save()
        return goal


class SessionService:
    """
    Tracks and closes timed study sessions.
    """

    @staticmethod
    @transaction.atomic
    def start_study_session(student, node_id: int | None = None) -> StudySession:
        # Close any lingering active session
        active_sessions = StudySession.objects.filter(student=student, is_active=True)
        for s in active_sessions:
            s.end_session()

        node = None
        if node_id:
            node = CourseStructure.objects.get(id=node_id)

        session = StudySession.objects.create(
            student=student,
            node=node,
            started_at=timezone.now(),
            is_active=True
        )
        return session

    @staticmethod
    @transaction.atomic
    def end_study_session(student, session_id) -> StudySession:
        session = StudySession.objects.get(id=session_id, student=student)
        if not session.is_active:
            return session

        session.end_session()

        # Award default XP (10 points base, plus 2 points per minute studied)
        minutes_studied = session.duration_seconds // 60
        xp_earned = 10 + (minutes_studied * 2)
        session.xp_earned = xp_earned
        session.save()

        # Cascade log metrics to progress tables using LearningHistoryService helper metrics
        if session.node:
            LearningHistoryService.log_lesson_visit(
                student=student,
                node_id=session.node.id,
                duration_seconds=session.duration_seconds,
                completed=False
            )

        return session


class StreakService:
    """
    Calculates learning streaks.
    """

    @staticmethod
    @transaction.atomic
    def update_login_streak(student) -> LearningStreak:
        today = timezone.now().date()
        streak, created = LearningStreak.objects.get_or_create(
            student=student,
            defaults={"streak_start_date": today}
        )

        if created:
            streak.current_streak = 1
            streak.longest_streak = 1
            streak.last_studied_date = today
            streak.save()
            return streak

        last_date = streak.last_studied_date
        if last_date == today:
            # Already checked in today
            return streak

        yesterday = today - datetime.timedelta(days=1)
        if last_date == yesterday:
            # Consecutive day!
            streak.current_streak += 1
            if streak.current_streak > streak.longest_streak:
                streak.longest_streak = streak.current_streak
        else:
            # Streak broken, reset
            streak.current_streak = 1
            streak.streak_start_date = today

        streak.last_studied_date = today
        streak.save()
        return streak

    @staticmethod
    def decay_streaks() -> None:
        """
        Cron decay service to find expired streak limits and reset.
        """
        yesterday = timezone.now().date() - datetime.timedelta(days=1)
        # Reset current streak to 0 if last_studied_date is older than yesterday
        LearningStreak.objects.filter(
            last_studied_date__lt=yesterday
        ).update(current_streak=0)


class AchievementService:
    """
    Evaluates, awards, and tracking achievement records.
    """

    @staticmethod
    @transaction.atomic
    def evaluate_achievements(student) -> list[StudentAchievement]:
        unlocked_records = []
        streak = LearningStreak.objects.filter(student=student).first()
        streak_count = streak.current_streak if streak else 0
        total_study_days = streak.total_study_days if streak else 0

        # Scan active Achievements
        achievements = Achievement.objects.filter(is_active=True)
        for ach in achievements:
            criteria = ach.criteria or {}
            target_streak = criteria.get("streak_days")
            target_days = criteria.get("total_study_days")

            unlocked = False
            progress = 0.0

            if target_streak:
                progress = min(float(streak_count), float(target_streak))
                if streak_count >= target_streak:
                    unlocked = True
            elif target_days:
                progress = min(float(total_study_days), float(target_days))
                if total_study_days >= target_days:
                    unlocked = True

            # Get or create tracking record
            record, created = StudentAchievement.objects.get_or_create(
                student=student,
                achievement=ach,
                defaults={"progress_value": progress}
            )

            if not record.is_unlocked:
                record.progress_value = progress
                if unlocked:
                    record.is_unlocked = True
                    record.unlocked_at = timezone.now()
                    # Award reward points
                    if streak:
                        streak.total_xp += ach.xp_reward
                        streak.save()
                record.save()

            if record.is_unlocked and (created or record.unlocked_at == record.updated_at):
                unlocked_records.append(record)

        return unlocked_records
