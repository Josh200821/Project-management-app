"""Unit tests for auth service."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.schemas.auth import RegisterRequest
from app.services.auth_service import AuthService


@pytest.fixture
def mock_session():
    session = AsyncMock()
    session.flush = AsyncMock()
    session.refresh = AsyncMock()
    return session


@pytest.fixture
def auth_service(mock_session):
    return AuthService(mock_session)


class TestRegister:
    async def test_register_creates_user(self, auth_service, mock_session):
        with patch("app.services.auth_service.UserRepository") as MockRepo:
            mock_repo = MockRepo.return_value
            mock_repo.get_by_email = AsyncMock(return_value=None)
            mock_repo.create = AsyncMock(
                return_value=MagicMock(id="test-uuid", email="test@example.com")
            )
            with patch("app.services.auth_service.create_access_token", return_value="token"):
                result = await auth_service.register(
                    RegisterRequest(
                        email="test@example.com", password="Secure123!", full_name="Test User"
                    )
                )
            assert result.access_token == "token"

    async def test_register_duplicate_email_raises(self, auth_service, mock_session):
        with patch("app.services.auth_service.UserRepository") as MockRepo:
            mock_repo = MockRepo.return_value
            mock_repo.get_by_email = AsyncMock(return_value=MagicMock())
            with pytest.raises(ValueError, match="already registered"):
                await auth_service.register(
                    RegisterRequest(
                        email="exists@example.com", password="Secure123!", full_name="Test"
                    )
                )


class TestPasswordHashing:
    def test_password_not_stored_in_plaintext(self):
        from app.core.security import hash_password, verify_password

        hashed = hash_password("MySecret123!")
        assert hashed != "MySecret123!"
        assert verify_password("MySecret123!", hashed)
        assert not verify_password("wrong", hashed)
