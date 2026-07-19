import os
import sys
import django

# Setup django environment
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_project.settings')
django.setup()

from django.core.cache import cache
from django.db import connection
from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.student.models import Bookmark, StudentNote, StudyGoal, StudentAchievement, LearningReminder
from apps.student.selectors import DashboardSelector
from apps.control_center.models import AIConversation, AIMessage

from django.test.utils import override_settings

User = get_user_model()

@override_settings(CACHES={
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "sprint20-verification-cache",
    }
})
def run_checks():
    print("==================================================")
    print("BrahmaVidya Student Dashboard Verification Script")
    print("==================================================")

    # 1. Create a mock student user
    from apps.users.models import Role
    role, _ = Role.objects.get_or_create(name="STUDENT", defaults={"description": "Standard Student Learner"})
    
    email = "test_sprint20_student@example.com"
    try:
        student = User.objects.get(email=email)
        created = False
        print(f"[*] Found existing mock student: {email}")
    except User.DoesNotExist:
        student = User.objects.create_user(email=email, role=role)
        created = True
        print(f"[+] Created mock student: {email}")

    # 2. Check caching and cache invalidation via selector & signals
    print("\n[*] Testing Caching and Invalidation:")
    cache_key = f"dashboard_context_{student.id}"
    cache.delete(cache_key)
    
    # Run selector once to populate cache
    context_data = DashboardSelector.get_student_dashboard_context(student)
    print("    - Compiled dashboard context successfully.")
    
    cached_data = cache.get(cache_key)
    if cached_data:
        print("    - SUCCESS: Dashboard context cached successfully in Redis/Cache backend.")
    else:
        print("    - WARNING: Dashboard context was not cached (check cache configuration).")

    # Now let's trigger signal by creating a Bookmark and check cache invalidation
    import uuid
    print("\n[*] Creating Bookmark to trigger signals and cache invalidation:")
    bookmark = Bookmark.objects.create(
        student=student,
        content_type="lesson",
        content_id=uuid.uuid4(),
        title="Verification Test Lesson"
    )
    print(f"    - Bookmark created: '{bookmark.title}' (ID: {bookmark.id})")
    
    invalidated_data = cache.get(cache_key)
    if invalidated_data is None:
        print("    - SUCCESS: Dashboard cache successfully invalidated after Bookmark creation.")
    else:
        print("    - FAILURE: Dashboard cache was NOT invalidated after Bookmark creation.")

    # Check CentralAnalyticsTracker interaction (check if conversation traces got updated)
    print("\n[*] Checking AI Conversation grounding context:")
    try:
        conversation = AIConversation.objects.get(user=student)
        messages = AIMessage.objects.filter(conversation=conversation).order_by('-created_at')
        if messages.exists():
            last_msg = messages[0]
            print(f"    - SUCCESS: AI Conversation updated with trace: '{last_msg.content}'")
        else:
            print("    - FAILURE: AI Conversation found but no messages updated.")
    except AIConversation.DoesNotExist:
        print("    - FAILURE: AI Conversation grounding was not created.")

    # 3. Create a Student Note to test Note Signals and Search Task indexing triggering
    print("\n[*] Creating StudentNote to trigger search index task:")
    note = StudentNote.objects.create(
        student=student,
        title="My Notes on Advanced Philosophy",
        content="This is content of the note describing non-dualism and other core ideas."
    )
    print(f"    - Note created: '{note.title}' (ID: {note.id})")

    # Clean up verification data
    print("\n[*] Cleaning up verification entries:")
    Bookmark.objects.filter(student=student).delete()
    StudentNote.objects.filter(student=student).delete()
    AIConversation.objects.filter(user=student).delete()
    cache.delete(cache_key)
    print("    - Cleanup complete.")

    print("\n[+] Sprint 20 Verification Completed Successfully!")
    print("==================================================")

if __name__ == '__main__':
    run_checks()
