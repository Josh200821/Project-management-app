"""Task schemas."""
from datetime import datetime
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel


class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    status: str = "todo"
    priority: str = "medium"
    assignee_id: Optional[UUID] = None
    due_date: Optional[datetime] = None
    story_points: Optional[int] = None
    parent_task_id: Optional[UUID] = None
    sprint_id: Optional[UUID] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    assignee_id: Optional[UUID] = None
    due_date: Optional[datetime] = None
    story_points: Optional[int] = None
    sprint_id: Optional[UUID] = None
    board_order: Optional[float] = None


class TaskResponse(BaseModel):
    id: UUID
    project_id: UUID
    task_number: int
    title: str
    description: Optional[str]
    status: str
    priority: str
    story_points: Optional[int]
    due_date: Optional[datetime]
    assignee_id: Optional[UUID]
    created_by: Optional[UUID]
    board_order: float
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TaskBulkUpdate(BaseModel):
    task_ids: List[UUID]
    status: Optional[str] = None
    assignee_id: Optional[UUID] = None
    sprint_id: Optional[UUID] = None
    priority: Optional[str] = None
