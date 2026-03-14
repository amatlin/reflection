from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.config import settings
from app.services.bigquery_client import get_cache_age_minutes, get_latest_metrics

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
async def landing(request: Request):
    metrics = get_latest_metrics()
    cache_age = get_cache_age_minutes()
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "posthog_api_key": settings.posthog_api_key,
            "posthog_host": settings.posthog_host,
            "metrics": metrics,
            "cache_age": cache_age,
        },
    )
