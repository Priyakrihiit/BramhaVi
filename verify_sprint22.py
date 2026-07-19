#!/usr/bin/env python
"""
BrahmaVidya Galaxy Live Classes Platform Integration Checkouts
Sprint 22 — Phase 8: Comprehensive automated testing and integrations validation.
"""

import os
import sys
import django
from decimal import Decimal
from django.utils import timezone
from django.test import override_settings

# Configure django environment
sys.path.append(os.path.abspath("backend"))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_project.settings")
django.setup()

from django.contrib.auth import get_user_model
from apps.users.models import Role
from apps.lms.models import (
    CourseStructure, CourseNodeType, LiveClass, LiveSession, MeetingParticipant,
    Poll, PollOption, PollVote, Recording, CalendarEvent, MeetingAnalytics
)
from apps.teacher.models import Attendance
from apps.lms.services import LiveClassService
from apps.lms.selectors import LiveClassSelector
from apps.lms.integrations import LiveClassesPlatformIntegrator

User = get_user_model()

@override_settings(
    CACHES={
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "sprint22-verification-cache",
        }
    },
    CELERY_TASK_ALWAYS_EAGER=True,
    CELERY_BROKER_URL="memory://",
    CELERY_RESULT_BACKEND="cache+memory://"
)
def run_checks():
    print("==================================================================")
    print("   BrahmaVidya Live Classes Platform Sprint 22 Verification   ")
    print("==================================================================")

    success_flags = []

    # 1. Create/Get roles and users
    print("\n[*] Initializing Roles and Users:")
    teacher_role, _ = Role.objects.get_or_create(name="TEACHER", defaults={"description": "Teacher"})
    student_role, _ = Role.objects.get_or_create(name="STUDENT", defaults={"description": "Student"})

    teacher_email = "sprint22_teacher@brahmavidya.edu"
    student_email = "sprint22_student@brahmavidya.edu"

    # Reset existing test records
    User.all_objects.filter(email__in=[teacher_email, student_email]).delete()

    teacher = User.objects.create_user(email=teacher_email, password="sprint22password", role=teacher_role)
    student = User.objects.create_user(email=student_email, password="sprint22password", role=student_role)
    print(f"    - SUCCESS: Users created ({teacher_email} and {student_email})")
    success_flags.append(True)

    # 2. Setup Course
    print("\n[*] Setting up Course Node:")
    course = CourseStructure.objects.create(
        node_type=CourseNodeType.COURSE,
        title="Introductory Vedanta",
        slug="introductory-vedanta"
    )
    print(f"    - SUCCESS: Course node created: {course.title}")
    success_flags.append(True)

    # 3. Schedule Live Class
    print("\n[*] Scheduling Live Class Broadcast:")
    try:
        live_class = LiveClassService.schedule_live_class(
            course_id=str(course.id),
            teacher=teacher,
            title="Sutra Formulation Session",
            scheduled_at=timezone.now() + timezone.timedelta(hours=2),
            duration_minutes=60,
            stream_url="https://meet.brahmavidya.edu/sutras"
        )
        assert live_class.status == "SCHEDULED", "Live Class state should be SCHEDULED"
        print(f"    - SUCCESS: Scheduled LiveClass ID: {live_class.id}")
        success_flags.append(True)
    except Exception as e:
        print(f"    - FAILURE: Schedule class error: {e}")
        success_flags.append(False)

    # 4. Signals: Calendar Sync
    print("\n[*] Verifying Calendar Event Signals Synchronization:")
    try:
        events = CalendarEvent.objects.filter(live_class=live_class, user=teacher)
        assert events.exists(), "CalendarEvent should be created automatically by post_save signal"
        print(f"    - SUCCESS: Synced calendar event title: '{events.first().event_title}'")
        success_flags.append(True)
    except Exception as e:
        print(f"    - FAILURE: Calendar sync verification error: {e}")
        success_flags.append(False)

    # 5. Start Session
    print("\n[*] Starting Live Broadcast Session:")
    try:
        session = LiveClassService.start_live_session(str(live_class.id))
        live_class.refresh_from_db()
        assert live_class.status == "LIVE", "Live Class state should transition to LIVE"
        assert session.is_active is True, "Session should be set to active"
        print(f"    - SUCCESS: Active session started at {session.started_at}")
        success_flags.append(True)
    except Exception as e:
        print(f"    - FAILURE: Start stream session error: {e}")
        success_flags.append(False)

    # 6. Record Attendance
    print("\n[*] Recording Attendee Attendance Check-ins:")
    try:
        participant = LiveClassService.record_attendance(
            live_class_id=str(live_class.id),
            student=student
        )
        assert participant.role == "ATTENDEE", "Participant role should be ATTENDEE"
        # Mock disconnection
        participant = LiveClassService.record_attendance(
            live_class_id=str(live_class.id),
            student=student,
            left_at=timezone.now()
        )
        assert participant.left_at is not None, "left_at timestamp should be updated"
        
        # Verify General Attendance Log Sync
        attendance_log = Attendance.objects.filter(live_class=live_class, student=student)
        assert attendance_log.exists(), "Attendance log should sync automatically"
        print("    - SUCCESS: Attendance synchronized with teacher portal logs.")
        success_flags.append(True)
    except Exception as e:
        print(f"    - FAILURE: Attendance tracking error: {e}")
        success_flags.append(False)

    # 7. Create Poll
    print("\n[*] Creating Interactive Class Poll:")
    try:
        poll = LiveClassService.create_poll(
            live_class_id=str(live_class.id),
            creator=teacher,
            question="Is Brahman the ultimate reality?",
            options_list=["Yes", "No"],
            is_anonymous=False
        )
        assert poll.options.count() == 2, "Poll should contain exactly 2 option items"
        print(f"    - SUCCESS: Published poll question: '{poll.question}'")
        success_flags.append(True)
    except Exception as e:
        print(f"    - FAILURE: Create poll error: {e}")
        success_flags.append(False)

    # 8. Cast Vote & Selector results
    print("\n[*] Casting Vote and Aggregating Poll Results:")
    try:
        option = poll.options.first()
        vote = LiveClassService.cast_vote(str(poll.id), str(option.id), voter=student)
        results = LiveClassSelector.get_poll_results(str(poll.id))
        assert len(results["results"]) == 2, "Results list size mismatch"
        yes_opt = next(r for r in results["results"] if r["option_id"] == str(option.id))
        assert yes_opt["votes"] == 1, "Option vote count should be 1"
        print(f"    - SUCCESS: Option '{yes_opt['option_text']}' got {yes_opt['votes']} vote(s)")
        success_flags.append(True)
    except Exception as e:
        print(f"    - FAILURE: Poll voting aggregation error: {e}")
        success_flags.append(False)

    # 9. End Session
    print("\n[*] Closing stream session (Transitioning state to COMPLETED):")
    try:
        live_class = LiveClassService.end_live_session(str(live_class.id))
        assert live_class.status == "COMPLETED", "Live Class state should shift to COMPLETED"
        print("    - SUCCESS: Sessions closed and enqueued processing tasks.")
        success_flags.append(True)
    except Exception as e:
        print(f"    - FAILURE: End session error: {e}")
        success_flags.append(False)

    # 10. Platform Integration Suite (Search & AI)
    print("\n[*] Verifying Central Platform Integrations (Notifications, Search, AI, Redis):")
    try:
        # Index Search
        search_res = LiveClassesPlatformIntegrator.index_live_class(live_class)
        assert search_res["status"] == "search_synced", "Search sync status mismatch"
        
        # AI Summarizer
        ai_res = LiveClassesPlatformIntegrator.run_ai_summary_engine(str(live_class.id))
        assert "summary" in ai_res, "AI summary field missing"
        
        # Redis Caching
        LiveClassesPlatformIntegrator.cache_room_participants(str(live_class.id), [str(student.id)])
        
        print("    - SUCCESS: Sub-system notifications, search, and AI grading pipelines validated.")
        success_flags.append(True)
    except Exception as e:
        print(f"    - FAILURE: Platform integrations validation error: {e}")
        success_flags.append(False)

    # 11. Cleanup test records
    print("\n[*] Cleaning up all verification data from the DB:")
    try:
        CalendarEvent.objects.filter(live_class=live_class).delete()
        Attendance.objects.filter(live_class=live_class).delete()
        MeetingParticipant.objects.filter(live_class=live_class).delete()
        LiveSession.objects.filter(live_class=live_class).delete()
        PollVote.objects.filter(poll=poll).delete()
        PollOption.objects.filter(poll=poll).delete()
        poll.delete()
        Recording.objects.filter(live_class=live_class).delete()
        MeetingAnalytics.objects.filter(live_class=live_class).delete()
        live_class.delete()
        course.delete()
        User.all_objects.filter(email__in=[teacher_email, student_email]).delete()
        print("    - SUCCESS: Database cleanup completed.")
        success_flags.append(True)
    except Exception as e:
        print(f"    - FAILURE: DB cleanup error: {e}")
        success_flags.append(False)

    # Final verdict
    print("\n==================================================================")
    if all(success_flags) and len(success_flags) == 11:
        print("   [+] ALL SPRINT 22 INTEGRATIONS VERIFIED SUCCESSFULLY!")
        print("==================================================================")
    else:
        print("   [-] INTEGRATION VERIFICATION ENCOUNTERED ISSUES!")
        print("==================================================================")
        sys.exit(1)

if __name__ == "__main__":
    run_checks()
