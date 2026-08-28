"""Organizations router."""

from fastapi import APIRouter

from app.dependencies import CurrentUser, DbSession
from app.schemas.common import ApiResponse
from app.schemas.organization import InviteMemberRequest, OrganizationCreate, OrganizationResponse
from app.services.organization_service import OrganizationService

router = APIRouter(prefix="/organizations")


@router.post("", response_model=ApiResponse[OrganizationResponse], status_code=201)
async def create_org(body: OrganizationCreate, current_user: CurrentUser, session: DbSession):
    svc = OrganizationService(session)
    org = await svc.create(body, current_user.id)
    return ApiResponse(data=OrganizationResponse.model_validate(org))


@router.get("", response_model=ApiResponse[list[OrganizationResponse]])
async def list_orgs(current_user: CurrentUser, session: DbSession):
    svc = OrganizationService(session)
    orgs = await svc.get_user_organizations(current_user.id)
    return ApiResponse(data=[OrganizationResponse.model_validate(o) for o in orgs])


@router.post("/{org_id}/members/invite")
async def invite_member(
    org_id: str, body: InviteMemberRequest, current_user: CurrentUser, session: DbSession
):
    from app.workers.email_tasks import send_invitation_email

    send_invitation_email.delay(org_id, body.email, body.role, str(current_user.id))
    return ApiResponse(data={"message": "Invitation sent"})
