"""AI features router."""

from fastapi import APIRouter

from app.dependencies import CurrentUser, DbSession
from app.schemas.common import ApiResponse
from app.services.ai_service import AIService

router = APIRouter(prefix="/ai")


@router.post("/tasks/{task_id}/summarize")
async def summarize_task(task_id: str, current_user: CurrentUser, session: DbSession):
    from uuid import UUID

    svc = AIService(session)
    result = await svc.summarize_task(UUID(task_id))
    return ApiResponse(data={"summary": result})


@router.post("/projects/{project_id}/status-report")
async def generate_status_report(project_id: str, current_user: CurrentUser, session: DbSession):
    from uuid import UUID

    svc = AIService(session)
    result = await svc.generate_status_report(UUID(project_id))
    return ApiResponse(data={"report": result})


@router.get("/organizations/{org_id}/workload")
async def workload_analysis(org_id: str, current_user: CurrentUser, session: DbSession):
    from uuid import UUID

    svc = AIService(session)
    result = await svc.analyze_workload(UUID(org_id))
    return ApiResponse(data=result)
