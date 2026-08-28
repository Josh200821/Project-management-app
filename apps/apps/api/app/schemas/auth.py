"""Auth schemas."""

from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    totp_code: str | None = None


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str | None = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class RefreshResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class MFASetupResponse(BaseModel):
    secret: str
    qr_code_url: str
    backup_codes: list[str]


class MFAVerifyRequest(BaseModel):
    totp_code: str


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str
