import uuid
from datetime import datetime
from django.db import transaction
from django.utils.text import slugify
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.users.permissions import HasRBACPermission
from apps.users.models import User
from apps.lms.models import CourseStructure, Assignment, AssignmentSubmission, LearningProgress, PracticeSession
from apps.cms.models import Page, NavigationMenu, Tutorial, Blog, Forum, ForumTopic, ForumPost
from apps.control_center.admin_serializers import (
    CertificateSerializer, BadgeSerializer
)
from apps.control_center.admin_store import (
    get_admin_collection, save_admin_item, read_admin_store, write_admin_store
)

class AdminLMSViewSet(viewsets.ModelViewSet):
    """
    Module 4 — Enterprise LMS Administration Control Tower.
    Direct management of programs, subjects, courses, assignments, and certificates.
    """
    queryset = CourseStructure.objects.all().order_by("node_type", "display_order")
    serializer_class = CertificateSerializer # will specify dynamic serialization based on action
    permission_classes = [HasRBACPermission]
    lookup_field = "id"
    filter_backends = [filters.SearchFilter]
    search_fields = ["title", "description"]

    required_permissions = {
        "list": "control:lms:view",
        "retrieve": "control:lms:view",
        "create_node": "control:lms:create",
        "update_node": "control:lms:update",
        "delete_node": "control:lms:delete",
        "list_assignments": "control:lms:view",
        "grade_submission": "control:lms:update",
        "certificates_list": "control:lms:view",
        "certificates_issue": "control:lms:create",
        "certificates_revoke": "control:lms:delete",
        "badges_list": "control:lms:view",
        "badges_award": "control:lms:create",
        "progress_report": "control:lms:view",
    }

    def get_serializer_class(self):
        # We can bypass or return standard dynamic serializer
        return super().get_serializer_class()

    # Dynamic Custom Node CRUD mappings to meet requirement 'ModelViewSets only' or custom actions
    @action(detail=False, methods=["get"], url_path="structures")
    def list_nodes(self, request):
        node_type = request.query_params.get("node_type")
        parent_id = request.query_params.get("parent")
        include_deleted = request.query_params.get("include_deleted", "false").lower() == "true"
        
        if include_deleted:
            qs = CourseStructure.all_objects.all()
        else:
            qs = CourseStructure.objects.all()
            
        if node_type:
            qs = qs.filter(node_type=node_type.upper())
        if parent_id:
            qs = qs.filter(parent_id=parent_id)
            
        data = []
        for n in qs:
            data.append({
                "id": n.id,
                "node_type": n.node_type,
                "parent_id": n.parent_id if n.parent else None,
                "title": n.title,
                "slug": n.slug,
                "description": n.description,
                "display_order": n.display_order,
                "metadata": n.metadata,
                "deleted_at": n.deleted_at
            })
        return Response(data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"], url_path="structures/create")
    def create_node(self, request):
        title = request.data.get("title")
        node_type = request.data.get("node_type")
        parent_id = request.data.get("parent_id")
        description = request.data.get("description", "")
        display_order = request.data.get("display_order", 0)
        metadata = request.data.get("metadata", {})
        
        if not title or not node_type:
            return Response({"error": "title and node_type are required fields."}, status=status.HTTP_400_BAD_REQUEST)
            
        node = CourseStructure.objects.create(
            title=title,
            node_type=node_type.upper(),
            parent_id=parent_id,
            slug=slugify(title),
            description=description,
            display_order=display_order,
            metadata=metadata
        )
        return Response({"id": node.id, "title": node.title, "slug": node.slug}, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["put", "patch"], url_path="structures/update")
    def update_node(self, request, id=None):
        node = CourseStructure.all_objects.filter(id=id).first()
        if not node:
            return Response({"detail": "Node not found."}, status=status.HTTP_404_NOT_FOUND)
            
        for key in ["title", "description", "display_order", "metadata", "node_type"]:
            if key in request.data:
                val = request.data[key]
                if key == "node_type":
                    val = val.upper()
                setattr(node, key, val)
        if "title" in request.data:
            node.slug = slugify(request.data["title"])
        node.save()
        return Response({"id": node.id, "title": node.title, "slug": node.slug}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["delete"], url_path="structures/delete")
    def delete_node(self, request, id=None):
        node = CourseStructure.objects.filter(id=id).first()
        if not node:
            return Response({"detail": "Node not found."}, status=status.HTTP_404_NOT_FOUND)
        node.delete() # soft delete
        return Response({"detail": "Node soft-deleted successfully."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="structures/restore")
    def restore_node(self, request, id=None):
        node = CourseStructure.all_objects.filter(id=id, deleted_at__isnull=False).first()
        if not node:
            return Response({"detail": "Node not found or not deleted."}, status=status.HTTP_404_NOT_FOUND)
        node.restore()
        return Response({"detail": "Node restored successfully."}, status=status.HTTP_200_OK)

    # Assignment Management
    @action(detail=False, methods=["get"], url_path="assignments")
    def list_assignments(self, request):
        qs = Assignment.objects.all().select_related("lesson")
        data = []
        for a in qs:
            data.append({
                "id": a.id,
                "lesson_id": a.lesson_id,
                "lesson_title": a.lesson.title if a.lesson else "",
                "title": a.title,
                "instructions": a.instructions,
                "max_points": a.max_points,
                "created_at": a.created_at
            })
        return Response(data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="grade-submission")
    def grade_submission(self, request, id=None):
        submission = AssignmentSubmission.objects.filter(id=id).first()
        if not submission:
            return Response({"error": "Submission not found."}, status=status.HTTP_404_NOT_FOUND)
            
        grade = request.data.get("grade")
        feedback = request.data.get("feedback", "")
        if grade is None:
            return Response({"error": "grade field is required."}, status=status.HTTP_400_BAD_REQUEST)
            
        submission.grade = grade
        submission.feedback = feedback
        submission.graded_by = request.user
        submission.graded_at = datetime.now()
        submission.save()
        return Response({"detail": "Submission graded successfully."}, status=status.HTTP_200_OK)

    # Certificates Segment (JSON persistent store)
    @action(detail=False, methods=["get"], url_path="certificates")
    def certificates_list(self, request):
        certs = get_admin_collection("certificates")
        include_deleted = request.query_params.get("include_deleted", "false").lower() == "true"
        if not include_deleted:
            certs = [c for c in certs if c.get("deleted_at") is None]
        return Response(certs, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"], url_path="certificates/issue")
    def certificates_issue(self, request):
        student_id = request.data.get("student_id")
        student_email = request.data.get("student_email")
        course_title = request.data.get("course_title")
        cert_url = request.data.get("certificate_url", f"https://brahmavidya.edu/certs/generate-{uuid.uuid4().hex[:6]}.pdf")
        
        if not student_id or not student_email or not course_title:
            return Response({"error": "student_id, student_email, and course_title are required."}, status=status.HTTP_400_BAD_REQUEST)
            
        cert = {
            "id": f"cert-{uuid.uuid4().hex[:8]}",
            "student_id": student_id,
            "student_email": student_email,
            "course_title": course_title,
            "issued_at": datetime.now().isoformat(),
            "certificate_url": cert_url,
            "status": "ACTIVE",
            "deleted_at": None
        }
        save_admin_item("certificates", cert["id"], cert)
        return Response(cert, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["delete"], url_path="certificates/revoke")
    def certificates_revoke(self, request, id=None):
        certs = get_admin_collection("certificates")
        for cert in certs:
            if cert["id"] == str(id):
                cert["deleted_at"] = datetime.now().isoformat()
                cert["status"] = "REVOKED"
                save_admin_item("certificates", id, cert)
                return Response({"detail": "Certificate successfully revoked."}, status=status.HTTP_200_OK)
        return Response({"error": "Certificate not found."}, status=status.HTTP_404_NOT_FOUND)

    # Badges Segment
    @action(detail=False, methods=["get"], url_path="badges")
    def badges_list(self, request):
        badges = get_admin_collection("badges")
        include_deleted = request.query_params.get("include_deleted", "false").lower() == "true"
        if not include_deleted:
            badges = [b for b in badges if b.get("deleted_at") is None]
        return Response(badges, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"], url_path="badges/award")
    def badges_award(self, request):
        student_id = request.data.get("student_id")
        name = request.data.get("name")
        description = request.data.get("description", "")
        icon = request.data.get("icon", "Award")
        
        if not student_id or not name:
            return Response({"error": "student_id and name are required."}, status=status.HTTP_400_BAD_REQUEST)
            
        badge = {
            "id": f"badge-{uuid.uuid4().hex[:8]}",
            "student_id": student_id,
            "name": name,
            "description": description,
            "icon": icon,
            "awarded_at": datetime.now().isoformat(),
            "deleted_at": None
        }
        save_admin_item("badges", badge["id"], badge)
        return Response(badge, status=status.HTTP_201_CREATED)

    # Progress & Completion Reports
    @action(detail=False, methods=["get"], url_path="progress-report")
    def progress_report(self, request):
        progress_records = LearningProgress.objects.select_related("student", "node").all()
        data = []
        for r in progress_records:
            data.append({
                "student_email": r.student.email if r.student else "",
                "node_title": r.node.title if r.node else "",
                "node_type": r.node.node_type if r.node else "",
                "progress_percentage": float(r.progress_percentage),
                "is_completed": r.is_completed,
                "last_accessed_at": r.last_accessed_at,
                "completed_at": r.completed_at
            })
        return Response(data, status=status.HTTP_200_OK)


class AdminCMSViewSet(viewsets.ModelViewSet):
    """
    Module 5 — Enterprise CMS Administration Control Tower.
    Enforces layout publishing rules, menu structure hierarchies, blogs and forum comments.
    """
    queryset = Page.all_objects.select_related("author").all().order_by("-updated_at")
    serializer_class = CertificateSerializer # fallback
    permission_classes = [HasRBACPermission]
    lookup_field = "id"

    required_permissions = {
        "list": "control:cms:view",
        "retrieve": "control:cms:view",
        "create_page": "control:cms:create",
        "update_page": "control:cms:update",
        "delete_page": "control:cms:delete",
        "menus_list": "control:cms:view",
        "menus_save": "control:cms:update",
        "tutorials_list": "control:cms:view",
        "tutorials_save": "control:cms:update",
        "blogs_list": "control:cms:view",
        "blogs_save": "control:cms:update",
        "forums_list": "control:cms:view",
        "posts_list": "control:cms:view",
    }

    # Pages API
    @action(detail=False, methods=["get"], url_path="pages")
    def list_pages(self, request):
        include_deleted = request.query_params.get("include_deleted", "false").lower() == "true"
        qs = Page.all_objects.all() if include_deleted else Page.objects.all()
        data = [{"id": p.id, "title": p.title, "slug": p.slug, "is_published": p.is_published, "author": p.author.email if p.author else None, "deleted_at": p.deleted_at} for p in qs]
        return Response(data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"], url_path="pages/create")
    def create_page(self, request):
        title = request.data.get("title")
        is_published = request.data.get("is_published", False)
        layout_data = request.data.get("layout_data", {})
        
        if not title:
            return Response({"error": "title is a required field."}, status=status.HTTP_400_BAD_REQUEST)
            
        page = Page.objects.create(
            title=title,
            slug=slugify(title),
            is_published=is_published,
            layout_data=layout_data,
            author=request.user
        )
        return Response({"id": page.id, "title": page.title, "slug": page.slug}, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["put", "patch"], url_path="pages/update")
    def update_page(self, request, id=None):
        page = Page.all_objects.filter(id=id).first()
        if not page:
            return Response({"detail": "Page not found."}, status=status.HTTP_404_NOT_FOUND)
            
        for key in ["title", "is_published", "layout_data"]:
            if key in request.data:
                setattr(page, key, request.data[key])
        if "title" in request.data:
            page.slug = slugify(request.data["title"])
        page.save()
        return Response({"id": page.id, "title": page.title, "slug": page.slug}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["delete"], url_path="pages/delete")
    def delete_page(self, request, id=None):
        page = Page.objects.filter(id=id).first()
        if not page:
            return Response({"detail": "Page not found."}, status=status.HTTP_404_NOT_FOUND)
        page.delete()
        return Response({"detail": "Page deleted successfully."}, status=status.HTTP_200_OK)

    # Menus API
    @action(detail=False, methods=["get"], url_path="menus")
    def menus_list(self, request):
        qs = NavigationMenu.objects.all()
        data = [{"id": m.id, "label": m.label, "url": m.url, "icon": m.icon, "display_order": m.display_order, "parent_id": m.parent_id if m.parent else None} for m in qs]
        return Response(data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"], url_path="menus/save")
    def menus_save(self, request):
        label = request.data.get("label")
        url = request.data.get("url")
        icon = request.data.get("icon")
        display_order = request.data.get("display_order", 0)
        parent_id = request.data.get("parent_id")
        
        if not label or not url:
            return Response({"error": "label and url are required."}, status=status.HTTP_400_BAD_REQUEST)
            
        menu = NavigationMenu.objects.create(
            label=label,
            url=url,
            icon=icon,
            display_order=display_order,
            parent_id=parent_id
        )
        return Response({"id": menu.id, "label": menu.label}, status=status.HTTP_201_CREATED)

    # Tutorials API
    @action(detail=False, methods=["get"], url_path="tutorials")
    def tutorials_list(self, request):
        qs = Tutorial.objects.all()
        data = [{"id": t.id, "title": t.title, "slug": t.slug, "is_published": t.is_published} for t in qs]
        return Response(data, status=status.HTTP_200_OK)

    # Blogs API
    @action(detail=False, methods=["get"], url_path="blogs")
    def blogs_list(self, request):
        qs = Blog.objects.all()
        data = [{"id": b.id, "title": b.title, "slug": b.slug, "is_published": b.is_published} for b in qs]
        return Response(data, status=status.HTTP_200_OK)

    # Forums & Posts
    @action(detail=False, methods=["get"], url_path="forums")
    def forums_list(self, request):
        qs = Forum.objects.all()
        data = [{"id": f.id, "name": f.name, "description": f.description} for f in qs]
        return Response(data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], url_path="posts")
    def posts_list(self, request):
        qs = ForumPost.objects.select_related("topic", "author").all()[:100]
        data = [{"id": p.id, "topic_title": p.topic.title if p.topic else "", "author": p.author.email if p.author else "Anonymous", "content": p.content} for p in qs]
        return Response(data, status=status.HTTP_200_OK)
