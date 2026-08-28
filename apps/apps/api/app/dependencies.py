"""Shared FastAPI dependencies."""

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_access_token
from app.db.base import get_session
from app.db.models.user import User
from app.repositories.user_repo import UserRepository

bearer = HTTPBearer()


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> User:
    token = credentials.credentials
    payload = decode_access_token(token)
    if not payload or payload.get("type") != "access":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    repo = UserRepository(session)
    user = await repo.get_active(payload.get("sub", ""))
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
DbSession = Annotated[AsyncSession, Depends(get_session)]


def require_role(*roles: str):
    """Gate an endpoint to organization members holding one of `roles`.

    NOTE: this only verifies the caller is authenticated; it does not yet check
    org-membership role, since the org id isn't available in a generic dependency
    without also depending on the path structure. Tracked as a known gap — see
    README "Not started". Prefer explicit per-route checks against
    OrganizationRepository until this is wired up.
    """

    async def _checker(current_user: CurrentUser) -> User:
        return current_user

    return _checker
