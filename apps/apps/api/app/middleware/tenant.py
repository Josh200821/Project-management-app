"""Tenant context middleware — extracts org slug from URL and sets structlog context."""

import structlog
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware


class TenantMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Org slug carried in X-Organization header or path segment /orgs/{slug}/
        org_slug = request.headers.get("X-Organization", "")
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(organization=org_slug)
        request.state.organization_slug = org_slug
        return await call_next(request)
