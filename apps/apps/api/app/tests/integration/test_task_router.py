"""Integration tests for task router."""

import pytest
from httpx import AsyncClient


@pytest.mark.integration
class TestTaskRouter:
    async def test_create_task_requires_auth(self, async_client: AsyncClient):
        # FastAPI's HTTPBearer (0.110+) raises 401 for a missing Authorization
        # header, not 403 -- 401 is the more spec-correct code here (401 =
        # unauthenticated; 403 = authenticated but not permitted).
        res = await async_client.post("/api/v1/projects/some-id/tasks", json={"title": "Test"})
        assert res.status_code == 401

    async def test_create_task_authenticated(
        self, async_client: AsyncClient, auth_headers: dict, test_project_id: str
    ):
        res = await async_client.post(
            f"/api/v1/projects/{test_project_id}/tasks",
            json={"title": "Integration test task", "priority": "high"},
            headers=auth_headers,
        )
        assert res.status_code == 201
        data = res.json()["data"]
        assert data["title"] == "Integration test task"
        assert data["status"] == "todo"
        assert data["task_number"] == 1

    async def test_get_board_returns_grouped_tasks(
        self, async_client: AsyncClient, auth_headers: dict, test_project_id: str
    ):
        # Create tasks first
        for status in ["todo", "in_progress", "done"]:
            await async_client.post(
                f"/api/v1/projects/{test_project_id}/tasks",
                json={"title": f"Task {status}", "status": status},
                headers=auth_headers,
            )
        res = await async_client.get(
            f"/api/v1/projects/{test_project_id}/tasks/board",
            headers=auth_headers,
        )
        assert res.status_code == 200
        board = res.json()["data"]
        assert isinstance(board, dict)
