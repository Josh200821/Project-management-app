"""SQLAlchemy async engine and session factory."""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import settings

engine = create_async_engine(
    settings.DATABASE_URL,
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_MAX_OVERFLOW,
    pool_pre_ping=True,
    echo=settings.DEBUG,
)

read_engine = create_async_engine(
    settings.effective_read_url,
    pool_size=10,
    max_overflow=5,
    pool_pre_ping=True,
)

AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
ReadAsyncSessionLocal = async_sessionmaker(read_engine, class_=AsyncSession, expire_on_commit=False)

# Alias kept for scripts (e.g. db/seed.py) that predate the get_session dependency.
async_session_factory = AsyncSessionLocal


class Base(DeclarativeBase):
    pass


# Imported for its side effect: registers every model with the declarative
# registry so string-based relationship() targets (e.g. "Comment", "Sprint")
# resolve correctly no matter which entrypoint (uvicorn, alembic, celery,
# pytest) imported this module first. Placed after `Base` is defined, since
# every model file does `from app.db.base import Base`.
from app.db import models as _models  # noqa: E402, F401


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency: yields a request-scoped session, committing on success."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_read_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency: yields a read-only session against the read replica (or primary)."""
    async with ReadAsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
