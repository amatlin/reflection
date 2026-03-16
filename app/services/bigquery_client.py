from __future__ import annotations

import json
import time

from google.cloud import bigquery
from google.oauth2 import service_account

from app.config import settings

_client: bigquery.Client | None = None
_cache: dict = {"data": None, "fetched_at": 0.0}
_export_cache: dict = {"data": None, "fetched_at": 0.0}
_CACHE_TTL = 3600  # 1 hour
_EXPORT_CACHE_TTL = 300  # 5 minutes


def get_client() -> bigquery.Client:
    """Lazy-init BigQuery client. Uses service account key if configured,
    otherwise falls back to default credentials (e.g. gcloud auth)."""
    global _client
    if _client is None:
        if settings.bigquery_key_json:
            info = json.loads(settings.bigquery_key_json)
            credentials = service_account.Credentials.from_service_account_info(
                info,
                scopes=["https://www.googleapis.com/auth/bigquery"],
            )
            _client = bigquery.Client(
                project=settings.bigquery_project, credentials=credentials
            )
        elif settings.bigquery_key_path:
            credentials = service_account.Credentials.from_service_account_file(
                settings.bigquery_key_path,
                scopes=["https://www.googleapis.com/auth/bigquery"],
            )
            _client = bigquery.Client(
                project=settings.bigquery_project, credentials=credentials
            )
        else:
            _client = bigquery.Client(project=settings.bigquery_project)
    return _client


def get_latest_metrics() -> dict | None:
    """Return the most recent row from metrics_daily as a dict.
    Results are cached in memory for _CACHE_TTL seconds."""
    global _cache
    now = time.time()

    if _cache["data"] is not None and (now - _cache["fetched_at"]) < _CACHE_TTL:
        return _cache["data"]

    try:
        table = f"{settings.bigquery_project}.{settings.bigquery_dataset}.metrics_daily"
        query = f"""
            SELECT *
            FROM `{table}`
            ORDER BY metric_date DESC
            LIMIT 1
        """
        result = get_client().query(query).result()
        rows = list(result)
        if not rows:
            return None

        data = dict(rows[0])
        _cache["data"] = data
        _cache["fetched_at"] = time.time()
        return data
    except Exception as e:
        print(f"[bigquery] Error fetching metrics: {e}")
        return None


def get_last_export_time() -> str | None:
    """Return ISO timestamp of the most recent event exported to BigQuery.
    Cached for 5 minutes to avoid hammering BQ on every page load."""
    global _export_cache
    now = time.time()

    if _export_cache["data"] is not None and (now - _export_cache["fetched_at"]) < _EXPORT_CACHE_TTL:
        return _export_cache["data"]

    try:
        table = f"{settings.bigquery_project}.{settings.bigquery_dataset}.posthog_events"
        query = f"SELECT MAX(timestamp) as last_ts FROM `{table}`"
        result = get_client().query(query).result()
        rows = list(result)
        if not rows or rows[0].last_ts is None:
            return None

        iso = rows[0].last_ts.isoformat()
        _export_cache["data"] = iso
        _export_cache["fetched_at"] = time.time()
        return iso
    except Exception as e:
        print(f"[bigquery] Error fetching last export time: {e}")
        return None


def get_cache_age_minutes() -> int | None:
    """Minutes since the cache was last populated. None if never fetched."""
    if _cache["fetched_at"] == 0.0:
        return None
    return int((time.time() - _cache["fetched_at"]) / 60)
