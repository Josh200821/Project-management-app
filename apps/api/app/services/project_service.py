"""Project service."""
from typing import List
from uuid import UUID

from slugify import slugify
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.project_repo import ProjectRepository
from app.schemas.project import ProjectCreate, ProjectUpdate


class ProjectService:
    def __init__(self, session: AsyncSession) -> None:
        self.repo = ProjectRepository(session)

    async def create(self, org_id: UUID, data: ProjectCreate, created_by: UUID):
        slug = data.slug or slugify(data.name)
        return await self.repo.create(
            organization_id=org_id,
            name=data.name,
            slug=slug,
            description=data.description,
            created_by=created_by,
        )

    async def list_by_org(self, org_id: UUID, offset: int = 0, limit: int = 20):
        return await self.repo.get_by_org(org_id, offset, limit)

    async def get(self, project_id: UUID):
        project = await self.repo.get(project_id)
        if not project:
            raise ValueError("Project not found")
        return project

    async def update(self, project_id: UUID, data: ProjectUpdate):
        project = await self.repo.get(project_id)
        if not project:
            raise ValueError("Project not found")
        return await self.repo.update(project, **data.model_dump(exclude_none=True))

    async def delete(self, project_id: UUID) -> None:
        project = await self.repo.get(project_id)
        if project:
            await self.repo.update(project, status="deleted")
