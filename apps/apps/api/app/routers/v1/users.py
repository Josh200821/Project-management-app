"""Users router."""

from fastapi import APIRouter

from app.dependencies import CurrentUser, DbSession
from app.repositories.user_repo import UserRepository
from app.schemas.common import ApiResponse
from app.schemas.user import UserResponse, UserUpdate

router = APIRouter(prefix="/users")


@router.get("/me", response_model=ApiResponse[UserResponse])
async def get_me(current_user: CurrentUser):
    return ApiResponse(data=UserResponse.model_validate(current_user))


@router.patch("/me", response_model=ApiResponse[UserResponse])
async def update_me(body: UserUpdate, current_user: CurrentUser, session: DbSession):
    repo = UserRepository(session)
    updated = await repo.update(current_user, **body.model_dump(exclude_none=True))
    return ApiResponse(data=UserResponse.model_validate(updated))
