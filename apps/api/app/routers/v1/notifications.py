"""Notifications router."""
from fastapi import APIRouter
from app.dependencies import CurrentUser, DbSession
from app.schemas.common import ApiResponse
from app.services.notification_service import NotificationService

router = APIRouter(prefix="/notifications")


@router.get("")
async def list_notifications(current_user: CurrentUser, session: DbSession):
    svc = NotificationService(session)
    notifs = await svc.get_unread(current_user.id)
    return ApiResponse(data=[{"id": str(n.id), "title": n.title, "body": n.body, "type": n.type, "created_at": str(n.created_at)} for n in notifs])


@router.post("/{notification_id}/read")
async def mark_read(notification_id: str, current_user: CurrentUser, session: DbSession):
    from uuid import UUID
    svc = NotificationService(session)
    await svc.mark_read(UUID(notification_id))
    return ApiResponse(data={"message": "Marked as read"})


@router.post("/read-all")
async def mark_all_read(current_user: CurrentUser, session: DbSession):
    svc = NotificationService(session)
    await svc.mark_all_read(current_user.id)
    return ApiResponse(data={"message": "All marked as read"})
