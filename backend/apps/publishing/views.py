import uuid
import logging
from datetime import datetime
from rest_framework import viewsets, status, serializers, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination

from apps.publishing.models import (
    AuthorProfile, PublisherProfile, Book, ProductOwnership, Order, OrderItem, ReadingProgress
)
from apps.publishing.serializers import (
    AuthorProfileSerializer, PublisherProfileSerializer, BookSerializer,
    ProductOwnershipSerializer, OrderSerializer, OrderItemSerializer, ReadingProgressSerializer
)

# Import permissions and portfolio/publishing stores
from apps.users.permissions import HasRBACPermission
from apps.portfolio.portfolio_store import (
    get_collection as get_portfolio_collection,
    get_item_by_id as get_portfolio_item_by_id,
    save_item as save_portfolio_item
)
from apps.publishing.publishing_store import (
    get_pub_collection, get_pub_item_by_key, save_pub_item,
    read_publishing_store, write_publishing_store
)
from apps.publishing.serializers import (
    PublishingConfigSerializer, PasswordVerifySerializer,
    SubdomainReservationSerializer, SubdomainAvailabilitySerializer,
    WebsiteVersionSerializer, CreateVersionSerializer, RollbackVersionSerializer,
    VersionComparisonSerializer, FormSubmissionSerializer,
    AnalyticsEventSerializer, AnalyticsAggregateSerializer,
    ImageOptimizationSerializer, AssetVersionSerializer,
    WebsiteRenderSerializer, PageRenderSerializer, SEOEnhancementSerializer
)

logger = logging.getLogger("brahmavidya.publishing")


class PublishingPagination(PageNumberPagination):
    """
    Standard enterprise pagination specifying default page size and size override parameter.
    """
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


class BasePublishingModelViewSet(viewsets.ModelViewSet):
    """
    Custom ModelViewSet that intercepts and handles data operations in-memory 
    using thread-safe JSON stores. This completely avoids DB queries and Django migration checks.
    """
    permission_classes = [HasRBACPermission]
    pagination_class = PublishingPagination
    queryset = []  # Dummy queryset to satisfy DRF signature checks

    def get_queryset(self):
        # Return empty list or overridden collection
        return []

    def paginate_memory_list(self, request, lst):
        page = self.paginate_queryset(lst)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(lst, many=True)
        return Response(serializer.data)


# ==========================================
# 1. WEBSITE RENDERING ENGINE & PUBLIC APIS
# ==========================================

