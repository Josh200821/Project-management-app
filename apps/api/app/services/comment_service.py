"""Comment service."""
import re
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.comment_repo import CommentRepository
from app.repositories.user_repo import UserRepository
from app.schemas.comment import CommentCreate, CommentUpdate


MENTION_RE = re.compile(r"@(\w+)")


class CommentService:
    def __init__(self, session: AsyncSession) -> None:
        self.repo = CommentRepository(session)
        self.user_repo = UserRepository(session)

    async def create(self, task_id: UUID, data: CommentCreate, author_id: UUID):
        comment = await self.repo.create(
            task_id=task_id, body=data.body, author_id=author_id
        )
        # Dispatch mention notifications asynchronously
        mentions = MENTION_RE.findall(data.body)
        if mentions:
            from app.workers.notification_tasks import send_mention_notifications
            send_mention_notifications.delay(
                str(task_id), str(author_id), mentions
            )
        return comment

    async def list_by_task(self, task_id: UUID):
        return await self.repo.get_by_task(task_id)

    async def update(self, comment_id: UUID, data: CommentUpdate):
        from datetime import datetime, timezone
        comment = await self.repo.get(comment_id)
        if not comment:
            raise ValueError("Comment not found")
        return await self.repo.update(comment, body=data.body, edited_at=datetime.now(timezone.utc))

    async def delete(self, comment_id: UUID) -> None:
        comment = await self.repo.get(comment_id)
        if comment:
            await self.repo.delete(comment)
