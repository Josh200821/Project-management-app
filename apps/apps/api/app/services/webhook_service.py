"""Webhook service."""

import hashlib
import hmac
import json
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.webhook import Webhook


class WebhookService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_active_webhooks(self, org_id: UUID) -> list[Webhook]:
        from sqlalchemy import select

        result = await self.session.execute(
            select(Webhook).where(
                Webhook.organization_id == org_id,
                Webhook.is_active.is_(True),
            )
        )
        return list(result.scalars().all())

    def sign_payload(self, secret: str, payload: dict) -> str:
        body = json.dumps(payload, separators=(",", ":"), sort_keys=True)
        return hmac.new(secret.encode(), body.encode(), hashlib.sha256).hexdigest()

    async def dispatch(self, org_id: UUID, event_type: str, payload: dict) -> None:
        """Fire-and-forget via Celery."""
        from app.workers.webhook_tasks import deliver_webhook

        webhooks = await self.get_active_webhooks(org_id)
        for wh in webhooks:
            if event_type in wh.events or "*" in wh.events:
                deliver_webhook.delay(str(wh.id), wh.url, wh.secret, event_type, payload)
