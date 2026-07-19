from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal

from apps.users.models import Role
from apps.teacher.models import TeacherProfile, TeacherWallet, TeacherEarning, TeacherCertificate, TeacherAnnouncement
from apps.lms.models import CourseStructure, Assignment, AssignmentSubmission, LearningProgress, CourseNodeType
from apps.cms.models import Blog
from apps.seo.models import SEOPage
from apps.teacher.integrations import TeacherPortalIntegrator

User = get_user_model()

class TeacherPortalIntegratorTestCase(TestCase):
    def setUp(self):
        # Create Roles
        self.teacher_role, _ = Role.objects.get_or_create(name="TEACHER", defaults={"description": "Teacher Role"})
        self.student_role, _ = Role.objects.get_or_create(name="STUDENT", defaults={"description": "Student Role"})

        # Create Users
        self.teacher_user = User.objects.create_user(
            email="teacher_test@brahmavidya.edu",
            password="testpassword",
            role=self.teacher_role
        )
        self.student_user = User.objects.create_user(
            email="student_test@brahmavidya.edu",
            password="testpassword",
            role=self.student_role
        )

        # Create Profile (triggers post_save which auto-creates the wallet)
        self.teacher_profile = TeacherProfile.objects.create(
            user=self.teacher_user,
            bio="An experienced teacher",
            experience_years=5,
            is_verified=True
        )
        self.teacher_wallet = TeacherWallet.objects.get(teacher=self.teacher_user)
        self.teacher_wallet.payout_method = "STRIPE"
        self.teacher_wallet.balance_amount = Decimal("0.00")
        self.teacher_wallet.save()

        # Create Course Structure: Course -> Lesson
        self.course_node = CourseStructure.objects.create(
            node_type=CourseNodeType.COURSE,
            title="Introduction to Philosophy",
            slug="intro-to-philosophy"
        )
        self.lesson_node = CourseStructure.objects.create(
            parent=self.course_node,
            node_type=CourseNodeType.LESSON,
            title="Lesson 1: What is Philosophy?",
            slug="lesson-1-what-is-philosophy"
        )

        # Create Assignment
        self.assignment = Assignment.objects.create(
            lesson=self.lesson_node,
            title="Essay on Epistemology",
            instructions="Write a 500-word essay on epistemology.",
            max_points=100
        )

        # Create Submission
        self.submission = AssignmentSubmission.objects.create(
            assignment=self.assignment,
            student=self.student_user,
            submission_payload={"text": "This is my essay on epistemology..."}
        )

    def test_integrate_lms_grade_submission(self):
        # Grade the submission
        submission = TeacherPortalIntegrator.integrate_lms_grade_submission(
            teacher=self.teacher_user,
            submission_id=self.submission.id,
            grade=95.0,
            feedback="Excellent essay!"
        )
        self.assertEqual(submission.grade, Decimal("95.00"))
        self.assertEqual(submission.feedback, "Excellent essay!")
        self.assertEqual(submission.graded_by, self.teacher_user)

    def test_integrate_cms_broadcast_to_blog(self):
        announcement = TeacherAnnouncement.objects.create(
            teacher=self.teacher_user,
            course=self.course_node,
            title="Important Announcement",
            content="Class is postponed to Friday."
        )
        res = TeacherPortalIntegrator.integrate_cms_broadcast_to_blog(
            teacher=self.teacher_user,
            announcement_id=announcement.id
        )
        self.assertIn("blog_id", res)
        self.assertIn("slug", res)
        blog = Blog.objects.get(id=res["blog_id"])
        self.assertEqual(blog.title, "Important Announcement")
        self.assertEqual(blog.author, self.teacher_user)

    def test_integrate_analytics_event(self):
        TeacherPortalIntegrator.integrate_analytics_event(
            user=self.teacher_user,
            metric_name="Teacher Logged In",
            value=1.0,
            context={"browser": "Chrome"}
        )

    def test_integrate_notifications_dispatch(self):
        TeacherPortalIntegrator.integrate_notifications_dispatch(
            user=self.student_user,
            event_type="GRADE_RELEASED",
            title="Assignment Graded",
            message="Your epistemology essay has been graded.",
            channels=["in_app"]
        )

    def test_integrate_search_indexing(self):
        res = TeacherPortalIntegrator.integrate_search_indexing("course", str(self.course_node.id))
        self.assertEqual(res["status"], "search_synced")

    def test_integrate_ai_grading_assistant(self):
        res = TeacherPortalIntegrator.integrate_ai_grading_assistant(self.submission.id)
        self.assertIn("ai_evaluation", res)
        self.assertGreater(res["prompt_tokens"], 0)
        self.assertGreater(res["completion_tokens"], 0)
        self.assertGreater(res["estimated_cost_usd"], 0.0)

    def test_integrate_wallet_payout_ledger(self):
        earning = TeacherPortalIntegrator.integrate_wallet_payout_ledger(
            teacher=self.teacher_user,
            amount=150.00,
            points=10,
            earning_type="GRADING_BONUS",
            description="Grading reward"
        )
        self.assertEqual(earning.amount, Decimal("150.00"))
        self.assertEqual(earning.points, 10)
        self.assertEqual(earning.earning_type, "GRADING_BONUS")
        self.teacher_wallet.refresh_from_db()
        self.assertEqual(self.teacher_wallet.balance_amount, Decimal("150.00"))
        self.assertEqual(self.teacher_wallet.balance_points, 10)

    def test_integrate_certificates_generation(self):
        TeacherPortalIntegrator.integrate_certificates_generation(self.student_user, self.course_node)

    def test_integrate_seo_registration(self):
        seo_page = TeacherPortalIntegrator.integrate_seo_registration(
            page_type="COURSE",
            page_id=str(self.course_node.id),
            title="Introduction to Philosophy",
            description="Learn the basics of philosophical thought."
        )
        self.assertEqual(seo_page.page_type, "COURSE")
        self.assertEqual(seo_page.title, "Introduction to Philosophy")
        self.assertIn("Philosophy", seo_page.meta_title)

    def test_integrate_redis_dashboard_caching(self):
        res = TeacherPortalIntegrator.integrate_redis_dashboard_caching(self.teacher_user.id)
        self.assertIn("source", res)

    def test_integrate_celery_task_dispatch(self):
        task_id = TeacherPortalIntegrator.integrate_celery_task_dispatch(self.teacher_user.id)
        self.assertTrue(task_id)
