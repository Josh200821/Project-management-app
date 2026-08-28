"""Global search router."""

from fastapi import APIRouter, Query

from app.dependencies import CurrentUser, DbSession
from app.schemas.common import ApiResponse
from app.services.task_service import TaskService

router = APIRouter(prefix="/search")


@router.get("")
async def search(
    current_user: CurrentUser,
    session: DbSession,
    q: str = Query(..., min_length=2),
    org_id: str = Query(...),
):
    from uuid import UUID

    svc = TaskService(session)
    results = await svc.search(UUID(org_id), q)
    return ApiResponse(data=results)
