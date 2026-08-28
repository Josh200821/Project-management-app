"""Project service."""

from uuid import UUID

from slugify import slugify
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.project import Project
from app.repositories.project_repo import ProjectRepository
from app.schemas.project import ProjectCreate, ProjectUpdate


class ProjectService:
    """Note: the repository is constructed per-method (not cached on self) so unit
    tests can patch app.services.project_service.ProjectRepository per-call. See
    tests/unit/test_project_service.py."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, org_id: UUID, data: ProjectCreate, created_by: UUID) -> Project:
        repo = ProjectRepository(self.session)
        base_slug = data.slug or slugify(data.name)
        slug = base_slug
        suffix = 1
        while await repo.get_by_slug(org_id, slug):
            suffix += 1
            slug = f"{base_slug}-{suffix}"
        return await repo.create(
            organization_id=org_id,
            name=data.name,
            slug=slug,
            description=data.description,
            created_by=created_by,
        )

    async def list_by_org(self, org_id: UUID, offset: int = 0, limit: int = 20) -> list[Project]:
        repo = ProjectRepository(self.session)
        return await repo.get_by_org(org_id, offset, limit)

    async def get(self, project_id: UUID) -> Project:
        repo = ProjectRepository(self.session)
        project = await repo.get(project_id)
        if not project:
            raise ValueError("Project not found")
        return project

    async def update(self, project_id: UUID, data: ProjectUpdate) -> Project:
        repo = ProjectRepository(self.session)
        project = await repo.get(project_id)
        if not project:
            raise ValueError("Project not found")
        return await repo.update(project, **data.model_dump(exclude_none=True))

    async def delete(self, project_id: UUID) -> None:
        repo = ProjectRepository(self.session)
        project = await repo.get(project_id)
        if project:
            await repo.update(project, status="deleted")
