# Reflection

A website whose sole purpose is to analyze itself.

You visit it, interact with it, and those interactions become the data you can explore on the site. The more people use it, the more interesting the data becomes.

## Stack

- **PostHog** — event capture, sessions, behavioral analytics
- **Supabase** — Postgres database + real-time subscriptions for the live event stream
- **FastAPI** — Python backend, validates and dual-writes events
- **Vanilla JS** — lightweight frontend with WebSocket-powered stream

## Running locally

```bash
conda create -n reflection python=3.12
conda activate reflection
pip install -r requirements.txt
cp .env.example .env  # fill in your keys
uvicorn app.main:app --reload --port 8000
```

## Project docs

- [`plan.md`](plan.md) — milestones and roadmap
- [`spirit.md`](spirit.md) — creative identity and tone
- [`architecture.md`](architecture.md) — system design and event schema
- [`LAB_NOTEBOOK.md`](LAB_NOTEBOOK.md) — chronological decision history
