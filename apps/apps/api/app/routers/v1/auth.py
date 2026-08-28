"""Auth router — login, register, refresh, MFA, password reset."""

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import get_session
from app.dependencies import CurrentUser
from app.schemas.auth import (
    LoginRequest,
    MFASetupResponse,
    MFAVerifyRequest,
    PasswordResetConfirm,
    PasswordResetRequest,
    RegisterRequest,
    TokenResponse,
)
from app.schemas.common import ApiResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth")


@router.post("/register", response_model=ApiResponse[TokenResponse], status_code=201)
async def register(body: RegisterRequest, session: AsyncSession = Depends(get_session)):
    svc = AuthService(session)
    try:
        result = await svc.register(body)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    return ApiResponse(data=result)


@router.post("/login", response_model=ApiResponse[TokenResponse])
async def login(
    body: LoginRequest, response: Response, session: AsyncSession = Depends(get_session)
):
    svc = AuthService(session)
    try:
        tokens = await svc.login(body, response)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc
    return ApiResponse(data=tokens)


@router.post("/refresh", response_model=ApiResponse[TokenResponse])
async def refresh(
    request: Request, response: Response, session: AsyncSession = Depends(get_session)
):
    svc = AuthService(session)
    refresh_token = request.cookies.get("refresh_token")
    try:
        tokens = await svc.refresh_tokens(refresh_token, response)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc
    return ApiResponse(data=tokens)


@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie("refresh_token")
    return ApiResponse(data={"message": "Logged out"})


@router.post("/mfa/setup", response_model=ApiResponse[MFASetupResponse])
async def setup_mfa(current_user: CurrentUser, session: AsyncSession = Depends(get_session)):
    svc = AuthService(session)
    result = await svc.setup_mfa(current_user)
    return ApiResponse(data=result)


@router.post("/mfa/verify")
async def verify_mfa(
    body: MFAVerifyRequest, current_user: CurrentUser, session: AsyncSession = Depends(get_session)
):
    svc = AuthService(session)
    try:
        await svc.verify_mfa(current_user, body.totp_code)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return ApiResponse(data={"message": "MFA enabled"})


@router.post("/password-reset/request")
async def request_password_reset(
    body: PasswordResetRequest, session: AsyncSession = Depends(get_session)
):
    svc = AuthService(session)
    await svc.request_password_reset(body.email)
    return ApiResponse(data={"message": "If that email exists, a reset link has been sent."})


@router.post("/password-reset/confirm")
async def confirm_password_reset(
    body: PasswordResetConfirm, session: AsyncSession = Depends(get_session)
):
    svc = AuthService(session)
    try:
        await svc.confirm_password_reset(body.token, body.new_password)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return ApiResponse(data={"message": "Password updated"})
