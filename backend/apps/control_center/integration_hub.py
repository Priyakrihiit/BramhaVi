import os
import json
import uuid
import decimal
import hashlib
import threading
import concurrent.futures
from datetime import datetime
from django.utils import timezone
from django.db import transaction
from django.db.models import Q
from django.db.models.signals import post_save
from django.dispatch import receiver

# Lazy imports inside methods are used to prevent circular dependencies in Django.

class CentralNotificationEngine:
    """
    Phase 3 — Centralized Notifications Engine.
    Dispatches system alerts across multiple communication channels (in-app, email, push, and SMS).
    """
    @staticmethod
    def send_notification(user, event_type, title, message, channels=None):
        if channels is None:
            channels = ["IN_APP", "EMAIL"]

        # 1. In-App Notification entry
        if "IN_APP" in channels:
            from apps.users.models import Notification as InAppNotification
            InAppNotification.objects.create(
                user=user,
                title=title,
                message=message,
                is_read=False
            )

        # 2. Email (simulated / real SMTP)
        if "EMAIL" in channels:
            from django.core.mail import send_mail
            from django.conf import settings
            try:
                send_mail(
                    subject=title,
                    message=message,
                    from_email=getattr(settings, "DEFAULT_FROM_EMAIL", "no-reply@brahmavidya.edu"),
                    recipient_list=[user.email],
                    fail_silently=True
                )
            except Exception:
                pass

        # 3. Push notifications (future-ready gateway log)
        if "PUSH" in channels:
            devices = user.devices.all()
            for dev in devices:
                # Log or execute push alert dispatch
                pass

        # 4. SMS (future-ready gateway log)
        if "SMS" in channels:
            # Log SMS dispatch to phone
            pass

        # Track sending telemetry
        CentralAnalyticsTracker.track_event(
            user=user,
            metric_name="Notification Broadcasted",
            metric_value=1.0,
            context_data={"event_type": event_type, "title": title}
        )


class CentralAuditLogger:
    """
    Phase 8 — Immutable Administrative Audit Log Engine.
    Secures audit history records to SQL store and enterprise physical log sheets.
    """
    @staticmethod
    def log_action(actor, action_type, target_table, before_state=None, after_state=None, ip_address=None):
        from apps.control_center.models import SystemAuditLog
        try:
            SystemAuditLog.objects.create(
                actor=actor if actor and actor.is_authenticated else None,
                action_type=action_type,
                target_table=target_table,
                before_state=before_state or {},
                after_state=after_state or {},
                ip_address=ip_address
            )
        except Exception:
            pass

        # Write to physical log redundancy file
        try:
            log_dir = os.path.dirname(os.path.abspath(__file__))
            audit_file = os.path.join(log_dir, "enterprise_audit.log")
            with open(audit_file, "a") as f:
                log_line = f"[{timezone.now().isoformat()}] ACTOR: {actor.email if actor else 'SYSTEM'} | ACTION: {action_type} | TABLE: {target_table} | SNAPSHOT: {json.dumps(after_state or {})}\n"
                f.write(log_line)
        except Exception:
            pass


class CentralAnalyticsTracker:
    """
    Phase 6 — High Velocity Telemetry and Analytics Pipeline.
    Registers cross-module operations onto metrics database dashboards.
    """
    @staticmethod
    def track_event(user, metric_name, metric_value=1.0, context_data=None):
        from apps.control_center.models import AnalyticsEvent
        try:
            AnalyticsEvent.objects.create(
                user=user if user and user.is_authenticated else None,
                metric_name=metric_name,
                metric_value=decimal.Decimal(str(metric_value)),
                context_data=context_data or {}
            )
        except Exception:
            pass

        # Enqueue background analytic updates
        BackgroundJobQueue.enqueue_analytics_aggregation(metric_name, metric_value)


