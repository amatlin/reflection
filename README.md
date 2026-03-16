# Reflection

A website whose sole purpose is to analyze itself.

**Live at [reflection.sh](https://www.reflection.sh)**

You visit it, interact with it, and those interactions become the data you can explore on the site. The more people use it, the more interesting the data becomes.

The homepage has two views: a **live event stream** (real-time WebSocket feed of every action on the site) and an **analytics tab** (daily metrics from the data warehouse, server-rendered with a 1-hour cache).

You can also [query the raw data in BigQuery](https://console.cloud.google.com/bigquery?project=reflection-data&d=reflection&p=reflection-data&page=dataset) (free with a Google account).

## Stack

- **PostHog** — event capture, sessions, behavioral analytics
- **Supabase** — Postgres database + real-time subscriptions for the live event stream
- **FastAPI** — Python backend, validates and dual-writes events
- **Vanilla JS** — lightweight frontend with WebSocket-powered stream
- **BigQuery** — analytical warehouse (PostHog batch export, hourly)
- **dbt Core** — data transformation (staging → facts → dimensions → daily metrics)

## Running locally

```bash
conda create -n reflection python=3.12
conda activate reflection
pip install -r requirements.txt
pip install -r requirements-pipeline.txt  # for dbt (optional)
cp .env.example .env  # fill in your keys
uvicorn app.main:app --reload --port 8000
```

## Data pipeline

PostHog exports events to BigQuery hourly. dbt transforms them into mart tables:

```
posthog_events (raw) → stg_events (view) → fct_events (table) → metrics_daily (table)
                                          → dim_visitors (table)
```

Run the pipeline manually:

```bash
cd pipeline/dbt
dbt build  # runs all models + tests
```

## Deployment

Hosted on [Railway](https://railway.app). The app runs as a Docker container. Environment variables are set in Railway's dashboard. The BigQuery service account key is passed as `BIGQUERY_KEY_JSON` (the full JSON string) since Railway can't mount key files.

## Project docs

- [`plan.md`](plan.md) — milestones and roadmap
- [`spirit.md`](spirit.md) — creative identity and tone
- [`architecture.md`](architecture.md) — system design and event schema
- [`LAB_NOTEBOOK.md`](LAB_NOTEBOOK.md) — chronological decision history
