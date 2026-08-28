"""Task summarization prompt — v1."""

SYSTEM_PROMPT = (
    "You are a concise project management assistant. "
    "Summarize tasks into exactly 5 bullet points. "
    "Be factual, specific, and actionable. No fluff."
)


def build_prompt(title: str, description: str, comments: list[str]) -> str:
    comments_text = "\n".join(f"- {c}" for c in comments[:20])
    return f"""Task: {title}

Description:
{description or "No description provided."}

Comments ({len(comments)} total, showing up to 20):
{comments_text or "No comments."}

Summarize this task in exactly 5 bullet points covering:
1. What needs to be done
2. Current status / progress
3. Key blockers or risks
4. Next immediate action
5. Who is involved"""
