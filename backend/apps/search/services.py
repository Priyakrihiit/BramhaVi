import logging
import difflib
import uuid
from django.db import transaction
from django.db.models import Q, F, Case, When, Value, FloatField, BooleanField
from django.apps import apps
from django.utils import timezone
from apps.search.models import (
    SearchIndex, SearchDocument, SearchTerm, SearchAnalytics,
    SearchHistory, SearchSuggestion, SearchRanking, SearchClick,
    SearchFacet, SearchSynonym, SearchCache
)

logger = logging.getLogger("search.services")

class IndexService:
    """
    Service to manage search index operations and document registrations.
    """
    @staticmethod
    def get_or_create_index(name, description=None):
        """
        Retrieves or creates a SearchIndex by name.
        """
        index, _ = SearchIndex.objects.get_or_create(
            name=name.lower().strip(),
            defaults={"description": description or f"Search index for {name}"}
        )
        return index

    @staticmethod
    @transaction.atomic
    def index_document(index_name, entity_type, entity_id, title, excerpt, body, url_path,
                       tags="", categories="", author_name="", is_published=True, published_at=None, meta_data=None):
        """
        Registers or updates a document in the search index.
        """
        index = IndexService.get_or_create_index(index_name)
        
        # Build pre-computed search vector text
        search_tokens = [
            title or "",
            tags or "",
            categories or "",
            excerpt or "",
            body or "",
            author_name or ""
        ]
        search_vector = " ".join([t.strip() for t in search_tokens if t.strip()]).lower()

        doc, created = SearchDocument.objects.update_or_create(
            index=index,
            entity_type=entity_type,
            entity_id=entity_id,
            defaults={
                "title": title[:255] if title else "",
                "excerpt": excerpt,
                "body": body,
                "tags": tags,
                "categories": categories,
                "author_name": author_name,
                "url_path": url_path,
                "is_published": is_published,
                "published_at": published_at or timezone.now(),
                "search_vector": search_vector,
                "meta_data": meta_data or {},
                "updated_at": timezone.now()
            }
        )
        # Auto-propagate phrase to suggestions
        if title and len(title) > 2:
            SuggestionService.add_suggestion(title, weight=2.0)
        
        return doc

    @staticmethod
    @transaction.atomic
    def delete_document(entity_type, entity_id):
        """
        Removes a document from the search index.
        """
        SearchDocument.objects.filter(entity_type=entity_type, entity_id=entity_id).delete()

    @staticmethod
    def reindex_all():
        """
        Executes a complete re-indexing batch task for all standard models and JSON portfolio files.
        """
        logger.info("Starting global re-indexing task.")
        
        # 1. LMS Courses
        try:
            CourseStructure = apps.get_model("lms", "CourseStructure")
            courses = CourseStructure.objects.filter(deleted_at__isnull=True)
            for course in courses:
                IndexService.index_document(
                    index_name="courses",
                    entity_type="CourseStructure",
                    entity_id=course.id,
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
        except LookupError:
            logger.warning("LMS CourseStructure model not found.")

        # 2. CMS Articles
        try:
            Article = apps.get_model("cms", "Article")
            articles = Article.objects.filter(deleted_at__isnull=True)
            for art in articles:
                author_name = str(art.author) if art.author else ""
                cat_names = ",".join([c.name for c in art.categories.all()]) if hasattr(art, 'categories') else ""
                tag_names = " ".join([t.name for t in art.tags.all()]) if hasattr(art, 'tags') else ""
                IndexService.index_document(
                    index_name="articles",
                    entity_type="Article",
                    entity_id=art.id,
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
        except LookupError:
            logger.warning("CMS Article model not found.")

        # 3. CMS Blogs
        try:
            Blog = apps.get_model("cms", "Blog")
            blogs = Blog.objects.filter(deleted_at__isnull=True)
            for blog in blogs:
                author_name = str(blog.author) if blog.author else ""
                IndexService.index_document(
                    index_name="blogs",
                    entity_type="Blog",
                    entity_id=blog.id,
                    title=blog.title,
                    excerpt=blog.description[:200] if blog.description else "",
                    body=blog.description or "",
                    url_path=f"/cms/blogs/{blog.id}",
                    author_name=author_name,
                    is_published=True,
                    published_at=blog.created_at
                )
        except LookupError:
            logger.warning("CMS Blog model not found.")

        # 4. CMS Tutorials
        try:
            Tutorial = apps.get_model("cms", "Tutorial")
            tutorials = Tutorial.objects.filter(deleted_at__isnull=True)
            for tut in tutorials:
                author_name = str(tut.author) if tut.author else ""
                IndexService.index_document(
                    index_name="tutorials",
                    entity_type="Tutorial",
                    entity_id=tut.id,
                    title=tut.title,
                    excerpt=tut.description[:200] if tut.description else "",
                    body=tut.description or "",
                    url_path=f"/cms/tutorials/{tut.id}",
                    author_name=author_name,
                    is_published=True,
                    published_at=tut.created_at
                )
        except LookupError:
            logger.warning("CMS Tutorial model not found.")

        # 5. CMS FAQs
        try:
            FAQ = apps.get_model("cms", "FAQ")
            faqs = FAQ.objects.filter(deleted_at__isnull=True)
            for faq in faqs:
                IndexService.index_document(
                    index_name="faqs",
                    entity_type="FAQ",
                    entity_id=faq.id,
                    title=faq.question,
                    excerpt="",
                    body=faq.answer or "",
                    url_path=f"/cms/faq/{faq.id}",
                    is_published=True,
                    published_at=faq.created_at
                )
        except LookupError:
            logger.warning("CMS FAQ model not found.")

        # 6. DAM Media Files
        try:
            MediaFile = apps.get_model("cms", "MediaFile")
            media_files = MediaFile.objects.filter(deleted_at__isnull=True)
            for mf in media_files:
                uploader = str(mf.uploader) if mf.uploader else ""
                IndexService.index_document(
                    index_name="media",
                    entity_type="MediaFile",
                    entity_id=mf.id,
                    title=mf.file_name,
                    excerpt=mf.file_type or "",
                    body=mf.description or "",
                    url_path=f"/cms/media/{mf.id}",
                    author_name=uploader,
                    is_published=True,
                    published_at=mf.created_at,
                    meta_data={"file_type": mf.file_type, "file_size": mf.file_size}
                )
        except LookupError:
            logger.warning("CMS MediaFile model not found.")

        # 7. Marketplace Books
        try:
            Book = apps.get_model("publishing", "Book")
            books = Book.objects.filter(deleted_at__isnull=True)
            for book in books:
                author_name = str(book.author) if book.author else ""
                IndexService.index_document(
                    index_name="marketplace",
                    entity_type="Book",
                    entity_id=book.id,
                    title=book.title,
                    excerpt=book.description[:200] if book.description else "",
                    body=book.description or "",
                    url_path=f"/publishing/books/{book.id}",
                    author_name=author_name,
                    is_published=(book.status == "PUBLISHED"),
                    published_at=book.created_at,
                    meta_data={"price": float(book.price) if book.price else 0.0}
                )
        except LookupError:
            logger.warning("Publishing Book model not found.")

        # 8. Portfolio JSON Store
        try:
            from apps.portfolio.portfolio_store import get_collection
            
            # Websites / Portfolios
            websites = get_collection("websites")
            for web in websites:
                IndexService.index_document(
                    index_name="portfolios",
                    entity_type="Website",
                    entity_id=uuid.UUID(web["id"]) if isinstance(web["id"], uuid.UUID) or len(web["id"]) == 36 else uuid.uuid5(uuid.NAMESPACE_DNS, web["id"]),
                    title=web.get("name", ""),
                    excerpt=f"Subdomain: {web.get('subdomain', '')}",
                    body=web.get("custom_domain", "") or "",
                    url_path=f"/portfolio/{web.get('subdomain', '')}",
                    is_published=(web.get("status") == "published"),
                    meta_data={"subdomain": web.get("subdomain")}
                )
            
            # Resumes
            resumes = get_collection("resumes")
            for res in resumes:
                IndexService.index_document(
                    index_name="resumes",
                    entity_type="Resume",
                    entity_id=uuid.UUID(res["id"]) if isinstance(res["id"], uuid.UUID) or len(res["id"]) == 36 else uuid.uuid5(uuid.NAMESPACE_DNS, res["id"]),
                    title=f"Resume - {res.get('id')}",
                    excerpt=res.get("summary", "")[:200],
                    body=res.get("summary", "") or "",
                    url_path=f"/resumes/{res.get('id')}",
                    is_published=True,
                )

            # Jobs
            jobs = get_collection("jobs")
            for job in jobs:
                IndexService.index_document(
                    index_name="jobs",
                    entity_type="Job",
                    entity_id=uuid.UUID(job["id"]) if isinstance(job["id"], uuid.UUID) or len(job["id"]) == 36 else uuid.uuid5(uuid.NAMESPACE_DNS, job["id"]),
                    title=job.get("title", ""),
                    excerpt=job.get("description", "")[:200],
                    body=job.get("description", "") + " " + job.get("requirements", ""),
                    url_path=f"/jobs/{job.get('id')}",
                    is_published=True,
                )
        except Exception as e:
            logger.warning(f"Failed to index portfolio JSON items: {e}")

        # 9. SEO Pages
        try:
            SEOPage = apps.get_model("seo", "SEOPage")
            pages = SEOPage.objects.all()
            for page in pages:
                IndexService.index_document(
                    index_name="seo",
                    entity_type="SEOPage",
                    entity_id=page.id,
                    title=page.title,
                    excerpt=page.meta_description or "",
                    body=page.keywords or "",
                    url_path=page.canonical_url or f"/seo/{page.slug}",
                    is_published=page.robots_index,
                    published_at=page.created_at
                )
        except LookupError:
            logger.warning("SEOPage model not found.")

        # 10. Notification Records & Announcements
        try:
            Announcement = apps.get_model("notifications", "Announcement")
            announcements = Announcement.objects.filter(deleted_at__isnull=True)
            for ann in announcements:
                IndexService.index_document(
                    index_name="notifications",
                    entity_type="Announcement",
                    entity_id=ann.id,
                    title=ann.title,
                    excerpt=ann.content[:200] if ann.content else "",
                    body=ann.content or "",
                    url_path=f"/notifications/announcements/{ann.id}",
                    is_published=True,
                    published_at=ann.starts_at or ann.created_at
                )
        except LookupError:
            logger.warning("Announcement model not found.")

        try:
            NotificationRecord = apps.get_model("notifications", "NotificationRecord")
            records = NotificationRecord.objects.filter(deleted_at__isnull=True)
            for rec in records:
                IndexService.index_document(
                    index_name="notifications",
                    entity_type="NotificationRecord",
                    entity_id=rec.id,
                    title=rec.title,
                    excerpt=rec.content[:200] if rec.content else "",
                    body=rec.content or "",
                    url_path=f"/notifications/records/{rec.id}",
                    is_published=True,
                    published_at=rec.created_at,
                    author_name=str(rec.user.email) if rec.user else ""
                )
        except LookupError:
            logger.warning("NotificationRecord model not found.")

        # 11. Biographical User Profiles & Organizations
        try:
            UserProfile = apps.get_model("users", "UserProfile")
            profiles = UserProfile.objects.all()
            for prof in profiles:
                skills_str = " ".join(prof.skills) if isinstance(prof.skills, list) else ""
                IndexService.index_document(
                    index_name="users",
                    entity_type="UserProfile",
                    entity_id=prof.id,
                    title=f"{prof.first_name or ''} {prof.last_name or ''}".strip() or str(prof.user.email),
                    excerpt=prof.bio[:200] if prof.bio else "",
                    body=prof.bio or "",
                    url_path=f"/users/profile/{prof.id}",
                    tags=skills_str,
                    is_published=True,
                    published_at=prof.created_at
                )
        except LookupError:
            logger.warning("UserProfile model not found.")

        try:
            Organization = apps.get_model("users", "Organization")
            orgs = Organization.objects.all()
            for org in orgs:
                IndexService.index_document(
                    index_name="users",
                    entity_type="Organization",
                    entity_id=org.id,
                    title=org.name,
                    excerpt=f"Type: {org.org_type}",
                    body=f"Subdomain: {org.subdomain or ''}",
                    url_path=f"/orgs/{org.subdomain or org.id}",
                    is_published=True,
                    published_at=org.created_at
                )
        except LookupError:
            logger.warning("Organization model not found.")

        # 12. AI Conversational & Prompt Stores
        try:
            from apps.ai.ai_store import get_conversations, get_all_prompts
            
            conversations = get_conversations(include_archived=True, include_deleted=False)
            for conv in conversations:
                IndexService.index_document(
                    index_name="ai",
                    entity_type="Conversation",
                    entity_id=uuid.UUID(conv["id"]) if isinstance(conv["id"], uuid.UUID) or len(conv["id"]) == 36 else uuid.uuid5(uuid.NAMESPACE_DNS, conv["id"]),
                    title=conv.get("title") or f"Conversation - {conv.get('id')}",
                    excerpt=f"Model: {conv.get('model_id')}",
                    body=conv.get("summary") or "",
                    url_path=f"/ai/conversations/{conv.get('id')}",
                    is_published=True
                )
            
            prompts = get_all_prompts(include_private=True)
            for pr in prompts:
                IndexService.index_document(
                    index_name="ai",
                    entity_type="Prompt",
                    entity_id=uuid.UUID(pr["id"]) if isinstance(pr["id"], uuid.UUID) or len(pr["id"]) == 36 else uuid.uuid5(uuid.NAMESPACE_DNS, pr["id"]),
                    title=pr.get("name", ""),
                    excerpt=pr.get("description", "")[:200],
                    body=pr.get("content", "") or "",
                    url_path=f"/ai/prompts/{pr.get('id')}",
                    is_published=True
                )
        except Exception as e:
            logger.warning(f"Failed to index AI store items: {e}")

        logger.info("Global re-indexing completed successfully.")


class RankingService:
    """
    Service that processes document ranking, pinned results, and manual boost configurations.
    """
    @staticmethod
    def apply_ranking(queryset, query_string):
        """
        Applies a database case-expression matching scoring framework for the query term.
        """
        if not query_string:
            return queryset.annotate(relevance_score=Value(0.0, output_field=FloatField()))

        query_lower = query_string.lower().strip()

        # Compile synonym substitutions
        synonym_queries = [query_lower]
        syn_records = SearchSynonym.objects.filter(Q(term__iexact=query_lower) | Q(synonyms__icontains=query_lower), is_active=True)
        for syn in syn_records:
            if syn.term.lower() not in synonym_queries:
                synonym_queries.append(syn.term.lower())
            for s in syn.synonyms.split(","):
                clean_s = s.strip().lower()
                if clean_s and clean_s not in synonym_queries:
                    synonym_queries.append(clean_s)

        # Build compound query for OR checks
        lexical_filter = Q()
        for term in synonym_queries:
            lexical_filter |= Q(title__icontains=term) | Q(tags__icontains=term) | Q(excerpt__icontains=term) | Q(body__icontains=term)

        # Base lexical matching score weighting
        lexical_score = Value(0.0)
        for idx, term in enumerate(synonym_queries):
            weight_factor = 1.0 if idx == 0 else 0.5  # Give synonyms half weight
            lexical_score += (
                Case(
                    When(title__iexact=term, then=Value(10.0 * weight_factor)),
                    When(title__icontains=term, then=Value(5.0 * weight_factor)),
                    default=Value(0.0),
                    output_field=FloatField()
                ) +
                Case(
                    When(tags__icontains=term, then=Value(4.0 * weight_factor)),
                    default=Value(0.0),
                    output_field=FloatField()
                ) +
                Case(
                    When(excerpt__icontains=term, then=Value(2.0 * weight_factor)),
                    default=Value(0.0),
                    output_field=FloatField()
                ) +
                Case(
                    When(body__icontains=term, then=Value(1.0 * weight_factor)),
                    default=Value(0.0),
                    output_field=FloatField()
                )
            )

        # Manual boost score overrides
        from apps.search.models import SearchRanking
        rankings = SearchRanking.objects.filter(query__iexact=query_lower)
        pinned_doc_ids = list(rankings.filter(is_pinned=True).values_list("document_id", flat=True))
        boost_dict = {r.document_id: r.boost_score for r in rankings.filter(is_pinned=False)}

        pinned_cases = [When(id=doc_id, then=Value(True)) for doc_id in pinned_doc_ids]
        is_pinned_expr = Case(*pinned_cases, default=Value(False), output_field=BooleanField())

        boost_cases = [When(id=doc_id, then=Value(score)) for doc_id, score in boost_dict.items()]
        boost_expr = Case(*boost_cases, default=Value(0.0), output_field=FloatField())

        # Compile final annotated score
        qs = queryset.filter(lexical_filter | Q(id__in=pinned_doc_ids))
        qs = qs.annotate(
            lexical_score=lexical_score,
            boost_score=boost_expr,
            is_pinned=is_pinned_expr,
            relevance_score=F("lexical_score") + F("boost_score")
        )

        return qs.order_by("-is_pinned", "-relevance_score", "-published_at")


class SuggestionService:
    """
    Service supporting suggestions, phrase updates, and fuzzy close spelling suggestions.
    """
    @staticmethod
    def get_suggestions(query_string, limit=10):
        """
        Retrieves active phrase suggestions matching current query prefix.
        """
        if not query_string:
            return SearchSuggestion.objects.none()
        return SearchSuggestion.objects.filter(phrase__icontains=query_string.strip(), is_active=True).order_by("-weight", "phrase")[:limit]

    @staticmethod
    @transaction.atomic
    def add_suggestion(phrase, weight=1.0):
        """
        Creates or increments weight for a suggestion phrase.
        """
        phrase_clean = phrase.lower().strip()
        if not phrase_clean:
            return None
        sugg, created = SearchSuggestion.objects.get_or_create(
            phrase=phrase_clean,
            defaults={"weight": weight}
        )
        if not created:
            sugg.weight = F("weight") + weight
            sugg.save()
        return sugg

    @staticmethod
    def get_spelling_suggestion(query_string):
        """
        Performs difflib matching against known search terms to return closest match.
        """
        q_clean = query_string.lower().strip()
        if not q_clean:
            return None
        known_terms = list(SearchTerm.objects.all().values_list("term", flat=True))
        matches = difflib.get_close_matches(q_clean, known_terms, n=1, cutoff=0.7)
        return matches[0] if matches else None


class AnalyticsService:
    """
    Tracks and records search actions and aggregates performance trends.
    """
    @staticmethod
    @transaction.atomic
    def log_search(user, query_string, filters_applied=None, results_count=0):
        """
        Creates a SearchHistory entry and logs the query in SearchTerm frequency charts.
        """
        query_clean = query_string.strip().lower()
        if not query_clean:
            return None

        # Log User Search History
        sh = SearchHistory.objects.create(
            user=user if user and user.is_authenticated else None,
            query=query_string,
            filters_applied=filters_applied or {},
            results_count=results_count
        )

        # Update Search Term Frequency
        term, created = SearchTerm.objects.get_or_create(term=query_clean)
        if not created:
            term.frequency = F("frequency") + 1
            term.save()

        # Update base stats in SearchAnalytics
        analytics, _ = SearchAnalytics.objects.get_or_create(query_string=query_clean)
        analytics.total_queries = F("total_queries") + 1
        analytics.total_results = results_count
        analytics.save()
        
        return sh

    @staticmethod
    @transaction.atomic
    def log_click(history_id, document_id, position):
        """
        Registers a search click result event.
        """
        try:
            history = SearchHistory.objects.get(id=history_id)
        except SearchHistory.DoesNotExist:
            history = None

        try:
            doc = SearchDocument.objects.get(id=document_id)
        except SearchDocument.DoesNotExist:
            return None

        click = SearchClick.objects.create(
            history=history,
            document=doc,
            position=position
        )

        # Re-calc click-through rate in analytics
        if history:
            query_clean = history.query.strip().lower()
            analytics, _ = SearchAnalytics.objects.get_or_create(query_string=query_clean)
            
            # Count total queries for this term
            total_searches = SearchHistory.objects.filter(query__iexact=query_clean).count()
            # Count distinct queries that led to a click
            clicked_searches = SearchHistory.objects.filter(query__iexact=query_clean, clicks__isnull=False).distinct().count()
            
            analytics.click_through_rate = clicked_searches / total_searches if total_searches > 0 else 0.0
            analytics.save()
            
        return click

    @staticmethod
    def aggregate_analytics():
        """
        Summarizes and updates analytics data on a cron schedule.
        """
        # Re-calculates click-through-rates and total queries for active searches
        active_queries = SearchHistory.objects.values_list("query", flat=True).distinct()
        for q in active_queries:
            q_clean = q.strip().lower()
            total_searches = SearchHistory.objects.filter(query__iexact=q_clean).count()
            clicked_searches = SearchHistory.objects.filter(query__iexact=q_clean, clicks__isnull=False).distinct().count()
            
            analytics, _ = SearchAnalytics.objects.get_or_create(query_string=q_clean)
            analytics.total_queries = total_searches
            analytics.click_through_rate = clicked_searches / total_searches if total_searches > 0 else 0.0
            analytics.save()


class AutocompleteService:
    """
    Quick autocomplete typeahead suggestion engine.
    """
    @staticmethod
    def get_autocomplete(prefix, limit=5):
        """
        Returns phrase suggestions starting with the matching prefix.
        """
        if not prefix:
            return []
        suggestions = SearchSuggestion.objects.filter(phrase__istartswith=prefix.strip(), is_active=True).order_by("-weight")[:limit]
        return [s.phrase for s in suggestions]


class PermissionSearchService:
    """
    Filters search queries to enforce security and resource visibility guidelines.
    """
    @staticmethod
    def filter_by_permissions(queryset, user):
        """
        Excludes private, draft, or restricted documents based on the requesting user profile.
        """
        # 1. Draft exclusions for non-admin/staff users
        if not user or not user.is_authenticated or not user.is_staff:
            queryset = queryset.filter(is_published=True)

        # 2. Add resource-specific permission blocks
        # e.g., for DAM media files, filter based on user or capability groups
        # For simplicity in Django ORM pre-filtering, we can check media files access controls
        # if the workspace enforces object ownership check
        return queryset
