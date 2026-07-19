import os
import sys
import time
import django

# Setup Django Environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend"))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_project.settings")
django.setup()

from django.contrib.auth import get_user_model
from apps.notifications.models import NotificationRecord, NotificationDelivery
from apps.notifications.tasks import send_batch_notifications_task

def run_stress_test(count):
    print(f"\n--- STRESS TESTING: {count} NOTIFICATIONS ---")
    User = get_user_model()
    admin = User.objects.get(email="admin@brahmavidya.edu")

    # 1. Bulk create NotificationRecord models
    start_time = time.time()
    records = [
        NotificationRecord(
            user=admin,
            category="welcome",
            title=f"Stress Test Alert {i}",
            content="Bulk processing load evaluation.",
            metadata={"index": i}
        )
        for i in range(count)
    ]
    created_records = NotificationRecord.objects.bulk_create(records, batch_size=2000)
    record_duration = time.time() - start_time
    print(f"1. Bulk created {len(created_records)} NotificationRecords in {record_duration:.4f}s")

    # 2. Bulk create NotificationDelivery queue payloads
    start_time = time.time()
    deliveries = [
        NotificationDelivery(
            notification=rec,
            channel="in_app",
            status="pending"
        )
        for rec in created_records
    ]
    created_deliveries = NotificationDelivery.objects.bulk_create(deliveries, batch_size=2000)
    delivery_duration = time.time() - start_time
    print(f"2. Bulk created {len(created_deliveries)} NotificationDeliveries in {delivery_duration:.4f}s")

    # 3. Simulate Worker Processing in Batches
    start_time = time.time()
    delivery_ids = [str(d.id) for d in created_deliveries]
    
    # Process in chunks of 1000
    chunk_size = 1000
    success_total = 0
    for i in range(0, len(delivery_ids), chunk_size):
        chunk = delivery_ids[i:i+chunk_size]
        res = send_batch_notifications_task(chunk)
        success_total += res["success"]

    process_duration = time.time() - start_time
    rate = count / process_duration if process_duration > 0 else 0
    print(f"3. Processed {success_total} items in {process_duration:.4f}s ({rate:.2f} items/sec)")

def main():
    # Execute stress checks
    run_stress_test(1000)
    run_stress_test(10000)

if __name__ == "__main__":
    main()
