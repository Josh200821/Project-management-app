"""Auth router — login, register, refresh, MFA, OAuth."""
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import get_session
from app.schemas.auth import (
    LoginRequest, RegisterRequest, TokenResponse,
    MFASetupResponse, MFAVerifyRequest, PasswordResetRequest, PasswordResetConfirm,
)
from app.schemas.common import ApiResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth")


@router.post("/register", response_model=ApiResponse[TokenResponse], status_code=201)
async def register(body: RegisterRequest, session: AsyncSession = Depends(get_session)):
    svc = AuthService(session)
    result = await svc.register(body)
    return ApiResponse(data=result)


@router.post("/login", response_model=ApiResponse[TokenResponse])
async def login(body: LoginRequest, response: Response, session: AsyncSession = Depends(get_session)):
    svc = AuthService(session)
    tokens = await svc.login(body, response)
    return ApiResponse(data=tokens)


@router.post("/refresh", response_model=ApiResponse[TokenResponse])
async def refresh(response: Response, session: AsyncSession = Depends(get_session)):
    # Refresh token read from httpOnly cookie inside service
    svc = AuthService(session)
    tokens = await svc.refresh_tokens(response)
    return ApiResponse(data=tokens)


@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie("refresh_token")
    return ApiResponse(data={"message": "Logged out"})


@router.post("/mfa/setup", response_model=ApiResponse[MFASetupResponse])
async def setup_mfa(session: AsyncSession = Depends(get_session)):
    svc = AuthService(session)
    result = await svc.setup_mfa()
    return ApiResponse(data=result)


@router.post("/mfa/verify")
async def verify_mfa(body: MFAVerifyRequest, session: AsyncSession = Depends(get_session)):
    svc = AuthService(session)
    await svc.verify_mfa(body.totp_code)
    return ApiResponse(data={"message": "MFA enabled"})


@router.post("/password-reset/request")
async def request_password_reset(body: PasswordResetRequest, session: AsyncSession = Depends(get_session)):
    svc = AuthService(session)
    await svc.request_password_reset(body.email)
    return ApiResponse(data={"message": "If that email exists, a reset link has been sent."})


@router.post("/password-reset/confirm")
async def confirm_password_reset(body: PasswordResetConfirm, session: AsyncSession = Depends(get_session)):
    svc = AuthService(session)
    await svc.confirm_password_reset(body.token, body.new_password)
    return ApiResponse(data={"message": "Password updated"})
