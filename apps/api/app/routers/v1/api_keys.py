"""API Keys router."""
import secrets
import hashlib
from fastapi import APIRouter
from app.dependencies import CurrentUser, DbSession
from app.schemas.common import ApiResponse
from app.db.models.api_key import ApiKey

router = APIRouter(prefix="/api-keys")


@router.post("", status_code=201)
async def create_api_key(name: str, org_id: str, current_user: CurrentUser, session: DbSession):
    from uuid import UUID
    raw_key = f"sp_{secrets.token_urlsafe(32)}"
    key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
    key = ApiKey(
        user_id=current_user.id, organization_id=UUID(org_id),
        name=name, key_hash=key_hash, key_prefix=raw_key[:8],
    )
    session.add(key)
    await session.flush()
    return ApiResponse(data={"id": str(key.id), "key": raw_key, "prefix": key.key_prefix})


@router.get("")
async def list_api_keys(current_user: CurrentUser, session: DbSession):
    from sqlalchemy import select
    result = await session.execute(select(ApiKey).where(ApiKey.user_id == current_user.id))
    keys = result.scalars().all()
    return ApiResponse(data=[{"id": str(k.id), "name": k.name, "prefix": k.key_prefix, "created_at": str(k.created_at)} for k in keys])


@router.delete("/{key_id}", status_code=204)
async def revoke_api_key(key_id: str, current_user: CurrentUser, session: DbSession):
    from sqlalchemy import select
    from uuid import UUID
    result = await session.execute(select(ApiKey).where(ApiKey.id == UUID(key_id), ApiKey.user_id == current_user.id))
    key = result.scalar_one_or_none()
    if key:
        await session.delete(key)
        await session.flush()
