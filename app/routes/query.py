"""Endpoints for running SQL queries and natural-language questions against BigQuery."""

from __future__ import annotations

import re
import time

from fastapi import APIRouter
from google.cloud.bigquery import QueryJobConfig
from pydantic import BaseModel

from app.services.bigquery_client import get_client

router = APIRouter(prefix="/api")

# ── Validation helpers ──

_DDL_DML = re.compile(
    r"\b(INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|TRUNCATE|MERGE)\b",
    re.IGNORECASE,
)

_LIMIT_RE = re.compile(r"\bLIMIT\s+\d+", re.IGNORECASE)

ALLOWED_DATASET = "reflection-data.reflection"


def _validate_sql(sql: str) -> str | None:
    """Return an error message if the SQL is invalid, else None."""
    stripped = sql.strip()
    # Remove leading comments
    while stripped.startswith("--") or stripped.startswith("/*"):
        if stripped.startswith("--"):
            stripped = stripped.split("\n", 1)[-1].strip()
        elif stripped.startswith("/*"):
            end = stripped.find("*/")
            if end == -1:
                return "Unterminated comment"
            stripped = stripped[end + 2 :].strip()

    if not stripped.upper().startswith("SELECT"):
        return "Only SELECT queries are allowed"

    if _DDL_DML.search(sql):
        return "DDL/DML statements are not allowed"

    # Check for table references outside our dataset
    # Match fully qualified table references like `project.dataset.table` or project.dataset.table
    table_refs = re.findall(
        r"`([^`]+\.[^`]+\.[^`]+)`|(?<!\w)(\w[\w-]*\.\w[\w-]*\.\w+)(?!\w)", sql
    )
    for ref_tuple in table_refs:
        ref = ref_tuple[0] or ref_tuple[1]
        if not ref.startswith(ALLOWED_DATASET):
            return f"Queries must use tables in {ALLOWED_DATASET}"

    return None


def _ensure_limit(sql: str) -> str:
    """Append LIMIT 100 if no LIMIT clause is present."""
    if not _LIMIT_RE.search(sql):
        return sql.rstrip().rstrip(";") + "\nLIMIT 100"
    return sql


# ── Request/response models ──


class QueryRequest(BaseModel):
    sql: str


class AskRequest(BaseModel):
    question: str


# ── Endpoints ──


@router.post("/query")
async def run_query(req: QueryRequest):
    error = _validate_sql(req.sql)
    if error:
        return {"error": error}

    sql = _ensure_limit(req.sql)

    try:
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
    except Exception as e:
        return {"error": str(e)}


@router.post("/ask")
async def ask_question(req: AskRequest):
    if not req.question.strip():
        return {"error": "Question cannot be empty"}

    try:
        from app.services.claude_client import question_to_sql

        sql = question_to_sql(req.question)
    except Exception as e:
        return {"error": f"Failed to generate SQL: {e}"}

    # Validate the generated SQL
    error = _validate_sql(sql)
    if error:
        return {"error": error, "sql": sql}

    sql = _ensure_limit(sql)

    try:
        client = get_client()
        job_config = QueryJobConfig()
        job_config.maximum_bytes_billed = 100 * 1024 * 1024

        start = time.time()
        job = client.query(sql, job_config=job_config, timeout=10)
        result = job.result(timeout=10)
        duration_ms = int((time.time() - start) * 1000)

        columns = [field.name for field in result.schema]
        rows = []
        for row in result:
            rows.append([_serialize(row[col]) for col in columns])

        return {
            "sql": sql,
            "columns": columns,
            "rows": rows,
            "row_count": len(rows),
            "duration_ms": duration_ms,
        }
    except Exception as e:
        return {"error": str(e), "sql": sql}


def _serialize(val):
    """Convert BigQuery values to JSON-safe types."""
    if val is None:
        return None
    if hasattr(val, "isoformat"):
        return val.isoformat()
    if isinstance(val, (int, float, str, bool)):
        return val
    return str(val)
