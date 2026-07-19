# verify_sprint11.py
import os
import sys
import django
import urllib.request
import urllib.error
import json

sys.path.append(os.path.abspath("backend"))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "backend")))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_project.settings")
django.setup()

from django.contrib.auth import get_user_model
from apps.users.models import Role, Permission, RolePermission
from apps.lms.models import CourseStructure
from apps.cms.models import Blog
from apps.seo.models import SEOPage, SEOAudit

User = get_user_model()
base_url = "http://127.0.0.1:8000"

def make_request(path, method="GET", payload=None, token=None):
    url = f"{base_url}{path}"
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
        
    data = json.dumps(payload).encode("utf-8") if payload else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    
    try:
        with urllib.request.urlopen(req) as res:
            content_type = res.headers.get("Content-Type", "")
            if "application/xml" in content_type or "text/plain" in content_type:
                return res.status, res.read().decode("utf-8")
            return res.status, json.loads(res.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        try:
            err_data = json.loads(e.read().decode("utf-8"))
        except:
            err_data = e.reason
        return e.code, err_data
    except Exception as e:
        return 500, str(e)

def seed_sprint11_permissions():
    print("Seeding Sprint 11 SEO & Sitemap permissions...")
    roles = {
        "SUPERADMIN": ["seo:page:view", "seo:page:create", "seo:page:update", "seo:page:delete"],
        "ADMIN": ["seo:page:view", "seo:page:create", "seo:page:update", "seo:page:delete"],
        "TEACHER": ["seo:page:view"],
        "STUDENT": ["seo:page:view"]
    }
    for role_name, codenames in roles.items():
        try:
            role = Role.objects.get(name=role_name)
            for code in codenames:
                perm, _ = Permission.objects.get_or_create(codename=code, defaults={"description": f"Enables {code}"})
                RolePermission.objects.get_or_create(role=role, permission=perm)
        except Exception as e:
            print(f"Skipping role {role_name}: {e}")
    print("Seeding complete.")

def run_tests():
    print("--- STARTING SPRINT 11 SEO PLATFORM INTEGRATION TESTS ---")
    seed_sprint11_permissions()
    
    # 1. Authenticate users
    print("\n1. Authenticating Admin user...")
    status, res_admin = make_request("/api/v1/users/users/login/", "POST", {"email": "admin@brahmavidya.edu", "password": "adminpassword123"})
    admin_token = res_admin.get("token")
    assert status == 200

    # 2. SEO Page CRUD
    print("\n2. Verifying SEO Page Creation (POST /seo/pages/)...")
    # Clean up first
    SEOPage.objects.filter(page_id="course-101").delete()
    
    status, page = make_request("/api/v1/seo/pages/", "POST", {
        "page_type": "COURSE",
        "page_id": "course-101",
        "title": "Advanced Quantum Computing",
        "meta_title": "Quantum Mechanics & Computing Guide",
        "meta_description": "Learn quantum states, spin matrices, and qubits logic.",
        "keywords": "quantum, computing, physics",
        "schema_json": {"@type": "Course", "name": "Advanced Quantum Computing"}
    }, token=admin_token)
    print(f"Create SEO Page: Status {status}, ID: {page.get('id') if isinstance(page, dict) else None}")
    assert status == 201

    # 3. Retrieve SEO Audit
    print("\n3. Verifying SEO Page Audit (GET /seo/pages/audit/{page_id}/)...")
    status, audit = make_request(f"/api/v1/seo/pages/audit/course-101/", "GET", token=admin_token)
    print(f"SEO Page Audit: Status {status}, SEO Score: {audit.get('seo_score')}/100, Recommendations: {len(audit.get('recommendations', []))}")
    assert status == 200
    assert audit.get("seo_score") > 60

    # 4. Generate Meta AI Service
    print("\n4. Verifying AI Meta tags generation (POST /seo/generate-meta/)...")
    status, meta = make_request("/api/v1/seo/generate-meta/", "POST", {
        "page_type": "BLOG",
        "title": "Sanskrit Grammar structure for Lexers",
        "description": "Analyzing Paninian Ashtadhyayi sutras inside parsing compilation."
    }, token=admin_token)
    print(f"AI Meta Tags: Status {status}, Slug: {meta.get('slug')}, Meta Title: {meta.get('meta_title')}")
    assert status == 200
    assert "Sanskrit" in meta.get("meta_title")

    # 5. Generate Schema AI Service
    print("\n5. Verifying AI Schema.org structured data generation (POST /seo/generate-schema/)...")
    status, schema = make_request("/api/v1/seo/generate-schema/", "POST", {
        "schema_type": "Course",
        "name": "Introduction to Vedic Mathematics",
        "description": "Sutras of arithmetic multiplications and integration calculations."
    }, token=admin_token)
    print(f"AI Schema: Status {status}, Type: {schema.get('@type')}, Provider: {schema.get('provider', {}).get('name')}")
    assert status == 200
    assert schema.get("@type") == "Course"

    # 6. Verify Check SEO Analysis Endpoint
    print("\n6. Verifying SEO Check validation (POST /seo/check-seo/)...")
    status, check = make_request("/api/v1/seo/check-seo/", "POST", {
        "meta_title": "Vedic Code",
        "meta_description": "Vedic sutras calculations and system compiler design parameters guide.",
        "keywords": "vedic, math, code",
        "schema_json": {"@type": "Course"}
    }, token=admin_token)
    print(f"Check SEO: Status {status}, Score: {check.get('seo_score')}/100, Recommendations Count: {len(check.get('recommendations'))}")
    assert status == 200
    assert check.get("seo_score") >= 80

    # 7. XML Sitemap generation
    print("\n7. Verifying dynamic XML Sitemap (GET /seo/sitemap.xml)...")
    status, sitemap_xml = make_request("/seo/sitemap.xml", "GET")
    print(f"XML Sitemap: Status {status}, Sample slice: {sitemap_xml[:150]}")
    assert status == 200
    assert "urlset" in sitemap_xml

    # 8. Robots txt rules list
    print("\n8. Verifying dynamic Robots instruction guide (GET /robots.txt)...")
    status, robots_txt = make_request("/robots.txt", "GET")
    print(f"Robots Rules: Status {status}, content:\n{robots_txt}")
    assert status == 200
    assert "Disallow" in robots_txt

    # 9. Automatic SEO Updates Signals
    print("\n9. Verifying Automatic SEO trigger save signals on models...")
    # Add a course structure node to verify post_save signal
    CourseStructure.objects.filter(slug="auto-seo-signal-node").delete()
    
    course_node = CourseStructure.objects.create(
        node_type="COURSE",
        title="Automatic SEO Signals Test Course",
        slug="auto-seo-signal-node",
        description="Dynamic integration testing representing automatic SEO page creation signal triggers."
    )
    
    # Query corresponding SEOPage record automatically registered
    seo_page = SEOPage.objects.filter(page_id=str(course_node.id)).first()
    print(f"Automatic SEO record found: {seo_page is not None}")
    assert seo_page is not None
    print(f"Synchronized properties: Title: '{seo_page.title}', Meta Title: '{seo_page.meta_title}', Slug: '{seo_page.slug}'")
    assert seo_page.title == "Automatic SEO Signals Test Course"
    
    print("\n--- SPRINT 11 SEO PLATFORM INTEGRATION TESTS PASSED ---")

if __name__ == "__main__":
    run_tests()
