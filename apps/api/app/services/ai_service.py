"""Anthropic Claude API proxy service — all calls server-side only."""
import json

import anthropic
import redis.asyncio as aioredis
import structlog

from app.config import settings
from app.prompts import task_summary, status_report, workload_analysis

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
