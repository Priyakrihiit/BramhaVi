import os
import sys
import django

# Setup Django Environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend"))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_project.settings")
django.setup()

from django.contrib.auth import get_user_model
from apps.notifications.models import NotificationTemplate, NotificationRecord, NotificationPreference, NotificationDelivery
from apps.notifications.services import EmailService, SMSService, PushNotificationService

def run_tests():
    print("--- STARTING SPRINT 14 NOTIFICATION PLATFORM INTEGRATION TESTS ---")
    User = get_user_model()
    
    # 1. Fetch existing admin user
    user = User.objects.get(email="admin@brahmavidya.edu")
    print("1. Fetched admin user.")

    # 2. Verify Phone E.164 validations
    valid_phone = "+14155552671"
    invalid_phone = "14155552671"
    assert SMSService.validate_phone_number(valid_phone) == True, "Phone verification failed for valid E.164 format."
    assert SMSService.validate_phone_number(invalid_phone) == False, "Phone verification passed for invalid E.164 format."
    print("2. E.164 SMS validation checks passed.")

    # 3. Create Template
    template, created = NotificationTemplate.objects.update_or_create(
        code="test_template",
        defaults={
            "name": "Integration Test Template",
            "subject": "Hello, {{ name }}!",
            "body_html": "<p>Content: {{ content }}</p>",
            "body_text": "Content: {{ content }}"
        }
    )
    print("3. NotificationTemplate updated in database.")

    # 4. Create Preference
    pref, created = NotificationPreference.objects.update_or_create(
        user=user,
        category="test_template",
        defaults={"email_enabled": True, "sms_enabled": False, "push_enabled": True}
    )
    print("4. NotificationPreferences seeded.")

    # 5. Create Record
    record = NotificationRecord.objects.create(
        user=user,
        category="test_template",
        title="Welcome Alert Test",
        content="This is a test notification."
    )
    print(f"5. NotificationRecord created: {record.id}")

    # 6. Verify Deliveries Triggering
    delivery = NotificationDelivery.objects.create(
        notification=record,
        channel="email",
        status="pending"
    )
    
    success, error = EmailService.send_email(
        to_email=user.email,
        template_code="test_template",
        context_data={"name": user.email, "content": record.content}
    )
    assert success == True, f"Email delivery execution failed: {error}"
    delivery.status = "sent"
    delivery.save()
    print("6. Email dispatch verified successfully.")

    print("--- SPRINT 14 NOTIFICATION PLATFORM INTEGRATION TESTS PASSED ---")

if __name__ == "__main__":
    run_tests()
