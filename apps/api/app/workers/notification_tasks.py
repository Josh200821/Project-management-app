"""In-app notification delivery tasks."""
import structlog
from celery import shared_task

logger = structlog.get_logger()


@shared_task
def send_notification(user_id: str, notification_type: str, title: str, body: str, entity_id: str | None = None) -> None:
    logger.info("notification_sent", user_id=user_id, type=notification_type)
    # In production: insert into notifications table, publish to Redis pub/sub
    # for WebSocket delivery
