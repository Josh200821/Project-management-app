"""Organization repository."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.organization import Organization
from app.db.models.organization_member import OrganizationMember
from app.repositories.base import BaseRepository


class OrganizationRepository(BaseRepository[Organization]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Organization, session)

    async def get_by_slug(self, slug: str) -> Organization | None:
        result = await self.session.execute(select(Organization).where(Organization.slug == slug))
        return result.scalar_one_or_none()

    async def get_user_organizations(self, user_id: UUID) -> list[Organization]:
        result = await self.session.execute(
            select(Organization)
            .join(OrganizationMember, OrganizationMember.organization_id == Organization.id)
            .where(OrganizationMember.user_id == user_id)
        )
        return list(result.scalars().all())
