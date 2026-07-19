# Enterprise DAM Developer Guide

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
  │   └── mediaApi.ts # API fetch clients
  └── components/cms/ # Modular view panels
```

## 2. Dynamic Antivirus Scans
Antivirus scanning is mocked inside `scan_file_for_virus_task` in `tasks.py`. To plug in an active AV scanner, overwrite the method body with direct HTTP/CLI calls.
