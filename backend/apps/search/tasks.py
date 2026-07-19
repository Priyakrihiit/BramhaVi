import logging
from celery import shared_task
from django.apps import apps
from django.utils import timezone
from apps.search.services import IndexService, AnalyticsService

logger = logging.getLogger("search.tasks")

@shared_task(name="apps.search.tasks.index_document_task")
def index_document_task(entity_type, entity_id):
    """
    Asynchronously indexes a Django model instance.
    """
    logger.info(f"Asynchronously indexing document: {entity_type} ({entity_id})")
    
    # CMS models mapping
    if entity_type == "Article":
        Article = apps.get_model("cms", "Article")
        try:
            art = Article.objects.get(id=entity_id)
            if art.deleted_at is not None:
                IndexService.delete_document(entity_type, entity_id)
                return
            author_name = str(art.author) if art.author else ""
            cat_names = ",".join([c.name for c in art.categories.all()]) if hasattr(art, 'categories') else ""
            tag_names = " ".join([t.name for t in art.tags.all()]) if hasattr(art, 'tags') else ""
            IndexService.index_document(
                index_name="articles",
                entity_type=entity_type,
                entity_id=entity_id,
                title=art.title,
                excerpt=art.excerpt or "",
                body=art.body or "",
                url_path=f"/cms/articles/{art.id}",
                tags=tag_names,
                categories=cat_names,
                author_name=author_name,
                is_published=art.is_published,
                published_at=art.published_at or art.created_at
            )
        except Article.DoesNotExist:
            IndexService.delete_document(entity_type, entity_id)
            
    elif entity_type == "Blog":
        Blog = apps.get_model("cms", "Blog")
        try:
            blog = Blog.objects.get(id=entity_id)
            if blog.deleted_at is not None:
                IndexService.delete_document(entity_type, entity_id)
                return
            author_name = str(blog.author) if blog.author else ""
            IndexService.index_document(
                index_name="blogs",
                entity_type=entity_type,
                entity_id=entity_id,
                title=blog.title,
                excerpt=blog.description[:200] if blog.description else "",
                body=blog.description or "",
                url_path=f"/cms/blogs/{blog.id}",
                author_name=author_name,
                is_published=True,
                published_at=blog.created_at
            )
        except Blog.DoesNotExist:
            IndexService.delete_document(entity_type, entity_id)

    elif entity_type == "Page":
        Page = apps.get_model("cms", "Page")
        try:
            page = Page.objects.get(id=entity_id)
            if page.deleted_at is not None:
                IndexService.delete_document(entity_type, entity_id)
                return
            author_name = str(page.author) if page.author else ""
            IndexService.index_document(
                index_name="pages",
                entity_type=entity_type,
                entity_id=entity_id,
                title=page.title,
                excerpt=page.slug,
                body=str(page.layout_data),
                url_path=f"/pages/{page.slug}",
                author_name=author_name,
                is_published=page.is_published,
                published_at=page.created_at
            )
        except Page.DoesNotExist:
            IndexService.delete_document(entity_type, entity_id)

    elif entity_type == "Tutorial":
        Tutorial = apps.get_model("cms", "Tutorial")
        try:
            tut = Tutorial.objects.get(id=entity_id)
            if tut.deleted_at is not None:
                IndexService.delete_document(entity_type, entity_id)
                return
            author_name = str(tut.author) if tut.author else ""
            IndexService.index_document(
                index_name="tutorials",
                entity_type=entity_type,
                entity_id=entity_id,
                title=tut.title,
                excerpt=tut.description[:200] if tut.description else "",
                body=tut.description or "",
                url_path=f"/cms/tutorials/{tut.id}",
                author_name=author_name,
                is_published=True,
                published_at=tut.created_at
            )
        except Tutorial.DoesNotExist:
            IndexService.delete_document(entity_type, entity_id)

    elif entity_type == "FAQ":
        FAQ = apps.get_model("cms", "FAQ")
        try:
            faq = FAQ.objects.get(id=entity_id)
            if faq.deleted_at is not None:
                IndexService.delete_document(entity_type, entity_id)
                return
            IndexService.index_document(
                index_name="faqs",
                entity_type=entity_type,
                entity_id=entity_id,
                title=faq.question,
                excerpt="",
                body=faq.answer or "",
                url_path=f"/cms/faq/{faq.id}",
                is_published=True,
                published_at=faq.created_at
            )
        except FAQ.DoesNotExist:
            IndexService.delete_document(entity_type, entity_id)

    elif entity_type == "MediaFile":
        MediaFile = apps.get_model("cms", "MediaFile")
        try:
            mf = MediaFile.objects.get(id=entity_id)
            if mf.deleted_at is not None:
                IndexService.delete_document(entity_type, entity_id)
                return
            uploader = str(mf.uploader) if mf.uploader else ""
            IndexService.index_document(
                index_name="media",
                entity_type=entity_type,
                entity_id=entity_id,
                title=mf.file_name,
                excerpt=mf.file_type or "",
                body=mf.description or "",
                url_path=f"/cms/media/{mf.id}",
                author_name=uploader,
                is_published=True,
                published_at=mf.created_at,
                meta_data={"file_type": mf.file_type, "file_size": mf.file_size}
            )
        except MediaFile.DoesNotExist:
            IndexService.delete_document(entity_type, entity_id)

    elif entity_type == "CourseStructure":
        CourseStructure = apps.get_model("lms", "CourseStructure")
        try:
            course = CourseStructure.objects.get(id=entity_id)
            if course.deleted_at is not None:
                IndexService.delete_document(entity_type, entity_id)
                return
            IndexService.index_document(
                index_name="courses",
                entity_type=entity_type,
                entity_id=entity_id,
                title=course.title,
                excerpt=course.description[:200] if course.description else "",
                body=course.description or "",
                url_path=f"/lms/courses/{course.slug}" if course.slug else f"/lms/node/{course.id}",
                tags=course.metadata.get("tags", ""),
                categories=course.node_type,
                is_published=True,
                published_at=course.created_at,
                meta_data={"node_type": course.node_type}
            )
        except CourseStructure.DoesNotExist:
            IndexService.delete_document(entity_type, entity_id)

    elif entity_type == "Book":
        Book = apps.get_model("publishing", "Book")
        try:
            book = Book.objects.get(id=entity_id)
            if book.deleted_at is not None:
                IndexService.delete_document(entity_type, entity_id)
                return
            author_name = str(book.author) if book.author else ""
            IndexService.index_document(
                index_name="marketplace",
                entity_type=entity_type,
                entity_id=entity_id,
                title=book.title,
                excerpt=book.description[:200] if book.description else "",
                body=book.description or "",
                url_path=f"/publishing/books/{book.id}",
                author_name=author_name,
                is_published=(book.status == "PUBLISHED"),
                published_at=book.created_at,
                meta_data={"price": float(book.price) if book.price else 0.0}
            )
        except Book.DoesNotExist:
            IndexService.delete_document(entity_type, entity_id)

    elif entity_type == "SEOPage":
        SEOPage = apps.get_model("seo", "SEOPage")
        try:
            page = SEOPage.objects.get(id=entity_id)
            if page.deleted_at is not None:
                IndexService.delete_document(entity_type, entity_id)
                return
            IndexService.index_document(
                index_name="seo",
                entity_type=entity_type,
                entity_id=entity_id,
                title=page.title,
                excerpt=page.meta_description or "",
                body=page.keywords or "",
                url_path=page.canonical_url or f"/seo/{page.slug}",
                is_published=page.robots_index,
                published_at=page.created_at
            )
        except SEOPage.DoesNotExist:
            IndexService.delete_document(entity_type, entity_id)

    elif entity_type == "Announcement":
        Announcement = apps.get_model("notifications", "Announcement")
        try:
            ann = Announcement.objects.get(id=entity_id)
            if ann.deleted_at is not None:
                IndexService.delete_document(entity_type, entity_id)
                return
            IndexService.index_document(
                index_name="notifications",
                entity_type=entity_type,
                entity_id=entity_id,
                title=ann.title,
                excerpt=ann.content[:200] if ann.content else "",
                body=ann.content or "",
                url_path=f"/notifications/announcements/{ann.id}",
                is_published=True,
                published_at=ann.starts_at or ann.created_at
            )
        except Announcement.DoesNotExist:
            IndexService.delete_document(entity_type, entity_id)

    elif entity_type == "NotificationRecord":
        NotificationRecord = apps.get_model("notifications", "NotificationRecord")
        try:
            rec = NotificationRecord.objects.get(id=entity_id)
            if rec.deleted_at is not None:
                IndexService.delete_document(entity_type, entity_id)
                return
            IndexService.index_document(
                index_name="notifications",
                entity_type=entity_type,
                entity_id=entity_id,
                title=rec.title,
                excerpt=rec.content[:200] if rec.content else "",
                body=rec.content or "",
                url_path=f"/notifications/records/{rec.id}",
                is_published=True,
                published_at=rec.created_at,
                author_name=str(rec.user.email) if rec.user else ""
            )
        except NotificationRecord.DoesNotExist:
            IndexService.delete_document(entity_type, entity_id)

    elif entity_type == "UserProfile":
        UserProfile = apps.get_model("users", "UserProfile")
        try:
            prof = UserProfile.objects.get(id=entity_id)
            skills_str = " ".join(prof.skills) if isinstance(prof.skills, list) else ""
            IndexService.index_document(
                index_name="users",
                entity_type=entity_type,
                entity_id=entity_id,
                title=f"{prof.first_name or ''} {prof.last_name or ''}".strip() or str(prof.user.email),
                excerpt=prof.bio[:200] if prof.bio else "",
                body=prof.bio or "",
                url_path=f"/users/profile/{prof.id}",
                tags=skills_str,
                is_published=True,
                published_at=prof.created_at
            )
        except UserProfile.DoesNotExist:
            IndexService.delete_document(entity_type, entity_id)

    elif entity_type == "Organization":
        Organization = apps.get_model("users", "Organization")
        try:
            org = Organization.objects.get(id=entity_id)
            if org.deleted_at is not None:
                IndexService.delete_document(entity_type, entity_id)
                return
            IndexService.index_document(
                index_name="users",
                entity_type=entity_type,
                entity_id=entity_id,
                title=org.name,
                excerpt=f"Type: {org.org_type}",
                body=f"Subdomain: {org.subdomain or ''}",
                url_path=f"/orgs/{org.subdomain or org.id}",
                is_published=True,
                published_at=org.created_at
            )
        except Organization.DoesNotExist:
            IndexService.delete_document(entity_type, entity_id)

    elif entity_type == "StudentNote":
        try:
            StudentNote = apps.get_model("student", "StudentNote")
            note = StudentNote.objects.get(id=entity_id)
            IndexService.index_document(
                index_name="student_notes",
                entity_type=entity_type,
                entity_id=entity_id,
                title=note.title or f"Note on {note.node.title if note.node else 'General'}",
                excerpt=note.content[:200] if note.content else "",
                body=note.content or "",
                url_path=f"/student/notes/{note.id}",
                is_published=True,
                published_at=note.created_at,
                author_name=note.student.email if note.student else ""
            )
        except Exception:
            IndexService.delete_document(entity_type, entity_id)


