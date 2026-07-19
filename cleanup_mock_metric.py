import os, sys, django
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_project.settings')
django.setup()
from django.db import connection
cursor = connection.cursor()
cursor.execute("DELETE FROM analytics_metric_definitions WHERE key='mock_test_runs'")
print(f"Deleted {cursor.rowcount} stale mock metric rows.")
