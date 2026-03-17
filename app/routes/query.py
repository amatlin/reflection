"""Endpoints for running fixed SQL queries and insights against BigQuery."""

from __future__ import annotations

import time

from fastapi import APIRouter
from google.cloud.bigquery import QueryJobConfig

from app.services.bigquery_client import get_client

router = APIRouter(prefix="/api")

# ── Fixed warehouse queries ──

WAREHOUSE_QUERIES: dict[str, str] = {
    "events-by-type": """SELECT
  event_name,
  COUNT(*) AS events,
  COUNT(DISTINCT visitor_id) AS visitors
FROM `reflection-data.reflection.fct_events`
GROUP BY event_name
ORDER BY events DESC
LIMIT 100""",
    "visitors-today": """SELECT
  COUNT(DISTINCT visitor_id) AS visitors_today
FROM `reflection-data.reflection.fct_events`
WHERE DATE(event_timestamp) = CURRENT_DATE()""",
    "exhibit-completion": """SELECT
  step_name,
  step_number,
  unique_visitors,
  ROUND(completion_rate, 2) AS completion_rate
FROM `reflection-data.reflection.exhibit_funnel`
ORDER BY step_number""",
}

# ── Fixed insight questions ──

INSIGHT_QUESTIONS: dict[str, str] = {
    "exhibit-completion": "how many visitors complete the exhibit?",
    "most-common-event": "what's the most common event?",
    "mobile-percentage": "what percentage of visitors are on mobile?",
}

# ── Module-level caches (key -> {data, expires_at}) ──

_warehouse_cache: dict[str, dict] = {}
_insight_cache: dict[str, dict] = {}
_CACHE_TTL = 86400  # 24 hours


# ── Helpers ──

def _run_sql(sql: str) -> dict:
    """Execute a SQL query and return results dict."""
    client = get_client()
    job_config = QueryJobConfig()
    job_config.maximum_bytes_billed = 100 * 1024 * 1024  # 100 MB safety limit

    start = time.time()
    job = client.query(sql, job_config=job_config, timeout=10)
    result = job.result(timeout=10)
    duration_ms = int((time.time() - start) * 1000)

    columns = [field.name for field in result.schema]
    rows = []
    for row in result:
        rows.append([_serialize(row[col]) for col in columns])

    return {
        "columns": columns,
        "rows": rows,
        "row_count": len(rows),
        "duration_ms": duration_ms,
    }


def _serialize(val):
    """Convert BigQuery values to JSON-safe types."""
    if val is None:
        return None
    if hasattr(val, "isoformat"):
        return val.isoformat()
    if isinstance(val, (int, float, str, bool)):
        return val
    return str(val)


# ── Endpoints ──

@router.get("/warehouse/{key}")
async def warehouse_query(key: str):
    if key not in WAREHOUSE_QUERIES:
        return {"error": f"Unknown warehouse query: {key}"}

    # Check cache
    now = time.time()
    cached = _warehouse_cache.get(key)
    if cached and cached["expires_at"] > now:
        return {**cached["data"], "cached": True}

    sql = WAREHOUSE_QUERIES[key]
    try:
        data = _run_sql(sql)
        data["sql"] = sql
        data["cached"] = False
        _warehouse_cache[key] = {"data": data, "expires_at": now + _CACHE_TTL}
        return data
    except Exception as e:
        return {"error": str(e), "sql": sql}


@router.get("/insights/{key}")
async def insight_query(key: str):
    if key not in INSIGHT_QUESTIONS:
        return {"error": f"Unknown insight: {key}"}

    # Check cache
    now = time.time()
    cached = _insight_cache.get(key)
    if cached and cached["expires_at"] > now:
        return {**cached["data"], "cached": True}

    question = INSIGHT_QUESTIONS[key]
    try:
        from app.services.claude_client import question_to_sql
        sql = question_to_sql(question)
    except Exception as e:
        return {"error": f"Failed to generate SQL: {e}"}

    try:
        data = _run_sql(sql)
        data["sql"] = sql
        data["question"] = question
        data["cached"] = False
        _insight_cache[key] = {"data": data, "expires_at": now + _CACHE_TTL}
        return data
    except Exception as e:
        return {"error": str(e), "sql": sql}
