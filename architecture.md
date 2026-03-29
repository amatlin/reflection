# Architecture

## System Overview

```
Browser event happens
  → PostHog JS SDK (analytics: sessions, funnels, behavioral data)
  → FastAPI /api/events → Supabase events table → in-process WebSocket broadcast → stream strip

PostHog batch export (hourly) → BigQuery (raw)
  → dbt: stg_events (view) → fct_events → metrics_daily
                              → dim_visitors
         stg_events (view) → exhibit_funnel

Page load → FastAPI queries BigQuery metrics_daily (1-hour in-memory cache) → analytics strip
Visitor clicks warehouse chip → FastAPI GET /api/warehouse/{key} → BigQuery (daily cache) → results table in warehouse strip
Visitor clicks insight chip → FastAPI GET /api/insights/{key} → Claude NL→SQL (daily cache) → BigQuery → analytics strip
```

### Two data paths

1. **Real-time path** (stream strip): Browser → PostHog SDK `_onCapture` → FastAPI → Supabase insert → in-process WebSocket broadcast → stream panel. Latency: ~50ms.
2. **Analytical path** (analytics strip + warehouse strip): PostHog → BigQuery (hourly batch export) → dbt models → FastAPI queries `metrics_daily` → server-rendered HTML. Visitors can explore BigQuery data via 3 fixed warehouse query chips and 3 fixed insight question chips, all cached daily server-side.

## Decision Framework

### Two-way doors (pick what's fastest, switch later)
- **Frontend framework** — Vanilla HTML/CSS/JS with Jinja2 templates. No build step. Can be rewritten cheaply.
- **Hosting** — Railway. Docker container, single uvicorn process. Changing is a config change and redeploy.
- **Database product** — Supabase (Postgres). The data is portable as long as it's Postgres-compatible.

### One-way doors (spend design energy here)
- **Event schema** — the shape of the events table and what gets logged. Every milestone builds on this. Changing it later means versioning and backfills.
- **Event tracking contract** — what actions are captured, in what format, with what metadata. Once real data is flowing and analytics are built on top, this is expensive to change.

## Components

### Event Tracking — PostHog
PostHog handles event capture, session management, visitor/user identification, device metadata, and behavioral analytics. PostHog's JS SDK auto-tracks page views and clicks; custom events are sent for exhibit interactions, SQL queries, and questionnaire submissions.

### Database — Supabase (Postgres)
Supabase serves as the live event store. Events are written to a Supabase table in addition to PostHog. The FastAPI backend reads recent events from Supabase on WebSocket connect (backfill of last 50 events) and inserts new events on arrival. This dual-write ensures the live stream has low latency without depending on PostHog's API speed.

### Backend API
FastAPI (Python). Routes:
- `GET /` — homepage with server-rendered Jinja2 template, metrics baked in from BigQuery cache
- `POST /api/events` — event ingestion (validates, writes to Supabase, broadcasts via WebSocket)
- `WebSocket /ws/events` — live event stream (backfills last 50 events on connect, broadcasts new events, tracks presence count)
- `GET /api/warehouse/{key}` — run one of 3 fixed SQL queries against BigQuery (keys: `events-by-type`, `visitors-this-week`, `exhibit-completion`). Results cached in-memory for 24 hours. Returns SQL, columns, rows, and cached flag.
- `GET /api/insights/{key}` — run one of 3 fixed insight queries (keys: `exhibit-completion`, `most-common-event`, `mobile-percentage`). Hardcoded SQL, cached 24 hours. Claude summarizes results in 1-2 sentences (optional — works without API key). Returns SQL, question, columns, rows, summary, and cached flag.
- `POST /api/checkout/create-session` — creates a Stripe Checkout Session for "keep the lights on" donations. Accepts `{ item_id, item_name, price }`, validates, returns `{ url }` for redirect.
- `POST /api/stripe/webhook` — receives Stripe webhook events. On `checkout.session.completed`, inserts a `purchase_complete` event into Supabase and broadcasts via WebSocket.

### Services
- `bigquery_client.py` — lazy-init BigQuery client, `get_latest_metrics()` with 1-hour cache, `get_last_export_time()` with 5-minute cache for pipeline countdowns, `get_cache_age_minutes()` for data freshness display
- `claude_client.py` — Claude API client (Sonnet). Summarizes insight query results in 1-2 sentences. Gracefully returns None if no API key or on error.
- `supabase_client.py` — Supabase client for event inserts and recent event reads

### Frontend
Vanilla HTML + CSS + JS. Server-rendered Jinja2 templates. No build step, no framework.

The homepage has a split layout:
- **Left panel:** concept explanation, "Enter the exhibit" button, event journey card, pipeline countdowns (next warehouse export + dbt refresh)
- **Right panel:** four collapsible strips arranged as a vertical accordion:
  - **Stream strip** — live event feed via WebSocket, presence count, "you" labels on your own events
  - **Warehouse strip** — 3 clickable query chips, readonly SQL textarea (shows the query being run), results table. Queries are fixed server-side and cached for 24 hours.
  - **Analytics strip** — server-rendered daily metrics from `metrics_daily`, plus 3 clickable insight chips with hardcoded SQL queries and Claude-generated summaries (cached daily)
  - **Shop strip** — 2 gift shop items (a visualization, keep the lights on). "Keep the lights on" has a live Stripe Checkout flow; the visualization has a "coming soon" overlay. Buy buttons fire `checkout_started` events; Stripe webhook fires `purchase_complete` events back through the pipeline.

