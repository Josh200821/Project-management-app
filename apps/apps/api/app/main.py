"""FastAPI application factory."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import sentry_sdk
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from prometheus_fastapi_instrumentator import Instrumentator

from app.config import settings
from app.core.logging import configure_logging
from app.core.telemetry import configure_telemetry
from app.db.base import engine
from app.middleware.correlation_id import CorrelationIdMiddleware
from app.middleware.logging import RequestLoggingMiddleware
from app.middleware.security_headers import SecurityHeadersMiddleware
from app.middleware.tenant import TenantMiddleware
from app.routers.v1 import (
    ai,
    analytics,
    api_keys,
    attachments,
    auth,
    billing,
    comments,
    notifications,
    organizations,
    projects,
    search,
    sprints,
    tasks,
    time_entries,
    users,
    webhooks,
)
from app.routers.ws import notifications as ws_notifications


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan events."""
    configure_logging()
    configure_telemetry()
    if settings.SENTRY_DSN:
        sentry_sdk.init(dsn=settings.SENTRY_DSN, environment=settings.ENVIRONMENT)
    yield
    await engine.dispose()


def create_app() -> FastAPI:
    app = FastAPI(
        title="SaaS PM Platform API",
        description="Pre-alpha prototype multi-tenant project management API",
        version=settings.VERSION,
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
        lifespan=lifespan,
    )

    # ── Exception handling ───────────────────────────────────────────────
    # Services raise plain ValueError for "not found" and validation failures;
    # routers that don't already translate it themselves (see auth.py) fall
    # back to this handler instead of surfacing an unhandled 500.
    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError) -> JSONResponse:
        message = str(exc)
        code = (
            status.HTTP_404_NOT_FOUND
            if "not found" in message.lower()
            else status.HTTP_400_BAD_REQUEST
        )
        return JSONResponse(
            status_code=code, content={"data": None, "meta": None, "errors": [message]}
        )

    # ── Middleware ────────────────────────────────────────────────────
    app.add_middleware(CorrelationIdMiddleware)
    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(TenantMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    if not settings.DEBUG:
        app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.ALLOWED_HOSTS)

    # ── Prometheus ────────────────────────────────────────────────────
    Instrumentator().instrument(app).expose(app, endpoint="/metrics")

    # ── Routers ───────────────────────────────────────────────────────
    prefix = "/api/v1"
    app.include_router(auth.router, prefix=prefix, tags=["auth"])
    app.include_router(users.router, prefix=prefix, tags=["users"])
    app.include_router(organizations.router, prefix=prefix, tags=["organizations"])
    app.include_router(projects.router, prefix=prefix, tags=["projects"])
    app.include_router(tasks.router, prefix=prefix, tags=["tasks"])
    app.include_router(comments.router, prefix=prefix, tags=["comments"])
    app.include_router(sprints.router, prefix=prefix, tags=["sprints"])
    app.include_router(attachments.router, prefix=prefix, tags=["attachments"])
    app.include_router(notifications.router, prefix=prefix, tags=["notifications"])
    app.include_router(search.router, prefix=prefix, tags=["search"])
    app.include_router(analytics.router, prefix=prefix, tags=["analytics"])
    app.include_router(time_entries.router, prefix=prefix, tags=["time-entries"])
    app.include_router(webhooks.router, prefix=prefix, tags=["webhooks"])
    app.include_router(api_keys.router, prefix=prefix, tags=["api-keys"])
    app.include_router(billing.router, prefix=prefix, tags=["billing"])
    app.include_router(ai.router, prefix=prefix, tags=["ai"])
    app.include_router(ws_notifications.router, tags=["websocket"])

    # ── Health checks ─────────────────────────────────────────────────
    @app.get("/health", tags=["health"])
    async def health() -> dict:
        return {"status": "ok", "version": settings.VERSION}

    return app


app = create_app()
