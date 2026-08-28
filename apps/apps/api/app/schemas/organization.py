"""Organization schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class OrganizationCreate(BaseModel):
    name: str
    slug: str | None = None


class OrganizationUpdate(BaseModel):
    name: str | None = None
    logo_url: str | None = None


class OrganizationResponse(BaseModel):
    id: UUID
    name: str
    slug: str
    logo_url: str | None
    plan: str
    created_at: datetime

    model_config = {"from_attributes": True}


class InviteMemberRequest(BaseModel):
    email: str
    role: str = "member"


class MemberResponse(BaseModel):
    user_id: UUID
    email: str
    full_name: str | None
    role: str
    accepted_at: datetime | None

    model_config = {"from_attributes": True}
