# Architecture

## System Overview

```
Browser event happens
  → PostHog JS SDK (analytics: sessions, funnels, dashboards, behavioral data)
  → Your API → Supabase events table (powers live stream via real-time subscriptions)

Supabase: transactional data (users, orders, reviews, merch) + events for live stream
PostHog: behavioral analytics, session tracking, visitor identification
Both: queryable for SQL playground and dashboards
PostHog export → warehouse (offline layer, dbt)
```

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
TBD — start with whatever is fastest for milestone 1 (Lovable, server-rendered HTML + minimal JS, etc.).

### Hosting
TBD — pick a managed platform (Railway, Render, Fly.io) to minimize ops. Not a consequential decision at this stage.

### Offline / Analytical Layer
PostHog export → warehouse (e.g. BigQuery, Snowflake, or just a separate Postgres). Transform with dbt. This is milestone 3.

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

Additional event types will be added in milestone 2 as flows are built out.
