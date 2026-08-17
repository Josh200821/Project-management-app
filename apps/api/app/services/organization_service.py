"""Organization service."""
from typing import List
from uuid import UUID

from slugify import slugify
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.organization_repo import OrganizationRepository
from app.schemas.organization import OrganizationCreate, OrganizationUpdate


class OrganizationService:
    def __init__(self, session: AsyncSession) -> None:
        self.repo = OrganizationRepository(session)

    async def create(self, data: OrganizationCreate, owner_id: UUID):
        slug = data.slug or slugify(data.name)
        existing = await self.repo.get_by_slug(slug)
        if existing:
            slug = f"{slug}-{str(owner_id)[:8]}"
        org = await self.repo.create(name=data.name, slug=slug)
        # Add owner as admin member
        from app.db.models.organization_member import OrganizationMember
        member = OrganizationMember(
            organization_id=org.id, user_id=owner_id, role="admin"
        )
        self.repo.session.add(member)
        await self.repo.session.flush()
        return org

    async def get_user_organizations(self, user_id: UUID):
        return await self.repo.get_user_organizations(user_id)

    async def update(self, org_id: UUID, data: OrganizationUpdate):
        org = await self.repo.get(org_id)
        if not org:
            raise ValueError("Organization not found")
        return await self.repo.update(org, **data.model_dump(exclude_none=True))
