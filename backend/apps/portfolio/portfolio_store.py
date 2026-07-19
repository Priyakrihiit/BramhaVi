import os
import json
import uuid
import threading
from datetime import datetime, date

DATA_FILE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "portfolio_store.json")
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

def get_default_themes():
    """
    Initial pre-seeded creative themes for website customization.
    """
    return [
        {
            "id": "theme-100",
            "website_id": "site-1",
            "name": "Minimalist Light",
            "theme_type": "light",
            "primary_color": "#1A1A1A",
            "secondary_color": "#4A4A4A",
            "background_color": "#FAFAFA",
            "text_color": "#212121",
            "font_family_sans": "Inter",
            "font_family_heading": "Outfit",
            "layout_style": "clean-grid",
            "animation_settings": {
                "hover_transition": "all 0.2s ease-in-out",
                "fade_in_delay_ms": 150
            },
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "deleted_at": None
        },
        {
            "id": "theme-101",
            "website_id": "site-1",
            "name": "Cybernetic Indigo",
            "theme_type": "dark",
            "primary_color": "#6366F1",
            "secondary_color": "#A5B4FC",
            "background_color": "#0F172A",
            "text_color": "#F8FAFC",
            "font_family_sans": "Fira Code",
            "font_family_heading": "Space Grotesk",
            "layout_style": "bento-box",
            "animation_settings": {
                "hover_transition": "all 0.3s cubic-bezier(0.4, 0, 0.2, 1)",
                "fade_in_delay_ms": 200
            },
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "deleted_at": None
        }
    ]

def get_default_media_library():
    """
    Initial pre-seeded media items across images, videos, PDFs, icons, and logos.
    """
    return [
        {
            "id": "media-201",
            "website_id": "site-1",
            "name": "profile_avatar.png",
            "file_type": "image",
            "file_size": 154200,
            "url": "https://brahmavidya.edu/assets/profile_avatar.png",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "deleted_at": None
        },
        {
            "id": "media-202",
            "website_id": "site-1",
            "name": "professional_resume_2026.pdf",
            "file_type": "pdf",
            "file_size": 450800,
            "url": "https://brahmavidya.edu/assets/professional_resume_2026.pdf",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "deleted_at": None
        },
        {
            "id": "media-203",
            "website_id": "site-1",
            "name": "galaxy_brand_logo.svg",
            "file_type": "logo",
            "file_size": 24500,
            "url": "https://brahmavidya.edu/assets/galaxy_brand_logo.svg",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "deleted_at": None
        }
    ]

def get_default_navigation():
    """
    Hierarchical primary and nested dropdown menus.
    """
    return [
        {
            "id": "nav-1",
            "website_id": "site-1",
            "parent_id": None,
            "label": "Home",
            "url": "/",
            "icon": "home",
            "display_order": 1,
            "is_visible": True,
            "is_external": False,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "deleted_at": None
        },
        {
            "id": "nav-2",
            "website_id": "site-1",
            "parent_id": None,
            "label": "About",
            "url": "/about",
            "icon": "user",
            "display_order": 2,
            "is_visible": True,
            "is_external": False,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "deleted_at": None
        },
        {
            "id": "nav-3",
            "website_id": "site-1",
            "parent_id": None,
            "label": "Works",
            "url": "/portfolio",
            "icon": "briefcase",
            "display_order": 3,
            "is_visible": True,
            "is_external": False,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "deleted_at": None
        },
        {
            "id": "nav-4",
            "website_id": "site-1",
            "parent_id": "nav-3",
            "label": "Case Studies",
            "url": "/portfolio/case-studies",
            "icon": "folder",
            "display_order": 1,
            "is_visible": True,
            "is_external": False,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "deleted_at": None
        },
        {
            "id": "nav-5",
            "website_id": "site-1",
            "parent_id": None,
            "label": "Contact",
            "url": "/contact",
            "icon": "mail",
            "display_order": 4,
            "is_visible": True,
            "is_external": False,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "deleted_at": None
        }
    ]

def get_default_sections():
    """
    Sections mapped across different pages.
    """
    return [
        {
            "id": "sec-301",
            "page_id": "page-1",  # Home
            "section_type": "hero",
            "title": "Welcome to BrahmaVidya Creative Nexus",
            "subtitle": "Engineering the Future of Blockchain and Academic Integrity",
            "content": {
                "cta_text": "Explore Portfolios",
                "cta_url": "/portfolio",
                "hero_image_url": "https://brahmavidya.edu/assets/hero_nebula.jpg",
                "layout_alignment": "center"
            },
            "display_order": 1,
            "is_active": True,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "deleted_at": None
        },
        {
            "id": "sec-302",
            "page_id": "page-1",  # Home
            "section_type": "services",
            "title": "Core Technical Services",
            "subtitle": "Comprehensive full-stack engineering, cloud deployments, and AI mentoring",
            "content": {
                "services_list": [
                    {"title": "Automated Smart Auditing", "icon": "shield", "description": "Analyzing solidity layouts for potential double-spend vulnerabilities."},
                    {"title": "Custom LMS Provisioning", "icon": "graduation-cap", "description": "Spinning up dedicated courseware portals in milliseconds."}
                ]
            },
            "display_order": 2,
            "is_active": True,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "deleted_at": None
        },
        {
            "id": "sec-303",
            "page_id": "page-2",  # About
            "section_type": "about",
            "title": "About Our Enterprise Hub",
            "subtitle": "Academic excellence backed by decentralized cryptographic consensus.",
            "content": {
                "about_body": "At BrahmaVidya Galaxy, we believe that academic and professional portfolios should be verifiable and expressive. Our platform combines web curation tools with decentralized cryptographic checks.",
                "founded_year": 2026,
                "team_size": 42
            },
            "display_order": 1,
            "is_active": True,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "deleted_at": None
        }
    ]

