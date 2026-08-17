"""Comment schemas."""
from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel


class CommentCreate(BaseModel):
    body: str


class CommentUpdate(BaseModel):
    body: str


class CommentResponse(BaseModel):
    id: UUID
    task_id: UUID
    author_id: UUID
    body: str
    edited_at: Optional[datetime]
    created_at: datetime

    model_config = {"from_attributes": True}
