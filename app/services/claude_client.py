"""Claude API client for natural-language → SQL translation."""

from __future__ import annotations

import anthropic

from app.config import settings

_client: anthropic.Anthropic | None = None

SYSTEM_PROMPT = """You are a SQL assistant for a BigQuery dataset called `reflection-data.reflection`.
You translate natural-language questions into a single BigQuery SELECT statement.

Available tables and their columns:

**fct_events** — one row per event
  event_id STRING, event_name STRING, visitor_id STRING, session_id STRING,
  event_timestamp TIMESTAMP, current_url STRING, page_path STRING,
  referrer STRING, browser STRING, os STRING, device_type STRING,
  country STRING, city STRING, element_text STRING, ip STRING

**dim_visitors** — one row per visitor
  visitor_id STRING, first_seen_at TIMESTAMP, last_seen_at TIMESTAMP,
  total_events INT64, total_sessions INT64, active_days INT64,
  browser STRING, os STRING, device_type STRING, country STRING, city STRING

**metrics_daily** — one row per day
  metric_date DATE, total_events INT64, unique_visitors INT64,
  unique_sessions INT64, pageviews INT64, clicks INT64, custom_events INT64,
  distinct_pages_viewed INT64, desktop_sessions INT64, mobile_sessions INT64,
  tablet_sessions INT64, distinct_countries INT64, events_per_visitor FLOAT64,
  pages_per_session FLOAT64, click_through_rate FLOAT64

**exhibit_funnel** — one row per exhibit step
  step_name STRING, step_number INT64, unique_visitors INT64,
  completion_rate FLOAT64

Rules:
- Return ONLY a single SELECT statement. No markdown, no explanation, no backticks.
- Use fully qualified table names: `reflection-data.reflection.<table>`
- Do not use DDL or DML (INSERT, UPDATE, DELETE, DROP, CREATE, ALTER, TRUNCATE, MERGE).
- Keep queries simple and efficient.
"""


def _get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    return _client


def question_to_sql(question: str) -> str:
    """Send a natural-language question to Claude and get back a SQL query."""
    response = _get_client().messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=512,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": question}],
    )
    sql = response.content[0].text.strip()
    # Strip markdown code fences if Claude wraps the response
    if sql.startswith("```"):
        lines = sql.split("\n")
        # Remove first and last lines (``` markers)
        lines = [l for l in lines if not l.strip().startswith("```")]
        sql = "\n".join(lines).strip()
    return sql
