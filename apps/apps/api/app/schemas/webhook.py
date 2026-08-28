"""Webhook schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class WebhookCreate(BaseModel):
    url: str
    events: list[str]


class WebhookUpdate(BaseModel):
    url: str | None = None
    events: list[str] | None = None
    is_active: bool | None = None


class WebhookResponse(BaseModel):
    id: UUID
    url: str
    events: list[str]
    is_active: bool
    failure_count: int
    last_success_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}
