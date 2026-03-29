"""Claude API client for summarizing query results."""

from __future__ import annotations

import anthropic

from app.config import settings

_client: anthropic.Anthropic | None = None

SYSTEM_PROMPT = """You analyze data from a self-referential website called Reflection.
Given query results, provide a 1-2 sentence summary of what's interesting.
Be direct, no hedging. Use specific numbers from the data."""


def _get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    return _client


def summarize_results(question: str, columns: list[str], rows: list[list]) -> str | None:
    """Summarize query results in plain English. Returns None on any error."""
    if not settings.anthropic_api_key:
        return None
    try:
        # Format results as a simple table
        header = " | ".join(columns)
        lines = [header]
        for row in rows[:20]:  # cap at 20 rows to keep prompt small
            lines.append(" | ".join(str(v) for v in row))
        table_text = "\n".join(lines)

        response = _get_client().messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=150,
            system=SYSTEM_PROMPT,
            messages=[{
                "role": "user",
                "content": f"Question: {question}\n\nResults:\n{table_text}",
            }],
        )
        return response.content[0].text.strip()
    except Exception:
        return None