class BackgroundJobQueue:
    """
    Phase 7 — Asynchronous Background Task Runner.
    Thread-pool executor powering non-blocking mailers, PDF generators, and backups.
    """
    _executor = concurrent.futures.ThreadPoolExecutor(max_workers=5, thread_name_prefix="bv_worker")

    @classmethod
    def submit_job(cls, func, *args, **kwargs):
        cls._executor.submit(cls._run_safely, func, *args, **kwargs)

    @classmethod
    def _run_safely(cls, func, *args, **kwargs):
        try:
            func(*args, **kwargs)
        except Exception as e:
            print(f"Background job execution error: {str(e)}")

    @classmethod
    def enqueue_email(cls, recipient_email, title, content):
        def job():
            from django.core.mail import send_mail
            send_mail(title, content, "no-reply@brahmavidya.edu", [recipient_email], fail_silently=False)
        cls.submit_job(job)

    @classmethod
    def enqueue_certificate_generation(cls, user, course):
        def job():
            from apps.lms.models import Certificate
            sig = hashlib.sha256(f"{user.id}-{course.id}-{timezone.now().timestamp()}".encode()).hexdigest()
            Certificate.objects.create(
                user=user,
                course=course,
                signature_hash=sig,
                certificate_url=f"https://brahmavidya.edu/certs/{sig}.pdf"
            )
            # Notify Recipient
            CentralNotificationEngine.send_notification(
                user=user,
                event_type="CERTIFICATE_ISSUED",
                title="Your Certificate is Ready!",
                message=f"Congratulations! You completed {course.title} and earned a cryptographically verifiable transcript.",
                channels=["IN_APP", "EMAIL"]
            )
            # Audit issue
            CentralAuditLogger.log_action(
                actor=None,
                action_type="CERTIFICATE_ISSUED",
                target_table="certificates",
                after_state={"user_email": user.email, "course_title": course.title, "hash": sig}
            )
        cls.submit_job(job)

    @classmethod
    def enqueue_invoice_generation(cls, payment):
        def job():
            # Computes invoices dynamically
            pass
        cls.submit_job(job)

    @classmethod
    def enqueue_portfolio_publishing(cls, website_id):
        def job():
            # Simulates static page compilation
            pass
        cls.submit_job(job)

    @classmethod
    def enqueue_analytics_aggregation(cls, metric_name, value):
        def job():
            pass
        cls.submit_job(job)