class PublicWebsiteViewSet(BasePublishingModelViewSet):
    """
    ModelViewSet serving public, optimized, cached, and password-protected websites,
    pages, navigation maps, sitemaps, and robots declarations.
    """
    serializer_class = WebsiteRenderSerializer
    required_permissions = {
        "list": "publishing:public:view",
        "retrieve": "publishing:public:view",
        "home": "publishing:public:view",
        "page_by_slug": "publishing:public:view",
        "blog": "publishing:public:view",
        "sitemap": "publishing:public:view",
        "robots": "publishing:public:view",
        "navigation": "publishing:public:view",
        "footer": "publishing:public:view",
        "verify_password": "publishing:public:view",
    }

    def _hydrate_website_payload(self, website):
        w_id = str(website["id"])
        
        # 1. Fetch Theme
        themes = get_portfolio_collection("themes")
        site_themes = [t for t in themes if str(t.get("website_id")) == w_id]
        theme = site_themes[0] if site_themes else {
            "name": "Default Theme", "theme_type": "light", "primary_color": "#1A1A1A",
            "secondary_color": "#4A4A4A", "background_color": "#FAFAFA", "text_color": "#212121",
            "font_family_sans": "Inter", "font_family_heading": "Outfit", "layout_style": "clean-grid",
            "animation_settings": {}
        }

        # 2. Fetch Navigation Menus
        navs = get_portfolio_collection("navigation_menus")
        site_navs = [n for n in navs if str(n.get("website_id")) == w_id]
        site_navs = sorted(site_navs, key=lambda x: x.get("display_order", 0))

        # 3. Fetch Security / Publishing Config
        pub_config = get_pub_item_by_key("publishing_configs", w_id)
        if not pub_config:
            pub_config = {
                "website_id": w_id, "is_private": False, "password_protected": False,
                "is_maintenance": False, "is_suspended": False, "rate_limit_rpm": 60,
                "suspended_reason": ""
            }

        # 4. Fetch Pages and nested Sections
        pages = get_portfolio_collection("pages")
        site_pages = [p for p in pages if str(p.get("website_id")) == w_id]
        site_pages = sorted(site_pages, key=lambda x: x.get("display_order", 0))

        sections = get_portfolio_collection("sections")

        hydrated_pages = []
        for p in site_pages:
            p_id = str(p["id"])
            p_sections = [s for s in sections if str(s.get("page_id")) == p_id and s.get("is_active", True)]
            p_sections = sorted(p_sections, key=lambda x: x.get("display_order", 0))
            hydrated_pages.append({
                "id": p_id,
                "slug": p.get("slug"),
                "title": p.get("title"),
                "page_type": p.get("page_type", "custom"),
                "seo": p.get("seo", {}),
                "sections": p_sections
            })

        return {
            "website": website,
            "theme": theme,
            "navigation": site_navs,
            "pages": hydrated_pages,
            "footer": website.get("footer_builder", {}),
            "security": {
                "is_private": pub_config.get("is_private", False),
                "password_protected": pub_config.get("password_protected", False),
                "is_maintenance": pub_config.get("is_maintenance", False),
                "is_suspended": pub_config.get("is_suspended", False),
                "rate_limit_rpm": pub_config.get("rate_limit_rpm", 60),
                "suspended_reason": pub_config.get("suspended_reason", "")
            }
        }

    def _get_website_by_subdomain_or_id(self, identifier):
        websites = get_portfolio_collection("websites")
        # Try lookup by UUID first
        for w in websites:
            if str(w.get("id")) == identifier:
                return w
        # Try lookup by subdomain
        for w in websites:
            if w.get("subdomain") == identifier:
                return w
        return None

    def _validate_access_security(self, security_config, request):
        if security_config.get("is_suspended"):
            return Response(
                {"detail": f"This website has been suspended. Reason: {security_config.get('suspended_reason', 'N/A')}"},
                status=status.HTTP_403_FORBIDDEN
            )
        if security_config.get("is_maintenance"):
            return Response(
                {"detail": "This website is currently undergoing scheduled maintenance. Please check back shortly."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        if security_config.get("is_private") and not request.user.is_authenticated:
            return Response(
                {"detail": "Access restricted. Private website requires login authentication."},
                status=status.HTTP_401_UNAUTHORIZED
            )
        # Password check (handled via dynamic verification endpoints, but flagged here if not verified)
        if security_config.get("password_protected"):
            # Client can check header or session token (mocked here)
            verified = request.headers.get("X-Website-Password-Verified") == "true"
            if not verified:
                return Response(
                    {"detail": "This website is password protected.", "password_required": True},
                    status=status.HTTP_403_FORBIDDEN
                )
        return None

    @action(detail=False, methods=["get"], url_path="render")
    def render_website(self, request):
        """
        Dynamically aggregates, hydrates and serves complete layout payload of a website.
        Can look up by 'subdomain' or 'website_id' query params.
        """
        identifier = request.query_params.get("subdomain") or request.query_params.get("website_id")
        if not identifier:
            return Response({"detail": "Please specify 'subdomain' or 'website_id'."}, status=status.HTTP_400_BAD_REQUEST)

        website = self._get_website_by_subdomain_or_id(identifier)
        if not website:
            return Response({"detail": "Website not found."}, status=status.HTTP_404_NOT_FOUND)

        hydrated = self._hydrate_website_payload(website)
        
        # Check security guards
        security_resp = self._validate_access_security(hydrated["security"], request)
        if security_resp:
            return security_resp

        # Log public visitor analytics event
        self._log_analytics(website["id"], hydrated["pages"][0]["id"] if hydrated["pages"] else None, "/render", request)

        return Response(hydrated, status=status.HTTP_200_OK)

    def _log_analytics(self, website_id, page_id, path, request):
        try:
            store = read_publishing_store()
            user_agent = request.META.get('HTTP_USER_AGENT', 'Unknown')
            # Extract browser/device/country/referrer info
            browser = "Chrome" if "Chrome" in user_agent else "Safari" if "Safari" in user_agent else "Firefox" if "Firefox" in user_agent else "Edge" if "Edg" in user_agent else "Mobile Browser" if "Mobile" in user_agent else "Unknown Browser"
            device = "mobile" if "Mobile" in user_agent or "Android" in user_agent or "iPhone" in user_agent else "desktop"
            referrer = request.META.get('HTTP_REFERER', 'Direct')
            country = "India" if "IN" in request.headers.get("CF-IPCountry", "") or "IN" in request.headers.get("X-AppEngine-Country", "") else "United States"

            event = {
                "id": f"event-{uuid.uuid4()}",
                "website_id": str(website_id),
                "page_id": str(page_id) if page_id else None,
                "path": path,
                "visitor_id": request.COOKIES.get("visitor_id", f"visitor-{uuid.uuid4()}"),
                "ip_address": request.META.get('REMOTE_ADDR', '127.0.0.1'),
                "device": device,
                "browser": browser,
                "country": country,
                "referrer": referrer,
                "created_at": datetime.now().isoformat()
            }
            store["analytics_events"].append(event)
            write_publishing_store(store)
        except Exception as e:
            logger.error(f"Failed to log public analytics event: {e}")

    @action(detail=False, methods=["post"], url_path="verify-password")
    def verify_password(self, request):
        identifier = request.query_params.get("subdomain") or request.query_params.get("website_id")
        if not identifier:
            return Response({"detail": "Please specify 'subdomain' or 'website_id'."}, status=status.HTTP_400_BAD_REQUEST)

        website = self._get_website_by_subdomain_or_id(identifier)
        if not website:
            return Response({"detail": "Website not found."}, status=status.HTTP_404_NOT_FOUND)

        pub_config = get_pub_item_by_key("publishing_configs", website["id"])
        if not pub_config or not pub_config.get("password_protected"):
            return Response({"detail": "This website is not password-protected."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = PasswordVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        input_pwd = serializer.validated_data["password"]
        stored_hash = pub_config.get("password_hash")

        # Basic verification: for simple mock, compare hash directly
        if input_pwd == stored_hash or str(hash(input_pwd)) == stored_hash:
            return Response({"detail": "Password successfully verified.", "token": "verified-token-success"}, status=status.HTTP_200_OK)
        return Response({"detail": "Incorrect password validation."}, status=status.HTTP_401_UNAUTHORIZED)

    @action(detail=False, methods=["get"], url_path="homepage")
    def homepage(self, request):
        """
        Public homepage endpoint fetching only the root "/" or "home" page configuration.
        """
        identifier = request.query_params.get("subdomain") or request.query_params.get("website_id")
        if not identifier:
            return Response({"detail": "Please specify 'subdomain' or 'website_id'."}, status=status.HTTP_400_BAD_REQUEST)

        website = self._get_website_by_subdomain_or_id(identifier)
        if not website:
            return Response({"detail": "Website not found."}, status=status.HTTP_404_NOT_FOUND)

        hydrated = self._hydrate_website_payload(website)
        security_resp = self._validate_access_security(hydrated["security"], request)
        if security_resp:
            return security_resp

        # Filter the home page
        home_page = next((p for p in hydrated["pages"] if p["slug"] in ["/", "home", "homepage"]), None)
        if not home_page and hydrated["pages"]:
            home_page = hydrated["pages"][0]

        if not home_page:
            return Response({"detail": "No home page configured for this website."}, status=status.HTTP_404_NOT_FOUND)

        self._log_analytics(website["id"], home_page["id"], f"/{home_page['slug']}", request)
        return Response(home_page, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], url_path="pages/(?P<slug>[^/.]+)")
    def page_by_slug(self, request, slug=None):
        """
        Public page endpoint fetching rendering data for a specific page slug.
        """
        identifier = request.query_params.get("subdomain") or request.query_params.get("website_id")
        if not identifier:
            return Response({"detail": "Please specify 'subdomain' or 'website_id'."}, status=status.HTTP_400_BAD_REQUEST)

        website = self._get_website_by_subdomain_or_id(identifier)
        if not website:
            return Response({"detail": "Website not found."}, status=status.HTTP_404_NOT_FOUND)

        hydrated = self._hydrate_website_payload(website)
        security_resp = self._validate_access_security(hydrated["security"], request)
        if security_resp:
            return security_resp

        target_page = next((p for p in hydrated["pages"] if p["slug"] == slug), None)
        if not target_page:
            return Response({"detail": "Page not found.", "meta_404": {"title": "404 Not Found", "description": "Requested page does not exist."}}, status=status.HTTP_404_NOT_FOUND)

        self._log_analytics(website["id"], target_page["id"], f"/{slug}", request)
        return Response(target_page, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], url_path="blog")
    def blog(self, request):
        """
        Public blog feed. Aggregates and returns sections categorized as blog_posts across all pages.
        """
        identifier = request.query_params.get("subdomain") or request.query_params.get("website_id")
        if not identifier:
            return Response({"detail": "Please specify 'subdomain' or 'website_id'."}, status=status.HTTP_400_BAD_REQUEST)

        website = self._get_website_by_subdomain_or_id(identifier)
        if not website:
            return Response({"detail": "Website not found."}, status=status.HTTP_404_NOT_FOUND)

        # Gather blog sections
        sections = get_portfolio_collection("sections")
        pages = get_portfolio_collection("pages")
        site_pages = [p for p in pages if str(p.get("website_id")) == str(website["id"])]
        site_page_ids = [str(p["id"]) for p in site_pages]

        blog_sections = [s for s in sections if str(s.get("page_id")) in site_page_ids and s.get("section_type") == "blog_posts" and s.get("is_active", True)]

        return Response({
            "website_id": website["id"],
            "blog_sections": blog_sections,
            "posts_count": len(blog_sections)
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], url_path="sitemap")
    def sitemap(self, request):
        """
        Generates robust XML-style sitemap metadata including change frequencies and priorities.
        """
        identifier = request.query_params.get("subdomain") or request.query_params.get("website_id")
        if not identifier:
            return Response({"detail": "Please specify 'subdomain' or 'website_id'."}, status=status.HTTP_400_BAD_REQUEST)

        website = self._get_website_by_subdomain_or_id(identifier)
        if not website:
            return Response({"detail": "Website not found."}, status=status.HTTP_404_NOT_FOUND)

        pages = get_portfolio_collection("pages")
        site_pages = [p for p in pages if str(p.get("website_id")) == str(website["id"]) and p.get("is_published", True)]

        domain = website.get("custom_domain") or f"{website.get('subdomain')}.brahmavidya.edu"

        urls = []
        for p in site_pages:
            urls.append({
                "loc": f"https://{domain}/{p.get('slug')}",
                "lastmod": p.get("updated_at", datetime.now().isoformat()),
                "changefreq": "weekly" if p.get("page_type") in ["blog", "projects"] else "monthly",
                "priority": 1.0 if p.get("page_type") == "home" else 0.7
            })

        xml_sitemap = f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        for u in urls:
            xml_sitemap += f'  <url>\n    <loc>{u["loc"]}</loc>\n    <lastmod>{u["lastmod"]}</lastmod>\n    <changefreq>{u["changefreq"]}</changefreq>\n    <priority>{u["priority"]}</priority>\n  </url>\n'
        xml_sitemap += '</urlset>'

        return Response({"xml": xml_sitemap, "structured": urls}, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], url_path="robots")
    def robots(self, request):
        """
        Public crawling instructions for SEO search engines.
        """
        identifier = request.query_params.get("subdomain") or request.query_params.get("website_id")
        if not identifier:
            return Response({"detail": "Please specify 'subdomain' or 'website_id'."}, status=status.HTTP_400_BAD_REQUEST)

        website = self._get_website_by_subdomain_or_id(identifier)
        if not website:
            return Response({"detail": "Website not found."}, status=status.HTTP_404_NOT_FOUND)

        domain = website.get("custom_domain") or f"{website.get('subdomain')}.brahmavidya.edu"

        robots_text = f"User-agent: *\nDisallow: /admin/\nDisallow: /api/\nSitemap: https://{domain}/sitemap.xml\n"
        return Response({"robots_txt": robots_text}, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], url_path="navigation")
    def navigation(self, request):
        identifier = request.query_params.get("subdomain") or request.query_params.get("website_id")
        if not identifier:
            return Response({"detail": "Please specify 'subdomain' or 'website_id'."}, status=status.HTTP_400_BAD_REQUEST)

        website = self._get_website_by_subdomain_or_id(identifier)
        if not website:
            return Response({"detail": "Website not found."}, status=status.HTTP_404_NOT_FOUND)

        navs = get_portfolio_collection("navigation_menus")
        site_navs = [n for n in navs if str(n.get("website_id")) == str(website["id"]) and n.get("is_visible", True)]
        site_navs = sorted(site_navs, key=lambda x: x.get("display_order", 0))

        return Response(site_navs, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], url_path="footer")
    def footer(self, request):
        identifier = request.query_params.get("subdomain") or request.query_params.get("website_id")
        if not identifier:
            return Response({"detail": "Please specify 'subdomain' or 'website_id'."}, status=status.HTTP_400_BAD_REQUEST)

        website = self._get_website_by_subdomain_or_id(identifier)
        if not website:
            return Response({"detail": "Website not found."}, status=status.HTTP_404_NOT_FOUND)

        return Response(website.get("footer_builder", {}), status=status.HTTP_200_OK)


