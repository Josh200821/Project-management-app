"""Notification service."""
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.notification_repo import NotificationRepository


class NotificationService:
    def __init__(self, session: AsyncSession) -> None:
        self.repo = NotificationRepository(session)

    async def get_unread(self, user_id: UUID):
        return await self.repo.get_unread(user_id)

    async def mark_read(self, notification_id: UUID) -> None:
        from datetime import datetime, timezone
        notif = await self.repo.get(notification_id)
        if notif:
            await self.repo.update(notif, read_at=datetime.now(timezone.utc))

    async def mark_all_read(self, user_id: UUID) -> None:
        await self.repo.mark_all_read(user_id)

    async def create(self, user_id: UUID, org_id: UUID, type: str, title: str, body: str = "", entity_type: str = "", entity_id: UUID = None):
        return await self.repo.create(
            user_id=user_id,
            organization_id=org_id,
            type=type,
            title=title,
            body=body,
            entity_type=entity_type,
            entity_id=entity_id,
        )
