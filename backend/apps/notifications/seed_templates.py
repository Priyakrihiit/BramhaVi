import os
import sys
import django

# Setup Django Environment
backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, backend_dir)
sys.path.insert(0, os.path.dirname(backend_dir))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_project.settings")
django.setup()

from apps.notifications.models import NotificationTemplate

def seed_templates():
    templates = [
        {
            "code": "welcome",
            "name": "Welcome Onboarding Email",
            "subject": "Welcome to BrahmaVidya Galaxy, {{ name }}!",
            "body_html": "<h1>Welcome Onboarding</h1><p>Dear {{ name }}, welcome to your personalized technical dashboard.</p>",
            "body_text": "Dear {{ name }}, welcome to your personalized technical dashboard."
        },
        {
            "code": "password_reset",
            "name": "Password Reset OTP",
            "subject": "Reset your Password - BrahmaVidya",
            "body_html": "<h1>Password Reset Request</h1><p>Use code <strong>{{ token }}</strong> to reset your password.</p>",
            "body_text": "Use code {{ token }} to reset your password."
        },
        {
            "code": "certificate",
            "name": "Course Certificate Issuance",
            "subject": "Congratulations! Certificate Issued for {{ course_name }}",
            "body_html": "<h1>Certificate Unlocked</h1><p>You have successfully completed {{ course_name }}. Certificate Hash: {{ hash }}.</p>",
            "body_text": "You have successfully completed {{ course_name }}. Certificate Hash: {{ hash }}."
        },
        {
            "code": "exam_reminder",
            "name": "Upcoming Exam Reminder",
            "subject": "Exam Reminder: {{ exam_title }}",
            "body_html": "<h1>Exam Reminder</h1><p>Hi {{ name }}, your exam {{ exam_title }} starts on {{ date }}.</p>",
            "body_text": "Hi {{ name }}, your exam {{ exam_title }} starts on {{ date }}."
        },
        {
            "code": "wallet",
            "name": "Wallet Deposit/Debit Notification",
            "subject": "Wallet Transaction Alert: {{ type }}",
            "body_html": "<h1>Transaction Completed</h1><p>Your wallet has been {{ type }}ed by {{ amount }} {{ currency }}. Reference: {{ ref }}.</p>",
            "body_text": "Your wallet has been {{ type }}ed by {{ amount }} {{ currency }}. Reference: {{ ref }}."
        },
        {
            "code": "payment",
            "name": "Payment Confirmation Receipt",
            "subject": "Payment Receipt - Thank You",
            "body_html": "<h1>Payment Confirmed</h1><p>We received your payment of {{ amount }} {{ currency }} for Order {{ order_id }}.</p>",
            "body_text": "We received your payment of {{ amount }} {{ currency }} for Order {{ order_id }}."
        },
        {
            "code": "course",
            "name": "Course Enrolled Alert",
            "subject": "Enrolled: {{ course_name }}",
            "body_html": "<h1>Course Enrollment Confirmed</h1><p>You are now enrolled in {{ course_name }}. Get started today!</p>",
            "body_text": "You are now enrolled in {{ course_name }}. Get started today!"
        },
        {
            "code": "announcement",
            "name": "System Wide Announcement",
            "subject": "Important Platform Update: {{ title }}",
            "body_html": "<h1>Announcement</h1><p>{{ content }}</p>",
            "body_text": "Announcement: {{ content }}"
        }
    ]

    for t in templates:
        obj, created = NotificationTemplate.objects.update_or_create(
            code=t["code"],
            defaults={
                "name": t["name"],
                "subject": t["subject"],
                "body_html": t["body_html"],
                "body_text": t["body_text"]
            }
        )
        status = "Created" if created else "Updated"
        print(f"Template '{t['code']}': {status}")

if __name__ == "__main__":
    seed_templates()