The **museum exhibit** is a dark overlay with 5 hash-routed steps (`#exhibit-1` through `#exhibit-5`): Welcome → Stream → Warehouse → Analytics → Shop. Strips are hidden initially and fade in at relevant steps (stream at step 2, warehouse at step 3, analytics at step 4, shop at step 5). Exhibit steps reference the chips in the strips rather than duplicating them. Mobile responsive with stacked layout.

### Payments — Stripe
The "keep the lights on" donation uses Stripe Checkout (hosted payment page). Flow:
1. Visitor enters amount, clicks Buy → frontend POSTs to `/api/checkout/create-session` → creates a Stripe Checkout Session → redirects visitor to Stripe
2. Visitor completes payment on Stripe → Stripe sends `checkout.session.completed` webhook to `/api/stripe/webhook`
3. Webhook handler inserts a `purchase_complete` event into Supabase (with `item_id`, `item_name`, `price`, `stripe_session_id`) and broadcasts it via WebSocket to the live stream
4. Visitor is redirected back to `/?checkout=success` and sees a thank-you toast

Purchase events flow through the same pipeline as all other events (Supabase → BigQuery → dbt), so they appear in warehouse queries and analytics alongside behavioral data. Stripe is the source of truth for payment state; the Supabase event is an analytical record.

### Hosting — Railway
Docker container (Python 3.12, single uvicorn process). Custom domain `reflection.sh` via Namecheap DNS (CNAME → Railway). Environment variables set in Railway's dashboard. The BigQuery service account key is passed as `BIGQUERY_KEY_JSON` (the full JSON string) since Railway can't mount key files.

### Analytical Layer — BigQuery + dbt
PostHog batch exports events to BigQuery hourly. dbt Core transforms them on a daily GitHub Actions cron (`dbt build --target prod` at 6am UTC, with manual trigger). The workflow writes the BigQuery service account key from a GitHub secret to a temp file.
- `stg_events` (view) — cleans raw export, extracts JSON properties into typed columns, deduplicates
- `fct_events` (table) — clean event fact table
- `dim_visitors` (table) — one row per visitor with first/last seen, device, geo
- `metrics_daily` (table) — daily aggregates: volume, event mix, device split, geo, ratios
- `exhibit_funnel` (table) — step completion rates from `funnel_step` events (maps step names to numbers 1–5, calculates unique visitors and completion rate per step)

The FastAPI backend queries `metrics_daily` via `bigquery_client.py` with a 1-hour in-memory cache. Results are baked into the HTML at render time. Visitors can also explore data via 3 fixed warehouse query chips (`/api/warehouse/{key}`) and 3 fixed insight question chips (`/api/insights/{key}`), both cached for 24 hours in module-level dicts.

### Caching
`bigquery_client.py` uses two module-level dict caches:
- `_cache` — latest `metrics_daily` row, 3600-second (1-hour) TTL. On cache miss, runs a BigQuery query. On error, returns `None` and the template shows a fallback message.
- `_export_cache` — last PostHog export timestamp, 300-second (5-minute) TTL. Used to display pipeline countdowns in the UI.

`query.py` uses two additional module-level dict caches:
- `_warehouse_cache` — results of fixed warehouse queries, 86400-second (24-hour) TTL. Keyed by query name. On error, does NOT cache (next request retries).
- `_insight_cache` — results of fixed insight questions, 86400-second (24-hour) TTL. Keyed by question name. On error, does NOT cache.

All caches are per-process (not shared across workers), which is fine for single-process Railway deployment.

### WebSocket Broadcasting
The live event stream uses in-process WebSocket broadcasting (not Supabase Realtime). `events.py` maintains a set of active WebSocket connections. On new event ingestion, the event is broadcast to all connected clients. On connect, the last 50 events are backfilled from Supabase so the stream isn't blank. Presence count is tracked and broadcast when connections open or close. This is simple and sufficient for single-process deployment.

## Event Schema

PostHog handles session IDs, visitor IDs, device metadata, and timestamps automatically. Custom events use structured properties validated at the API layer.

### Event types

| event_type | properties | source |
|---|---|---|
| `$pageview` | (auto-tracked by PostHog) | PostHog SDK |
| `$autocapture` | (auto-tracked by PostHog — clicks, inputs) | PostHog SDK |
| `fire_event` | (none — synthetic test event) | Exhibit step 2 |
| `funnel_step` | `step` ("welcome", "the-loop", "the-warehouse", "the-pipeline", "the-apparatus") | Exhibit navigation |
| `questionnaire_response` | `response_text` (string, max 500 chars, validated server-side) | Exhibit step 6 |
| `checkout_started` | `item_id` (string), `item_name` (string), `price` (number, > 0) | Shop strip buy button |
| `purchase_complete` | `item_id` (string), `item_name` (string), `price` (number), `stripe_session_id` (string) | Stripe webhook |
