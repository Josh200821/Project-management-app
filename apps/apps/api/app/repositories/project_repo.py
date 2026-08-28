"""Project repository."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.project import Project
from app.repositories.base import BaseRepository


class ProjectRepository(BaseRepository[Project]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Project, session)

    async def get_by_org(self, org_id: UUID, offset: int = 0, limit: int = 20) -> list[Project]:
        result = await self.session.execute(
            select(Project)
            .where(Project.organization_id == org_id, Project.status != "deleted")
            .offset(offset)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_slug(self, org_id: UUID, slug: str) -> Project | None:
        result = await self.session.execute(
            select(Project).where(Project.organization_id == org_id, Project.slug == slug)
        )
        return result.scalar_one_or_none()

    async def increment_task_counter(self, project_id: UUID) -> int:
        project = await self.get(project_id)
        if project:
            project.task_counter += 1
            await self.session.flush()
            return project.task_counter
        return 1
