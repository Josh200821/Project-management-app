"""Integration tests for project router."""
import pytest
from httpx import AsyncClient


@pytest.mark.integration
class TestProjectRouter:
    async def test_create_project(self, async_client: AsyncClient, auth_headers: dict, test_org_id: str):
        res = await async_client.post(
            f"/api/v1/organizations/{test_org_id}/projects",
            json={"name": "Integration Test Project", "description": "Test description"},
            headers=auth_headers,
        )
        assert res.status_code == 201
        data = res.json()["data"]
        assert data["name"] == "Integration Test Project"
        assert data["slug"] == "integration-test-project"
        assert data["status"] == "active"

    async def test_list_projects_for_org(self, async_client: AsyncClient, auth_headers: dict, test_org_id: str):
        res = await async_client.get(
            f"/api/v1/organizations/{test_org_id}/projects",
            headers=auth_headers,
        )
        assert res.status_code == 200
        assert isinstance(res.json()["data"], list)

    async def test_delete_project_soft_deletes(self, async_client: AsyncClient, auth_headers: dict, test_org_id: str):
        create_res = await async_client.post(
            f"/api/v1/organizations/{test_org_id}/projects",
            json={"name": "To Delete"},
            headers=auth_headers,
        )
        project_id = create_res.json()["data"]["id"]
        del_res = await async_client.delete(
            f"/api/v1/organizations/{test_org_id}/projects/{project_id}",
            headers=auth_headers,
        )
        assert del_res.status_code == 204
