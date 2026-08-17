"""Integration tests for auth endpoints."""
import pytest


@pytest.mark.asyncio
async def test_register_new_user(client):
    response = await client.post("/api/v1/auth/register", json={
        "email": "test@example.com",
        "password": "SecurePass123!",
        "full_name": "Test User",
    })
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "id" in data


@pytest.mark.asyncio
async def test_login_with_valid_credentials(client):
    # Register first
    await client.post("/api/v1/auth/register", json={
        "email": "logintest@example.com",
        "password": "SecurePass123!",
    })
    response = await client.post("/api/v1/auth/login", json={
        "email": "logintest@example.com",
        "password": "SecurePass123!",
    })
    assert response.status_code == 200
    assert "access_token" in response.json()


@pytest.mark.asyncio
async def test_login_wrong_password_returns_401(client):
    response = await client.post("/api/v1/auth/login", json={
        "email": "nobody@example.com",
        "password": "wrongpassword",
    })
    assert response.status_code == 401
