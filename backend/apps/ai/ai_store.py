import os
import json
import uuid
import threading
from datetime import datetime, date

DATA_FILE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ai_store.json")
_lock = threading.Lock()

class DateTimeEncoder(json.JSONEncoder):
    """
    JSON encoder that serializes datetime and UUID objects cleanly.
    """
    def default(self, obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        if isinstance(obj, uuid.UUID):
            return str(obj)
        return super().default(obj)

def get_default_models():
    """
    Initial seed for available AI models.
    """
    return [
        {
            "id": "gemini-1.5-pro",
            "name": "Gemini 1.5 Pro",
            "provider": "Gemini",
            "is_active": True,
            "is_default": True,
            "context_window": 2000000,
            "max_tokens": 8192,
            "default_temperature": 0.7,
            "pricing_metadata": {
                "prompt_token_rate": 0.00000125,
                "completion_token_rate": 0.00000375
            },
            "status": "ACTIVE"
        },
        {
            "id": "gemini-1.5-flash",
            "name": "Gemini 1.5 Flash",
            "provider": "Gemini",
            "is_active": True,
            "is_default": False,
            "context_window": 1000000,
            "max_tokens": 8192,
            "default_temperature": 1.0,
            "pricing_metadata": {
                "prompt_token_rate": 0.000000075,
                "completion_token_rate": 0.0000003
            },
            "status": "ACTIVE"
        },
        {
            "id": "gpt-4o",
            "name": "GPT-4o",
            "provider": "GPT",
            "is_active": True,
            "is_default": False,
            "context_window": 1280000,
            "max_tokens": 4096,
            "default_temperature": 0.7,
            "pricing_metadata": {
                "prompt_token_rate": 0.000005,
                "completion_token_rate": 0.000015
            },
            "status": "ACTIVE"
        },
        {
            "id": "claude-3-5-sonnet",
            "name": "Claude 3.5 Sonnet",
            "provider": "Claude",
            "is_active": True,
            "is_default": False,
            "context_window": 200000,
            "max_tokens": 8192,
            "default_temperature": 0.7,
            "pricing_metadata": {
                "prompt_token_rate": 0.000003,
                "completion_token_rate": 0.000015
            },
            "status": "ACTIVE"
        },
        {
            "id": "llama-3-70b",
            "name": "Llama 3 70B",
            "provider": "Open Source Models",
            "is_active": True,
            "is_default": False,
            "context_window": 8192,
            "max_tokens": 2048,
            "default_temperature": 0.6,
            "pricing_metadata": {
                "prompt_token_rate": 0.0000005,
                "completion_token_rate": 0.0000008
            },
            "status": "ACTIVE"
        },
        {
            "id": "mistral-large",
            "name": "Mistral Large",
            "provider": "Open Source Models",
            "is_active": True,
            "is_default": False,
            "context_window": 32768,
            "max_tokens": 4096,
            "default_temperature": 0.7,
            "pricing_metadata": {
                "prompt_token_rate": 0.000002,
                "completion_token_rate": 0.000006
            },
            "status": "ACTIVE"
        }
    ]

def get_default_prompts():
    """
    Initial seed for the enterprise prompt library covering all categories.
    """
    categories = [
        "Education", "Programming", "Resume", "Portfolio", "Career",
        "Translation", "Business", "Marketing", "Blog Writing", "Research",
        "Mathematics", "Science"
    ]
    prompts = []
    for i, category in enumerate(categories):
        prompts.append({
            "id": str(uuid.UUID(int=i + 1)),
            "title": f"Ultimate {category} Guide",
            "prompt_text": f"You are an expert assistant specialized in {category}. Please provide a comprehensive overview and answer the user's specific request using structured analysis, clear explanations, and professional recommendations.",
            "category": category,
            "version": "1.0.0",
            "is_active": True,
            "is_public": True,
            "is_favorite": i % 3 == 0,
            "owner_id": None,
            "created_at": datetime.now().isoformat()
        })
    return prompts

def get_initial_store():
    return {
        "conversations": {},
        "messages": {},
        "feedback": {},
        "prompts": {p["id"]: p for p in get_default_prompts()},
        "models": {m["id"]: m for m in get_default_models()},
        "sessions": {},
        "usage_tracking": []
    }

def read_store():
    """
    Safely load the JSON store from disk with thread locking.
    """
    with _lock:
        if not os.path.exists(DATA_FILE_PATH):
            initial = get_initial_store()
            with open(DATA_FILE_PATH, "w") as f:
                json.dump(initial, f, cls=DateTimeEncoder, indent=2)
            return initial
        try:
            with open(DATA_FILE_PATH, "r") as f:
                data = json.load(f)
                # Ensure all root tables exist
                initial = get_initial_store()
                for key, val in initial.items():
                    if key not in data:
                        data[key] = val
                return data
        except Exception:
            return get_initial_store()

def write_store(data):
    """
    Safely persist the JSON store to disk with thread locking.
    """
    with _lock:
        try:
            with open(DATA_FILE_PATH, "w") as f:
                json.dump(data, f, cls=DateTimeEncoder, indent=2)
        except Exception as e:
            print(f"Error writing to ai_store.json: {e}")

# ==========================================
# DATA ACCESS INTERFACES (CRUD)
# ==========================================

# Conversations
def get_conversations(user_id=None, include_archived=False, include_deleted=False) -> list:
    store = read_store()
    convs = list(store["conversations"].values())
    if user_id:
        convs = [c for c in convs if str(c.get("user_id")) == str(user_id)]
    if not include_archived:
        convs = [c for c in convs if not c.get("is_archived", False)]
    if not include_deleted:
        convs = [c for c in convs if not c.get("is_deleted", False)]
    return convs

def get_conversation_by_id(id_str: str) -> dict:
    store = read_store()
    return store["conversations"].get(str(id_str))

def save_conversation(conv_data: dict):
    store = read_store()
    c_id = str(conv_data["id"])
    store["conversations"][c_id] = conv_data
    write_store(store)

    try:
        from apps.search.tasks import index_ai_item_task
        index_ai_item_task.delay("conversations", c_id)
    except Exception as e:
        print(f"Failed to dispatch conversation index task: {e}")

def delete_conversation_by_id(id_str: str) -> bool:
    store = read_store()
    c_id = str(id_str)
    if c_id in store["conversations"]:
        store["conversations"][c_id]["is_deleted"] = True
        store["conversations"][c_id]["updated_at"] = datetime.now().isoformat()
        write_store(store)

        try:
            from apps.search.tasks import index_ai_item_task
            index_ai_item_task.delay("conversations", c_id)
        except Exception as e:
            print(f"Failed to dispatch conversation delete task: {e}")
        return True
    return False

# Messages
def get_messages_for_conversation(conv_id_str: str) -> list:
    store = read_store()
    msgs = list(store["messages"].values())
    filtered = [m for m in msgs if str(m.get("conversation_id")) == str(conv_id_str)]
    return sorted(filtered, key=lambda x: x.get("created_at", ""))

def get_message_by_id(msg_id_str: str) -> dict:
    store = read_store()
    return store["messages"].get(str(msg_id_str))

def save_message(msg_data: dict):
    store = read_store()
    m_id = str(msg_data["id"])
    store["messages"][m_id] = msg_data
    write_store(store)

# Feedback
def get_all_feedback() -> list:
    store = read_store()
    return list(store["feedback"].values())

def get_feedback_for_message(msg_id_str: str) -> dict:
    store = read_store()
    for f in store["feedback"].values():
        if str(f.get("message_id")) == str(msg_id_str):
            return f
    return None

def save_feedback(feedback_data: dict):
    store = read_store()
    f_id = str(feedback_data["id"])
    store["feedback"][f_id] = feedback_data
    write_store(store)

# Prompt Templates
def get_all_prompts(user_id=None, include_private=False) -> list:
    store = read_store()
    prompts = list(store["prompts"].values())
    if not include_private:
        # public or owned by user
        prompts = [p for p in prompts if p.get("is_public") or (user_id and str(p.get("owner_id")) == str(user_id))]
    elif user_id:
        prompts = [p for p in prompts if p.get("is_public") or str(p.get("owner_id")) == str(user_id)]
    return prompts

def get_prompt_by_id(id_str: str) -> dict:
    store = read_store()
    return store["prompts"].get(str(id_str))

def save_prompt(prompt_data: dict):
    store = read_store()
    p_id = str(prompt_data["id"])
    store["prompts"][p_id] = prompt_data
    write_store(store)

    try:
        from apps.search.tasks import index_ai_item_task
        index_ai_item_task.delay("prompts", p_id)
    except Exception as e:
        print(f"Failed to dispatch prompt index task: {e}")

def delete_prompt_by_id(id_str: str) -> bool:
    store = read_store()
    p_id = str(id_str)
    if p_id in store["prompts"]:
        del store["prompts"][p_id]
        write_store(store)

        try:
            from apps.search.tasks import index_ai_item_task
            index_ai_item_task.delay("prompts", p_id)
        except Exception as e:
            print(f"Failed to dispatch prompt delete task: {e}")
        return True
    return False

# AI Models
def get_all_models() -> list:
    store = read_store()
    return list(store["models"].values())

def get_model_by_id(id_str: str) -> dict:
    store = read_store()
    return store["models"].get(str(id_str))

def save_model(model_data: dict):
    store = read_store()
    m_id = str(model_data["id"])
    store["models"][m_id] = model_data
    write_store(store)

def delete_model_by_id(id_str: str) -> bool:
    store = read_store()
    m_id = str(id_str)
    if m_id in store["models"]:
        del store["models"][m_id]
        write_store(store)
        return True
    return False

# Sessions
def get_session_by_id(sess_id_str: str) -> dict:
    store = read_store()
    return store["sessions"].get(str(sess_id_str))

def get_user_sessions(user_id: str) -> list:
    store = read_store()
    return [s for s in store["sessions"].values() if str(s.get("user_id")) == str(user_id)]

def save_session(sess_data: dict):
    store = read_store()
    s_id = str(sess_data["id"])
    store["sessions"][s_id] = sess_data
    write_store(store)

# Usage Tracking
def log_usage(usage_record: dict):
    store = read_store()
    store["usage_tracking"].append(usage_record)
    write_store(store)

def get_all_usage() -> list:
    store = read_store()
    return store["usage_tracking"]