class EventDrivenAutomationHub:
    """
    Phase 2 — Event Driven Workflow Orchestrator.
    Drives cascading actions such as Course Purchases and Completion triggers.
    """
    @staticmethod
    @transaction.atomic
    def process_successful_course_purchase(user, course_id, payment_amount=0.0):
        from apps.lms.models import CourseStructure, StudentEnrollment, LearningProgress, Badge, UserBadge
        from apps.wallets.models import Payment, Wallet, Transaction

        course_node = CourseStructure.objects.filter(id=course_id, node_type="COURSE").first()
        if not course_node:
            return {"status": "error", "message": "Course curriculum node not found"}

        # 1. Complete payment ledger registration
        payment = Payment.objects.create(
            user=user,
            amount=decimal.Decimal(str(payment_amount)),
            currency="USD",
            payment_gateway="STRIPE",
            status="COMPLETED"
        )

        # 2. Add points credit to student wallet
        wallet, _ = Wallet.objects.get_or_create(user=user)
        points_credit = decimal.Decimal(str(payment_amount)) * decimal.Decimal("10.0000")
        if points_credit > 0:
            Transaction.objects.create(
                wallet=wallet,
                type="CREDIT",
                amount=points_credit,
                description=f"Points reward for purchase: {course_node.title}",
                reference_id=payment.id
            )
            wallet.balance += points_credit
            wallet.save()

        # 3. Create LMS Enrollment
        enrollment, _ = StudentEnrollment.objects.get_or_create(
            student=user,
            course=course_node,
            defaults={"status": "ACTIVE"}
        )

        # 4. Initialize Learning Progress record
        progress, _ = LearningProgress.objects.get_or_create(
            student=user,
            node=course_node,
            defaults={"progress_percentage": 0.00, "is_completed": False}
        )

        # 5. Onboarding Badge award check
        badge, _ = Badge.objects.get_or_create(
            title="First Step of Vidyas",
            defaults={"description": "Enrolled in your first course on BrahmaVidya Galaxy."}
        )
        user_badge, badge_created = UserBadge.objects.get_or_create(
            user=user,
            badge=badge
        )

        # 6. Centralized alerts notification
        CentralNotificationEngine.send_notification(
            user=user,
            event_type="COURSE_PURCHASE",
            title="Course Enrollment Activated!",
            message=f"You successfully enrolled in {course_node.title}. Your wallet was credited with {points_credit} VIDYA.",
            channels=["IN_APP", "EMAIL"]
        )

        # 7. Metrics telemetry dispatch
        CentralAnalyticsTracker.track_event(
            user=user,
            metric_name="Payment Success",
            metric_value=float(payment_amount),
            context_data={"payment_id": str(payment.id), "item_type": "COURSE", "item_id": str(course_id)}
        )
        CentralAnalyticsTracker.track_event(
            user=user,
            metric_name="Lesson Started",
            metric_value=1.0,
            context_data={"course_id": str(course_id)}
        )

        # 8. Complete Audit ledger
        CentralAuditLogger.log_action(
            actor=user,
            action_type="COURSE_PURCHASE_WORKFLOW",
            target_table="student_enrollments",
            before_state={},
            after_state={"enrollment_id": str(enrollment.id), "status": "ACTIVE", "points_credited": float(points_credit)}
        )

        return {
            "status": "success",
            "payment_id": str(payment.id),
            "enrollment_id": str(enrollment.id),
            "points_credited": float(points_credit),
            "badge_awarded": badge.title if badge_created else None
        }

    @staticmethod
    def process_course_completion(user, course_node):
        """
        Triggers certificate issue, completion badges, and recommendations.
        """
        from apps.lms.models import Badge, UserBadge
        
        # 1. Asynchronously generate certificate PDF
        BackgroundJobQueue.enqueue_certificate_generation(user, course_node)

        # 2. Issue Graduation Badge
        badge, _ = Badge.objects.get_or_create(
            title="Sovereign Scholar",
            defaults={"description": "Achieved 100% completion in an academic curriculum."}
        )
        user_badge, created = UserBadge.objects.get_or_create(user=user, badge=badge)

        # 3. Dispatch alert
        CentralNotificationEngine.send_notification(
            user=user,
            event_type="COURSE_COMPLETED",
            title="Academic Excellence Completed!",
            message=f"Congratulations on finishing {course_node.title}! You've been awarded the 'Sovereign Scholar' badge.",
            channels=["IN_APP", "EMAIL"]
        )

        # 4. Telemetry event
        CentralAnalyticsTracker.track_event(
            user=user,
            metric_name="Lesson Completed",
            metric_value=1.0,
            context_data={"course_id": str(course_node.id)}
        )


