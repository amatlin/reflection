from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.config import settings
from app.services.bigquery_client import get_last_export_time, get_latest_metrics

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
async def landing(request: Request):
    last_export_iso = get_last_export_time()
    metrics = get_latest_metrics()
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "posthog_api_key": settings.posthog_api_key,
            "posthog_host": settings.posthog_host,
            "last_export_iso": last_export_iso or "",
            "dbt_cron_minute": settings.dbt_cron_minute,
            "metrics": metrics,
        },
    )
