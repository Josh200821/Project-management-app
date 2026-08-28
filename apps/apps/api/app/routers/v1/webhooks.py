"""Webhooks router."""

import secrets

from fastapi import APIRouter

from app.db.models.webhook import Webhook
from app.dependencies import CurrentUser, DbSession
from app.schemas.common import ApiResponse
from app.schemas.webhook import WebhookCreate, WebhookResponse

router = APIRouter(prefix="/organizations/{org_id}/webhooks")


@router.post("", status_code=201)
async def create_webhook(
    org_id: str, body: WebhookCreate, current_user: CurrentUser, session: DbSession
):
    from uuid import UUID

    wh = Webhook(
        organization_id=UUID(org_id),
        url=body.url,
        events=body.events,
        secret=secrets.token_hex(32),
    )
    session.add(wh)
    await session.flush()
    return ApiResponse(data=WebhookResponse.model_validate(wh))


@router.get("")
async def list_webhooks(org_id: str, current_user: CurrentUser, session: DbSession):
    from uuid import UUID

    from sqlalchemy import select

    result = await session.execute(select(Webhook).where(Webhook.organization_id == UUID(org_id)))
    webhooks = result.scalars().all()
    return ApiResponse(data=[WebhookResponse.model_validate(w) for w in webhooks])


@router.delete("/{webhook_id}", status_code=204)
async def delete_webhook(
    org_id: str, webhook_id: str, current_user: CurrentUser, session: DbSession
):
    from uuid import UUID

    from sqlalchemy import select

    result = await session.execute(select(Webhook).where(Webhook.id == UUID(webhook_id)))
    wh = result.scalar_one_or_none()
    if wh:
        await session.delete(wh)
        await session.flush()