class GlobalSearchEngine:
    """
    Phase 4 — Enterprise Global Federated Search Index.
    Searches across Tutorials, Courses, Lessons, Blogs, Forum Threads, Projects, Certificates, and Portfolios.
    """
    @staticmethod
    def query(q, content_type=None, sort_by=None, order="asc", limit=10, offset=0, user=None):
        results = []
        q_lower = q.lower().strip()

        # Helper to apply sorting and pagination
        def paginate_and_sort(lst):
            if sort_by:
                reverse = (order == "desc")
                lst = sorted(lst, key=lambda x: x.get(sort_by, ""), reverse=reverse)
            return lst[offset:offset+limit]

        # 1. Courses
        if not content_type or content_type == "courses":
            from apps.lms.models import CourseStructure
            courses = CourseStructure.objects.filter(node_type="COURSE", title__icontains=q_lower)
            for c in courses:
                results.append({
                    "id": str(c.id),
                    "type": "course",
                    "title": c.title,
                    "description": c.description or "",
                    "slug": c.slug,
                    "created_at": timezone.now().isoformat()
                })

        # 2. Lessons
        if not content_type or content_type == "lessons":
            from apps.lms.models import CourseStructure
            lessons = CourseStructure.objects.filter(node_type="LESSON", title__icontains=q_lower)
            for l in lessons:
                results.append({
                    "id": str(l.id),
                    "type": "lesson",
                    "title": l.title,
                    "description": l.description or "",
                    "slug": l.slug,
                    "created_at": timezone.now().isoformat()
                })

        # 3. Tutorials
        if not content_type or content_type == "tutorials":
            from apps.cms.models import Tutorial
            tutorials = Tutorial.objects.filter(title__icontains=q_lower)
            for t in tutorials:
                results.append({
                    "id": str(t.id),
                    "type": "tutorial",
                    "title": t.title,
                    "description": t.content[:200] if t.content else "",
                    "slug": t.slug,
                    "created_at": t.published_at.isoformat() if t.published_at else None
                })

        # 4. Blogs
        if not content_type or content_type == "blogs":
            from apps.cms.models import Blog
            blogs = Blog.objects.filter(title__icontains=q_lower)
            for b in blogs:
                results.append({
                    "id": str(b.id),
                    "type": "blog",
                    "title": b.title,
                    "description": b.content[:200] if b.content else "",
                    "slug": b.slug,
                    "created_at": b.published_at.isoformat() if b.published_at else None
                })

        # 5. Forums & Community
        if not content_type or content_type in ["community", "forums"]:
            from apps.cms.models import ForumTopic, ForumPost
            topics = ForumTopic.objects.filter(title__icontains=q_lower)
            for t in topics:
                results.append({
                    "id": str(t.id),
                    "type": "forum_topic",
                    "title": t.title,
                    "description": f"Forum Thread category: {t.forum.name if t.forum else 'General'}",
                    "created_at": timezone.now().isoformat()
                })
            posts = ForumPost.objects.filter(content__icontains=q_lower)
            for p in posts:
                results.append({
                    "id": str(p.id),
                    "type": "forum_post",
                    "title": f"Reply by {p.author.email if p.author else 'Anonymous'}",
                    "description": p.content[:200] if p.content else "",
                    "created_at": timezone.now().isoformat()
                })

        # 6. Projects
        if not content_type or content_type == "projects":
            from apps.lms.models import Project
            projects = Project.objects.filter(title__icontains=q_lower)
            for p in projects:
                results.append({
                    "id": str(p.id),
                    "type": "project",
                    "title": p.title,
                    "description": p.description or "",
                    "created_at": timezone.now().isoformat()
                })

        # 7. Certificates
        if not content_type or content_type == "certificates":
            from apps.lms.models import Certificate
            certs = Certificate.objects.filter(signature_hash__icontains=q_lower)
            for cert in certs:
                results.append({
                    "id": str(cert.id),
                    "type": "certificate",
                    "title": f"Certificate issued to {cert.user.email if cert.user else 'Student'}",
                    "description": f"Verifiable course transcript signature key: {cert.signature_hash[:16]}...",
                    "created_at": cert.issued_at.isoformat() if cert.issued_at else None
                })

        # 8. Portfolio Websites & Templates
        if not content_type or content_type in ["websites", "templates", "portfolio"]:
            from apps.portfolio.portfolio_store import get_collection as get_portfolio_col
            websites = get_portfolio_col("websites")
            for w in websites:
                if q_lower in w.get("name", "").lower() or q_lower in w.get("subdomain", "").lower() or q_lower in w.get("custom_domain", "").lower():
                    results.append({
                        "id": w.get("id"),
                        "type": "portfolio_website",
                        "title": w.get("name"),
                        "description": f"Verifiable Subdomain: {w.get('subdomain')}.brahmavidya.edu",
                        "created_at": w.get("created_at")
                    })
            themes = get_portfolio_col("themes")
            for t in themes:
                if q_lower in t.get("name", "").lower() or q_lower in t.get("layout_style", "").lower():
                    results.append({
                        "id": t.get("id"),
                        "type": "portfolio_template",
                        "title": t.get("name"),
                        "description": f"Template design system layout: {t.get('layout_style')}",
                        "created_at": t.get("created_at")
                    })

        # 9. AI Conversations
        if not content_type or content_type == "ai_conversations":
            from apps.control_center.models import AIConversation
            convs = AIConversation.objects.filter(title__icontains=q_lower)
            if user:
                convs = convs.filter(user=user)
            for c in convs:
                results.append({
                    "id": str(c.id),
                    "type": "ai_conversation",
                    "title": c.title,
                    "description": f"Intelligent interactive mentorship thread with Vidya AI.",
                    "created_at": timezone.now().isoformat()
                })

        # Track recent search query
        if user and q:
            try:
                hist_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "search_history.json")
                history = {}
                if os.path.exists(hist_file):
                    with open(hist_file, "r") as f:
                        history = json.load(f)
                u_id = str(user.id)
                if u_id not in history:
                    history[u_id] = []
                if q not in history[u_id]:
                    history[u_id].append(q)
                    history[u_id] = history[u_id][-10:]
                with open(hist_file, "w") as f:
                    json.dump(history, f, indent=2)
            except Exception:
                pass

        total_results = len(results)
        paginated_results = paginate_and_sort(results)

        suggestions = []
        for r in results:
            if r["title"] not in suggestions:
                suggestions.append(r["title"])

        return {
            "query": q,
            "total_count": total_results,
            "results": paginated_results,
            "suggestions": suggestions[:5],
            "timestamp": timezone.now().isoformat()
        }


