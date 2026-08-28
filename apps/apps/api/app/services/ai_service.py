"""Anthropic Claude API proxy service — all calls server-side only."""

import json
from uuid import UUID

import anthropic
import redis.asyncio as aioredis
import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db.models.project import Project
from app.db.models.task import Task
from app.prompts import status_report, task_summary, workload_analysis
from app.repositories.comment_repo import CommentRepository
from app.repositories.organization_repo import OrganizationRepository
from app.repositories.project_repo import ProjectRepository
from app.repositories.task_repo import TaskRepository

logger = structlog.get_logger()
_client: anthropic.AsyncAnthropic | None = None


def get_client() -> anthropic.AsyncAnthropic:
    global _client
    if _client is None:
        _client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
    return _client


async def _cached_completion(cache_key: str, prompt: str, system: str) -> str:
    r = aioredis.from_url(settings.REDIS_URL)
    cached = await r.get(cache_key)
    if cached:
        logger.info("ai_cache_hit", key=cache_key)
        return cached.decode()

    response = await get_client().messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1000,
        system=system,
        messages=[{"role": "user", "content": prompt}],
    )
    result = response.content[0].text
    await r.setex(cache_key, settings.AI_CACHE_TTL_SECONDS, result)
    return result


async def summarize_task(task_id: str, title: str, description: str, comments: list[str]) -> str:
    cache_key = f"ai:task_summary:{task_id}"
    prompt = task_summary.build_prompt(title, description, comments)
    return await _cached_completion(cache_key, prompt, task_summary.SYSTEM_PROMPT)


async def generate_status_report(project_id: str, project_data: dict) -> str:
    cache_key = f"ai:status_report:{project_id}"
    prompt = status_report.build_prompt(project_data)
    return await _cached_completion(cache_key, prompt, status_report.SYSTEM_PROMPT)


async def analyze_workload(org_id: str, team_data: dict) -> dict:
    cache_key = f"ai:workload:{org_id}"
    prompt = workload_analysis.build_prompt(team_data)
    raw = await _cached_completion(cache_key, prompt, workload_analysis.SYSTEM_PROMPT)
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"raw": raw}


class AIService:
    """Fetches the DB context each feature needs, then delegates to the
    module-level functions above (which is also what the Celery tasks in
    workers/ai_tasks.py call directly when the caller already has the data
    in hand, e.g. from a webhook payload)."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def summarize_task(self, task_id: UUID) -> str:
        task = await TaskRepository(self.session).get(task_id)
        if not task:
            raise ValueError("Task not found")
        comments = await CommentRepository(self.session).get_by_task(task_id)
        return await summarize_task(
            str(task_id), task.title, task.description or "", [c.body for c in comments]
        )

    async def generate_status_report(self, project_id: UUID) -> str:
        project = await ProjectRepository(self.session).get(project_id)
        if not project:
            raise ValueError("Project not found")
        tasks = await TaskRepository(self.session).get_by_project(project_id, limit=500)
        by_status: dict[str, int] = {}
        for task in tasks:
            by_status[task.status] = by_status.get(task.status, 0) + 1
        project_data = {
            "name": project.name,
            "description": project.description,
            "total_tasks": len(tasks),
            "tasks_by_status": by_status,
        }
        return await generate_status_report(str(project_id), project_data)

    async def analyze_workload(self, org_id: UUID) -> dict:
        org = await OrganizationRepository(self.session).get(org_id)
        if not org:
            raise ValueError("Organization not found")
        result = await self.session.execute(
            select(Task.assignee_id, Task.status)
            .join(Project, Project.id == Task.project_id)
            .where(Project.organization_id == org_id, Task.status != "done")
        )
        counts: dict[str, int] = {}
        for assignee_id, _status in result.all():
            key = str(assignee_id) if assignee_id else "unassigned"
            counts[key] = counts.get(key, 0) + 1
        team_data = {"open_task_counts_by_assignee": counts}
        return await analyze_workload(str(org_id), team_data)
