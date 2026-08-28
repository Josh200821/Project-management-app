"""User schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    email: EmailStr
    full_name: str | None = None
    avatar_url: str | None = None


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    full_name: str | None = None
    avatar_url: str | None = None


class UserResponse(UserBase):
    id: UUID
    mfa_enabled: bool
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}
