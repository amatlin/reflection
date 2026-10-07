# Reflection

A website that tracks and analyzes its own usage, then shows you how it did it.

**Live at [reflection.sh](https://www.reflection.sh)**

## What it does

You visit it, you interact with it, and those interactions flow through a real data pipeline that you can see end-to-end. Every click, every page view — captured, streamed live, transformed, and aggregated through the same tools a real company would use.

The homepage shows collapsible strips — a live event stream, a SQL warehouse, an analytics panel, a modeling visualization, and a gift shop. Click "Start the walkthrough" for a guided tour through the data pipeline step by step. Fire a real event in step 2 and watch it travel through the system. Run fixed SQL queries against BigQuery in step 3. Explore insight questions about the data in step 4. Leave a thought in step 5 — it gets embedded and projected onto a 2D map once enough responses exist.

The warehouse strip has 3 clickable query chips and a readonly SQL textarea that shows the actual query being run. The analytics strip shows server-rendered daily metrics and 3 insight chips with hardcoded SQL and Claude-generated summaries. All query and insight results are cached daily server-side.

Pipeline countdowns show when the next BigQuery export and dbt refresh will run. The walkthrough generates `funnel_step` events on each navigation and `questionnaire_response` events on submit, enriching the analytics pipeline.

## How it works

Events travel two paths:

1. **Real-time** — PostHog JS SDK captures events → FastAPI backend → Supabase insert → WebSocket broadcast → live stream panel (~50ms)
2. **Analytical** — PostHog → BigQuery (hourly batch export) → dbt transforms → `metrics_daily` + `exhibit_funnel` marts → analytics strip + warehouse query chips + insight chips (daily cache)

## Stack

- **PostHog** — event capture, sessions, behavioral analytics
- **Supabase** — Postgres database + real-time subscriptions for the live event stream
- **FastAPI** — Python backend, validates and dual-writes events, serves cached warehouse queries and insight results
- **BigQuery** — analytical warehouse (PostHog batch export, hourly)
- **dbt Core** — data transformation (staging → facts → dimensions → daily metrics → walkthrough funnel)
- **Claude API** — summarizes insight query results in plain English
- **Cloud Run** — hosting (Docker container, scale-to-zero)

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
                       stg_events (view) → exhibit_funnel (table)
```

The pipeline runs automatically via a daily GitHub Actions cron (6am UTC). To run manually:

```bash
cd pipeline/dbt
dbt build  # runs all models + tests
```

## Deployment

Hosted on [Cloud Run](https://cloud.google.com/run) in the same GCP project as BigQuery. The app runs as a Docker container with a single uvicorn process (`--max-instances 1` for in-process WebSocket broadcast). Secrets are stored in Secret Manager. The app's service account has BigQuery read access, so no key file is needed. Custom domain `reflection.sh` via Namecheap DNS (CNAME → Cloud Run).

Redeploy: `gcloud run deploy reflection --source . --region us-central1`

## Project docs

- [`plan.md`](plan.md) — milestones and roadmap
- [`spirit.md`](spirit.md) — project identity and tone
- [`architecture.md`](architecture.md) — system design and event schema
- [`LAB_NOTEBOOK.md`](LAB_NOTEBOOK.md) — chronological decision history
