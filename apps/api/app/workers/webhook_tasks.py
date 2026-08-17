"""Outbound webhook delivery with HMAC signing and retry queue."""
import hashlib
import hmac
import json
import time
from datetime import datetime

import httpx
import structlog
from celery import shared_task

logger = structlog.get_logger()
MAX_RETRIES = 5


@shared_task(bind=True, max_retries=MAX_RETRIES)
def deliver_webhook(self, webhook_id: str, url: str, secret: str, event_type: str, payload: dict) -> bool:
    body = json.dumps(payload, default=str)
    timestamp = str(int(time.time()))
    signature = hmac.new(
        secret.encode(), f"{timestamp}.{body}".encode(), hashlib.sha256
    ).hexdigest()

    headers = {
        "Content-Type": "application/json",
        "X-Signature-256": f"sha256={signature}",
        "X-Timestamp": timestamp,
        "X-Event-Type": event_type,
    }

    try:
        response = httpx.post(url, content=body, headers=headers, timeout=10)
        response.raise_for_status()
        logger.info("webhook_delivered", webhook_id=webhook_id, status=response.status_code)
        return True
    except Exception as exc:
        delay = 2 ** self.request.retries * 60
        logger.warning("webhook_failed", webhook_id=webhook_id, attempt=self.request.retries, error=str(exc))
        raise self.retry(exc=exc, countdown=delay)


@shared_task
def fire_event(event_type: str, payload: dict, organization_id: str) -> None:
    """Fan out a platform event to all active webhooks for an org."""
    # In production: query DB for active webhooks matching event_type for org
    logger.info("event_fired", event_type=event_type, org=organization_id)
