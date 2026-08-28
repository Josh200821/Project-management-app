"""AI feature Celery tasks — all Anthropic calls go through here."""

import structlog
from celery import shared_task

logger = structlog.get_logger()


@shared_task
def summarize_task_async(task_id: str, title: str, description: str, comments: list) -> str:
    import asyncio

    from app.services.ai_service import summarize_task

    result = asyncio.run(summarize_task(task_id, title, description, comments))
    logger.info("task_summarized", task_id=task_id)
    return result


@shared_task
def send_standup_updates() -> None:
    """Daily Celery beat job: send AI standup digests to all active users."""
    logger.info("standup_updates_started")
    # In production: query active users, generate per-user digest, enqueue emails


@shared_task
def analyze_team_workload(org_id: str, team_data: dict) -> dict:
    import asyncio

    from app.services.ai_service import analyze_workload

    result = asyncio.run(analyze_workload(org_id, team_data))
    logger.info("workload_analyzed", org_id=org_id)
    return result
