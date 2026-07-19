# CMS Developer Guide

## 1. Codebase Directories

```
backend/apps/cms/
  ├── models.py       # DB Table Entities
  ├── serializers.py  # Deserialization & validation
  ├── permissions.py  # RBAC, CBAC & overrides
  ├── views.py        # ViewSets & REST actions
  ├── urls.py         # Route maps
  └── signals.py      # Automations & integrations hooks
src/
  ├── services/
  │   └── cmsApi.ts   # API fetch clients
  └── components/cms/ # Modular view panels
```

## 2. Extending Permissions
Custom authorization classes reside in `permissions.py`. Check request rules or roles inside `has_permission` or `has_object_permission` override hooks.

## 3. Celery Development Settings
For development work without active Redis clusters, enforce synchronous executions inside `settings.py` by configuring `CELERY_TASK_ALWAYS_EAGER = True`.
