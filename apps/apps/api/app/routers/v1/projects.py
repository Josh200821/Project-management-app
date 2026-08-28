"""Projects router."""

from fastapi import APIRouter

from app.dependencies import CurrentUser, DbSession
from app.schemas.common import ApiResponse
from app.schemas.project import ProjectCreate, ProjectResponse, ProjectUpdate
from app.services.project_service import ProjectService

router = APIRouter(prefix="/organizations/{org_id}/projects")


@router.post("", response_model=ApiResponse[ProjectResponse], status_code=201)
async def create_project(
    org_id: str, body: ProjectCreate, current_user: CurrentUser, session: DbSession
):
    from uuid import UUID

    svc = ProjectService(session)
    project = await svc.create(UUID(org_id), body, current_user.id)
    return ApiResponse(data=ProjectResponse.model_validate(project))


@router.get("", response_model=ApiResponse[list[ProjectResponse]])
async def list_projects(
    org_id: str, current_user: CurrentUser, session: DbSession, page: int = 1, per_page: int = 20
):
    from uuid import UUID

    svc = ProjectService(session)
    projects = await svc.list_by_org(UUID(org_id), offset=(page - 1) * per_page, limit=per_page)
    return ApiResponse(data=[ProjectResponse.model_validate(p) for p in projects])


@router.get("/{project_id}", response_model=ApiResponse[ProjectResponse])
async def get_project(org_id: str, project_id: str, current_user: CurrentUser, session: DbSession):
    from uuid import UUID

    svc = ProjectService(session)
    project = await svc.get(UUID(project_id))
    return ApiResponse(data=ProjectResponse.model_validate(project))


@router.patch("/{project_id}", response_model=ApiResponse[ProjectResponse])
async def update_project(
    org_id: str, project_id: str, body: ProjectUpdate, current_user: CurrentUser, session: DbSession
):
    from uuid import UUID

    svc = ProjectService(session)
    project = await svc.update(UUID(project_id), body)
    return ApiResponse(data=ProjectResponse.model_validate(project))


@router.delete("/{project_id}", status_code=204)
async def delete_project(
    org_id: str, project_id: str, current_user: CurrentUser, session: DbSession
):
    from uuid import UUID

    svc = ProjectService(session)
    await svc.delete(UUID(project_id))
