"""Attachments router."""

import uuid

from fastapi import APIRouter

from app.dependencies import CurrentUser
from app.schemas.common import ApiResponse
from app.services.storage_service import StorageService

router = APIRouter(prefix="/tasks/{task_id}/attachments")


@router.post("/presigned-upload")
async def get_upload_url(
    task_id: str, file_name: str, content_type: str, current_user: CurrentUser
):
    svc = StorageService()
    key = f"attachments/{task_id}/{uuid.uuid4()}/{file_name}"
    url = svc.generate_presigned_upload_url(key, content_type)
    return ApiResponse(data={"upload_url": url, "key": key})


@router.get("/{key:path}/download")
async def get_download_url(task_id: str, key: str, current_user: CurrentUser):
    svc = StorageService()
    url = svc.generate_presigned_download_url(key)
    return ApiResponse(data={"download_url": url})
