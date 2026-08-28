"""Workload balancing prompt — v1."""

SYSTEM_PROMPT = (
    "You are a resource management expert. "
    "Analyze team workload and provide rebalancing recommendations. "
    "Output JSON only — no markdown, no preamble."
)


def build_prompt(team_data: dict) -> str:
    return f"""Analyze this team workload data and recommend rebalancing:

{team_data}

Return JSON with this exact structure:
{{
  "overloaded": [{{"user_id": "...", "task_count": 0, "reason": "..."}}],
  "underloaded": [{{"user_id": "...", "available_capacity": 0}}],
  "recommendations": [
    {{
      "from_user_id": "...",
      "to_user_id": "...",
      "task_id": "...",
      "rationale": "..."
    }}
  ],
  "team_health": "balanced|warning|critical"
}}"""
