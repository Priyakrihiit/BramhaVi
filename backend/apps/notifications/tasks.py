import logging
import time
from celery import shared_task
from django.db import transaction
from apps.notifications.models import NotificationDelivery
from apps.notifications.services import EmailService, SMSService, PushNotificationService

logger = logging.getLogger("notifications")

@shared_task(bind=True, max_retries=5)
def send_notification_task(self, delivery_id):
    """
    Asynchronous Celery task processing a single NotificationDelivery queue record.
    Supports retries with exponential backoff.
    """
    start_time = time.time()
    try:
        delivery = NotificationDelivery.objects.select_related("notification", "notification__user").get(id=delivery_id)
    except NotificationDelivery.DoesNotExist:
        logger.error(f"[QUEUE ERROR] Delivery record {delivery_id} not found.")
        return

    record = delivery.notification
    channel = delivery.channel
    user_email = record.user.email
    user_phone = getattr(record.user, "phone_number", None) or getattr(record.user, "phone", None) or ""

    logger.info(f"[QUEUE INFO] Dispatching delivery {delivery_id} on channel {channel}")
    
    success = False
    error_msg = None

    if channel == "email":
        success, error_msg = EmailService.send_email(
            to_email=user_email,
            template_code=record.category,
            context_data={
                "name": record.user.username or record.user.email,
                "title": record.title,
                "content": record.content,
                **record.metadata
            }
        )
    elif channel == "sms":
        if user_phone:
            success, error_msg = SMSService.send_sms(
                to_phone=user_phone,
                template_code=record.category,
                context_data={
                    "name": record.user.username or record.user.email,
                    "content": record.content,
                    **record.metadata
                }
            )
        else:
            error_msg = "User phone number not configured."
    elif channel == "push":
        success, error_msg = PushNotificationService.send_push(
            user_phone_or_id=str(record.user.id),
            title=record.title,
            body=record.content,
            deep_link=record.metadata.get("deep_link")
        )
    elif channel == "in_app":
        success = True

    duration = time.time() - start_time
    logger.info(f"[QUEUE METRIC] Task {self.request.id} processed in {duration:.4f}s")

    if success:
        delivery.status = "sent"
        delivery.save()
        logger.info(f"[QUEUE SUCCESS] Delivery {delivery_id} successfully sent.")
    else:
        delivery.error_message = error_msg
        delivery.retry_count = self.request.retries + 1
        delivery.save()
        
        if self.request.retries < self.max_retries:
            logger.warning(f"[QUEUE WARN] Delivery {delivery_id} failed: {error_msg}. Retrying...")
            countdown = (2 ** self.request.retries) * 10
            raise self.retry(exc=Exception(error_msg), countdown=countdown)
        else:
            delivery.status = "failed"
            delivery.save()
            logger.error(f"[QUEUE DLQ] Delivery {delivery_id} exceeded max retries. Moved to DLQ. Reason: {error_msg}")


@shared_task
def send_batch_notifications_task(delivery_ids):
    """
    Processes a list of NotificationDelivery IDs in batch.
    Optimizes DB connection usage and updates statuses in bulk.
    """
    start_time = time.time()
    logger.info(f"[QUEUE BATCH] Starting batch process for {len(delivery_ids)} items.")
    
    deliveries = NotificationDelivery.objects.filter(id__in=delivery_ids).select_related("notification", "notification__user")
    
    success_count = 0
    fail_count = 0

    with transaction.atomic():
        for delivery in deliveries:
            record = delivery.notification
            channel = delivery.channel
            success = False
            
            if channel == "email":
                success, _ = EmailService.send_email(
                    to_email=record.user.email,
                    template_code=record.category,
                    context_data={"name": record.user.email, "content": record.content, **record.metadata}
                )
            elif channel == "sms":
                phone = getattr(record.user, "phone_number", None) or getattr(record.user, "phone", None) or ""
                if phone:
                    success, _ = SMSService.send_sms(
                        to_phone=phone,
                        template_code=record.category,
                        context_data={"name": record.user.email, "content": record.content, **record.metadata}
                    )
            elif channel in ["in_app", "push"]:
                success = True
                
            if success:
                delivery.status = "sent"
                success_count += 1
            else:
                delivery.status = "failed"
                fail_count += 1
            delivery.save()

    duration = time.time() - start_time
    logger.info(f"[QUEUE METRIC] Batch of {len(delivery_ids)} finished in {duration:.4f}s. Success: {success_count}, Failed: {fail_count}")
    return {"success": success_count, "failed": fail_count}
