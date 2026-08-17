"""Organization schemas."""
from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel


class OrganizationCreate(BaseModel):
    name: str
    slug: Optional[str] = None


class OrganizationUpdate(BaseModel):
    name: Optional[str] = None
    logo_url: Optional[str] = None


class OrganizationResponse(BaseModel):
    id: UUID
    name: str
    slug: str
    logo_url: Optional[str]
    plan: str
    created_at: datetime

    model_config = {"from_attributes": True}


class InviteMemberRequest(BaseModel):
    email: str
    role: str = "member"


class MemberResponse(BaseModel):
    user_id: UUID
    email: str
    full_name: Optional[str]
    role: str
    accepted_at: Optional[datetime]

    model_config = {"from_attributes": True}
