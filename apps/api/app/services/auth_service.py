"""Authentication service."""
import uuid
from datetime import datetime, timezone

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
)
from app.db.models.user import User
from app.repositories.base import BaseRepository

logger = structlog.get_logger()


class AuthService:
    def __init__(self, session: AsyncSession) -> None:
        self.user_repo = BaseRepository(User, session)
        self.session = session

    async def register(self, email: str, password: str, full_name: str | None = None) -> User:
        existing = await self.user_repo.list(email=email)
        if existing:
            raise ValueError("Email already registered")
        user = await self.user_repo.create(
            email=email,
            password_hash=hash_password(password),
            full_name=full_name,
        )
        logger.info("user_registered", user_id=str(user.id), email=email)
        return user

    async def authenticate(self, email: str, password: str) -> tuple[str, str] | None:
        users = await self.user_repo.list(email=email)
        if not users:
            return None
        user = users[0]
        if not user.password_hash or not verify_password(password, user.password_hash):
            logger.warning("auth_failed", email=email)
            return None
        await self.user_repo.update(
            user, last_login_at=datetime.now(timezone.utc)
        )
        access_token = create_access_token(str(user.id), {"email": user.email})
        refresh_token = create_refresh_token(str(user.id))
        logger.info("user_authenticated", user_id=str(user.id))
        return access_token, refresh_token
