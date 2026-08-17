"""Comments router."""
from fastapi import APIRouter
from app.dependencies import CurrentUser, DbSession
from app.schemas.comment import CommentCreate, CommentResponse, CommentUpdate
from app.schemas.common import ApiResponse
from app.services.comment_service import CommentService

router = APIRouter(prefix="/tasks/{task_id}/comments")


@router.post("", response_model=ApiResponse[CommentResponse], status_code=201)
async def create_comment(task_id: str, body: CommentCreate, current_user: CurrentUser, session: DbSession):
    from uuid import UUID
    svc = CommentService(session)
    comment = await svc.create(UUID(task_id), body, current_user.id)
    return ApiResponse(data=CommentResponse.model_validate(comment))


@router.get("", response_model=ApiResponse[list[CommentResponse]])
async def list_comments(task_id: str, current_user: CurrentUser, session: DbSession):
    from uuid import UUID
    svc = CommentService(session)
    comments = await svc.list_by_task(UUID(task_id))
    return ApiResponse(data=[CommentResponse.model_validate(c) for c in comments])


@router.patch("/{comment_id}", response_model=ApiResponse[CommentResponse])
async def update_comment(task_id: str, comment_id: str, body: CommentUpdate, current_user: CurrentUser, session: DbSession):
    from uuid import UUID
    svc = CommentService(session)
    comment = await svc.update(UUID(comment_id), body)
    return ApiResponse(data=CommentResponse.model_validate(comment))


@router.delete("/{comment_id}", status_code=204)
async def delete_comment(task_id: str, comment_id: str, current_user: CurrentUser, session: DbSession):
    from uuid import UUID
    svc = CommentService(session)
    await svc.delete(UUID(comment_id))
