"""PostgreSQL Row-Level Security tenant context setter."""

from sqlalchemy.ext.asyncio import AsyncSession


async def set_tenant_context(session: AsyncSession, tenant_id: str) -> None:
    """Set the app.tenant_id parameter for RLS policies."""
    await session.execute(f"SET LOCAL app.tenant_id = '{tenant_id}'")
