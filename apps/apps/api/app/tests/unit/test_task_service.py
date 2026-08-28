"""Unit tests for TaskService.

Note: rewritten to call the service's actual method names (create/get/update/
delete/list_by_project), which match every other service in this codebase
(ProjectService, SprintService, ...) and what routers/v1/tasks.py actually
calls. The original file exercised create_task/get_task/delete_task methods
that didn't exist on TaskService at all.
"""

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
async def test_create_assigns_task_number(mock_session):
    service = TaskService(mock_session)
    project_id = uuid.uuid4()
    service.project_repo.increment_task_counter = AsyncMock(return_value=5)
    service.repo.create = AsyncMock(return_value=MagicMock(id=uuid.uuid4(), task_number=5))

    from app.schemas.task import TaskCreate

    task = await service.create(
        project_id=project_id,
        data=TaskCreate(title="Test task"),
        created_by=uuid.uuid4(),
    )

    service.project_repo.increment_task_counter.assert_called_once_with(project_id)
    assert task.task_number == 5


@pytest.mark.asyncio
async def test_get_task_raises_for_missing(mock_session):
    service = TaskService(mock_session)
    service.repo.get = AsyncMock(return_value=None)
    with pytest.raises(ValueError, match="not found"):
        await service.get(uuid.uuid4())


@pytest.mark.asyncio
async def test_delete_task_is_noop_when_not_found(mock_session):
    service = TaskService(mock_session)
    service.repo.get = AsyncMock(return_value=None)
    service.repo.delete = AsyncMock()
    await service.delete(uuid.uuid4())
    service.repo.delete.assert_not_called()