@shared_task(name="apps.search.tasks.delete_document_task")
def delete_document_task(entity_type, entity_id):
    """
    Asynchronously deletes a search document.
    """
    logger.info(f"Asynchronously deleting document: {entity_type} ({entity_id})")
    IndexService.delete_document(entity_type, entity_id)


@shared_task(name="apps.search.tasks.index_ai_item_task")
def index_ai_item_task(collection_name, item_id):
    """
    Asynchronously indexes a file-based AI JSON item.
    """
    import uuid
    logger.info(f"Asynchronously indexing AI item: {collection_name} ({item_id})")
    from apps.ai.ai_store import get_conversation_by_id, get_prompt_by_id
    
    doc_id = uuid.UUID(item_id) if isinstance(item_id, uuid.UUID) or len(item_id) == 36 else uuid.uuid5(uuid.NAMESPACE_DNS, item_id)

    if collection_name == "conversations":
        conv = get_conversation_by_id(item_id)
        if not conv or conv.get("is_deleted", False):
            IndexService.delete_document("Conversation", doc_id)
            return
        IndexService.index_document(
            index_name="ai",
            entity_type="Conversation",
            entity_id=doc_id,
            title=conv.get("title") or f"Conversation - {conv.get('id')}",
            excerpt=f"Model: {conv.get('model_id')}",
            body=conv.get("summary") or "",
            url_path=f"/ai/conversations/{conv.get('id')}",
            is_published=True
        )
    elif collection_name == "prompts":
        pr = get_prompt_by_id(item_id)
        if not pr:
            IndexService.delete_document("Prompt", doc_id)
            return
        IndexService.index_document(
            index_name="ai",
            entity_type="Prompt",
            entity_id=doc_id,
            title=pr.get("name", ""),
            excerpt=pr.get("description", "")[:200],
            body=pr.get("content", "") or "",
            url_path=f"/ai/prompts/{pr.get('id')}",
            is_published=True
        )


