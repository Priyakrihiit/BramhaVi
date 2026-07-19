# Django Application Structure - BrahmaVidya Galaxy

## 1. Django Monolithic / Apps Design
When building or migrating BrahmaVidya Galaxy to a Python/Django backend, we structure the project using **Django REST Framework (DRF)**. To maintain modularity, the system is separated into dedicated Django apps:

```
/django_project (Django Root)
├── manage.py
├── /galaxy_core                # Project configurations and global settings
│   ├── settings.py             # Security, databases, and middleware
│   ├── urls.py                 # Global route register
│   └── wsgi.py
│
├── /apps
│   ├── /identity               # Custom User, Role, and Permission models
│   ├── /cms                    # Pages, layouts (JSONB), and recursive Menus
│   ├── /lms                    # Recursive CourseStructures and Progress logs
│   ├── /certificates           # Cryptographic signing and QR codes
│   └── /finance                # Wallet ledgers and split logic
```

---

## 2. Core App Layout & Architecture

Each subsystem app under `/apps` implements a clean separation of concerns:

```
/apps/[app_name]
├── models.py           # Database entity declarations
├── serializers.py      # Translates database rows into validated JSON formats
├── views.py            # Route controllers parsing requests and applying logic
├── permissions.py      # Overrides DRF BasePermission to perform RBAC validation
├── urls.py             # Maps endpoint strings to view methods
└── services.py         # Encapsulates business actions (e.g., calling Gemini SDK)
```

---

## 3. Implementation Code Patterns (Django & DRF)

### 3.1 JSONB Database Fields (LMS / CMS App)
To implement our flexible layouts and structures in Python, we utilize PostgreSQL's native JSONB field integrations:
```python
# apps/cms/models.py
from django.db import models
from django.db.models import JSONField

class Page(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    layout_data = JSONField(default=list)  # Direct storage for LayoutBlock structures
    seo_title = models.CharField(max_length=255, blank=True, null=True)
    seo_description = models.TextField(blank=True, null=True)
    keywords = models.TextField(blank=True, null=True) # Comma-separated SEO tags
    is_published = models.BooleanField(default=False)
```

### 3.2 Dynamic RBAC Authorization Classes (DRF)
We override DRF permissions to validate session roles against system permissions dynamically:
```python
# apps/identity/permissions.py
from rest_framework import permissions

class HasGranularPermission(permissions.BasePermission):
    def __init__(self, required_permission):
        self.required_permission = required_permission

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        # Retrieve all permissions assigned to the user's role
        user_permissions = user.role.permissions.values_list('code', flat=True)
        return self.required_permission in user_permissions
```

### 3.3 Serializers for Nested Recursive Models (CMS App)
For recursive navigation trees, DRF serializers can render nested structural hierarchies:
```python
# apps/cms/serializers.py
from rest_framework import serializers
from .models import NavigationMenu

class NavigationMenuSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = NavigationMenu
        fields = ['id', 'title', 'url', 'icon', 'display_order', 'required_permission', 'children']

    def get_children(self, obj):
        # Fetch submenu items recursively
        serializer = NavigationMenuSerializer(obj.children.all(), many=True)
        return serializer.data
```
This architecture mirrors our Node.js design perfectly while utilizing the strength of Django's native ORM.
