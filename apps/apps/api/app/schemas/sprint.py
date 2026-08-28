"""Sprint schemas."""

from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel


class SprintCreate(BaseModel):
    name: str
    goal: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    capacity_points: int | None = None


class SprintUpdate(BaseModel):
    name: str | None = None
    goal: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    status: str | None = None
    capacity_points: int | None = None


class SprintResponse(BaseModel):
    id: UUID
    project_id: UUID
    name: str
    goal: str | None
    start_date: date | None
    end_date: date | None
    status: str
    capacity_points: int | None
    velocity_points: int | None
    created_at: datetime

    model_config = {"from_attributes": True}