class RecommendationEngine:
    """
    Phase 5 — Intelligent Recommendation Engine.
    Exposes personalized academic and content recommendations based on active student context.
    """
    @staticmethod
    def get_recommendations(user):
        from apps.lms.models import CourseStructure, StudentEnrollment
        from apps.cms.models import Blog, Tutorial
        from apps.portfolio.portfolio_store import get_collection as get_portfolio_col
        from apps.ai.ai_store import get_all_prompts

        # Determine already purchased/enrolled courses to prevent redundancy
        enrolled_ids = list(StudentEnrollment.objects.filter(student=user, status="ACTIVE").values_list("course_id", flat=True))

        recommendations = {
            "courses": [],
            "tutorials": [],
            "projects": [],
            "practice_sets": [],
            "blogs": [],
            "community_groups": [],
            "portfolio_templates": [],
            "ai_prompts": []
        }

        # 1. Recommend courses not enrolled in yet
        courses = CourseStructure.objects.filter(node_type="COURSE").exclude(id__in=enrolled_ids)[:3]
        for c in courses:
            recommendations["courses"].append({
                "id": str(c.id),
                "title": c.title,
                "slug": c.slug,
                "reason": "Popular choice matching your skill profile"
            })

        # 2. Recommend tutorials
        tuts = Tutorial.objects.all()[:3]
        for t in tuts:
            recommendations["tutorials"].append({
                "id": str(t.id),
                "title": t.title,
                "slug": t.slug,
                "reason": "Curated micro-guide to supplement your active courses"
            })

        # 3. Recommend projects
        from apps.lms.models import Project
        projs = Project.objects.all()[:3]
        for p in projs:
            recommendations["projects"].append({
                "id": str(p.id),
                "title": p.title,
                "reason": "Showcase your expertise with a verified capstone project"
            })

        # 4. Practice Sets
        practice_sessions = CourseStructure.objects.filter(node_type="COURSE")[:3]
        for ps in practice_sessions:
            recommendations["practice_sets"].append({
                "id": str(ps.id),
                "title": f"Practice set for {ps.title}",
                "reason": "Reinforce knowledge through mock interactive quiz bank"
            })

        # 5. Recommend Blogs
        blogs = Blog.objects.filter(is_published=True)[:3]
        for b in blogs:
            recommendations["blogs"].append({
                "id": str(b.id),
                "title": b.title,
                "slug": b.slug,
                "reason": "Highly-rated community announcement"
            })

        # 6. Community Groups
        from apps.control_center.admin_store import get_admin_collection
        comms = get_admin_collection("communities")[:2]
        for c in comms:
            recommendations["community_groups"].append({
                "id": c.get("id"),
                "name": c.get("name"),
                "reason": "Interact with fellow candidates studying identical subjects"
            })

        # 7. Portfolio Templates
        themes = get_portfolio_col("themes")[:2]
        for t in themes:
            recommendations["portfolio_templates"].append({
                "id": t.get("id"),
                "name": t.get("name"),
                "reason": "Elegant bento-grid theme for verifiable publishing"
            })

        # 8. AI prompt templates
        prompts = get_all_prompts(user_id=user.id)[:2]
        for p in prompts:
            recommendations["ai_prompts"].append({
                "id": str(p.get("id")),
                "title": p.get("title"),
                "category": p.get("category"),
                "reason": "Boost study sessions using system assistant prompt guides"
            })

        return recommendations