# ==========================================
# 2. WEBSITE PUBLISHING & TRANSITIONS
# ==========================================

class WebsitePublishingViewSet(BasePublishingModelViewSet):
    """
    ModelViewSet for triggering state transitions on websites: Draft, Preview, Publish, Unpublish, Archive, Republish,
    and managing password protection, maintenance flags, and suspend states.
    """
    serializer_class = PublishingConfigSerializer
    required_permissions = {
        "list": "publishing:admin:view",
        "retrieve": "publishing:admin:view",
        "update_config": "publishing:admin:update",
        "publish": "publishing:admin:update",
        "unpublish": "publishing:admin:update",
        "archive": "publishing:admin:update",
        "republish": "publishing:admin:update",
        "maintenance_mode": "publishing:admin:update",
        "suspend": "publishing:admin:update",
        "unsuspend": "publishing:admin:update",
    }

    def retrieve(self, request, pk=None):
        config = get_pub_item_by_key("publishing_configs", pk)
        if not config:
            # Create a default if missing
            config = {
                "website_id": str(pk), "is_private": False, "password_protected": False,
                "password_hash": None, "is_maintenance": False, "is_suspended": False,
                "rate_limit_rpm": 60, "suspended_reason": "",
                "created_at": datetime.now().isoformat(), "updated_at": datetime.now().isoformat()
            }
            save_pub_item("publishing_configs", pk, config)
        return Response(config, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="config")
    def update_config(self, request, pk=None):
        config = get_pub_item_by_key("publishing_configs", pk) or {
            "website_id": str(pk), "is_private": False, "password_protected": False,
            "password_hash": None, "is_maintenance": False, "is_suspended": False,
            "rate_limit_rpm": 60, "suspended_reason": "",
            "created_at": datetime.now().isoformat()
        }
        serializer = PublishingConfigSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        for key, val in serializer.validated_data.items():
            if key != "website_id":
                config[key] = val
        config["updated_at"] = datetime.now().isoformat()
        save_pub_item("publishing_configs", pk, config)
        return Response(config, status=status.HTTP_200_OK)

    def _transition_status(self, website_id, new_status):
        website = get_portfolio_item_by_id("websites", website_id)
        if not website:
            return None
        website["status"] = new_status
        website["updated_at"] = datetime.now().isoformat()
        save_portfolio_item("websites", website)
        return website

    @action(detail=True, methods=["post"], url_path="publish")
    def publish(self, request, pk=None):
        website = self._transition_status(pk, "published")
        if not website:
            return Response({"detail": "Website not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response({"detail": "Website transitioned successfully to 'published'.", "website": website}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="unpublish")
    def unpublish(self, request, pk=None):
        website = self._transition_status(pk, "draft")
        if not website:
            return Response({"detail": "Website not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response({"detail": "Website transitioned successfully to 'draft'.", "website": website}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="archive")
    def archive(self, request, pk=None):
        website = self._transition_status(pk, "archived")
        if not website:
            return Response({"detail": "Website not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response({"detail": "Website transitioned successfully to 'archived'.", "website": website}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="republish")
    def republish(self, request, pk=None):
        # Create a new version snapshot before republishing
        self._create_version_snapshot(pk, request.user.id, "Auto-generated snapshot during republishing.")
        website = self._transition_status(pk, "published")
        if not website:
            return Response({"detail": "Website not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response({"detail": "Website republished successfully with active snapshot.", "website": website}, status=status.HTTP_200_OK)

    def _create_version_snapshot(self, website_id, user_id, desc):
        website = get_portfolio_item_by_id("websites", website_id)
        if not website:
            return None
        
        pages = get_portfolio_collection("pages")
        site_pages = [p for p in pages if str(p.get("website_id")) == str(website_id)]
        
        store = read_publishing_store()
        existing_versions = [v for v in store["website_versions"] if str(v["website_id"]) == str(website_id)]
        next_ver = max([v["version_number"] for v in existing_versions]) + 1 if existing_versions else 1

        new_ver = {
            "id": f"ver-{uuid.uuid4()}",
            "website_id": str(website_id),
            "version_number": next_ver,
            "description": desc,
            "snapshot": {
                "website": website,
                "pages": site_pages
            },
            "created_by": str(user_id),
            "created_at": datetime.now().isoformat()
        }
        store["website_versions"].append(new_ver)
        write_publishing_store(store)
        return new_ver

    @action(detail=True, methods=["post"], url_path="maintenance")
    def maintenance_mode(self, request, pk=None):
        config = get_pub_item_by_key("publishing_configs", pk)
        if not config:
            return Response({"detail": "Publishing config not found."}, status=status.HTTP_404_NOT_FOUND)
        
        enable = request.data.get("enable", True)
        config["is_maintenance"] = enable
        config["updated_at"] = datetime.now().isoformat()
        save_pub_item("publishing_configs", pk, config)
        return Response({"detail": f"Maintenance mode successfully set to: {enable}.", "config": config}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="suspend")
    def suspend(self, request, pk=None):
        config = get_pub_item_by_key("publishing_configs", pk)
        if not config:
            return Response({"detail": "Publishing config not found."}, status=status.HTTP_404_NOT_FOUND)

        reason = request.data.get("reason", "Violation of terms of service.")
        config["is_suspended"] = True
        config["suspended_reason"] = reason
        config["updated_at"] = datetime.now().isoformat()
        save_pub_item("publishing_configs", pk, config)
        return Response({"detail": "Website successfully suspended.", "config": config}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="unsuspend")
    def unsuspend(self, request, pk=None):
        config = get_pub_item_by_key("publishing_configs", pk)
        if not config:
            return Response({"detail": "Publishing config not found."}, status=status.HTTP_404_NOT_FOUND)

        config["is_suspended"] = False
        config["suspended_reason"] = ""
        config["updated_at"] = datetime.now().isoformat()
        save_pub_item("publishing_configs", pk, config)
        return Response({"detail": "Website suspension lifted.", "config": config}, status=status.HTTP_200_OK)


# ==========================================
# 3. SUBDOMAIN & CUSTOM DOMAIN MANAGEMENT
# ==========================================

class SubdomainManagementViewSet(BasePublishingModelViewSet):
    """
    ModelViewSet for reserving subdomains, checking namespace availability and mapping custom domains.
    """
    serializer_class = SubdomainReservationSerializer
    required_permissions = {
        "list": "publishing:subdomain:view",
        "retrieve": "publishing:subdomain:view",
        "create": "publishing:subdomain:create",
        "check_availability": "publishing:subdomain:view",
        "release": "publishing:subdomain:delete",
    }

    def list(self, request):
        reservations = get_pub_collection("subdomain_reservations")
        return self.paginate_memory_list(request, reservations)

    def create(self, request):
        serializer = SubdomainReservationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        subdomain = serializer.validated_data["subdomain"].lower().strip()
        website_id = serializer.validated_data["website_id"]

        # Check availability
        store = read_publishing_store()
        if subdomain in store["subdomain_reservations"]:
            return Response({"detail": f"Subdomain '{subdomain}' is already reserved."}, status=status.HTTP_400_BAD_REQUEST)

        # Ensure website does not already have a different subdomain
        for res in store["subdomain_reservations"].values():
            if str(res.get("website_id")) == str(website_id):
                return Response({"detail": "This website already has a reserved subdomain. Please release it first."}, status=status.HTTP_400_BAD_REQUEST)

        reservation = {
            "subdomain": subdomain,
            "website_id": str(website_id),
            "reserved_by": str(request.user.id),
            "is_active": True,
            "created_at": datetime.now().isoformat()
        }
        store["subdomain_reservations"][subdomain] = reservation
        write_publishing_store(store)

        # Update subdomain on website record
        website = get_portfolio_item_by_id("websites", website_id)
        if website:
            website["subdomain"] = subdomain
            website["updated_at"] = datetime.now().isoformat()
            save_portfolio_item("websites", website)

        return Response(reservation, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["get"], url_path="check")
    def check_availability(self, request):
        subdomain = request.query_params.get("subdomain")
        if not subdomain:
            return Response({"detail": "Please specify 'subdomain' parameter."}, status=status.HTTP_400_BAD_REQUEST)

        import re
        subdomain = subdomain.lower().strip()
        if not re.match(r"^[a-zA-Z0-9\-]+$", subdomain):
            return Response({
                "subdomain": subdomain,
                "available": False,
                "reason": "Subdomain can only contain alphanumeric characters and hyphens."
            }, status=status.HTTP_200_OK)

        store = read_publishing_store()
        reserved = subdomain in store["subdomain_reservations"]
        return Response({
            "subdomain": subdomain,
            "available": not reserved,
            "reason": "Subdomain is available for registration." if not reserved else "Subdomain is already reserved."
        }, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="release")
    def release(self, request, pk=None):
        """
        Releases a subdomain namespace reservation.
        """
        store = read_publishing_store()
        subdomain = str(pk).lower().strip()
        if subdomain not in store["subdomain_reservations"]:
            return Response({"detail": "Subdomain reservation not found."}, status=status.HTTP_404_NOT_FOUND)

        res = store["subdomain_reservations"][subdomain]
        # Check permissions
        if str(res.get("reserved_by")) != str(request.user.id) and not request.user.is_superuser:
            return Response({"detail": "Permission denied to release this subdomain."}, status=status.HTTP_403_FORBIDDEN)

        # Delete reservation
        del store["subdomain_reservations"][subdomain]
        write_publishing_store(store)

        return Response({"detail": f"Subdomain '{subdomain}' has been successfully released."}, status=status.HTTP_200_OK)


# ==========================================
# 4. WEBSITE VERSIONING ENGINE
# ==========================================

class WebsiteVersioningViewSet(BasePublishingModelViewSet):
    """
    ModelViewSet managing structural version control snapshots, compares, and rollbacks.
    """
    serializer_class = WebsiteVersionSerializer
    required_permissions = {
        "list": "publishing:version:view",
        "retrieve": "publishing:version:view",
        "create": "publishing:version:create",
        "compare": "publishing:version:view",
        "rollback": "publishing:version:update",
    }

    def list(self, request):
        website_id = request.query_params.get("website_id")
        if not website_id:
            return Response({"detail": "Please specify 'website_id' query parameter."}, status=status.HTTP_400_BAD_REQUEST)

        versions = get_pub_collection("website_versions")
        site_versions = [v for v in versions if str(v.get("website_id")) == str(website_id)]
        site_versions = sorted(site_versions, key=lambda x: x.get("version_number", 0), reverse=True)

        return self.paginate_memory_list(request, site_versions)

    def create(self, request):
        website_id = request.data.get("website_id")
        if not website_id:
            return Response({"detail": "Please specify 'website_id'."}, status=status.HTTP_400_BAD_REQUEST)

        website = get_portfolio_item_by_id("websites", website_id)
        if not website:
            return Response({"detail": "Website not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = CreateVersionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        pages = get_portfolio_collection("pages")
        site_pages = [p for p in pages if str(p.get("website_id")) == str(website_id)]

        store = read_publishing_store()
        existing_versions = [v for v in store["website_versions"] if str(v["website_id"]) == str(website_id)]
        next_ver = max([v["version_number"] for v in existing_versions]) + 1 if existing_versions else 1

        new_version = {
            "id": f"ver-{uuid.uuid4()}",
            "website_id": str(website_id),
            "version_number": next_ver,
            "description": serializer.validated_data.get("description", ""),
            "snapshot": {
                "website": website,
                "pages": site_pages
            },
            "created_by": str(request.user.id),
            "created_at": datetime.now().isoformat()
        }
        store["website_versions"].append(new_version)
        write_publishing_store(store)

        return Response(new_version, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["get"], url_path="compare")
    def compare(self, request):
        website_id = request.query_params.get("website_id")
        source_ver = request.query_params.get("source_version")
        target_ver = request.query_params.get("target_version")

        if not all([website_id, source_ver, target_ver]):
            return Response({"detail": "Please specify 'website_id', 'source_version', and 'target_version'."}, status=status.HTTP_400_BAD_REQUEST)

        versions = get_pub_collection("website_versions")
        source_snap = next((v for v in versions if str(v["website_id"]) == str(website_id) and v["version_number"] == int(source_ver)), None)
        target_snap = next((v for v in versions if str(v["website_id"]) == str(website_id) and v["version_number"] == int(target_ver)), None)

        if not source_snap or not target_snap:
            return Response({"detail": "One or both versions not found."}, status=status.HTTP_404_NOT_FOUND)

        # Evaluate differential schema
        s_pages = {p["id"]: p for p in source_snap["snapshot"].get("pages", [])}
        t_pages = {p["id"]: p for p in target_snap["snapshot"].get("pages", [])}

        added_pages = [p for pid, p in t_pages.items() if pid not in s_pages]
        removed_pages = [p for pid, p in s_pages.items() if pid not in t_pages]
        modified_pages = []

        for pid, p in t_pages.items():
            if pid in s_pages:
                if p.get("title") != s_pages[pid].get("title") or p.get("slug") != s_pages[pid].get("slug"):
                    modified_pages.append({
                        "id": pid,
                        "old_title": s_pages[pid].get("title"),
                        "new_title": p.get("title"),
                        "old_slug": s_pages[pid].get("slug"),
                        "new_slug": p.get("slug")
                    })

        differences = {
            "pages": {
                "added": len(added_pages),
                "removed": len(removed_pages),
                "modified": len(modified_pages),
                "details": {
                    "added": added_pages,
                    "removed": removed_pages,
                    "modified": modified_pages
                }
            },
            "website_name_changed": source_snap["snapshot"]["website"].get("name") != target_snap["snapshot"]["website"].get("name")
        }

        return Response({
            "source_version": source_ver,
            "target_version": target_ver,
            "differences": differences
        }, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="rollback")
    def rollback(self, request, pk=None):
        """
        Reverts active website and page states back to chosen historical version snapshot.
        """
        version_id = str(pk)
        versions = get_pub_collection("website_versions")
        version = next((v for v in versions if v["id"] == version_id), None)
        if not version:
            return Response({"detail": "Version snapshot not found."}, status=status.HTTP_404_NOT_FOUND)

        website_id = version["website_id"]
        snapshot = version["snapshot"]

        # Restore Website
        website = get_portfolio_item_by_id("websites", website_id)
        if website:
            snap_web = snapshot["website"]
            for key, val in snap_web.items():
                website[key] = val
            website["updated_at"] = datetime.now().isoformat()
            save_portfolio_item("websites", website)

        # Restore Pages
        # First delete current pages for this website
        all_pages = get_portfolio_collection("pages")
        cleaned_pages = [p for p in all_pages if str(p.get("website_id")) != str(website_id)]
        
        # Hydrate pages from snapshot
        snap_pages = snapshot.get("pages", [])
        for sp in snap_pages:
            sp["updated_at"] = datetime.now().isoformat()
            cleaned_pages.append(sp)

        # Save pages list back
        p_store = read_publishing_store() # Actually write back to portfolio page collection
        from apps.portfolio.portfolio_store import read_store, write_store
        p_data = read_store()
        p_data["pages"] = {p["id"]: p for p in cleaned_pages}
        write_store(p_data)

        return Response({
            "detail": f"Successfully rolled back to version {version['version_number']}.",
            "rolled_back_to": version
        }, status=status.HTTP_200_OK)


# ==========================================
# 5. FORM SUBMISSION ENGINE
# ==========================================

class FormSubmissionViewSet(BasePublishingModelViewSet):
    """
    ModelViewSet for collecting contact forms, newsletter signups, lead generations, with integrated spam detection metadata.
    """
    serializer_class = FormSubmissionSerializer
    required_permissions = {
        "list": "publishing:submissions:view",
        "retrieve": "publishing:submissions:view",
        "create": "publishing:submissions:create",
        "destroy": "publishing:submissions:delete",
    }

    def get_queryset(self):
        return get_pub_collection("form_submissions")

    def list(self, request):
        website_id = request.query_params.get("website_id")
        form_type = request.query_params.get("form_type")

        submissions = get_pub_collection("form_submissions")
        if website_id:
            submissions = [s for s in submissions if str(s["website_id"]) == str(website_id)]
        if form_type:
            submissions = [s for s in submissions if s["form_type"] == form_type]

        submissions = sorted(submissions, key=lambda x: x.get("created_at", ""), reverse=True)
        return self.paginate_memory_list(request, submissions)

    def create(self, request):
        serializer = FormSubmissionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Extract info
        sub_id = f"form-{uuid.uuid4()}"
        website_id = serializer.validated_data["website_id"]
        form_type = serializer.validated_data["form_type"]
        data = serializer.validated_data["data"]

        # Basic anti-spam heuristics (length, links frequency, honey-pots)
        msg_content = str(data.get("message", "")) + str(data.get("email", ""))
        has_suspicious_links = msg_content.count("http://") + msg_content.count("https://") > 2
        is_honey_filled = request.data.get("honeypot") is not None and request.data.get("honeypot") != ""
        
        spam_score = 0.05
        if has_suspicious_links:
            spam_score += 0.45
        if is_honey_filled:
            spam_score += 0.50

        is_spam = spam_score >= 0.50

        submission = {
            "id": sub_id,
            "website_id": str(website_id),
            "form_type": form_type,
            "data": data,
            "is_spam": is_spam,
            "spam_score": spam_score,
            "created_at": datetime.now().isoformat()
        }
        
        save_pub_item("form_submissions", sub_id, submission)
        return Response(submission, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None):
        sub = get_pub_item_by_key("form_submissions", pk)
        if not sub:
            return Response({"detail": "Submission not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response(sub, status=status.HTTP_200_OK)


# ==========================================
# 6. ANALYTICS ENGINE
# ==========================================

class AnalyticsViewSet(BasePublishingModelViewSet):
    """
    ModelViewSet generating aggregate operational summaries over devices, countries, browsers, and pages views.
    """
    serializer_class = AnalyticsAggregateSerializer
    required_permissions = {
        "list": "publishing:analytics:view",
        "retrieve": "publishing:analytics:view",
    }

    def list(self, request):
        website_id = request.query_params.get("website_id")
        if not website_id:
            return Response({"detail": "Please specify 'website_id' query parameter."}, status=status.HTTP_400_BAD_REQUEST)

        events = get_pub_collection("analytics_events")
        site_events = [e for e in events if str(e.get("website_id")) == str(website_id)]

        # Unique visitors count
        visitors = set([e["visitor_id"] for e in site_events])

        # Helpers for aggregating list items
        def build_stats(key_name):
            counts = {}
            for e in site_events:
                val = e.get(key_name) or "Unknown"
                counts[val] = counts.get(val, 0) + 1
            return [{"key": k, "count": v} for k, v in sorted(counts.items(), key=lambda x: x[1], reverse=True)[:5]]

        devices = build_stats("device")
        browsers = build_stats("browser")
        countries = build_stats("country")
        referrers = build_stats("referrer")
        top_pages = build_stats("path")

        # Top websites overall
        all_events = get_pub_collection("analytics_events")
        web_counts = {}
        for e in all_events:
            w_id = e.get("website_id")
            web_counts[w_id] = web_counts.get(w_id, 0) + 1
        top_websites = [{"key": k, "count": v} for k, v in sorted(web_counts.items(), key=lambda x: x[1], reverse=True)[:5]]

        aggregate_report = {
            "total_page_views": len(site_events),
            "unique_visitors": len(visitors),
            "devices": devices,
            "browsers": browsers,
            "countries": countries,
            "referrers": referrers,
            "top_pages": top_pages,
            "top_websites": top_websites
        }

        return Response(aggregate_report, status=status.HTTP_200_OK)


# ==========================================
# 7. MEDIA DELIVERY & CACHE CONTROL
# ==========================================

class MediaDeliveryViewSet(BasePublishingModelViewSet):
    """
    ModelViewSet verifying asset deliveries, image resizing outputs, and cache control configurations.
    """
    serializer_class = ImageOptimizationSerializer
    required_permissions = {
        "list": "publishing:media:view",
        "create": "publishing:media:create",
        "optimize": "publishing:media:view",
    }

    @action(detail=False, methods=["post"], url_path="optimize")
    def optimize_image(self, request):
        """
        Validates output options (webp/format/resizing dimensions) and generates clean cache metadata wrappers.
        """
        serializer = ImageOptimizationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        url = serializer.validated_data["url"]
        width = serializer.validated_data.get("width")
        height = serializer.validated_data.get("height")
        quality = serializer.validated_data.get("quality", 85)
        out_format = serializer.validated_data.get("format", "webp")

        import hashlib
        # Generate hash for caching wrapper
        cache_key = hashlib.md5(f"{url}_{width}_{height}_{quality}_{out_format}".encode("utf-8")).hexdigest()

        optimized_metadata = {
            "original_url": url,
            "cache_key": f"optimized-{cache_key}",
            "applied_optimization": {
                "width": width or "original",
                "height": height or "original",
                "quality": quality,
                "format": out_format
            },
            "delivery_headers": {
                "Cache-Control": "public, max-age=31536000, immutable",
                "Content-Type": f"image/{out_format if out_format != 'jpg' else 'jpeg'}",
                "X-Asset-Version": f"v1.{cache_key[:8]}"
            }
        }

        return Response(optimized_metadata, status=status.HTTP_200_OK)


class AuthorProfileViewSet(viewsets.ModelViewSet):
    queryset = AuthorProfile.objects.select_related("user").all().order_by("name")
    serializer_class = AuthorProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "id"

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class PublisherProfileViewSet(viewsets.ModelViewSet):
    queryset = PublisherProfile.objects.all().order_by("name")
    serializer_class = PublisherProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "id"


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.select_related("author", "publisher").all().order_by("title")
    serializer_class = BookSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "id"

    @action(detail=True, methods=["post"])
    def approve_publication(self, request, id=None):
        book = self.get_object()
        user = request.user
        is_admin = user.is_superuser or (hasattr(user, "role") and user.role and user.role.name in ["SUPERADMIN", "ADMIN"])
        if not is_admin:
            return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)
            
        book.status = "APPROVED"
        book.save()
        
        from apps.control_center.models import SystemAuditLog
        SystemAuditLog.objects.create(
            actor=user,
            action_type="BOOK_PUBLICATION_APPROVED",
            target_table="books",
            after_state={"book_id": str(book.id), "title": book.title}
        )
        return Response({"success": True, "status": book.status, "message": "Book approved successfully."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"])
    def publish_book(self, request, id=None):
        book = self.get_object()
        if book.status != "APPROVED" and not request.user.is_superuser:
            return Response({"detail": "Only approved books can be published."}, status=status.HTTP_400_BAD_REQUEST)
            
        book.status = "PUBLISHED"
        book.save()
        return Response({"success": True, "status": book.status, "message": "Book published successfully."}, status=status.HTTP_200_OK)


class ProductOwnershipViewSet(viewsets.ModelViewSet):
    queryset = ProductOwnership.objects.select_related("book", "course", "owner_user", "wallet_destination").all()
    serializer_class = ProductOwnershipSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "id"


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.select_related("user").all().order_by("-created_at")
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "id"

    def get_queryset(self):
        user = self.request.user
        is_admin = user.is_superuser or (hasattr(user, "role") and user.role and user.role.name in ["SUPERADMIN", "ADMIN"])
        if is_admin:
            return self.queryset
        return self.queryset.filter(user=user)

    def perform_create(self, serializer):
        user = self.request.user
        items_data = self.request.data.get("items", [])
        if not items_data:
            raise serializers.ValidationError({"detail": "Items are required to create an order."})
            
        import decimal
        total_amount = decimal.Decimal("0.00")
        for item in items_data:
            total_amount += decimal.Decimal(str(item.get("price", "0.00")))
            
        order = serializer.save(user=user, total_amount=total_amount)
        
        for item in items_data:
            OrderItem.objects.create(
                order=order,
                book_id=item.get("book"),
                course_id=item.get("course"),
                price=decimal.Decimal(str(item.get("price")))
            )


class ReadingProgressViewSet(viewsets.ModelViewSet):
    queryset = ReadingProgress.objects.select_related("user", "book").all()
    serializer_class = ReadingProgressSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "id"

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        book_id = self.request.data.get("book")
        progress, created = ReadingProgress.objects.get_or_create(
            user=self.request.user,
            book_id=book_id,
            defaults={
                "progress_percentage": self.request.data.get("progress_percentage", 0.00),
                "current_location": self.request.data.get("current_location", ""),
                "notes": self.request.data.get("notes", "")
            }
        )
        if not created:
            progress.progress_percentage = self.request.data.get("progress_percentage", progress.progress_percentage)
            progress.current_location = self.request.data.get("current_location", progress.current_location)
            progress.notes = self.request.data.get("notes", progress.notes)
            progress.save()
            
        serializer.instance = progress
