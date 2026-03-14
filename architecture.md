# Architecture

## System Overview

```
Browser event happens
  → PostHog JS SDK (analytics: sessions, funnels, behavioral data)
  → FastAPI /api/events → Supabase events table → WebSocket broadcast (live stream tab)

PostHog batch export (hourly) → BigQuery (raw)
  → dbt: stg_events (view) → fct_events → metrics_daily
                             → dim_visitors

Page load → FastAPI queries BigQuery metrics_daily (1-hour in-memory cache) → analytics tab
```

### Two data paths

1. **Real-time path** (live stream tab): Browser → PostHog SDK `_onCapture` → FastAPI → Supabase insert → WebSocket broadcast → stream panel. Latency: ~50ms.
2. **Analytical path** (analytics tab): PostHog → BigQuery (hourly batch export) → dbt models → FastAPI queries `metrics_daily` → server-rendered HTML. Latency: up to 1 hour + cache TTL.

## Decision Framework

### Two-way doors (pick what's fastest, switch later)
- **Frontend framework** — Lovable, React, plain HTML, whatever gets milestone 1 working. The frontend is small at first and can be rewritten cheaply.
- **Hosting** — Railway, Render, Fly.io, etc. All run containers or similar. Changing is a config change and redeploy.
- **Database product** — Supabase, self-hosted Postgres, etc. The data is portable as long as it's Postgres-compatible.

### One-way doors (spend design energy here)
- **Event schema** — the shape of the events table and what gets logged. Every milestone builds on this. Changing it later means versioning and backfills.
- **Event tracking contract** — what actions are captured, in what format, with what metadata. Once real data is flowing and analytics are built on top, this is expensive to change.

## Components

### Event Tracking — PostHog
PostHog handles event capture, session management, visitor/user identification, device metadata, and behavioral analytics. This is how most real companies do it — using a third-party tool rather than building their own. PostHog's JS SDK auto-tracks page views and clicks; custom events are sent for actions like sign-up, checkout, review, and query execution.

PostHog also provides dashboards, funnels, and cohort analysis out of the box, which can supplement (or seed) the custom analytics layer in milestone 4.

### Database — Supabase (Postgres)
Supabase serves two roles:
1. **Transactional data** — users, orders, reviews, merch catalog. The application database.
2. **Live event stream** — events are written to a Supabase table in addition to PostHog. Supabase's real-time subscriptions (websockets) push new events to the browser instantly, powering the homepage stream. This dual-write ensures the live stream has low latency without depending on PostHog's API speed.

### Backend API
FastAPI (Python). Receives custom events from the browser (writes to both PostHog and Supabase), serves pages, handles transactional logic (checkout, reviews, etc.).

### Frontend
Vanilla HTML + CSS + JS. Server-rendered Jinja2 templates. No build step, no framework. The homepage is a split layout: left panel explains the concept, right panel has a tab bar toggling between the live event stream and the analytics view.

### Hosting
TBD — pick a managed platform (Railway, Render, Fly.io) to minimize ops. Not a consequential decision at this stage.

### Analytical Layer — BigQuery + dbt
PostHog batch exports events to BigQuery hourly. dbt Core transforms them:
- `stg_events` (view) — cleans raw export, extracts JSON properties into typed columns, deduplicates
- `fct_events` (table) — clean event fact table
- `dim_visitors` (table) — one row per visitor with first/last seen, device, geo
- `metrics_daily` (table) — daily aggregates: volume, event mix, device split, geo, ratios

The FastAPI backend queries `metrics_daily` via `app/services/bigquery_client.py` with a 1-hour in-memory cache. Results are baked into the HTML at render time — no client-side BigQuery calls.

### Analytics Caching
`bigquery_client.py` uses a module-level dict cache (`_cache`) with a 3600-second TTL. On cache miss, it runs a BigQuery query for the latest `metrics_daily` row. On error, returns `None` and the template shows a fallback message. The cache is per-process (not shared across workers), which is fine for single-process local dev.

## Event Schema

PostHog handles session IDs, visitor IDs, device metadata, and timestamps automatically. Custom events use structured, typed properties per event type — validated at the API layer before sending to PostHog.

### Typed payloads per event type

| event_type | properties |
|---|---|
| `page_view` | (auto-tracked by PostHog) |
| `click` | (auto-tracked by PostHog) |
| `sign_up` | method |
| `checkout` | item_id, item_name, price, currency |
| `review` | rating, review_text, item_id |
| `query_executed` | query_text, row_count, duration_ms |

Additional event types will be added in milestone 3 as flows are built out.
