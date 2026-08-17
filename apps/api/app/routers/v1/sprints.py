"""Sprints router."""
from fastapi import APIRouter
from app.dependencies import CurrentUser, DbSession
from app.schemas.common import ApiResponse
from app.schemas.sprint import SprintCreate, SprintResponse, SprintUpdate
from app.services.sprint_service import SprintService

router = APIRouter(prefix="/projects/{project_id}/sprints")


@router.post("", response_model=ApiResponse[SprintResponse], status_code=201)
async def create_sprint(project_id: str, body: SprintCreate, current_user: CurrentUser, session: DbSession):
    from uuid import UUID
    svc = SprintService(session)
    sprint = await svc.create(UUID(project_id), body)
    return ApiResponse(data=SprintResponse.model_validate(sprint))


@router.get("", response_model=ApiResponse[list[SprintResponse]])
async def list_sprints(project_id: str, current_user: CurrentUser, session: DbSession):
    from uuid import UUID
    svc = SprintService(session)
    sprints = await svc.list_by_project(UUID(project_id))
    return ApiResponse(data=[SprintResponse.model_validate(s) for s in sprints])


@router.get("/{sprint_id}", response_model=ApiResponse[SprintResponse])
async def get_sprint(project_id: str, sprint_id: str, current_user: CurrentUser, session: DbSession):
    from uuid import UUID
    svc = SprintService(session)
    sprint = await svc.get(UUID(sprint_id))
    return ApiResponse(data=SprintResponse.model_validate(sprint))


@router.patch("/{sprint_id}", response_model=ApiResponse[SprintResponse])
async def update_sprint(project_id: str, sprint_id: str, body: SprintUpdate, current_user: CurrentUser, session: DbSession):
    from uuid import UUID
    svc = SprintService(session)
    sprint = await svc.update(UUID(sprint_id), body)
    return ApiResponse(data=SprintResponse.model_validate(sprint))


@router.post("/{sprint_id}/close")
async def close_sprint(project_id: str, sprint_id: str, current_user: CurrentUser, session: DbSession):
    from uuid import UUID
    svc = SprintService(session)
    sprint = await svc.close(UUID(sprint_id))
    return ApiResponse(data=SprintResponse.model_validate(sprint))


@router.get("/{sprint_id}/burndown")
async def get_burndown(project_id: str, sprint_id: str, current_user: CurrentUser, session: DbSession):
    from uuid import UUID
    svc = SprintService(session)
    data = await svc.get_burndown(UUID(sprint_id))
    return ApiResponse(data=data)
