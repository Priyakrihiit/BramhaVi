import sys, os
sys.path.insert(0, 'backend')
os.environ['DJANGO_SETTINGS_MODULE'] = 'django_project.settings'
import django
django.setup()
from django.db import connection
cursor = connection.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'ai_%' ORDER BY name")
tables = [row[0] for row in cursor.fetchall()]
for t in tables:
    cursor.execute(f'SELECT COUNT(*) FROM "{t}"')
    count = cursor.fetchone()[0]
    print(f'{t}: {count} rows')
print(f'Total AI tables: {len(tables)}')
