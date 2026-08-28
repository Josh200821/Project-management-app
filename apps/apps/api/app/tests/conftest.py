"""Shared pytest fixtures.

Two things had to be fixed here to get integration tests running at all:

1. No JWT keypair existed anywhere for the app to sign/verify tokens with
   (see the README's "JWT keys are never generated" gap), so we generate a
   throwaway RS256 keypair to a temp dir and point Settings at it via env
   vars *before* app.config (and anything that imports it) is ever imported.

2. The original `client` fixture wrapped the real `app` directly, which uses
   app.db.base's module-level `engine` -- a singleton created once, bound to
   whatever event loop was active at import time. pytest-asyncio (mode=auto)
   gives each async test function its own event loop by default, so the
   second test to touch that engine would crash with "Future attached to a
   different loop" the moment it tried to reuse a pooled connection from a
   different test's loop. Fixed by making the test engine function-scoped
   (always built in the current test's loop) and overriding the app's
   get_session/get_read_session dependencies to use it instead of ever
   touching the real engine during tests.
"""

import os
import tempfile
from collections.abc import AsyncGenerator
from pathlib import Path
from uuid import UUID, uuid4

import pytest_asyncio
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

_key_dir = tempfile.mkdtemp(prefix="jwt-test-keys-")
_private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
_private_path = Path(_key_dir) / "private.pem"
_public_path = Path(_key_dir) / "public.pem"
_private_path.write_bytes(
    _private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption(),
    )
)
_public_path.write_bytes(
    _private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
)
os.environ.setdefault("JWT_PRIVATE_KEY_PATH", str(_private_path))
os.environ.setdefault("JWT_PUBLIC_KEY_PATH", str(_public_path))
os.environ.setdefault(
    "DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/saas_test"
)
os.environ.setdefault(
    "DATABASE_URL_SYNC", "postgresql://postgres:postgres@localhost:5432/saas_test"
)
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/1")
os.environ.setdefault("CELERY_BROKER_URL", "redis://localhost:6379/2")
os.environ.setdefault("ENVIRONMENT", "test")

from app.db.base import Base, get_read_session, get_session  # noqa: E402
from app.main import app  # noqa: E402

TEST_DATABASE_URL = os.environ["DATABASE_URL"]


@pytest_asyncio.fixture
async def test_engine():
    engine = create_async_engine(TEST_DATABASE_URL, echo=False, poolclass=NullPool)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    session_factory = async_sessionmaker(test_engine, expire_on_commit=False)
    async with session_factory() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def client(test_engine) -> AsyncGenerator[AsyncClient, None]:
    session_factory = async_sessionmaker(test_engine, expire_on_commit=False)

    async def _override_session() -> AsyncGenerator[AsyncSession, None]:
        async with session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    app.dependency_overrides[get_session] = _override_session
    app.dependency_overrides[get_read_session] = _override_session
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
            yield c
    finally:
        app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def async_client(client: AsyncClient) -> AsyncClient:
    """Alias: test_project_router.py/test_task_router.py use this name,
    test_auth_router.py uses `client` directly. Same underlying client."""
    return client


@pytest_asyncio.fixture
async def auth_headers(client: AsyncClient) -> dict:
    email = f"integration-{uuid4().hex[:8]}@example.com"
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "SecurePass123!",
            "full_name": "Integration Test User",
        },
    )
    res = await client.post(
        "/api/v1/auth/login", json={"email": email, "password": "SecurePass123!"}
    )
    token = res.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def test_org_id(db_session: AsyncSession) -> str:
    from app.db.models.organization import Organization

    org = Organization(name="Integration Test Org", slug=f"test-org-{uuid4().hex[:8]}")
    db_session.add(org)
    await db_session.commit()
    await db_session.refresh(org)
    return str(org.id)


@pytest_asyncio.fixture
async def test_project_id(db_session: AsyncSession, test_org_id: str) -> str:
    from app.db.models.project import Project

    project = Project(
        organization_id=UUID(test_org_id),
        name="Integration Test Project",
        slug=f"test-project-{uuid4().hex[:8]}",
    )
    db_session.add(project)
    await db_session.commit()
    await db_session.refresh(project)
    return str(project.id)
