"""Tasks router — CRUD + Kanban board."""

from fastapi import APIRouter

from app.dependencies import CurrentUser, DbSession
from app.schemas.common import ApiResponse
from app.schemas.task import TaskBulkUpdate, TaskCreate, TaskResponse, TaskUpdate
from app.services.task_service import TaskService

router = APIRouter(prefix="/projects/{project_id}/tasks")


@router.post("", response_model=ApiResponse[TaskResponse], status_code=201)
async def create_task(
    project_id: str, body: TaskCreate, current_user: CurrentUser, session: DbSession
):
    from uuid import UUID

    svc = TaskService(session)
    task = await svc.create(UUID(project_id), body, current_user.id)
    return ApiResponse(data=TaskResponse.model_validate(task))


@router.get("", response_model=ApiResponse[list[TaskResponse]])
async def list_tasks(
    project_id: str,
    current_user: CurrentUser,
    session: DbSession,
    status: str = None,
    page: int = 1,
    per_page: int = 50,
):
    from uuid import UUID

    svc = TaskService(session)
    tasks = await svc.list_by_project(UUID(project_id), status, (page - 1) * per_page, per_page)
    return ApiResponse(data=[TaskResponse.model_validate(t) for t in tasks])


@router.get("/board", response_model=ApiResponse[dict])
async def get_board(project_id: str, current_user: CurrentUser, session: DbSession):
    from uuid import UUID

    svc = TaskService(session)
    board = await svc.get_board(UUID(project_id))
    return ApiResponse(
        data={
            status: [TaskResponse.model_validate(t) for t in tasks]
            for status, tasks in board.items()
        }
    )


@router.get("/{task_id}", response_model=ApiResponse[TaskResponse])
async def get_task(project_id: str, task_id: str, current_user: CurrentUser, session: DbSession):
    from uuid import UUID

    svc = TaskService(session)
    task = await svc.get(UUID(task_id))
    return ApiResponse(data=TaskResponse.model_validate(task))


@router.patch("/{task_id}", response_model=ApiResponse[TaskResponse])
async def update_task(
    project_id: str, task_id: str, body: TaskUpdate, current_user: CurrentUser, session: DbSession
):
    from uuid import UUID

    svc = TaskService(session)
    task = await svc.update(UUID(task_id), body)
    return ApiResponse(data=TaskResponse.model_validate(task))


@router.delete("/{task_id}", status_code=204)
async def delete_task(project_id: str, task_id: str, current_user: CurrentUser, session: DbSession):
    from uuid import UUID

    svc = TaskService(session)
    await svc.delete(UUID(task_id))


@router.post("/bulk-update")
async def bulk_update(
    project_id: str, body: TaskBulkUpdate, current_user: CurrentUser, session: DbSession
):
    svc = TaskService(session)
    for task_id in body.task_ids:
        update_data = body.model_dump(exclude={"task_ids"}, exclude_none=True)
        from app.schemas.task import TaskUpdate

        await svc.update(task_id, TaskUpdate(**update_data))
    return ApiResponse(data={"updated": len(body.task_ids)})
