"""Celery application factory with beat schedule."""

from celery import Celery
from celery.schedules import crontab

from app.config import settings

celery_app = Celery(
    "saas-platform",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.REDIS_URL,
    include=[
        "app.workers.email_tasks",
        "app.workers.notification_tasks",
        "app.workers.webhook_tasks",
        "app.workers.ai_tasks",
        "app.workers.report_tasks",
        "app.workers.storage_tasks",
    ],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    task_soft_time_limit=300,
    task_time_limit=600,
)

celery_app.conf.beat_schedule = {
    "weekly-status-reports": {
        "task": "app.workers.report_tasks.send_weekly_status_reports",
        "schedule": crontab(day_of_week="monday", hour=8, minute=0),
    },
    "daily-standup-updates": {
        "task": "app.workers.ai_tasks.send_standup_updates",
        "schedule": crontab(hour=9, minute=0),
    },
    "refresh-task-search-index": {
        "task": "app.workers.report_tasks.refresh_task_search",
        "schedule": crontab(minute="*/15"),
    },
}
