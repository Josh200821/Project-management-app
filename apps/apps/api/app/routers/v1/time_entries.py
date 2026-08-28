"""Time entries router."""

from datetime import datetime

from fastapi import APIRouter
from pydantic import BaseModel

from app.dependencies import CurrentUser, DbSession
from app.schemas.common import ApiResponse

router = APIRouter(prefix="/time-entries")


class TimeEntryCreate(BaseModel):
    task_id: str
    started_at: datetime
    stopped_at: datetime | None = None
    description: str | None = None
    billable: bool = True


@router.post("", status_code=201)
async def create_time_entry(body: TimeEntryCreate, current_user: CurrentUser, session: DbSession):
    from uuid import UUID

    from app.db.models.time_entry import TimeEntry

    duration = None
    if body.stopped_at and body.started_at:
        duration = int((body.stopped_at - body.started_at).total_seconds())
    entry = TimeEntry(
        task_id=UUID(body.task_id),
        user_id=current_user.id,
        started_at=body.started_at,
        stopped_at=body.stopped_at,
        duration_seconds=duration,
        description=body.description,
        billable=body.billable,
    )
    session.add(entry)
    await session.flush()
    return ApiResponse(data={"id": str(entry.id), "duration_seconds": duration})


@router.get("/tasks/{task_id}")
async def list_for_task(task_id: str, current_user: CurrentUser, session: DbSession):
    from uuid import UUID

    from sqlalchemy import select

    from app.db.models.time_entry import TimeEntry

    result = await session.execute(select(TimeEntry).where(TimeEntry.task_id == UUID(task_id)))
    entries = result.scalars().all()
    return ApiResponse(
        data=[
            {
                "id": str(e.id),
                "started_at": str(e.started_at),
                "duration_seconds": e.duration_seconds,
            }
            for e in entries
        ]
    )
