"""Scheduled report generation tasks."""

import structlog
from celery import shared_task

logger = structlog.get_logger()


@shared_task
def send_weekly_status_reports() -> None:
    logger.info("weekly_reports_started")


@shared_task
def refresh_task_search() -> None:
    """Refresh the task_search materialized view every 15 minutes."""
    import asyncio

    from app.db.base import AsyncSessionLocal

    async def _refresh():
        async with AsyncSessionLocal() as session:
            await session.execute("REFRESH MATERIALIZED VIEW CONCURRENTLY task_search")
            await session.commit()

    asyncio.run(_refresh())
    logger.info("task_search_refreshed")
