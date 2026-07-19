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
    print("--- STARTING SPRINT 16 ENTERPRISE DAM INTEGRATION TESTS ---")
    
    # 1. Authenticate Admin user
    print("1. Authenticating Admin user...")
    status, res_admin = make_request("/api/v1/users/users/login/", "POST", {
        "email": "admin@brahmavidya.edu",
        "password": "adminpassword123"
    })
    assert status == 200, f"Login failed: {res_admin}"
    token = res_admin.get("token")
    print("   Login successful.")

    # 2. Check Folders list
    print("2. Verifying Folders list (GET /api/v1/cms/folders/)...")
    status, folders = make_request("/api/v1/cms/folders/", "GET", token=token)
    assert status == 200, f"Failed: {folders}"
    print("   Folders retrieved successfully.")

    # 3. Create Folder
    print("3. Creating Folder (POST /api/v1/cms/folders/)...")
    status, new_folder = make_request("/api/v1/cms/folders/", "POST", {
        "name": "Math Homework Graphics"
    }, token=token)
    assert status == 201, f"Failed: {new_folder}"
    folder_id = new_folder.get("id")
    print(f"   Folder created. ID: {folder_id}")

    # 4. Check Collections list
    print("4. Verifying Collections list (GET /api/v1/cms/collections/)...")
    status, collections = make_request("/api/v1/cms/collections/", "GET", token=token)
    assert status == 200, f"Failed: {collections}"
    print("   Collections retrieved successfully.")

    print("--- SPRINT 16 ENTERPRISE DAM INTEGRATION TESTS PASSED ---")

if __name__ == "__main__":
    run_tests()
