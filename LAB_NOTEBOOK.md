# Lab Notebook

A chronological record of how Reflection's ideas and decisions evolved.

---

## 2026-03-08 — The idea

Started with a simple premise: build a website whose sole purpose is to analyze itself. Motivated by the difficulty of finding live, real behavioral data outside of a job. Public datasets are static; synthetic data never feels right. What if a website generated its own data by existing?

## 2026-03-08 — The self-referential loop

The core insight: the website is introspective. You visit it, do things, and those things become the data you're looking at. The more people use it, the more interesting the data becomes. This isn't a feature — it *is* the idea.

## 2026-03-08 — Real-time matters

Debated whether real-time event display is necessary or if batch/daily snapshots would suffice. Conclusion: real-time is the idea, not a feature. The "I can see myself in the data right now" moment is what makes it a mirror, not a photograph from yesterday. But both layers are needed — live database for the immediate experience, offline snapshots for heavier analytics. This mirrors how real companies actually work.

## 2026-03-08 — It's art, not comedy

Explored the creative identity. Early drafts leaned toward irreverence and comedy. Refined through discussion: there's no joke, no wink. The site presents itself straightforwardly and lets the visitor make of it what they will. Influences: Seinfeld (obsessive observation of nothing), Duchamp (removing the product and leaving the apparatus), Warhol (making commercial machinery the subject). The concept lives in the gap between the scale of the infrastructure and the triviality of what it measures.

## 2026-03-08 — Renamed to Reflection

Changed the project name from "Mirror" to "Reflection." Better captures the self-analytical nature and has a double meaning — self-analysis and looking back at data. Also evokes a reflection pool, which inspired the blue-gray visual direction.

## 2026-03-08 — Milestones over MVP

Shifted from thinking in terms of a single MVP to a sequence of incremental milestones, each demo-able:
1. Landing page with live event stream
2. Meaningful data model (sign-up, checkout, review flows)
3. Offline data layer and business pipelines
4. Exposed analytics layer (schema docs, dashboards, SQL playground)
5. Written content and tutorial notebooks

The whole system needs to be set up for success from the beginning — the MVP isn't an isolated deliverable, it's the first step in a planned sequence.

## 2026-03-08 — Event schema: structured payloads

Decided on structured, typed payloads per event type rather than a loose JSONB bag. Inspired by Airbnb's Jitney logging framework. Each event type has a defined schema validated at the API layer. This is a one-way door — getting it right early matters because changing it means versioning and backfills.

## 2026-03-08 — The homepage leads with the concept

The homepage shouldn't jump straight to the event stream. It should first explain what the site is — plainly, without cleverness. "This website exists to analyze itself." Then the live stream follows as proof. The concept and the stream should feel like one continuous thought.

## 2026-03-13 — PostHog for event tracking

Explored whether to build event capture from scratch or use an existing tool. Decided on PostHog. Reasoning:
- Most real companies use third-party event tracking (PostHog, Segment, Amplitude) — using one is more authentic, not less
- PostHog handles session management, visitor IDs, device metadata, and schema versioning out of the box, eliminating several design decisions
- It has an API for reading events back, plus export capabilities for the offline warehouse layer
- Frees up effort to focus on the presentation layer — the part that makes Reflection unique

## 2026-03-13 — Dual-write to Supabase for live stream

PostHog captures events for analytics, but the live event stream on the homepage needs guaranteed low latency. Solution: dual-write events to both PostHog (analytics) and a Supabase events table (live stream). Supabase's real-time subscriptions push new rows to the browser via websocket instantly. This separates the analytical path from the display path.

## 2026-03-13 — Architecture settled for milestone 1

The stack:
- **PostHog** — event capture, sessions, behavioral analytics
- **Supabase** — transactional database (users, orders, reviews) + events table for live stream
- **FastAPI** — Python backend, validates and dual-writes events
- **Frontend** — TBD, two-way door
- **Hosting** — TBD, two-way door

One-way doors (event schema, tracking contract) are partially addressed by PostHog's auto-tracking. Custom events still need careful schema design.

## 2026-03-13 — Milestone 1 code scaffolded

All code for M1 is written and in place. The full project structure:

```
reflection/
├── .env.example / .gitignore / requirements.txt
├── scripts/create_events_table.sql   — Supabase DDL (not yet run)
├── app/
│   ├── config.py                     — Pydantic Settings, loads .env
│   ├── main.py                       — FastAPI app, mounts static + routers
│   ├── models/events.py              — EventIn / EventOut pydantic models
│   ├── services/supabase_client.py   — singleton client, insert_event(), recent_events()
│   ├── routes/pages.py               — GET / serves index.html with PostHog keys
│   ├── routes/events.py              — POST /api/events + WebSocket /ws/events
│   ├── templates/index.html          — split layout, PostHog SDK with _onCapture callback
│   └── static/style.css, stream.js   — dark theme, WebSocket stream client
```

Key design choices in code:
- **In-process WebSocket broadcast** (`set[WebSocket]`) instead of Supabase Realtime — simpler for single-process local dev
- **PostHog `_onCapture` callback** forwards every captured event to `/api/events`
- **Backfill on WebSocket connect** — sends last 50 events so stream isn't blank on first load
- **Flat events table** with `raw_properties` JSONB as escape valve

## 2026-03-13 — Infrastructure wired up

Completed all setup steps using Supabase and PostHog MCPs from within Claude Code:

1. **Events table created** — ran `create_events_table.sql` as a Supabase migration via MCP. Table has 9 columns, RLS enabled (anon can read, service_role can insert), index on timestamp desc, realtime publication enabled.
2. **`.env` populated** — Supabase URL and anon key pulled via MCP. Service_role key and PostHog API key grabbed manually from dashboards (service_role is intentionally not exposed via API since it bypasses RLS).
3. **Conda environment created** — `conda create -n reflection python=3.12`, packages installed via `pip install -r requirements.txt`.
4. **App starts** — `uvicorn app.main:app --reload --port 8000` runs without errors. Homepage loads.

Also added Playwright and GitHub MCPs for future use (browser testing, repo management).

Updated CLAUDE.md to note this is a learning project — Claude should explain what it's doing in detail.

## 2026-03-13 — Bug: live event stream not populating

The app starts and the homepage renders, but the live event stream panel doesn't show any events. The server runs without errors. Need to debug in next session.

Likely causes to investigate:
- PostHog `_onCapture` callback may not be firing or forwarding events to `/api/events`
- WebSocket connection from `stream.js` may not be establishing
- Supabase insert may be failing silently (check service_role key format — new `sb_secret_` format vs legacy JWT)
- Check browser console for JS errors and FastAPI logs for incoming requests

### Environment
- Conda env: `reflection` (Python 3.12)
- Run: `conda activate reflection && cd /Users/annamatlin/repos/reflection && uvicorn app.main:app --reload --port 8000`
- Supabase project ID: `yekfjtfjaxqwrhmwncry`
- MCPs available: Supabase, PostHog, Playwright (needs Claude Code restart)

## 2026-03-13 — GitHub MCP setup

Added GitHub Personal Access Token to `~/.zshrc` so the GitHub MCP can authenticate. The MCP was already registered via the Claude plugins marketplace but was failing to connect due to missing token.

### Next session
- Restart Claude Code to pick up the new env var, then verify GitHub MCP connects with `/mcp`
- Debug the live event stream bug (causes listed above) — use Playwright MCP to inspect browser console
- Once stream works, create a GitHub repo and push the initial codebase
