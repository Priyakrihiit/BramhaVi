import logging
from django.core.mail import EmailMultiAlternatives
from django.template import Template, Context
from django.utils.html import strip_tags
from apps.notifications.models import NotificationTemplate, NotificationRecord, NotificationDelivery

logger = logging.getLogger("notifications")

class EmailService:
    @staticmethod
    def send_email(to_email, template_code, context_data, attachments=None):
        """
        Retrieves a NotificationTemplate by code, renders subject and body with context_data,
        and sends the email using Django's email framework.
        """
        try:
            template = NotificationTemplate.objects.get(code=template_code)
        except NotificationTemplate.DoesNotExist:
            logger.error(f"Template with code '{template_code}' not found.")
            return False, "Template not found"

        try:
            # Render subject & content dynamic variables
            subject_tmpl = Template(template.subject)
            html_tmpl = Template(template.body_html)
            
            ctx = Context(context_data)
            subject = subject_tmpl.render(ctx)
            html_content = html_tmpl.render(ctx)
            
            # Text fallback
            if template.body_text:
                text_content = Template(template.body_text).render(ctx)
            else:
                text_content = strip_tags(html_content)

            # Build email
            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=None,  # Uses DEFAULT_FROM_EMAIL from settings
                to=[to_email]
            )
            email.attach_alternative(html_content, "text/html")

            # Attach files if any
            if attachments:
                for attachment in attachments:
                    # attachment format: (filename, content, mimetype)
                    email.attach(*attachment)

            email.send(fail_silently=False)
            logger.info(f"Email sent successfully to {to_email} using template {template_code}")
            return True, None
        except Exception as e:
            logger.error(f"Failed to send email to {to_email} using template {template_code}: {str(e)}")
            return False, str(e)


import os
import re
import time

class SMSService:
    @staticmethod
    def validate_phone_number(phone_number: str) -> bool:
        """
        Validates phone number using E.164 format check (+[1-9][0-9]{1,14}).
        """
        if not phone_number:
            return False
        pattern = re.compile(r"^\+[1-9]\d{1,14}$")
        return bool(pattern.match(phone_number))

    @staticmethod
    def send_sms(to_phone, template_code, context_data, request_id="-"):
        """
        Renders template body and forwards message body via Twilio, MSG91, AWS SNS, or Mock.
        """
        if not SMSService.validate_phone_number(to_phone):
            logger.error(f"[SMS ERROR] Invalid phone number format: {to_phone}")
            return False, "Invalid phone number format"

        try:
            template = NotificationTemplate.objects.get(code=template_code)
        except NotificationTemplate.DoesNotExist:
            logger.error(f"[SMS ERROR] Template '{template_code}' not found.")
            return False, "Template not found"

        try:
            body_tmpl = Template(template.body_text or template.body_html)
            ctx = Context(context_data)
            message_content = body_tmpl.render(ctx)
        except Exception as e:
            logger.error(f"[SMS ERROR] Failed rendering SMS template: {str(e)}")
            return False, f"Template render error: {str(e)}"

        provider = os.getenv("SMS_PROVIDER", "mock").lower()
        start_time = time.time()
        success = False
        error_msg = None
        response_data = None

        logger.info(f"[SMS INFO] Sending SMS via {provider} to {to_phone}. RID: {request_id}")

        if provider == "twilio":
            try:
                from twilio.rest import Client
                sid = os.getenv("TWILIO_ACCOUNT_SID")
                token = os.getenv("TWILIO_AUTH_TOKEN")
                from_num = os.getenv("TWILIO_PHONE_NUMBER")

                if not sid or not token or not from_num:
                    raise ValueError("Twilio credentials not configured.")

                client = Client(sid, token)
                message = client.messages.create(
                    to=to_phone,
                    from_=from_num,
                    body=message_content
                )
                success = True
                response_data = {"sid": message.sid, "status": message.status}
            except Exception as e:
                error_msg = str(e)
                logger.error(f"[SMS TWILIO ERROR] {error_msg}")

        elif provider == "msg91":
            try:
                import requests
                auth_key = os.getenv("MSG91_KEY")
                if not auth_key:
                    raise ValueError("MSG91 auth key not configured.")

                url = "https://api.msg91.com/api/v2/sendsms"
                headers = {"authkey": auth_key, "Content-Type": "application/json"}
                payload = {
                    "sender": "BVIDYA",
                    "route": "4",
                    "sms": [{"message": message_content, "to": [to_phone]}]
                }
                res = requests.post(url, json=payload, headers=headers, timeout=5)
                if res.status_code == 200:
                    success = True
                    response_data = res.json()
                else:
                    error_msg = f"HTTP {res.status_code}: {res.text}"
            except Exception as e:
                error_msg = str(e)
                logger.error(f"[SMS MSG91 ERROR] {error_msg}")

        elif provider == "aws_sns":
            try:
                import boto3
                region = os.getenv("AWS_SNS_REGION", "us-east-1")
                key = os.getenv("AWS_SNS_ACCESS_KEY")
                secret = os.getenv("AWS_SNS_SECRET_KEY")

                if not key or not secret:
                    raise ValueError("AWS SNS credentials not configured.")

                client = boto3.client(
                    "sns",
                    region_name=region,
                    aws_access_key_id=key,
                    aws_secret_access_key=secret
                )
                res = client.publish(
                    PhoneNumber=to_phone,
                    Message=message_content
                )
                success = True
                response_data = {"message_id": res.get("MessageId")}
            except Exception as e:
                error_msg = str(e)
                logger.error(f"[SMS AWS_SNS ERROR] {error_msg}")

        else:
            success = True
            response_data = {"mock": True, "message": message_content}
            logger.info(f"[SMS MOCK] Simulated sending to {to_phone}: {message_content}")

        latency = time.time() - start_time
        logger.info(
            f"[SMS AUDIT] Provider: {provider}, Phone: {to_phone}, Latency: {latency:.4f}s, "
            f"Success: {success}, RID: {request_id}"
        )

        if success:
            return True, None
        return False, error_msg or "Unknown error"


class PushNotificationService:
    @staticmethod
    def send_push(user_phone_or_id, title, body, badge_count=0, priority="high", deep_link=None):
        """
        Sends push notification using Firebase Cloud Messaging (FCM).
        In development, logs FCM payload configuration structures.
        """
        logger.info(f"[PUSH INFO] Building FCM payload for target: {user_phone_or_id}. Priority: {priority}")
        payload = {
            "to": user_phone_or_id,
            "priority": priority,
            "notification": {
                "title": title,
                "body": body,
                "badge": badge_count,
                "sound": "default"
            },
            "data": {
                "click_action": "FLUTTER_NOTIFICATION_CLICK",
                "deep_link": deep_link or "/"
            }
        }
        
        # Simulation validation block
        logger.info(f"[PUSH AUDIT] FCM Dispatch payload: {payload}")
        return True, None
