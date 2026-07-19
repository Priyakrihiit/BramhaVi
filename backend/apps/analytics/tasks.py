import logging
from celery import shared_task
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import ExportJob, ReportSchedule, Report
from .services import EventCollectorService, AggregationService, ExportService

User = get_user_model()
logger = logging.getLogger("brahmavidya.analytics.tasks")


@shared_task(
    name="apps.analytics.tasks.track_event_task",
    bind=True,
    max_retries=3,
    default_retry_delay=30,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_jitter=True,
    queue="analytics",
    acks_late=True,
    ignore_result=True,
)
def track_event_task(self, user_id, metric_name, value, context_data):
    """
    Asynchronously registers raw metric events.
    Retries up to 3 times with exponential backoff on failure.
    """
    logger.info(f"Tracking event async: {metric_name} value={value}")
    try:
        user = User.objects.filter(id=user_id).first() if user_id else None
        EventCollectorService.track_event(user, metric_name, value, context_data)
    except Exception as exc:
        logger.error(f"track_event_task failed for {metric_name}: {exc}", exc_info=True)
        raise self.retry(exc=exc)


@shared_task(
    name="apps.analytics.tasks.aggregate_daily_metrics_task",
    bind=True,
    max_retries=2,
    default_retry_delay=120,
    autoretry_for=(Exception,),
    retry_backoff=True,
    queue="analytics-bulk",
    acks_late=True,
    soft_time_limit=300,
    time_limit=600,
)
def aggregate_daily_metrics_task(self, target_date_str=None):
    """
    Asynchronously aggregates all metric statistics for a given day.
    Scheduled daily by Celery Beat at midnight UTC.
    """
    logger.info("Starting daily metrics aggregate build.")
    try:
        target_date = (
            timezone.datetime.strptime(target_date_str, "%Y-%m-%d").date()
            if target_date_str
            else timezone.now().date()
        )
        summaries = AggregationService.run_global_daily_aggregation(target_date)
        count = len(summaries)
        logger.info(f"Daily aggregation complete: {count} summary records written for {target_date}.")
        return count
    except Exception as exc:
        logger.error(f"aggregate_daily_metrics_task failed: {exc}", exc_info=True)
        raise self.retry(exc=exc)


@shared_task(
    name="apps.analytics.tasks.run_export_job_task",
    bind=True,
    max_retries=2,
    default_retry_delay=60,
    autoretry_for=(Exception,),
    queue="analytics-bulk",
    acks_late=True,
    soft_time_limit=240,
    time_limit=480,
)
def run_export_job_task(self, job_id):
    """
    Asynchronously generates file exports (CSV, PDF, or Excel).
    Updates ExportJob status to COMPLETED or FAILED.
    """
    logger.info(f"Starting export worker for job_id={job_id}")
    job = ExportJob.objects.filter(id=job_id).first()
    if not job:
        logger.error(f"ExportJob {job_id} not found — aborting.")
        return

    job.status = "RUNNING"
    job.save(update_fields=["status", "updated_at"])

    try:
        import os
        from django.conf import settings as django_settings

        content = ""
        ext = "csv"
        if job.job_type == "CSV":
            content = ExportService.export_events_csv(job_id)
            ext = "csv"
        elif job.job_type == "EXCEL":
            content = ExportService.export_events_excel(job_id)
            ext = "xls"
        elif job.job_type == "PDF":
            content = ExportService.export_events_pdf(job_id)
            ext = "pdf"

        out_dir = os.path.join(django_settings.BASE_DIR, "logs")
        os.makedirs(out_dir, exist_ok=True)
        file_path = os.path.join(out_dir, f"export_{job_id}.{ext}")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        job.status = "COMPLETED"
        job.file_url = f"/static/exports/export_{job_id}.{ext}"
        job.save(update_fields=["status", "file_url", "updated_at"])
        logger.info(f"Export job {job_id} completed: {job.file_url}")

    except Exception as exc:
        job.status = "FAILED"
        job.error_message = str(exc)[:500]
        job.save(update_fields=["status", "error_message", "updated_at"])
        logger.error(f"Export job {job_id} failed: {exc}", exc_info=True)
        raise self.retry(exc=exc)


@shared_task(
    name="apps.analytics.tasks.process_scheduled_reports_task",
    bind=True,
    max_retries=2,
    default_retry_delay=120,
    queue="analytics-bulk",
    acks_late=True,
    soft_time_limit=180,
    time_limit=360,
)
def process_scheduled_reports_task(self):
    """
    Hourly scheduled task: checks for due report schedules and triggers exports.
    """
    now = timezone.now()
    logger.info(f"Processing scheduled report triggers at {now.isoformat()}")
    try:
        schedules = ReportSchedule.objects.filter(
            is_active=True,
            next_run_at__lte=now,
            deleted_at__isnull=True,
        ).select_related()

        count = 0
        for sched in schedules:
            Report.objects.create(
                title=sched.report_title,
                description=f"Auto-scheduled: {sched.frequency}",
                format="PDF",
                status="COMPLETED",
                file_path=f"/static/reports/sched_{sched.id}.pdf",
            )
            delta_map = {"DAILY": 1, "WEEKLY": 7, "MONTHLY": 30}
            days = delta_map.get(sched.frequency, 7)
            sched.next_run_at = now + timezone.timedelta(days=days)
            sched.save(update_fields=["next_run_at", "updated_at"])
            count += 1
            logger.info(f"Dispatched report schedule: {sched.report_title} (next: {sched.next_run_at})")

        return count
    except Exception as exc:
        logger.error(f"process_scheduled_reports_task failed: {exc}", exc_info=True)
        raise self.retry(exc=exc)
