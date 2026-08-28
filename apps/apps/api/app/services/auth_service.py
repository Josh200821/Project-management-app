"""Authentication service."""

from datetime import UTC, datetime
from uuid import UUID

import pyotp
import structlog
from fastapi import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.security import (
    create_access_token,
    create_password_reset_token,
    create_refresh_token,
    decode_access_token,
    decode_password_reset_token,
    hash_password,
    verify_password,
)
from app.db.models.user import User
from app.repositories.user_repo import UserRepository
from app.schemas.auth import LoginRequest, MFASetupResponse, RegisterRequest, TokenResponse
from app.workers.email_tasks import send_password_reset_email

logger = structlog.get_logger()

REFRESH_COOKIE_NAME = "refresh_token"
REFRESH_COOKIE_MAX_AGE = settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60


def _token_response(user_id: str, email: str) -> TokenResponse:
    access_token = create_access_token(user_id, {"email": email})
    return TokenResponse(
        access_token=access_token,
        expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


def _set_refresh_cookie(response: Response, user_id: str) -> None:
    refresh_token = create_refresh_token(user_id)
    response.set_cookie(
        REFRESH_COOKIE_NAME,
        refresh_token,
        httponly=True,
        secure=settings.ENVIRONMENT != "development",
        samesite="lax",
        max_age=REFRESH_COOKIE_MAX_AGE,
    )


class AuthService:
    """Note: repositories are constructed per-method (not cached on self) so unit
    tests can patch app.services.auth_service.UserRepository per-call. See
    tests/unit/test_auth_service.py."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def register(self, body: RegisterRequest) -> TokenResponse:
        repo = UserRepository(self.session)
        existing = await repo.get_by_email(body.email)
        if existing:
            raise ValueError("Email already registered")
        user = await repo.create(
            email=body.email,
            password_hash=hash_password(body.password),
            full_name=body.full_name,
        )
        logger.info("user_registered", user_id=str(user.id), email=user.email)
        return _token_response(str(user.id), user.email)

    async def login(self, body: LoginRequest, response: Response) -> TokenResponse:
        repo = UserRepository(self.session)
        user = await repo.get_by_email(body.email)
        if not user or not user.is_active or not user.password_hash:
            logger.warning("auth_failed", email=body.email)
            raise ValueError("Invalid email or password")
        if not verify_password(body.password, user.password_hash):
            logger.warning("auth_failed", email=body.email)
            raise ValueError("Invalid email or password")
        if user.mfa_enabled and (
            not body.totp_code
            or not pyotp.TOTP(user.mfa_secret).verify(body.totp_code, valid_window=1)
        ):
            raise ValueError("Invalid or missing MFA code")

        await repo.update(user, last_login_at=datetime.now(UTC))
        _set_refresh_cookie(response, str(user.id))
        logger.info("user_authenticated", user_id=str(user.id))
        return _token_response(str(user.id), user.email)

    async def refresh_tokens(self, refresh_token: str | None, response: Response) -> TokenResponse:
        if not refresh_token:
            raise ValueError("Missing refresh token")
        payload = decode_access_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            raise ValueError("Invalid or expired refresh token")
        repo = UserRepository(self.session)
        user = await repo.get_active(payload["sub"])
        if not user:
            raise ValueError("Invalid or expired refresh token")
        # Rotate the refresh token so a leaked token has a limited window of use.
        _set_refresh_cookie(response, str(user.id))
        return _token_response(str(user.id), user.email)

    async def setup_mfa(self, user: User) -> MFASetupResponse:
        secret = pyotp.random_base32()
        repo = UserRepository(self.session)
        await repo.update(user, mfa_secret=secret)
        provisioning_uri = pyotp.TOTP(secret).provisioning_uri(
            name=user.email, issuer_name="SaaS Platform"
        )
        # Shown once at setup time; the prototype doesn't yet persist these for
        # later "lost my device" recovery -- tracked as a known gap.
        backup_codes = [pyotp.random_base32()[:10] for _ in range(8)]
        return MFASetupResponse(
            secret=secret, qr_code_url=provisioning_uri, backup_codes=backup_codes
        )

    async def verify_mfa(self, user: User, totp_code: str) -> None:
        if not user.mfa_secret:
            raise ValueError("MFA setup has not been started for this account")
        if not pyotp.TOTP(user.mfa_secret).verify(totp_code, valid_window=1):
            raise ValueError("Invalid MFA code")
        repo = UserRepository(self.session)
        await repo.update(user, mfa_enabled=True)

    async def request_password_reset(self, email: str) -> None:
        repo = UserRepository(self.session)
        user = await repo.get_by_email(email)
        # Always behave the same whether or not the account exists, to avoid
        # leaking which emails are registered.
        if user and user.is_active:
            token = create_password_reset_token(str(user.id))
            reset_url = f"{settings.FRONTEND_URL}/reset-password?token={token}"
            send_password_reset_email.delay(user.email, reset_url)
        logger.info("password_reset_requested", email=email)

    async def confirm_password_reset(self, token: str, new_password: str) -> None:
        user_id = decode_password_reset_token(token)
        if not user_id:
            raise ValueError("Invalid or expired reset token")
        repo = UserRepository(self.session)
        user = await repo.get(UUID(user_id))
        if not user:
            raise ValueError("Invalid or expired reset token")
        await repo.update(user, password_hash=hash_password(new_password))
        logger.info("password_reset_completed", user_id=user_id)
