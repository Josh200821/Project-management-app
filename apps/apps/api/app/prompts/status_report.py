"""Weekly project status report prompt — v1."""

SYSTEM_PROMPT = (
    "You are a senior project manager writing concise weekly status reports. "
    "Be direct, data-driven, and flag risks clearly. "
    "Output JSON only — no markdown, no preamble."
)


def build_prompt(project_data: dict) -> str:
    return f"""Generate a weekly status report for this project data:

{project_data}

Return JSON with this exact structure:
{{
  "summary": "2-sentence executive summary",
  "progress_percentage": 0-100,
  "completed_this_week": ["item1", "item2"],
  "in_progress": ["item1", "item2"],
  "blockers": ["blocker1"],
  "risks": [{{"description": "...", "severity": "high|medium|low"}}],
  "next_week_goals": ["goal1", "goal2"],
  "health": "green|yellow|red"
}}"""
