import os
import json
import uuid
import threading
from datetime import datetime, date

DATA_FILE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "publishing_store.json")
_lock = threading.Lock()

class DateTimeEncoder(json.JSONEncoder):
    """
    JSON encoder that serializes datetime, date, and UUID objects cleanly.
    """
    def default(self, obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        if isinstance(obj, uuid.UUID):
            return str(obj)
        return super().default(obj)

def get_initial_publishing_store():
    return {
        "publishing_configs": {
            "site-1": {
                "website_id": "site-1",
                "is_private": False,
                "password_protected": False,
                "password_hash": None,
                "is_maintenance": False,
                "is_suspended": False,
                "rate_limit_rpm": 60,
                "suspended_reason": "",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
        },
        "website_versions": [
            {
                "id": "ver-101",
                "website_id": "site-1",
                "version_number": 1,
                "description": "Initial Stable Pre-seed Release",
                "snapshot": {
                    "website": {
                        "id": "site-1",
                        "name": "Official BrahmaVidya Galaxy Hub",
                        "subdomain": "creative",
                        "custom_domain": "portfolio.brahmavidya.edu",
                        "status": "published"
                    },
                    "pages": [
                        {"id": "page-1", "slug": "home", "title": "Home", "page_type": "home", "is_published": True, "display_order": 1}
                    ]
                },
                "created_by": "1",
                "created_at": datetime.now().isoformat()
            }
        ],
        "analytics_events": [
            {
                "id": "event-1",
                "website_id": "site-1",
                "page_id": "page-1",
                "path": "/home",
                "visitor_id": "visitor-999",
                "ip_address": "127.0.0.1",
                "device": "desktop",
                "browser": "Chrome",
                "country": "India",
                "referrer": "https://google.com",
                "created_at": datetime.now().isoformat()
            }
        ],
        "form_submissions": [
            {
                "id": "form-1",
                "website_id": "site-1",
                "form_type": "contact",
                "data": {
                    "name": "Siddharth Gautam",
                    "email": "siddharth@galaxy.edu",
                    "message": "Interested in partnering for smart auditing workflows."
                },
                "is_spam": False,
                "spam_score": 0.05,
                "created_at": datetime.now().isoformat()
            }
        ],
        "subdomain_reservations": {
            "creative": {
                "subdomain": "creative",
                "website_id": "site-1",
                "reserved_by": "1",
                "is_active": True,
                "created_at": datetime.now().isoformat()
            }
        }
    }

def read_publishing_store():
    """
    Safely load the JSON store from disk with thread locking.
    """
    with _lock:
        if not os.path.exists(DATA_FILE_PATH):
            initial = get_initial_publishing_store()
            with open(DATA_FILE_PATH, "w") as f:
                json.dump(initial, f, cls=DateTimeEncoder, indent=2)
            return initial
        try:
            with open(DATA_FILE_PATH, "r") as f:
                data = json.load(f)
                initial = get_initial_publishing_store()
                for key, val in initial.items():
                    if key not in data:
                        data[key] = val
                return data
        except Exception:
            return get_initial_publishing_store()

def write_publishing_store(data):
    """
    Safely persist the JSON store to disk with thread locking.
    """
    with _lock:
        try:
            with open(DATA_FILE_PATH, "w") as f:
                json.dump(data, f, cls=DateTimeEncoder, indent=2)
        except Exception as e:
            print(f"Error writing to publishing_store.json: {e}")

# Reusable CRUD helpers for publishing

def get_pub_collection(col_name: str) -> list:
    store = read_publishing_store()
    items = store.get(col_name)
    if isinstance(items, dict):
        return list(items.values())
    return items or []

def get_pub_item_by_key(col_name: str, key: str) -> dict:
    store = read_publishing_store()
    col = store.get(col_name, {})
    if isinstance(col, dict):
        return col.get(str(key))
    elif isinstance(col, list):
        for item in col:
            if item.get("id") == str(key):
                return item
    return None

def save_pub_item(col_name: str, key: str, item_data: dict):
    store = read_publishing_store()
    if isinstance(store.get(col_name), dict):
        store[col_name][str(key)] = item_data
    elif isinstance(store.get(col_name), list):
        # Update or append
        col_list = store[col_name]
        updated = False
        for idx, item in enumerate(col_list):
            if item.get("id") == str(key):
                col_list[idx] = item_data
                updated = True
                break
        if not updated:
            col_list.append(item_data)
    write_publishing_store(store)