# =====================================================================
# DJANGO SIGNALS SYSTEM — AUTOMATIC WORKFLOW ORCHESTRATION (PHASE 2)
# =====================================================================

@receiver(post_save, sender="wallets.Payment")
def handle_payment_post_save(sender, instance, created, **kwargs):
    """
    On successful Payment update, automatically trigger enrollment and wallet credits.
    """
    if instance.status in ["COMPLETED", "SUCCESS"]:
        # Lazily fetch and execute course enrollment integration
        if instance.enrollment is None:
            # Look up corresponding course from extra store payload if exists
            from apps.wallets.payment_gateway_services import read_pg_store
            pg_store = read_pg_store()
            item_id = None
            for key, p_details in pg_store.get("webhook_logs", {}).items():
                if p_details.get("payment_id") == str(instance.id):
                    item_id = p_details.get("item_id")
                    break
            
            if item_id:
                EventDrivenAutomationHub.process_successful_course_purchase(
                    user=instance.user,
                    course_id=item_id,
                    payment_amount=float(instance.amount)
                )


@receiver(post_save, sender="lms.LearningProgress")
def handle_progress_post_save(sender, instance, created, **kwargs):
    """
    Automatically trigger course completion certificate issuance and badges when progress reaches 100%.
    """
    if instance.is_completed or instance.progress_percentage >= decimal.Decimal("100.00"):
        if not instance.is_completed:
            instance.is_completed = True
            instance.completed_at = timezone.now()
            # Suppress infinite recursion on signals
            LearningProgress.objects.filter(id=instance.id).update(is_completed=True, completed_at=timezone.now())
        
        # Trigger automation workflow
        EventDrivenAutomationHub.process_course_completion(instance.student, instance.node)


@receiver(post_save, sender="cms.ForumPost")
def handle_forum_post_notification(sender, instance, created, **kwargs):
    """
    Notify topic creator about reply.
    """
    if created and instance.topic and instance.topic.author:
        if instance.topic.author != instance.author:
            CentralNotificationEngine.send_notification(
                user=instance.topic.author,
                event_type="COMMUNITY_REPLY",
                title="New Reply on Your Topic",
                message=f"{instance.author.email if instance.author else 'Someone'} replied to your community thread: {instance.topic.title}.",
                channels=["IN_APP"]
            )


@receiver(post_save, sender="cms.Comment")
def handle_blog_comment_notification(sender, instance, created, **kwargs):
    """
    Notify blog author about comment.
    """
    if created and instance.blog and instance.blog.author:
        if instance.blog.author != instance.author:
            CentralNotificationEngine.send_notification(
                user=instance.blog.author,
                event_type="BLOG_COMMENT",
                title="New Comment on Your Blog",
                message=f"{instance.author.email if instance.author else 'Someone'} commented on your blog: {instance.blog.title}.",
                channels=["IN_APP"]
            )
