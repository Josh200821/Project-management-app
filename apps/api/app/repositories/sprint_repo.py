"""Sprint repository."""
from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.sprint import Sprint
from app.repositories.base import BaseRepository


class SprintRepository(BaseRepository[Sprint]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Sprint, session)

    async def get_by_project(self, project_id: UUID) -> List[Sprint]:
        result = await self.session.execute(
            select(Sprint)
            .where(Sprint.project_id == project_id)
            .order_by(Sprint.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_active(self, project_id: UUID) -> Optional[Sprint]:
        result = await self.session.execute(
            select(Sprint).where(
                Sprint.project_id == project_id, Sprint.status == "active"
            )
        )
        return result.scalar_one_or_none()