def get_default_pages():
    """
    Initial pre-seeded layout pages matching user catalog requirements.
    """
    pages_list = [
        ("Home", "home", "home"),
        ("About Me", "about", "about"),
        ("My Services", "services", "services"),
        ("Key Projects", "projects", "projects"),
        ("Skills Portfolio", "skills", "skills"),
        ("Work Experience", "experience", "experience"),
        ("Education History", "education", "education"),
        ("Pricing Guides", "pricing", "pricing"),
        ("Contact Forms", "contact", "contact")
    ]
    pages = []
    for i, (title, slug, page_type) in enumerate(pages_list):
        pages.append({
            "id": f"page-{i+1}",
            "website_id": "site-1",
            "slug": slug,
            "title": title,
            "page_type": page_type,
            "is_published": True,
            "display_order": i + 1,
            "seo": {
                "meta_title": f"{title} | BrahmaVidya Professional Hub",
                "meta_description": f"Explore our comprehensive academic review of {title} features and tools.",
                "keywords": f"academic, portfolio, {page_type}, brahmavidya",
                "opengraph_image": "https://brahmavidya.edu/assets/opengraph_default.png"
            },
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "deleted_at": None
        })
    return pages

def get_initial_store():
    return {
        "websites": {
            "site-1": {
                "id": "site-1",
                "user_id": "1", # generic seed user
                "name": "Official BrahmaVidya Galaxy Hub",
                "subdomain": "creative",
                "custom_domain": "portfolio.brahmavidya.edu",
                "status": "published",
                "footer_builder": {
                    "footer_columns": [
                        {"title": "Product", "links": [{"label": "Features", "url": "/features"}, {"label": "Pricing", "url": "/pricing"}]},
                        {"title": "Resources", "links": [{"label": "Documentation", "url": "/docs"}, {"label": "API Status", "url": "/status"}]}
                    ],
                    "copyright_text": "© 2026 BrahmaVidya Galaxy. All Rights Reserved.",
                    "social_icons": ["github", "twitter", "linkedin", "youtube"]
                },
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "deleted_at": None
            }
        },
        "pages": {p["id"]: p for p in get_default_pages()},
        "navigation_menus": {n["id"]: n for n in get_default_navigation()},
        "sections": {s["id"]: s for s in get_default_sections()},
        "themes": {t["id"]: t for t in get_default_themes()},
        "media_library": {m["id"]: m for m in get_default_media_library()}
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
            print(f"Error writing to portfolio_store.json: {e}")

# ==========================================
# REUSABLE GENERIC CRUD LAYER FOR PORTFOLIO
# ==========================================

def get_collection(collection_name: str, include_deleted=False) -> list:
    store = read_store()
    items = list(store.get(collection_name, {}).values())
    if not include_deleted:
        items = [i for i in items if i.get("deleted_at") is None]
    return items

def get_item_by_id(collection_name: str, id_str: str) -> dict:
    store = read_store()
    return store.get(collection_name, {}).get(str(id_str))

def save_item(collection_name: str, item_data: dict):
    store = read_store()
    if collection_name not in store:
        store[collection_name] = {}
    i_id = str(item_data["id"])
    store[collection_name][i_id] = item_data
    write_store(store)

    # Hook search indexing
    if collection_name in ["websites", "resumes", "jobs"]:
        try:
            from apps.search.tasks import index_portfolio_item_task
            index_portfolio_item_task.delay(collection_name, i_id)
        except Exception as e:
            print(f"Failed to dispatch portfolio index task: {e}")

def soft_delete_item_by_id(collection_name: str, id_str: str) -> bool:
    store = read_store()
    c_id = str(id_str)
    if c_id in store.get(collection_name, {}):
        store[collection_name][c_id]["deleted_at"] = datetime.now().isoformat()
        store[collection_name][c_id]["updated_at"] = datetime.now().isoformat()
        write_store(store)

        # Hook search indexing
        if collection_name in ["websites", "resumes", "jobs"]:
            try:
                from apps.search.tasks import index_portfolio_item_task
                index_portfolio_item_task.delay(collection_name, c_id)
            except Exception as e:
                print(f"Failed to dispatch portfolio delete task: {e}")
        return True
    return False

def restore_item_by_id(collection_name: str, id_str: str) -> bool:
    store = read_store()
    c_id = str(id_str)
    if c_id in store.get(collection_name, {}):
        store[collection_name][c_id]["deleted_at"] = None
        store[collection_name][c_id]["updated_at"] = datetime.now().isoformat()
        write_store(store)

        # Hook search indexing
        if collection_name in ["websites", "resumes", "jobs"]:
            try:
                from apps.search.tasks import index_portfolio_item_task
                index_portfolio_item_task.delay(collection_name, c_id)
            except Exception as e:
                print(f"Failed to dispatch portfolio restore task: {e}")
        return True
    return False

def hard_delete_item_by_id(collection_name: str, id_str: str) -> bool:
    store = read_store()
    c_id = str(id_str)
    if c_id in store.get(collection_name, {}):
        del store[collection_name][c_id]
        write_store(store)

        # Hook search indexing
        if collection_name in ["websites", "resumes", "jobs"]:
            try:
                import uuid
                from apps.search.tasks import delete_document_task
                doc_id = uuid.UUID(c_id) if len(c_id) == 36 else uuid.uuid5(uuid.NAMESPACE_DNS, c_id)
                delete_document_task.delay(collection_name, str(doc_id))
            except Exception as e:
                print(f"Failed to dispatch portfolio hard delete task: {e}")
        return True
    return False
