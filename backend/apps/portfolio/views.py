import uuid
import logging
from datetime import datetime
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination

from apps.users.permissions import HasRBACPermission
from apps.portfolio.serializers import (
    WebsiteSerializer, PageSerializer, NavigationMenuSerializer,
    ThemeSerializer, MediaItemSerializer, SectionSerializer,
    ResumeSerializer, JobListingSerializer, CareerRoadmapSerializer
)
from apps.portfolio.portfolio_store import (
    get_collection, get_item_by_id, save_item,
    soft_delete_item_by_id, restore_item_by_id, hard_delete_item_by_id
)

logger = logging.getLogger("brahmavidya.portfolio")


class EnterprisePagination(PageNumberPagination):
    """
    Standard enterprise pagination class specifying default page size and size override parameter.
    """
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


class BasePortfolioViewSet(viewsets.ViewSet):
    """
    Base ViewSet for portfolio components implementing RBAC permissions and enterprise pagination.
    """
    permission_classes = [HasRBACPermission]

    def paginate_list(self, request, lst):
        """
        Paginates any list of dicts using EnterprisePagination rules.
        """
        paginator = EnterprisePagination()
        page = paginator.paginate_queryset(lst, request)
        if page is not None:
            return paginator, page
        return None, lst

    def filter_and_search(self, lst, request, search_fields=None, filter_keys=None):
        """
        Applies searches and filters dynamically to memory-based list of dictionaries.
        """
        result = lst
        # Soft delete filter
        include_deleted = request.query_params.get("include_deleted", "false").lower() == "true"
        if not include_deleted:
            result = [r for r in result if r.get("deleted_at") is None]
        else:
            result = [r for r in result if r.get("deleted_at") is not None]

        # Explicit filters
        if filter_keys:
            for key in filter_keys:
                if key in request.query_params:
                    val = request.query_params[key]
                    if val.lower() in ["true", "false"]:
                        bool_val = val.lower() == "true"
                        result = [r for r in result if r.get(key) == bool_val]
                    else:
                        result = [r for r in result if str(r.get(key)).lower() == val.lower().strip()]

        # Search query
        search_query = request.query_params.get("search")
        if search_query and search_fields:
            search_query = search_query.lower().strip()
            filtered = []
            for item in result:
                match = False
                for field in search_fields:
                    val = item.get(field)
                    if val and search_query in str(val).lower():
                        match = True
                        break
                if match:
                    filtered.append(item)
            result = filtered

        # Ordering
        ordering = request.query_params.get("ordering", "-created_at")
        reverse = False
        if ordering.startswith("-"):
            reverse = True
            ordering = ordering[1:]

        def get_sort_key(item):
            val = item.get(ordering)
            if val is None:
                return "" if reverse else "zzzzzzzz"
            return val

        try:
            result = sorted(result, key=get_sort_key, reverse=reverse)
        except Exception:
            pass

        return result


