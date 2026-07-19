from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import HttpResponse
from apps.seo.models import SEOPage, SEOAudit
from apps.seo.serializers import SEOPageSerializer, SEOAuditSerializer
from apps.seo.services import AISEOService
from apps.seo.permissions import HasSEORBACPermission
import uuid

class SEOPageViewSet(viewsets.ModelViewSet):
    """
    Standard REST ViewSet handling CRUD operations on SEO pages.
    """
    queryset = SEOPage.objects.all().order_by("-created_at")
    serializer_class = SEOPageSerializer
    permission_classes = [HasSEORBACPermission]
    required_permissions = {
        "list": "seo:page:view",
        "retrieve": "seo:page:view",
        "create": "seo:page:create",
        "update": "seo:page:update",
        "partial_update": "seo:page:update",
        "destroy": "seo:page:delete",
    }

    @action(detail=False, methods=["get"], url_path="audit/(?P<page_id>[^/.]+)")
    def get_audit(self, request, page_id=None):
        def is_valid_uuid(val):
            try:
                uuid.UUID(str(val))
                return True
            except ValueError:
                return False

        page = None
        if is_valid_uuid(page_id):
            page = SEOPage.objects.filter(id=page_id).first()
        if not page:
            page = SEOPage.objects.filter(page_id=page_id).first()
        if not page:
            return Response({"detail": "SEO Page not found"}, status=status.HTTP_404_NOT_FOUND)
        
        # Calculate scores dynamically or check existing
        audit = SEOAudit.objects.filter(page=page).first()
        if not audit:
            seo_score = AISEOService.calculate_seo_score(
                page.meta_title, page.meta_description, page.keywords, page.schema_json
            )
            readability_score = 75
            recommendations = []
            if not page.meta_title or len(page.meta_title) < 10:
                recommendations.append("Increase length of meta title for improved search relevance.")
            if not page.meta_description or len(page.meta_description) < 50:
                recommendations.append("Add descriptive meta summary information.")
            if not page.schema_json:
                recommendations.append("Add Schema.org structured JSON-LD data to enable rich snippet previews.")

            audit = SEOAudit.objects.create(
                page=page,
                seo_score=seo_score,
                readability_score=readability_score,
                broken_links=[],
                duplicate_title=False,
                duplicate_description=False,
                missing_alt_images=0,
                missing_h1=False,
                missing_schema=not bool(page.schema_json),
                recommendations=recommendations
            )
        
        return Response(SEOAuditSerializer(audit).data, status=status.HTTP_200_OK)


class GenerateMetaAPIView(APIView):
    permission_classes = [HasSEORBACPermission]
    required_permission = "seo:page:view"

    def post(self, request):
        page_type = request.data.get("page_type", "WEBSITE")
        title = request.data.get("title", "")
        description = request.data.get("description", "")
        if not title:
            return Response({"title": ["This field is required."]}, status=status.HTTP_400_BAD_REQUEST)
        
        meta_title = AISEOService.generate_meta_title(page_type, title, description)
        meta_description = AISEOService.generate_meta_description(page_type, title, description)
        keywords = AISEOService.suggest_keywords(page_type, title, description)
        slug = AISEOService.generate_slug(title)
        
        return Response({
            "meta_title": meta_title,
            "meta_description": meta_description,
            "keywords": keywords,
            "slug": slug
        }, status=status.HTTP_200_OK)


class GenerateSchemaAPIView(APIView):
    permission_classes = [HasSEORBACPermission]
    required_permission = "seo:page:view"

    def post(self, request):
        schema_type = request.data.get("schema_type", "Website")
        name = request.data.get("name", "")
        description = request.data.get("description", "")
        url = request.data.get("url", "")
        extra_data = request.data.get("extra_data", {})
        if not name:
            return Response({"name": ["This field is required."]}, status=status.HTTP_400_BAD_REQUEST)

        schema = AISEOService.generate_schema_org(schema_type, name, description, url, extra_data)
        return Response(schema, status=status.HTTP_200_OK)


class CheckSEOAPIView(APIView):
    permission_classes = [HasSEORBACPermission]
    required_permission = "seo:page:view"

    def post(self, request):
        meta_title = request.data.get("meta_title", "")
        meta_description = request.data.get("meta_description", "")
        keywords = request.data.get("keywords", "")
        schema_json = request.data.get("schema_json", {})
        
        seo_score = AISEOService.calculate_seo_score(meta_title, meta_description, keywords, schema_json)
        readability_score = 80 if meta_description and len(meta_description) > 50 else 60
        recommendations = []
        if not meta_title or len(meta_title) < 10:
            recommendations.append("Title length is too short.")
        if not meta_description or len(meta_description) < 50:
            recommendations.append("Description needs more action verbs.")
        if not schema_json:
            recommendations.append("Missing structured schema.org data.")
            
        return Response({
            "seo_score": seo_score,
            "readability_score": readability_score,
            "duplicate_title": False,
            "duplicate_description": False,
            "missing_alt_images": 0,
            "missing_h1": False,
            "missing_schema": not bool(schema_json),
            "recommendations": recommendations
        }, status=status.HTTP_200_OK)


class SitemapXMLView(APIView):
    permission_classes = []  # Public

    def get(self, request):
        pages = SEOPage.objects.all()
        xml_lines = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        ]
        
        for p in pages:
            loc = p.canonical_url or f"https://brahmavidya.edu/{p.page_type.lower()}/{p.slug or p.id}"
            xml_lines.append("  <url>")
            xml_lines.append(f"    <loc>{loc}</loc>")
            xml_lines.append(f"    <lastmod>{p.updated_at.strftime('%Y-%m-%d')}</lastmod>")
            xml_lines.append("    <changefreq>daily</changefreq>")
            xml_lines.append("    <priority>0.8</priority>")
            xml_lines.append("  </url>")
            
        xml_lines.append('</urlset>')
        xml_content = "\n".join(xml_lines)
        return HttpResponse(xml_content, content_type="application/xml")


class RobotsTXTView(APIView):
    permission_classes = []  # Public

    def get(self, request):
        txt_content = (
            "User-agent: *\n"
            "Disallow: /api/v1/control-center/admin/\n"
            "Allow: /\n\n"
            "Sitemap: https://brahmavidya.edu/api/v1/seo/sitemap.xml\n"
        )
        return HttpResponse(txt_content, content_type="text/plain")
