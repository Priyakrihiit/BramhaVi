# BrahmaVidya Galaxy — Teacher Portal Walkthrough

This guide provides a walkthrough of the Teacher Portal integration features and verification steps.

---

## 1. Automated Verification Checkouts

The verification script `verify_sprint21.py` runs 11 integration test checkouts to validate the entire teacher workflow.

### 1.1. Running the Verification Script
To run the automated validation test suite:

```powershell
python -u -c "import os, sys, django; sys.path.append('backend'); os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_project.settings'); django.setup(); from django.conf import settings; settings.CELERY_TASK_ALWAYS_EAGER = True; settings.CELERY_ALWAYS_EAGER = True; import verify_sprint21; verify_sprint21.run_checks()"
```

---

## 2. Dynamic Integration Walkthrough

The script validates the following modules:

*   **LMS Grading**: Processes grade updates for student assignments and checks for proper database commits.
*   **CMS Promotion**: Promotes an announcement or class postponed notification to the global blog page.
*   **Analytics Tracking**: Records grading activity telemetry events in the analytics database.
*   **Multi-Channel Notification**: Automatically fires email alerts and in-app feeds to notify students of grading releases.
*   **Global Search Indexing**: Schedules a Celery worker task to re-index the course structure contents.
*   **AI Evaluation Assistant**: Calls the AI assistant mock module to calculate evaluation token costs.
*   **Wallet Credit**: Adds payout credit rewards to the teacher's wallet.
*   **Certificates**: Enqueues and generates dynamic completion transcripts.
*   **SEO Schema**: Registers course metadata and JSON-LD sitemap schema headers.
*   **Redis Caching**: Caches dashboard summaries.
