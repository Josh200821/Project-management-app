"""Sprint schemas."""
from datetime import date, datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel


class SprintCreate(BaseModel):
    name: str
    goal: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    capacity_points: Optional[int] = None


class SprintUpdate(BaseModel):
    name: Optional[str] = None
    goal: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: Optional[str] = None
    capacity_points: Optional[int] = None


class SprintResponse(BaseModel):
    id: UUID
    project_id: UUID
    name: str
    goal: Optional[str]
    start_date: Optional[date]
    end_date: Optional[date]
    status: str
    capacity_points: Optional[int]
    velocity_points: Optional[int]
    created_at: datetime

    model_config = {"from_attributes": True}
