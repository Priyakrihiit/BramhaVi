import os
import json
import uuid
import threading
from datetime import datetime, date

DATA_FILE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "admin_store.json")
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

def get_initial_admin_store():
    return {
        "certificates": [
            {
                "id": "cert-1",
                "student_id": "std-101",
                "student_email": "student@brahmavidya.edu",
                "course_title": "Vedic Mathematics Masterclass",
                "issued_at": datetime.now().isoformat(),
                "certificate_url": "https://brahmavidya.edu/certificates/cert-1.pdf",
                "status": "ACTIVE",
                "deleted_at": None
            }
        ],
        "badges": [
            {
                "id": "badge-1",
                "student_id": "std-101",
                "name": "Brahma Pioneer",
                "description": "Awarded for completing the first subtopic assessment perfectly.",
                "icon": "Award",
                "awarded_at": datetime.now().isoformat(),
                "deleted_at": None
            }
        ],
        "coupons": [
            {
                "id": "coupon-1",
                "code": "GALAXY50",
                "discount_percentage": 50.00,
                "is_active": True,
                "expires_at": "2027-01-01T00:00:00",
                "deleted_at": None
            }
        ],
        "subscriptions": [
            {
                "id": "sub-1",
                "website_id": "site-1",
                "tier": "ENTERPRISE",
                "status": "ACTIVE",
                "price": 199.00,
                "billing_cycle": "monthly",
                "expires_at": "2027-07-07T00:00:00",
                "deleted_at": None
            }
        ],
        "ai_models": [
            {
                "id": "model-1",
                "name": "Gemini 1.5 Pro",
                "provider": "Google",
                "is_active": True,
                "token_limit": 1048576,
                "cost_per_million": 7.00,
                "average_response_time": 1.24,
                "deleted_at": None
            },
            {
                "id": "model-2",
                "name": "Gemini 1.5 Flash",
                "provider": "Google",
                "is_active": True,
                "token_limit": 1048576,
                "cost_per_million": 0.35,
                "average_response_time": 0.45,
                "deleted_at": None
            }
        ],
        "prompt_templates": [
            {
                "id": "prompt-1",
                "name": "Syllabus Summarizer",
                "system_instruction": "You are a professional Vedic academic summarizer.",
                "temperature": 0.4,
                "max_tokens": 2048,
                "deleted_at": None
            }
        ],
        "blocked_prompts": [
            {
                "id": "block-1",
                "phrase": "malicious injection query",
                "action": "BLOCK",
                "created_at": datetime.now().isoformat(),
                "deleted_at": None
            }
        ],
        "communities": [
            {
                "id": "comm-1",
                "name": "Sanskrit Scholars",
                "description": "A dedicated learning community for Sanskrit literature.",
                "member_count": 245,
                "is_active": True,
                "deleted_at": None
            }
        ],
        "moderation_queue": [
            {
                "id": "mod-1",
                "entity_type": "FORUM_POST",
                "entity_id": "post-99",
                "reported_by": "student@brahmavidya.edu",
                "reason": "Off-topic solicitation.",
                "status": "PENDING",
                "created_at": datetime.now().isoformat(),
                "deleted_at": None
            }
        ],
        "backups": [
            {
                "id": "backup-1",
                "backup_type": "DATABASE",
                "status": "COMPLETED",
                "file_size_mb": 145.2,
                "file_name": "backup_db_2026_07_07.sql.gz",
                "created_at": datetime.now().isoformat(),
                "deleted_at": None
            }
        ],
        "system_settings": {
            "platform_name": "BrahmaVidya Galaxy",
            "logo_url": "https://brahmavidya.edu/assets/logo.png",
            "favicon_url": "https://brahmavidya.edu/favicon.ico",
            "smtp_host": "smtp.brahmavidya.edu",
            "smtp_port": 587,
            "smtp_user": "no-reply@brahmavidya.edu",
            "sms_provider": "Twilio",
            "payment_gateway": "Stripe",
            "storage_provider": "Google Cloud Storage",
            "timezone": "Asia/Kolkata",
            "maintenance_mode": False,
            "feature_flags": {
                "enable_vidya_ai": True,
                "enable_wallet_withdrawals": False,
                "enable_portfolio_builder": True
            }
        },
        "notifications_history": [
            {
                "id": "notif-1",
                "channel": "EMAIL",
                "recipient": "all-users@brahmavidya.edu",
                "title": "Welcome to BrahmaVidya!",
                "message": "We have launched the new portfolio publishing systems.",
                "status": "SENT",
                "sent_at": datetime.now().isoformat(),
                "deleted_at": None
            }
        ],
        "blocked_words": ["spamword1", "inappropriatephrase"]
    }

def read_admin_store():
    """
    Safely load the JSON store from disk with thread locking.
    """
    with _lock:
        if not os.path.exists(DATA_FILE_PATH):
            initial = get_initial_admin_store()
            with open(DATA_FILE_PATH, "w") as f:
                json.dump(initial, f, cls=DateTimeEncoder, indent=2)
            return initial
        try:
            with open(DATA_FILE_PATH, "r") as f:
                data = json.load(f)
                initial = get_initial_admin_store()
                for key, val in initial.items():
                    if key not in data:
                        data[key] = val
                return data
        except Exception:
            return get_initial_admin_store()

def write_admin_store(data):
    """
    Safely persist the JSON store to disk with thread locking.
    """
    with _lock:
        try:
            with open(DATA_FILE_PATH, "w") as f:
                json.dump(data, f, cls=DateTimeEncoder, indent=2)
        except Exception as e:
            print(f"Error writing to admin_store.json: {e}")

def get_admin_collection(col_name: str) -> list:
    store = read_admin_store()
    return store.get(col_name, [])

def get_admin_item_by_key(col_name: str, key: str) -> dict:
    store = read_admin_store()
    col = store.get(col_name, [])
    for item in col:
        if item.get("id") == str(key):
            return item
    return None

def save_admin_item(col_name: str, key: str, item_data: dict):
    store = read_admin_store()
    col_list = store.get(col_name, [])
    updated = False
    for idx, item in enumerate(col_list):
        if item.get("id") == str(key):
            col_list[idx] = item_data
            updated = True
            break
    if not updated:
        col_list.append(item_data)
    store[col_name] = col_list
    write_admin_store(store)
