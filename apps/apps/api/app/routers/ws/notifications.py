"""WebSocket endpoint for real-time notifications."""

import asyncio

import redis.asyncio as aioredis
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.config import settings

router = APIRouter()

_connections: dict[str, list[WebSocket]] = {}


@router.websocket("/ws/notifications")
async def websocket_notifications(websocket: WebSocket, token: str):
    from app.core.security import decode_access_token

    payload = decode_access_token(token)
    if not payload:
        await websocket.close(code=4001)
        return

    user_id = payload.get("sub", "")
    await websocket.accept()
    _connections.setdefault(user_id, []).append(websocket)

    redis = aioredis.from_url(settings.REDIS_URL)
    pubsub = redis.pubsub()
    await pubsub.subscribe(f"notifications:{user_id}")

    try:

        async def listen():
            async for message in pubsub.listen():
                if message["type"] == "message":
                    await websocket.send_text(message["data"].decode())

        await asyncio.gather(listen(), websocket.receive_text())
    except WebSocketDisconnect:
        _connections[user_id].remove(websocket)
    finally:
        await pubsub.unsubscribe(f"notifications:{user_id}")
        await redis.aclose()
