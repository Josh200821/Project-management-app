"""SQLAlchemy async engine and session factory."""
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

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

ReadAsyncSessionLocal = async_sessionmaker(
    read_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_session():
    async with AsyncSessionLocal() as session:
        yield session


class Base(DeclarativeBase):
    pass

# Database
DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/saas_platform"
DATABASE_URL_SYNC: str = "postgresql://postgres:postgres@localhost:5432/saas_platform"
DATABASE_URL_REPLICA: str = ""

DATABASE_POOL_SIZE: int = 10
DATABASE_MAX_OVERFLOW: int = 20
