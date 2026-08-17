"""Webhook schemas."""
from datetime import datetime
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, HttpUrl


class WebhookCreate(BaseModel):
    url: str
    events: List[str]


class WebhookUpdate(BaseModel):
    url: Optional[str] = None
    events: Optional[List[str]] = None
    is_active: Optional[bool] = None


class WebhookResponse(BaseModel):
    id: UUID
    url: str
    events: List[str]
    is_active: bool
    failure_count: int
    last_success_at: Optional[datetime]
    created_at: datetime

    model_config = {"from_attributes": True}
