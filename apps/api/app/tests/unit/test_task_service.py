"""Unit tests for TaskService."""
import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.services.task_service import TaskService


@pytest.fixture
def mock_session():
    session = MagicMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.flush = AsyncMock()
    session.refresh = AsyncMock()
    return session


@pytest.mark.asyncio
async def test_create_task_assigns_task_number(mock_session):
    service = TaskService(mock_session)
    project_id = uuid.uuid4()
    service.repo.next_task_number = AsyncMock(return_value=5)
    service.repo.create = AsyncMock(return_value=MagicMock(id=uuid.uuid4(), task_number=5))

    task = await service.create_task(
        project_id=project_id,
        title="Test task",
        created_by=uuid.uuid4(),
    )

    service.repo.next_task_number.assert_called_once_with(project_id)
    assert task.task_number == 5


@pytest.mark.asyncio
async def test_get_task_returns_none_for_missing(mock_session):
    service = TaskService(mock_session)
    service.repo.get = AsyncMock(return_value=None)
    result = await service.get_task(uuid.uuid4())
    assert result is None


@pytest.mark.asyncio
async def test_delete_task_returns_false_when_not_found(mock_session):
    service = TaskService(mock_session)
    service.repo.get = AsyncMock(return_value=None)
    result = await service.delete_task(uuid.uuid4())
    assert result is False
