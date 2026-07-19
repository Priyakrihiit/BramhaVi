import os
import sys
import urllib.request
import urllib.error
import json

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
            return res.status, json.loads(res.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        try:
            err_data = json.loads(e.read().decode("utf-8"))
        except:
            err_data = e.reason
        return e.code, err_data
    except Exception as e:
        return 500, str(e)

def run_tests():
    print("--- STARTING SPRINT 15 ENTERPRISE CMS INTEGRATION TESTS ---")
    
    # 1. Authenticate Admin user
    print("1. Authenticating Admin user...")
    status, res_admin = make_request("/api/v1/users/users/login/", "POST", {
        "email": "admin@brahmavidya.edu",
        "password": "adminpassword123"
    })
    assert status == 200, f"Login failed: {res_admin}"
    token = res_admin.get("token")
    print("   Login successful.")

    # 2. Check Categories list
    print("2. Verifying Categories list (GET /api/v1/cms/categories/)...")
    status, categories = make_request("/api/v1/cms/categories/", "GET", token=token)
    assert status == 200, f"Failed: {categories}"
    print("   Categories retrieved successfully.")

    # 3. Create Article draft
    print("3. Creating Article draft (POST /api/v1/cms/articles/)...")
    status, article = make_request("/api/v1/cms/articles/", "POST", {
        "title": "Vedic Science Insights",
        "slug": f"vedic-science-insights-{os.getpid()}",
        "body": "Introductory notes on Vedic studies.",
        "excerpt": "Short summary.",
        "status": "draft"
    }, token=token)
    assert status == 201, f"Failed: {article}"
    article_id = article.get("id")
    print(f"   Article draft created. ID: {article_id}")

    # 4. Publish Article
    print("4. Publishing Article (POST /api/v1/cms/articles/{id}/publish/)...")
    status, pub_res = make_request(f"/api/v1/cms/articles/{article_id}/publish/", "POST", token=token)
    assert status == 200, f"Failed: {pub_res}"
    assert pub_res.get("is_published") == True, "Article failed to publish."
    print("   Article published successfully.")

    # 5. Check Search Index
    print("5. Verifying Search Index (GET /api/v1/cms/search/)...")
    status, search_res = make_request("/api/v1/cms/search/", "GET", token=token)
    assert status == 200, f"Failed: {search_res}"
    print("   Search index retrieved successfully.")

    print("--- SPRINT 15 ENTERPRISE CMS INTEGRATION TESTS PASSED ---")

if __name__ == "__main__":
    run_tests()