class WebsiteViewSet(BasePortfolioViewSet):
    """
    ViewSet for handling Portfolio Websites, custom domains and subdomains, and nesting pages.
    """
    required_permissions = {
        "list": "portfolio:website:view",
        "retrieve": "portfolio:website:view",
        "create": "portfolio:website:create",
        "update": "portfolio:website:update",
        "partial_update": "portfolio:website:update",
        "destroy": "portfolio:website:delete",
        "restore": "portfolio:website:update",
        "publish": "portfolio:website:update",
        "unpublish": "portfolio:website:update",
        "pages": "portfolio:website:view",
        "navigation_menus": "portfolio:website:view",
        "themes": "portfolio:website:view",
        "media_library": "portfolio:website:view",
    }

    def list(self, request):
        user_id = str(request.user.id)
        is_admin = request.user.is_superuser or (
            hasattr(request.user, "role") and request.user.role and request.user.role.name in ["SUPERADMIN", "ADMIN"]
        )

        websites = get_collection("websites", include_deleted=True)
        if not is_admin:
            websites = [w for w in websites if str(w.get("user_id")) == user_id]

        websites = self.filter_and_search(
            websites, request,
            search_fields=["name", "subdomain", "custom_domain"],
            filter_keys=["status", "subdomain"]
        )

        paginator, page = self.paginate_list(request, websites)
        serializer = WebsiteSerializer(page, many=True)
        if paginator:
            return paginator.get_paginated_response(serializer.data)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request):
        serializer = WebsiteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        w_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        item_data = {
            "id": w_id,
            "user_id": str(request.user.id),
            "name": serializer.validated_data["name"],
            "subdomain": serializer.validated_data["subdomain"],
            "custom_domain": serializer.validated_data.get("custom_domain", ""),
            "status": serializer.validated_data.get("status", "draft"),
            "footer_builder": serializer.validated_data.get("footer_builder", {
                "footer_columns": [], "copyright_text": "", "social_icons": []
            }),
            "created_at": now,
            "updated_at": now,
            "deleted_at": None
        }
        save_item("websites", item_data)
        return Response(item_data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None):
        website = get_item_by_id("websites", pk)
        if not website:
            return Response({"detail": "Website not found."}, status=status.HTTP_404_NOT_FOUND)

        is_admin = request.user.is_superuser or (
            hasattr(request.user, "role") and request.user.role and request.user.role.name in ["SUPERADMIN", "ADMIN"]
        )
        if not is_admin and str(website.get("user_id")) != str(request.user.id):
            return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

        return Response(website, status=status.HTTP_200_OK)

    def partial_update(self, request, pk=None):
        website = get_item_by_id("websites", pk)
        if not website:
            return Response({"detail": "Website not found."}, status=status.HTTP_404_NOT_FOUND)

        is_admin = request.user.is_superuser or (
            hasattr(request.user, "role") and request.user.role and request.user.role.name in ["SUPERADMIN", "ADMIN"]
        )
        if not is_admin and str(website.get("user_id")) != str(request.user.id):
            return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

        serializer = WebsiteSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        for key, val in serializer.validated_data.items():
            website[key] = val
        website["updated_at"] = datetime.now().isoformat()
        save_item("websites", website)

        return Response(website, status=status.HTTP_200_OK)

    def update(self, request, pk=None):
        return self.partial_update(request, pk)

    def destroy(self, request, pk=None):
        website = get_item_by_id("websites", pk)
        if not website:
            return Response({"detail": "Website not found."}, status=status.HTTP_404_NOT_FOUND)

        is_admin = request.user.is_superuser or (
            hasattr(request.user, "role") and request.user.role and request.user.role.name in ["SUPERADMIN", "ADMIN"]
        )
        if not is_admin and str(website.get("user_id")) != str(request.user.id):
            return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

        soft_delete_item_by_id("websites", pk)
        return Response({"detail": "Website soft-deleted successfully.", "deleted_at": datetime.now().isoformat()}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="restore")
    def restore(self, request, pk=None):
        website = get_item_by_id("websites", pk)
        if not website:
            return Response({"detail": "Website not found."}, status=status.HTTP_404_NOT_FOUND)

        is_admin = request.user.is_superuser or (
            hasattr(request.user, "role") and request.user.role and request.user.role.name in ["SUPERADMIN", "ADMIN"]
        )
        if not is_admin and str(website.get("user_id")) != str(request.user.id):
            return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

        restore_item_by_id("websites", pk)
        return Response({"detail": "Website successfully restored.", "deleted_at": None}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="publish")
    def publish(self, request, pk=None):
        website = get_item_by_id("websites", pk)
        if not website:
            return Response({"detail": "Website not found."}, status=status.HTTP_404_NOT_FOUND)

        is_admin = request.user.is_superuser or (
            hasattr(request.user, "role") and request.user.role and request.user.role.name in ["SUPERADMIN", "ADMIN"]
        )
        if not is_admin and str(website.get("user_id")) != str(request.user.id):
            return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

        website["status"] = "published"
        website["updated_at"] = datetime.now().isoformat()
        save_item("websites", website)
        return Response({"detail": "Website status successfully updated to published.", "status": "published"}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="unpublish")
    def unpublish(self, request, pk=None):
        website = get_item_by_id("websites", pk)
        if not website:
            return Response({"detail": "Website not found."}, status=status.HTTP_404_NOT_FOUND)

        is_admin = request.user.is_superuser or (
            hasattr(request.user, "role") and request.user.role and request.user.role.name in ["SUPERADMIN", "ADMIN"]
        )
        if not is_admin and str(website.get("user_id")) != str(request.user.id):
            return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

        website["status"] = "draft"
        website["updated_at"] = datetime.now().isoformat()
        save_item("websites", website)
        return Response({"detail": "Website status successfully updated to draft.", "status": "draft"}, status=status.HTTP_200_OK)

    # ==========================================
    # NESTED COLLECTIONS
    # ==========================================

    @action(detail=True, methods=["get", "post"], url_path="pages")
    def pages(self, request, pk=None):
        """
        Nested CRUD layer mapping /v1/portfolio/websites/{id}/pages/ requests.
        """
        website = get_item_by_id("websites", pk)
        if not website:
            return Response({"detail": "Parent Website not found."}, status=status.HTTP_404_NOT_FOUND)

        is_admin = request.user.is_superuser or (
            hasattr(request.user, "role") and request.user.role and request.user.role.name in ["SUPERADMIN", "ADMIN"]
        )
        if not is_admin and str(website.get("user_id")) != str(request.user.id):
            return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

        if request.method == "GET":
            pages = get_collection("pages", include_deleted=True)
            pages = [p for p in pages if str(p.get("website_id")) == str(pk)]
            pages = self.filter_and_search(pages, request, search_fields=["title", "slug"], filter_keys=["page_type", "is_published"])
            
            paginator, page = self.paginate_list(request, pages)
            serializer = PageSerializer(page, many=True)
            if paginator:
                return paginator.get_paginated_response(serializer.data)
            return Response(serializer.data, status=status.HTTP_200_OK)

        elif request.method == "POST":
            serializer = PageSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            p_id = str(uuid.uuid4())
            now = datetime.now().isoformat()
            page_data = {
                "id": p_id,
                "website_id": str(pk),
                "slug": serializer.validated_data["slug"],
                "title": serializer.validated_data["title"],
                "page_type": serializer.validated_data.get("page_type", "custom"),
                "is_published": serializer.validated_data.get("is_published", False),
                "display_order": serializer.validated_data.get("display_order", 0),
                "seo": serializer.validated_data.get("seo", {
                    "meta_title": "", "meta_description": "", "keywords": "", "opengraph_image": None
                }),
                "created_at": now,
                "updated_at": now,
                "deleted_at": None
            }
            save_item("pages", page_data)
            return Response(page_data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["get", "post"], url_path="navigation-menus")
    def navigation_menus(self, request, pk=None):
        """
        Nested CRUD mapping /v1/portfolio/websites/{id}/navigation-menus/
        """
        website = get_item_by_id("websites", pk)
        if not website:
            return Response({"detail": "Parent Website not found."}, status=status.HTTP_404_NOT_FOUND)

        is_admin = request.user.is_superuser or (
            hasattr(request.user, "role") and request.user.role and request.user.role.name in ["SUPERADMIN", "ADMIN"]
        )
        if not is_admin and str(website.get("user_id")) != str(request.user.id):
            return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

        if request.method == "GET":
            menus = get_collection("navigation_menus", include_deleted=True)
            menus = [m for m in menus if str(m.get("website_id")) == str(pk)]
            menus = self.filter_and_search(menus, request, search_fields=["label"], filter_keys=["parent_id", "is_visible"])

            paginator, page = self.paginate_list(request, menus)
            serializer = NavigationMenuSerializer(page, many=True)
            if paginator:
                return paginator.get_paginated_response(serializer.data)
            return Response(serializer.data, status=status.HTTP_200_OK)

        elif request.method == "POST":
            serializer = NavigationMenuSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            m_id = str(uuid.uuid4())
            now = datetime.now().isoformat()
            menu_data = {
                "id": m_id,
                "website_id": str(pk),
                "parent_id": serializer.validated_data.get("parent_id"),
                "label": serializer.validated_data["label"],
                "url": serializer.validated_data["url"],
                "icon": serializer.validated_data.get("icon", ""),
                "display_order": serializer.validated_data.get("display_order", 0),
                "is_visible": serializer.validated_data.get("is_visible", True),
                "is_external": serializer.validated_data.get("is_external", False),
                "created_at": now,
                "updated_at": now,
                "deleted_at": None
            }
            save_item("navigation_menus", menu_data)
            return Response(menu_data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["get", "post"], url_path="themes")
    def themes(self, request, pk=None):
        """
        Nested CRUD mapping /v1/portfolio/websites/{id}/themes/
        """
        website = get_item_by_id("websites", pk)
        if not website:
            return Response({"detail": "Parent Website not found."}, status=status.HTTP_404_NOT_FOUND)

        is_admin = request.user.is_superuser or (
            hasattr(request.user, "role") and request.user.role and request.user.role.name in ["SUPERADMIN", "ADMIN"]
        )
        if not is_admin and str(website.get("user_id")) != str(request.user.id):
            return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

        if request.method == "GET":
            themes = get_collection("themes", include_deleted=True)
            themes = [t for t in themes if str(t.get("website_id")) == str(pk)]
            themes = self.filter_and_search(themes, request, search_fields=["name"], filter_keys=["theme_type"])

            paginator, page = self.paginate_list(request, themes)
            serializer = ThemeSerializer(page, many=True)
            if paginator:
                return paginator.get_paginated_response(serializer.data)
            return Response(serializer.data, status=status.HTTP_200_OK)

        elif request.method == "POST":
            serializer = ThemeSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            t_id = str(uuid.uuid4())
            now = datetime.now().isoformat()
            theme_data = {
                "id": t_id,
                "website_id": str(pk),
                "name": serializer.validated_data["name"],
                "theme_type": serializer.validated_data.get("theme_type", "light"),
                "primary_color": serializer.validated_data.get("primary_color", "#1A1A1A"),
                "secondary_color": serializer.validated_data.get("secondary_color", "#4A4A4A"),
                "background_color": serializer.validated_data.get("background_color", "#FAFAFA"),
                "text_color": serializer.validated_data.get("text_color", "#212121"),
                "font_family_sans": serializer.validated_data.get("font_family_sans", "Inter"),
                "font_family_heading": serializer.validated_data.get("font_family_heading", "Outfit"),
                "layout_style": serializer.validated_data.get("layout_style", "clean-grid"),
                "animation_settings": serializer.validated_data.get("animation_settings", {}),
                "created_at": now,
                "updated_at": now,
                "deleted_at": None
            }
            save_item("themes", theme_data)
            return Response(theme_data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["get", "post"], url_path="media-library")
    def media_library(self, request, pk=None):
        """
        Nested CRUD mapping /v1/portfolio/websites/{id}/media-library/
        """
        website = get_item_by_id("websites", pk)
        if not website:
            return Response({"detail": "Parent Website not found."}, status=status.HTTP_404_NOT_FOUND)

        is_admin = request.user.is_superuser or (
            hasattr(request.user, "role") and request.user.role and request.user.role.name in ["SUPERADMIN", "ADMIN"]
        )
        if not is_admin and str(website.get("user_id")) != str(request.user.id):
            return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

        if request.method == "GET":
            media = get_collection("media_library", include_deleted=True)
            media = [m for m in media if str(m.get("website_id")) == str(pk)]
            media = self.filter_and_search(media, request, search_fields=["name"], filter_keys=["file_type"])

            paginator, page = self.paginate_list(request, media)
            serializer = MediaItemSerializer(page, many=True)
            if paginator:
                return paginator.get_paginated_response(serializer.data)
            return Response(serializer.data, status=status.HTTP_200_OK)

        elif request.method == "POST":
            serializer = MediaItemSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            m_id = str(uuid.uuid4())
            now = datetime.now().isoformat()
            media_data = {
                "id": m_id,
                "website_id": str(pk),
                "name": serializer.validated_data["name"],
                "file_type": serializer.validated_data.get("file_type", "image"),
                "file_size": serializer.validated_data["file_size"],
                "url": serializer.validated_data["url"],
                "created_at": now,
                "updated_at": now,
                "deleted_at": None
            }
            save_item("media_library", media_data)
            return Response(media_data, status=status.HTTP_201_CREATED)


