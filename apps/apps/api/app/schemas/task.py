"""Task schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class TaskCreate(BaseModel):
    title: str
    description: str | None = None
    status: str = "todo"
    priority: str = "medium"
    assignee_id: UUID | None = None
    due_date: datetime | None = None
    story_points: int | None = None
    parent_task_id: UUID | None = None
    sprint_id: UUID | None = None


class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    status: str | None = None
    priority: str | None = None
    assignee_id: UUID | None = None
    due_date: datetime | None = None
    story_points: int | None = None
    sprint_id: UUID | None = None
    board_order: float | None = None


class TaskResponse(BaseModel):
    id: UUID
    project_id: UUID
    task_number: int
    title: str
    description: str | None
    status: str
    priority: str
    story_points: int | None
    due_date: datetime | None
    assignee_id: UUID | None
    created_by: UUID | None
    board_order: float
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TaskBulkUpdate(BaseModel):
    task_ids: list[UUID]
    status: str | None = None
    assignee_id: UUID | None = None
    sprint_id: UUID | None = None
    priority: str | None = None
