"""Notification repository."""
from typing import List
from uuid import UUID
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.notification import Notification
from app.repositories.base import BaseRepository


class NotificationRepository(BaseRepository[Notification]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Notification, session)

    async def get_unread(self, user_id: UUID, limit: int = 30) -> List[Notification]:
        result = await self.session.execute(
            select(Notification)
            .where(Notification.user_id == user_id, Notification.read_at == None)
            .order_by(Notification.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def mark_all_read(self, user_id: UUID) -> None:
        from datetime import datetime, timezone
        await self.session.execute(
            update(Notification)
            .where(Notification.user_id == user_id, Notification.read_at == None)
            .values(read_at=datetime.now(timezone.utc))
        )
        await self.session.flush()
