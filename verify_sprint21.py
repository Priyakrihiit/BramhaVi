import os
import sys
import django
from decimal import Decimal

# Setup django environment
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_project.settings')
django.setup()

from django.core.cache import cache
from django.db import connection, transaction
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.test.utils import override_settings

# Import Sprint 21 Target Models and Integrator
from apps.users.models import Role
from apps.teacher.models import (
    TeacherProfile, TeacherWallet, TeacherEarning, TeacherCertificate, TeacherAnnouncement, TeacherActivityLog
)
from apps.lms.models import CourseStructure, Assignment, AssignmentSubmission, LearningProgress, CourseNodeType
from apps.cms.models import Blog
from apps.seo.models import SEOPage
from apps.teacher.integrations import TeacherPortalIntegrator

User = get_user_model()

@override_settings(CACHES={
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "sprint21-verification-cache",
    }
})
def run_checks():
    print("==================================================================")
    print("   BrahmaVidya Teacher Portal Sprint 21 Verification Script   ")
    print("==================================================================")

    # State tracking
    success_flags = []

    # 1. Create/Get roles
    print("\n[*] Initializing Roles and Users:")
    teacher_role, _ = Role.objects.get_or_create(name="TEACHER", defaults={"description": "Teacher Role"})
    student_role, _ = Role.objects.get_or_create(name="STUDENT", defaults={"description": "Student Role"})
    
    teacher_email = "sprint21_teacher@brahmavidya.edu"
    student_email = "sprint21_student@brahmavidya.edu"

    # Delete existing test data to start fresh
    User.objects.filter(email__in=[teacher_email, student_email]).delete()

    teacher_user = User.objects.create_user(
        email=teacher_email,
        password="sprint21password",
        role=teacher_role
    )
    student_user = User.objects.create_user(
        email=student_email,
        password="sprint21password",
        role=student_role
    )
    print(f"    - SUCCESS: Users initialized ({teacher_email} & {student_email})")
    success_flags.append(True)

    # 2. Create Profile & Wallet
    print("\n[*] Creating Teacher Profile & Wallet:")
    teacher_profile = TeacherProfile.objects.create(
        user=teacher_user,
        bio="An experienced verification tester",
        experience_years=8,
        is_verified=True
    )
    teacher_wallet = TeacherWallet.objects.get(teacher=teacher_user)
    teacher_wallet.payout_method = "STRIPE"
    teacher_wallet.balance_amount = Decimal("0.00")
    teacher_wallet.save()
    print("    - SUCCESS: Profile and Wallet models created.")
    success_flags.append(True)

    # 3. Create Course Structure: Course -> Lesson
    print("\n[*] Setting up Course and Lesson Nodes:")
    course_node = CourseStructure.objects.create(
        node_type=CourseNodeType.COURSE,
        title="Introductory Ethics",
        slug="introductory-ethics"
    )
    lesson_node = CourseStructure.objects.create(
        parent=course_node,
        node_type=CourseNodeType.LESSON,
        title="Ethics Lesson 1: Altruism",
        slug="ethics-lesson-1"
    )
    print("    - SUCCESS: Course and Lesson hierarchy created.")
    success_flags.append(True)

    # 4. Create Assignment and Submission
    print("\n[*] Creating Assignment and Submission records:")
    assignment = Assignment.objects.create(
        lesson=lesson_node,
        title="Ethics Reflection Essay",
        instructions="Analyze altruism in modern times.",
        max_points=100
    )
    submission = AssignmentSubmission.objects.create(
        assignment=assignment,
        student=student_user,
        submission_payload={"text": "This is my reflection essay on altruism..."}
    )
    print(f"    - SUCCESS: Assignment Submission created with ID: {submission.id}")
    success_flags.append(True)

    # Run the 11 integration checkouts
    print("\n==================================================================")
    print("      Executing 11 Integrations of TeacherPortalIntegrator        ")
    print("==================================================================")

    # INT 1: LMS
    print("\n[INT 1] LMS Grading Submission:")
    try:
        sub = TeacherPortalIntegrator.integrate_lms_grade_submission(
            teacher=teacher_user,
            submission_id=submission.id,
            grade=92.5,
            feedback="Well articulated points!"
        )
        assert sub.grade == Decimal("92.50"), "Grade mismatch"
        assert sub.graded_by == teacher_user, "Grader mismatch"
        print("    - SUCCESS: LMS grade submission processed and verified.")
        success_flags.append(True)
    except Exception as e:
        print(f"    - FAILURE: LMS Grading error: {e}")
        success_flags.append(False)

    # INT 2: CMS
    print("\n[INT 2] CMS Promotion to Blog:")
    try:
        announcement = TeacherAnnouncement.objects.create(
            teacher=teacher_user,
            course=course_node,
            title="Class Postponement Alert",
            content="Our live lecture has been moved due to server maintenance."
        )
        cms_res = TeacherPortalIntegrator.integrate_cms_broadcast_to_blog(
            teacher=teacher_user,
            announcement_id=announcement.id
        )
        assert "blog_id" in cms_res, "blog_id missing in response"
        blog = Blog.objects.get(id=cms_res["blog_id"])
        assert blog.title == "Class Postponement Alert", "Blog title mismatch"
        print(f"    - SUCCESS: Announcement successfully promoted to CMS Blog with slug: {cms_res['slug']}")
        success_flags.append(True)
    except Exception as e:
        print(f"    - FAILURE: CMS Blog promotion error: {e}")
        success_flags.append(False)

    # INT 3: Analytics
    print("\n[INT 3] Analytics Tracking Dispatch:")
    try:
        TeacherPortalIntegrator.integrate_analytics_event(
            user=teacher_user,
            metric_name="Verify Integration Run",
            value=1.0,
            context={"verification_script": True}
        )
        print("    - SUCCESS: Analytics event tracked seamlessly.")
        success_flags.append(True)
    except Exception as e:
        print(f"    - FAILURE: Analytics error: {e}")
        success_flags.append(False)

    # INT 4: Notifications
    print("\n[INT 4] Notifications Multi-Channel Dispatch:")
    try:
        TeacherPortalIntegrator.integrate_notifications_dispatch(
            user=student_user,
            event_type="GRADE_REPORT",
            title="Verification Notice",
            message="Your verification run has completed.",
            channels=["in_app", "email"]
        )
        print("    - SUCCESS: Notification dispatched successfully.")
        success_flags.append(True)
    except Exception as e:
        print(f"    - FAILURE: Notification dispatch error: {e}")
        success_flags.append(False)

    # INT 5: Search
    print("\n[INT 5] Global Search Indexing:")
    try:
        search_res = TeacherPortalIntegrator.integrate_search_indexing("course", str(course_node.id))
        assert "status" in search_res, "Search indexing response status missing"
        print("    - SUCCESS: Resource registered for search indexing.")
        success_flags.append(True)
    except Exception as e:
        print(f"    - FAILURE: Search indexing error: {e}")
        success_flags.append(False)

    # INT 6: AI Grading Assistant
    print("\n[INT 6] AI Grading Assistant Evaluation:")
    try:
        ai_res = TeacherPortalIntegrator.integrate_ai_grading_assistant(submission_id=submission.id)
        assert "ai_evaluation" in ai_res, "AI evaluation text missing"
        assert ai_res["prompt_tokens"] > 0, "AI tokens zero"
        print(f"    - SUCCESS: AI assistant evaluation returned with USD cost: ${ai_res['estimated_cost_usd']:.6f}")
        success_flags.append(True)
    except Exception as e:
        print(f"    - FAILURE: AI assistant error: {e}")
        success_flags.append(False)

    # INT 7: Financial Wallet Ledger Connect
    print("\n[INT 7] Wallet Ledger Transaction Credit:")
    try:
        earning = TeacherPortalIntegrator.integrate_wallet_payout_ledger(
            teacher=teacher_user,
            amount=75.00,
            points=5,
            earning_type="GRADING_BONUS",
            description="Verification task reward"
        )
        teacher_wallet.refresh_from_db()
        assert teacher_wallet.balance_amount == Decimal("75.00"), f"Wallet balance mismatch: {teacher_wallet.balance_amount}"
        assert teacher_wallet.balance_points == 5, f"Wallet points mismatch: {teacher_wallet.balance_points}"
        print(f"    - SUCCESS: Earning of ${earning.amount} credited and wallet verified.")
        success_flags.append(True)
    except Exception as e:
        print(f"    - FAILURE: Wallet credit error: {e}")
        success_flags.append(False)

    # INT 8: Certificates Queue Integration:
    print("\n[INT 8] Certificates Asynchronous Enqueue:")
    try:
        TeacherPortalIntegrator.integrate_certificates_generation(student_user, course_node)
        print("    - SUCCESS: Certificate generation task enqueued.")
        success_flags.append(True)
    except Exception as e:
        print(f"    - FAILURE: Certificate enqueue error: {e}")
        success_flags.append(False)

    # INT 9: SEO Registration:
    print("\n[INT 9] SEO and JSON-LD Schema Registration:")
    try:
        seo_page = TeacherPortalIntegrator.integrate_seo_registration(
            page_type="COURSE",
            page_id=str(course_node.id),
            title="Ethics and Morality Course",
            description="A verification-grade ethics syllabus."
        )
        assert seo_page.slug == "ethics-and-morality-course", f"SEO slug mismatch: {seo_page.slug}"
        print(f"    - SUCCESS: Meta tag registry and Schema.org registered under slug: {seo_page.slug}")
        success_flags.append(True)
    except Exception as e:
        print(f"    - FAILURE: SEO registration error: {e}")
        success_flags.append(False)

    # INT 10: Redis Dashboard Caching:
    print("\n[INT 10] Redis Dashboard Summary Caching:")
    try:
        cache_res = TeacherPortalIntegrator.integrate_redis_dashboard_caching(teacher_user.id)
        assert "source" in cache_res, "Cache response source missing"
        print(f"    - SUCCESS: Dashboard summary caching handled (Source: {cache_res['source']})")
        success_flags.append(True)
    except Exception as e:
        print(f"    - FAILURE: Caching error: {e}")
        success_flags.append(False)

    # INT 11: Celery Background Analysis Task:
    print("\n[INT 11] Celery Background Worker Task Dispatch:")
    try:
        task_id = TeacherPortalIntegrator.integrate_celery_task_dispatch(teacher_user.id)
        assert task_id is not None, "Celery task ID is None"
        print(f"    - SUCCESS: Background analytics task dispatched with Task ID: {task_id}")
        success_flags.append(True)
    except Exception as e:
        print(f"    - FAILURE: Celery task dispatch error: {e}")
        success_flags.append(False)

    # 5. Clean up verification entries
    print("\n[*] Cleaning up all verification data from the DB:")
    try:
        with transaction.atomic():
            # Delete models pointing to the user
            TeacherProfile.objects.filter(user=teacher_user).delete()
            TeacherWallet.objects.filter(teacher=teacher_user).delete()
            TeacherEarning.objects.filter(teacher=teacher_user).delete()
            TeacherAnnouncement.objects.filter(teacher=teacher_user).delete()
            TeacherActivityLog.objects.filter(teacher=teacher_user).delete()
            AssignmentSubmission.objects.filter(student=student_user).delete()
            Assignment.objects.filter(lesson=lesson_node).delete()
            CourseStructure.objects.filter(id__in=[course_node.id, lesson_node.id]).delete()
            SEOPage.objects.filter(page_id=str(course_node.id)).delete()
            Blog.objects.filter(title="Class Postponement Alert").delete()
            User.objects.filter(id__in=[teacher_user.id, student_user.id]).delete()
        print("    - SUCCESS: Database cleanup completed.")
    except Exception as e:
        print(f"    - WARNING: Cleanup failed: {e}")

    # Conclusion
    print("\n==================================================================")
    if all(success_flags):
        print("   [+] ALL SPRINT 21 INTEGRATIONS VERIFIED SUCCESSFULLY!")
        print("==================================================================")
        sys.exit(0)
    else:
        print("   [-] SOME INTEGRATIONS FAILED VERIFICATION. CHECK LOGS ABOVE.")
        print("==================================================================")
        sys.exit(1)

if __name__ == '__main__':
    run_checks()