class PageViewSet(BasePortfolioViewSet):
    """
    ViewSet for flat Page operations, metadata updates, and nesting sections.
    """
    required_permissions = {
        "list": "portfolio:website:view",
        "retrieve": "portfolio:website:view",
        "create": "portfolio:website:create",
        "update": "portfolio:website:update",
        "partial_update": "portfolio:website:update",
        "destroy": "portfolio:website:delete",
        "restore": "portfolio:website:update",
        "sections": "portfolio:website:view",
    }

    def list(self, request):
        pages = get_collection("pages", include_deleted=True)
        pages = self.filter_and_search(pages, request, search_fields=["title", "slug"], filter_keys=["website_id", "page_type", "is_published"])

        paginator, page = self.paginate_list(request, pages)
        serializer = PageSerializer(page, many=True)
        if paginator:
            return paginator.get_paginated_response(serializer.data)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        page = get_item_by_id("pages", pk)
        if not page:
            return Response({"detail": "Page not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response(page, status=status.HTTP_200_OK)

    def partial_update(self, request, pk=None):
        page = get_item_by_id("pages", pk)
        if not page:
            return Response({"detail": "Page not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = PageSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        for key, val in serializer.validated_data.items():
            page[key] = val
        page["updated_at"] = datetime.now().isoformat()
        save_item("pages", page)
        return Response(page, status=status.HTTP_200_OK)

    def update(self, request, pk=None):
        return self.partial_update(request, pk)

    def destroy(self, request, pk=None):
        soft_delete_item_by_id("pages", pk)
        return Response({"detail": "Page soft-deleted successfully."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="restore")
    def restore(self, request, pk=None):
        restore_item_by_id("pages", pk)
        return Response({"detail": "Page successfully restored."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get", "post"], url_path="sections")
    def sections(self, request, pk=None):
        """
        Nested CRUD mapping /v1/portfolio/pages/{id}/sections/
        """
        page = get_item_by_id("pages", pk)
        if not page:
            return Response({"detail": "Parent Page not found."}, status=status.HTTP_404_NOT_FOUND)

        if request.method == "GET":
            sections = get_collection("sections", include_deleted=True)
            sections = [s for s in sections if str(s.get("page_id")) == str(pk)]
            sections = self.filter_and_search(sections, request, search_fields=["title", "subtitle"], filter_keys=["section_type", "is_active"])

            paginator, page_data = self.paginate_list(request, sections)
            serializer = SectionSerializer(page_data, many=True)
            if paginator:
                return paginator.get_paginated_response(serializer.data)
            return Response(serializer.data, status=status.HTTP_200_OK)

        elif request.method == "POST":
            serializer = SectionSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            s_id = str(uuid.uuid4())
            now = datetime.now().isoformat()
            section_data = {
                "id": s_id,
                "page_id": str(pk),
                "section_type": serializer.validated_data["section_type"],
                "title": serializer.validated_data["title"],
                "subtitle": serializer.validated_data.get("subtitle", ""),
                "content": serializer.validated_data.get("content", {}),
                "display_order": serializer.validated_data.get("display_order", 0),
                "is_active": serializer.validated_data.get("is_active", True),
                "created_at": now,
                "updated_at": now,
                "deleted_at": None
            }
            save_item("sections", section_data)
            return Response(section_data, status=status.HTTP_201_CREATED)


class NavigationMenuViewSet(BasePortfolioViewSet):
    """
    ViewSet for flat Navigation Menu Link items.
    """
    required_permissions = {
        "list": "portfolio:website:view",
        "retrieve": "portfolio:website:view",
        "create": "portfolio:website:create",
        "update": "portfolio:website:update",
        "partial_update": "portfolio:website:update",
        "destroy": "portfolio:website:delete",
        "restore": "portfolio:website:update",
    }

    def list(self, request):
        menus = get_collection("navigation_menus", include_deleted=True)
        menus = self.filter_and_search(menus, request, search_fields=["label"], filter_keys=["website_id", "parent_id", "is_visible"])

        paginator, page = self.paginate_list(request, menus)
        serializer = NavigationMenuSerializer(page, many=True)
        if paginator:
            return paginator.get_paginated_response(serializer.data)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        menu = get_item_by_id("navigation_menus", pk)
        if not menu:
            return Response({"detail": "Navigation Menu item not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response(menu, status=status.HTTP_200_OK)

    def partial_update(self, request, pk=None):
        menu = get_item_by_id("navigation_menus", pk)
        if not menu:
            return Response({"detail": "Navigation Menu item not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = NavigationMenuSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        for key, val in serializer.validated_data.items():
            menu[key] = val
        menu["updated_at"] = datetime.now().isoformat()
        save_item("navigation_menus", menu)
        return Response(menu, status=status.HTTP_200_OK)

    def update(self, request, pk=None):
        return self.partial_update(request, pk)

    def destroy(self, request, pk=None):
        soft_delete_item_by_id("navigation_menus", pk)
        return Response({"detail": "Navigation Menu item soft-deleted successfully."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="restore")
    def restore(self, request, pk=None):
        restore_item_by_id("navigation_menus", pk)
        return Response({"detail": "Navigation Menu item successfully restored."}, status=status.HTTP_200_OK)


class ThemeViewSet(BasePortfolioViewSet):
    """
    ViewSet for flat Website Theme customization.
    """
    required_permissions = {
        "list": "portfolio:website:view",
        "retrieve": "portfolio:website:view",
        "create": "portfolio:website:create",
        "update": "portfolio:website:update",
        "partial_update": "portfolio:website:update",
        "destroy": "portfolio:website:delete",
        "restore": "portfolio:website:update",
    }

    def list(self, request):
        themes = get_collection("themes", include_deleted=True)
        themes = self.filter_and_search(themes, request, search_fields=["name"], filter_keys=["website_id", "theme_type"])

        paginator, page = self.paginate_list(request, themes)
        serializer = ThemeSerializer(page, many=True)
        if paginator:
            return paginator.get_paginated_response(serializer.data)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        theme = get_item_by_id("themes", pk)
        if not theme:
            return Response({"detail": "Theme not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response(theme, status=status.HTTP_200_OK)

    def partial_update(self, request, pk=None):
        theme = get_item_by_id("themes", pk)
        if not theme:
            return Response({"detail": "Theme not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = ThemeSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        for key, val in serializer.validated_data.items():
            theme[key] = val
        theme["updated_at"] = datetime.now().isoformat()
        save_item("themes", theme)
        return Response(theme, status=status.HTTP_200_OK)

    def update(self, request, pk=None):
        return self.partial_update(request, pk)

    def destroy(self, request, pk=None):
        soft_delete_item_by_id("themes", pk)
        return Response({"detail": "Theme soft-deleted successfully."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="restore")
    def restore(self, request, pk=None):
        restore_item_by_id("themes", pk)
        return Response({"detail": "Theme successfully restored."}, status=status.HTTP_200_OK)


class MediaItemViewSet(BasePortfolioViewSet):
    """
    ViewSet for flat Media Library files index.
    """
    required_permissions = {
        "list": "portfolio:website:view",
        "retrieve": "portfolio:website:view",
        "create": "portfolio:website:create",
        "update": "portfolio:website:update",
        "partial_update": "portfolio:website:update",
        "destroy": "portfolio:website:delete",
        "restore": "portfolio:website:update",
    }

    def list(self, request):
        media = get_collection("media_library", include_deleted=True)
        media = self.filter_and_search(media, request, search_fields=["name"], filter_keys=["website_id", "file_type"])

        paginator, page = self.paginate_list(request, media)
        serializer = MediaItemSerializer(page, many=True)
        if paginator:
            return paginator.get_paginated_response(serializer.data)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        item = get_item_by_id("media_library", pk)
        if not item:
            return Response({"detail": "Media asset not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response(item, status=status.HTTP_200_OK)

    def partial_update(self, request, pk=None):
        item = get_item_by_id("media_library", pk)
        if not item:
            return Response({"detail": "Media asset not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = MediaItemSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        for key, val in serializer.validated_data.items():
            item[key] = val
        item["updated_at"] = datetime.now().isoformat()
        save_item("media_library", item)
        return Response(item, status=status.HTTP_200_OK)

    def update(self, request, pk=None):
        return self.partial_update(request, pk)

    def destroy(self, request, pk=None):
        soft_delete_item_by_id("media_library", pk)
        return Response({"detail": "Media asset soft-deleted successfully."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="restore")
    def restore(self, request, pk=None):
        restore_item_by_id("media_library", pk)
        return Response({"detail": "Media asset successfully restored."}, status=status.HTTP_200_OK)


class SectionViewSet(BasePortfolioViewSet):
    """
    ViewSet for flat Section block updates.
    """
    required_permissions = {
        "list": "portfolio:website:view",
        "retrieve": "portfolio:website:view",
        "create": "portfolio:website:create",
        "update": "portfolio:website:update",
        "partial_update": "portfolio:website:update",
        "destroy": "portfolio:website:delete",
        "restore": "portfolio:website:update",
    }

    def list(self, request):
        sections = get_collection("sections", include_deleted=True)
        sections = self.filter_and_search(sections, request, search_fields=["title", "subtitle"], filter_keys=["page_id", "section_type", "is_active"])

        paginator, page = self.paginate_list(request, sections)
        serializer = SectionSerializer(page, many=True)
        if paginator:
            return paginator.get_paginated_response(serializer.data)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        section = get_item_by_id("sections", pk)
        if not section:
            return Response({"detail": "Section not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response(section, status=status.HTTP_200_OK)

    def partial_update(self, request, pk=None):
        section = get_item_by_id("sections", pk)
        if not section:
            return Response({"detail": "Section not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = SectionSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        for key, val in serializer.validated_data.items():
            section[key] = val
        section["updated_at"] = datetime.now().isoformat()
        save_item("sections", section)
        return Response(section, status=status.HTTP_200_OK)

    def update(self, request, pk=None):
        return self.partial_update(request, pk)

    def destroy(self, request, pk=None):
        soft_delete_item_by_id("sections", pk)
        return Response({"detail": "Section soft-deleted successfully."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="restore")
    def restore(self, request, pk=None):
        restore_item_by_id("sections", pk)
        return Response({"detail": "Section successfully restored."}, status=status.HTTP_200_OK)


class ResumeViewSet(BasePortfolioViewSet):
    required_permissions = {
        "list": "portfolio:website:view",
        "retrieve": "portfolio:website:view",
        "create": "portfolio:website:create",
        "update": "portfolio:website:update",
        "partial_update": "portfolio:website:update",
        "destroy": "portfolio:website:delete",
        "ats_score": "portfolio:website:view",
        "export_resume": "portfolio:website:view",
    }

    def list(self, request):
        resumes = get_collection("resumes")
        paginator, page = self.paginate_list(request, resumes)
        if paginator:
            return paginator.get_paginated_response(page)
        return Response(resumes, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        resume = get_item_by_id("resumes", pk)
        if not resume:
            return Response({"detail": "Resume not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response(resume, status=status.HTTP_200_OK)

    def create(self, request):
        serializer = ResumeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        item = {
            "id": str(uuid.uuid4()),
            "template_name": serializer.validated_data.get("template_name", "modern"),
            "data": serializer.validated_data.get("data", {}),
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "deleted_at": None
        }
        save_item("resumes", item)
        return Response(item, status=status.HTTP_201_CREATED)

    def partial_update(self, request, pk=None):
        resume = get_item_by_id("resumes", pk)
        if not resume:
            return Response({"detail": "Resume not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = ResumeSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        for key, val in serializer.validated_data.items():
            resume[key] = val
        resume["updated_at"] = datetime.now().isoformat()
        save_item("resumes", resume)
        return Response(resume, status=status.HTTP_200_OK)

    def update(self, request, pk=None):
        return self.partial_update(request, pk)

    def destroy(self, request, pk=None):
        soft_delete_item_by_id("resumes", pk)
        return Response({"detail": "Resume soft-deleted successfully."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="ats-score")
    def ats_score(self, request, pk=None):
        resume = get_item_by_id("resumes", pk)
        if not resume:
            return Response({"detail": "Resume not found."}, status=status.HTTP_404_NOT_FOUND)
        
        # Mock ATS analyzer
        resume_data = resume.get("data", {})
        skills = resume_data.get("skills", [])
        experience = resume_data.get("experience", [])
        
        score = 65
        feedback = ["Consider listing key tech stacks.", "Add descriptive action verbs in professional experience."]
        if len(skills) > 4:
            score += 15
            feedback.append("Excellent skills coverage.")
        if len(experience) > 1:
            score += 10
            feedback.append("Good professional history detail.")
            
        return Response({
            "ats_score": min(score, 100),
            "profile_gap_feedback": feedback,
            "ai_optimizer_recommendations": "Add certifications links to boost visibility by 20%."
        }, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="export")
    def export_resume(self, request, pk=None):
        resume = get_item_by_id("resumes", pk)
        if not resume:
            return Response({"detail": "Resume not found."}, status=status.HTTP_404_NOT_FOUND)
        
        export_format = request.data.get("format", "PDF").upper()
        return Response({
            "success": True,
            "export_format": export_format,
            "download_url": f"https://brahmavidya.galaxy/resumes/export/{pk}.{export_format.lower()}"
        }, status=status.HTTP_200_OK)


class JobListingViewSet(BasePortfolioViewSet):
    required_permissions = {
        "list": "portfolio:website:view",
        "retrieve": "portfolio:website:view",
        "create": "portfolio:website:create",
        "update": "portfolio:website:update",
        "partial_update": "portfolio:website:update",
        "destroy": "portfolio:website:delete",
        "apply": "portfolio:website:view",
    }

    def list(self, request):
        jobs = get_collection("jobs")
        paginator, page = self.paginate_list(request, jobs)
        if paginator:
            return paginator.get_paginated_response(page)
        return Response(jobs, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        job = get_item_by_id("jobs", pk)
        if not job:
            return Response({"detail": "Job not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response(job, status=status.HTTP_200_OK)

    def create(self, request):
        serializer = JobListingSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        item = {
            "id": str(uuid.uuid4()),
            "title": serializer.validated_data["title"],
            "company_name": serializer.validated_data["company_name"],
            "description": serializer.validated_data["description"],
            "location": serializer.validated_data.get("location", "Remote"),
            "job_type": serializer.validated_data.get("job_type", "FULL_TIME"),
            "salary_range": serializer.validated_data.get("salary_range", "Competitive"),
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "deleted_at": None
        }
        save_item("jobs", item)
        return Response(item, status=status.HTTP_201_CREATED)

    def partial_update(self, request, pk=None):
        job = get_item_by_id("jobs", pk)
        if not job:
            return Response({"detail": "Job not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = JobListingSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        for key, val in serializer.validated_data.items():
            job[key] = val
        job["updated_at"] = datetime.now().isoformat()
        save_item("jobs", job)
        return Response(job, status=status.HTTP_200_OK)

    def update(self, request, pk=None):
        return self.partial_update(request, pk)

    def destroy(self, request, pk=None):
        soft_delete_item_by_id("jobs", pk)
        return Response({"detail": "Job listing archived successfully."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="apply")
    def apply(self, request, pk=None):
        job = get_item_by_id("jobs", pk)
        if not job:
            return Response({"detail": "Job listing not found."}, status=status.HTTP_404_NOT_FOUND)
        
        return Response({
            "success": True,
            "job_id": pk,
            "candidate_user": str(request.user.id),
            "application_status": "SUBMITTED",
            "message": f"Successfully applied to {job.get('title')} at {job.get('company_name')}."
        }, status=status.HTTP_201_CREATED)


class CareerRoadmapViewSet(BasePortfolioViewSet):
    required_permissions = {
        "list": "portfolio:website:view",
        "retrieve": "portfolio:website:view",
        "create": "portfolio:website:create",
        "update": "portfolio:website:update",
        "partial_update": "portfolio:website:update",
        "destroy": "portfolio:website:delete",
    }

    def list(self, request):
        roadmaps = get_collection("roadmaps")
        paginator, page = self.paginate_list(request, roadmaps)
        if paginator:
            return paginator.get_paginated_response(page)
        return Response(roadmaps, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        roadmap = get_item_by_id("roadmaps", pk)
        if not roadmap:
            return Response({"detail": "Roadmap not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response(roadmap, status=status.HTTP_200_OK)

    def create(self, request):
        serializer = CareerRoadmapSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        item = {
            "id": str(uuid.uuid4()),
            "title": serializer.validated_data["title"],
            "description": serializer.validated_data["description"],
            "milestones": serializer.validated_data.get("milestones", []),
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "deleted_at": None
        }
        save_item("roadmaps", item)
        return Response(item, status=status.HTTP_201_CREATED)

    def partial_update(self, request, pk=None):
        roadmap = get_item_by_id("roadmaps", pk)
        if not roadmap:
            return Response({"detail": "Roadmap not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = CareerRoadmapSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        for key, val in serializer.validated_data.items():
            roadmap[key] = val
        roadmap["updated_at"] = datetime.now().isoformat()
        save_item("roadmaps", roadmap)
        return Response(roadmap, status=status.HTTP_200_OK)

    def update(self, request, pk=None):
        return self.partial_update(request, pk)

    def destroy(self, request, pk=None):
        soft_delete_item_by_id("roadmaps", pk)
        return Response({"detail": "Career roadmap deleted successfully."}, status=status.HTTP_200_OK)


class AICareerAssistantViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=["post"], url_path="mock-interview")
    def mock_interview(self, request):
        role = request.data.get("role", "Software Engineer")
        skill_level = request.data.get("level", "Junior")
        
        return Response({
            "role": role,
            "level": skill_level,
            "mock_questions": [
                f"Explain how you design a modular architecture for a {role} system.",
                "How do you handle race conditions in database transaction locks?",
                "What is your strategy for optimizing API response latencies?"
            ],
            "ai_evaluator_guidelines": "Highlight dynamic programming, selective DB indexes, and CDN edge caches."
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"], url_path="analyze-gap")
    def analyze_gap(self, request):
        target_role = request.data.get("target_role", "AI Architect")
        user_skills = request.data.get("skills", [])
        
        gaps = ["Deep Learning Models Tuning", "Infrastructure Orchestration"]
        recommendations = ["Complete BrahmaVidya Quantum Neural Nets Course", "Build 2 Kubernetes automation projects"]
        
        return Response({
            "target_role": target_role,
            "ats_compatibility_score": 72.5,
            "skills_gaps_identified": gaps,
            "learning_path_recommendations": recommendations
        }, status=status.HTTP_200_OK)
