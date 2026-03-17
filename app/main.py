from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.routes import events, pages, query

app = FastAPI(title="Reflection")

app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(pages.router)
app.include_router(events.router)
app.include_router(query.router)