@shared_task(name="apps.search.tasks.index_portfolio_item_task")
def index_portfolio_item_task(collection_name, item_id):
    """
    Asynchronously indexes a file-based portfolio JSON item.
    """
    import uuid
    logger.info(f"Asynchronously indexing portfolio item: {collection_name} ({item_id})")
    from apps.portfolio.portfolio_store import get_item_by_id
    item = get_item_by_id(collection_name, item_id)
    if not item or item.get("deleted_at") is not None:
        doc_id = uuid.UUID(item_id) if isinstance(item_id, uuid.UUID) or len(item_id) == 36 else uuid.uuid5(uuid.NAMESPACE_DNS, item_id)
        IndexService.delete_document(collection_name, doc_id)
        return

    doc_id = uuid.UUID(item_id) if isinstance(item_id, uuid.UUID) or len(item_id) == 36 else uuid.uuid5(uuid.NAMESPACE_DNS, item_id)

    if collection_name == "websites":
        IndexService.index_document(
            index_name="portfolios",
            entity_type="Website",
            entity_id=doc_id,
            title=item.get("name", ""),
            excerpt=f"Subdomain: {item.get('subdomain', '')}",
            body=item.get("custom_domain", "") or "",
            url_path=f"/portfolio/{item.get('subdomain', '')}",
            is_published=(item.get("status") == "published"),
            meta_data={"subdomain": item.get("subdomain")}
        )
    elif collection_name == "resumes":
        IndexService.index_document(
            index_name="resumes",
            entity_type="Resume",
            entity_id=doc_id,
            title=f"Resume - {item.get('id')}",
            excerpt=item.get("summary", "")[:200],
            body=item.get("summary", "") or "",
            url_path=f"/resumes/{item.get('id')}",
            is_published=True,
        )
    elif collection_name == "jobs":
        IndexService.index_document(
            index_name="jobs",
            entity_type="Job",
            entity_id=doc_id,
            title=item.get("title", ""),
            excerpt=item.get("description", "")[:200],
            body=item.get("description", "") + " " + item.get("requirements", ""),
            url_path=f"/jobs/{item.get('id')}",
            is_published=True,
        )


@shared_task(name="apps.search.tasks.reindex_all_task")
def reindex_all_task():
    """
    Background batch job to rebuild all indexes.
    """
    logger.info("Executing periodic global search re-index.")
    IndexService.reindex_all()


@shared_task(name="apps.search.tasks.aggregate_search_analytics_task")
def aggregate_search_analytics_task():
    """
    Aggregates logged queries and click rates.
    """
    logger.info("Aggregating search usage analytics.")
    AnalyticsService.aggregate_analytics()


@shared_task(name="apps.search.tasks.clear_expired_cache_task")
def clear_expired_cache_task():
    """
    Deletes expired search cache records from database.
    """
    from apps.search.models import SearchCache
    logger.info("Clearing expired search cache records.")
    deleted, _ = SearchCache.objects.filter(expires_at__lte=timezone.now()).delete()
    logger.info(f"Cleared {deleted} expired cache records.")
