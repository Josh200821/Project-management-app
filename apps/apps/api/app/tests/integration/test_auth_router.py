"""Integration tests for auth endpoints.

Note: these were rewritten to assert against the ApiResponse envelope
({"data": ..., "meta": ..., "errors": [...]}) that every router in this codebase
returns (see schemas/common.py) -- the original assertions here expected an
unwrapped body, which didn't match the router's declared response_model and
would have failed regardless of whether the endpoint worked.
"""

import pytest


@pytest.mark.asyncio
async def test_register_new_user(client):
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "SecurePass123!",
            "full_name": "Test User",
        },
    )
    assert response.status_code == 201
    data = response.json()["data"]
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_register_duplicate_email_returns_409(client):
    payload = {"email": "dupe@example.com", "password": "SecurePass123!", "full_name": "Dupe"}
    first = await client.post("/api/v1/auth/register", json=payload)
    assert first.status_code == 201
    second = await client.post("/api/v1/auth/register", json=payload)
    assert second.status_code == 409


@pytest.mark.asyncio
async def test_login_with_valid_credentials(client):
    # Register first
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "logintest@example.com",
            "password": "SecurePass123!",
        },
    )
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "logintest@example.com",
            "password": "SecurePass123!",
        },
    )
    assert response.status_code == 200
    assert "access_token" in response.json()["data"]
    # Refresh token should be set as an httpOnly cookie, not in the JSON body.
    assert "refresh_token" in response.cookies


@pytest.mark.asyncio
async def test_login_wrong_password_returns_401(client):
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "nobody@example.com",
            "password": "wrongpassword",
        },
    )
    assert response.status_code == 401
