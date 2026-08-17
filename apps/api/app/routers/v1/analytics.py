"""Analytics router."""
from fastapi import APIRouter
from app.dependencies import CurrentUser, DbSession
from app.schemas.common import ApiResponse
from app.schemas.analytics import ProjectAnalytics
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics")


@router.get("/projects/{project_id}", response_model=ApiResponse[ProjectAnalytics])
async def project_analytics(project_id: str, org_id: str, current_user: CurrentUser, session: DbSession):
    from uuid import UUID
    svc = AnalyticsService(session)
    data = await svc.get_project_analytics(UUID(project_id), UUID(org_id))
    return ApiResponse(data=data)
