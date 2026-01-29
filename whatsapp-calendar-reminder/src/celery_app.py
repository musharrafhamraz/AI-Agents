"""Celery application configuration."""

from celery import Celery
from celery.schedules import crontab
from src.config import settings

# Create Celery app
celery_app = Celery(
    "whatsapp_calendar_reminder",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["src.tasks.celery_tasks"]
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 5 minutes
    task_soft_time_limit=240,  # 4 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# Periodic task schedule
celery_app.conf.beat_schedule = {
    "sync-calendars": {
        "task": "src.tasks.celery_tasks.sync_calendars_task",
        "schedule": crontab(minute=f"*/{settings.sync_interval_minutes}"),  # Every N minutes
    },
    "schedule-pending-reminders": {
        "task": "src.tasks.celery_tasks.schedule_pending_reminders_task",
        "schedule": crontab(minute="*/5"),  # Every 5 minutes
    },
    "process-pending-reminders": {
        "task": "src.tasks.celery_tasks.process_pending_reminders_task",
        "schedule": crontab(minute="*/2"),  # Every 2 minutes
    },
    "retry-failed-messages": {
        "task": "src.tasks.celery_tasks.retry_failed_messages_task",
        "schedule": crontab(minute="0", hour="*/1"),  # Every hour
    },
}
