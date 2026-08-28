"""Unit tests for project service."""

from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest

from app.schemas.project import ProjectCreate
from app.services.project_service import ProjectService


@pytest.fixture
def mock_session():
    return AsyncMock()


@pytest.fixture
def project_service(mock_session):
    return ProjectService(mock_session)


class TestProjectService:
    async def test_create_generates_slug(self, project_service):
        owner_id = uuid4()
        with patch("app.services.project_service.ProjectRepository") as MockRepo:
            mock_repo = MockRepo.return_value
            mock_repo.get_by_slug = AsyncMock(return_value=None)
            mock_repo.create = AsyncMock(
                return_value=MagicMock(
                    id=uuid4(),
                    name="My Project",
                    slug="my-project",
                    organization_id=uuid4(),
                    status="active",
                    task_counter=0,
                    description=None,
                    created_at=MagicMock(),
                )
            )
            await project_service.create(uuid4(), ProjectCreate(name="My Project"), owner_id)
            call_kwargs = mock_repo.create.call_args.kwargs
            assert "slug" in call_kwargs

    async def test_get_not_found_raises(self, project_service):
        with patch("app.services.project_service.ProjectRepository") as MockRepo:
            mock_repo = MockRepo.return_value
            mock_repo.get = AsyncMock(return_value=None)
            with pytest.raises(ValueError, match="not found"):
                await project_service.get(uuid4())
