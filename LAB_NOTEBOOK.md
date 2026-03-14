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

## 2026-03-13 — Bug fixed: live event stream now works

Root cause: the `.env` had a Supabase `sb_secret_` key (new management API format) in the `supabase_service_role_key` field, but `supabase-py` talks to PostgREST which requires JWT tokens. The insert was failing with "Invalid API key".

Fix (two changes):
1. **Added `anon_insert` RLS policy** — `CREATE POLICY anon_insert ON public.events FOR INSERT TO anon WITH CHECK (true)`. Since events are public data, there's no reason to require the service_role superuser key for inserts.
2. **Switched Supabase client to use anon key** — changed `supabase_client.py` to use `settings.supabase_anon_key` instead of `settings.supabase_service_role_key`.

Verified with Playwright: page loads, PostHog fires `$pageview`, `_onCapture` forwards to `/api/events`, Supabase insert succeeds, WebSocket broadcasts to stream panel. Button clicks produce `$autocapture` events with element text. The full loop works.

**Milestone 1 is functional.** The self-referential loop is live.

### UX polish ideas (not blocking, revisit later)
- **Blank stream on first load** — ~3s gap while PostHog SDK loads from CDN. Options: self-host the SDK, emit a server-side `page_served` event on render, or show a placeholder.
- **PostHog internal event names** — `$pageview`, `$autocapture` are opaque to visitors. Could map to human-friendly labels.
- **Anonymous visitor IDs** — hex fragments don't create a "that's me" moment. Could use generated names or colors.
- **Buttons feel generic** — clicks produce `$autocapture` rather than intentional named events.
- **Sparse with one user** — stream needs volume to feel alive.

### Debugging approach that worked
1. **Start with Playwright** — navigate to the page, check console errors immediately. The 500 on `/api/events` pointed straight to the backend.
2. **Reproduce outside the browser** — hit the endpoint directly with `httpx` to isolate frontend vs backend. The 422 confirmed the backend was reachable but the 500 wasn't a schema issue.
3. **Test the service layer directly** — called `insert_event()` from Python. Got `SupabaseException: Invalid API key` — root cause in one step.
4. **Check config values** — printed key prefixes and lengths (not full secrets) to confirm the key format was wrong.

Key lesson: the app ran without errors on startup. The failure was **silent at runtime** — Supabase only rejected the key on actual insert. Browser console was the fastest signal that something was wrong.

### Next session
- Start thinking about Milestone 2 (meaningful data model — sign-up, checkout, review flows)

## 2026-03-13 — Claude Code plugins added

Installed plugins: context7, code-review, security-guidance, superpowers, claude-md-management, github, commit-commands, ralph-loop, code-simplifier, typescript-lsp, frontend-design.

How these help with upcoming milestones:

**Milestone 2 (meaningful data model — sign-up, checkout, review flows):**
- **superpowers:writing-plans** — plan the data model and new flows before writing code
- **superpowers:brainstorming** — explore feature design (what makes a checkout flow interesting? what data should reviews generate?)
- **context7** — look up current PostHog, Supabase, and FastAPI docs instead of guessing at APIs
- **frontend-design** — generate production-quality UI for new flows (sign-up forms, checkout, review pages) since the developer has minimal frontend experience
- **superpowers:dispatching-parallel-agents** — build independent flows (sign-up, checkout, review) in parallel
- **code-simplifier** — clean up code after rapid feature buildout

**Milestone 3+ (offline data, analytics layer, deployment):**
- **typescript-lsp** — if frontend moves to TypeScript/React, gives type checking and autocomplete
- **commit-commands** — streamlined git workflow as PRs become more frequent
- **superpowers:executing-plans** — execute multi-step infrastructure work (ETL pipelines, dbt) with review checkpoints
- **code-review** — review PRs before merging as the codebase grows

### Notes
- `supabase_service_role_key` is still in config and `.env.example` but unused. Keeping it for future admin operations that need to bypass RLS. The app runs entirely on the anon key.

## 2026-03-13 — Revised milestone ordering

Reviewed the plan after M1 completion. Key insight: the original ordering (M2: flows → M3: warehouse → M4: analytics) meant the site would accumulate data for two milestones before visitors could explore it analytically. The analytics layer is more central to the spirit than the data model — the apparatus is the art (Duchamp, Warhol). Moved analytics ahead of flows so the site stays demonstrably self-referential at every milestone.

Revised order:
1. ~~Live event stream~~ (done)
2. Analytics layer on existing data (dashboards + architecture diagram)
3. Meaningful flows (sign-up, checkout, review) — each immediately enriches M2's analytics
4. Offline data + deeper analytics (warehouse, dbt, SQL playground)
5. Write-up

Also promoted "expose the ETL pipeline as content" from future ideas into M4 — it's core to the concept, not a nice-to-have.

## 2026-03-13 — Live architecture diagram idea

The centerpiece of M2: an animated architecture diagram that shows events flowing through the real infrastructure in real time. When a visitor clicks a button, they watch their click travel: browser → API → Supabase → PostHog → (eventually) warehouse → dashboard.

Design principles:
- **Real vs. illustrated paths.** Real-time steps (event capture, DB insert, WebSocket broadcast) animate live on each action. Batch steps (snapshots, dbt transforms) show as "runs every N minutes" with a last-run timestamp. Honesty about timing teaches how data infrastructure actually works.
- **Grows with the project.** New segments light up as milestones are completed. Visitors at any point see exactly what exists and works.
- **Could replace the event stream.** Instead of a separate stream panel, events flow through the diagram. The stream becomes a view of one node in the pipeline.
- **The plumbing is the product.** This isn't documentation — it's the main experience.

Implementation approach: build directly in code (SVG + CSS animation) rather than designing in Figma first. The animation is the design — a static mockup wouldn't capture it. The `frontend-design` skill can generate the visual component, then wire it to the real event pipeline.

## 2026-03-13 — Self-optimization idea

The logical endpoint of the self-referential loop: the site doesn't just observe itself, it *optimizes* itself. Define business goals (north star metric, guardrails) for a business that doesn't exist, then let the site run experiments, measure results, and update its own UI automatically.

Why this is powerful:
- **Closes the loop.** Current flow is visit → track → analyze → display. This adds → act → visit. The site responds to what it observes about itself.
- **The metrics problem is the art.** What does "conversion" mean on a site about nothing? Defining and optimizing for goals that are inherently absurd — but doing it with real infrastructure — is the most Reflection thing possible.
- **Radical transparency.** Every website runs experiments on visitors. Reflection would be the only one that shows the hypothesis, the variant you're in, and the results. The optimization is the content.
- **Guardrails create real tension.** Companies don't optimize blindly — they balance competing metrics. Exposing that tradeoff is more educational than any blog post about experimentation.

This is a capstone milestone (M6), dependent on the full stack being in place. But it's worth keeping in mind as we build — the architecture should be designed so that this is possible.

### Next session
- Brainstorm the architecture diagram in detail — which nodes, what connections, what the animation looks like
- Build M2: analytics layer with the diagram + dashboards on existing PostHog/Supabase data

## 2026-03-13 — M2 redesigned: pipeline first, not presentation

Brainstormed what M2 should actually be. Original plan was an animated architecture diagram + dashboards on live data. Realized:
1. Dashboards on a live operational DB is just Datadog — not interesting or unique
2. The animated SVG diagram requires a big frontend investment the developer isn't ready for
3. The pipeline (warehouse + ETL + dbt) is the real substance — and it's in the developer's wheelhouse

Revised M2: build the analytical backbone. The architecture diagram moves to M4 when there's a full pipeline to visualize and the frontend investment pays off more.

## 2026-03-13 — Stack decisions for M2

- **Warehouse:** BigQuery (free tier, industry standard, new GCP project `reflection-data`)
- **ETL:** PostHog's built-in batch export to BigQuery (hourly) — discovered the Events API is deprecated and PostHog recommends batch exports instead. This eliminates the need for a custom extract/load script entirely.
- **Transform:** dbt Core (CLI, run locally)
- **Orchestration:** Simple cron or Python script that runs `dbt run` hourly after PostHog's export lands
- **Source:** PostHog only — it has richer metadata (sessions, device info, geo) than the Supabase events table. Supabase stays as the live stream source.

Key simplification: PostHog batch export handles extract + load automatically. Our pipeline script just needs to run dbt.

## 2026-03-13 — GCP and PostHog batch export set up

Completed infrastructure setup:
1. Installed gcloud CLI via Homebrew
2. Created GCP project `reflection-data`
3. Enabled BigQuery API, created `reflection` dataset
4. Created service account `reflection-pipeline` with BigQuery Data Editor + Job User roles
5. Downloaded service account key to `~/reflection-bq-key.json`
6. Configured PostHog batch export: events → BigQuery, hourly interval, structured fields enabled

Updated config: added `bigquery_project`, `bigquery_dataset`, `bigquery_key_path` to app Settings. Added `dbt-core`, `dbt-bigquery`, `google-cloud-bigquery`, `requests` to requirements.

## 2026-03-13 — dbt project scaffolded, dbt MCP attempted

Created the dbt project skeleton at `pipeline/dbt/`:
- `dbt_project.yml` — staging models as views, mart models as tables
- `profiles.yml` — BigQuery connection using the service account key
- `models/staging/stg_events.sql` — cleans raw PostHog export, extracts common properties (page info, device, geo, session) from JSON into real columns, deduplicates by UUID
- `models/staging/schema.yml` — documents the staging model, defines source table `posthog_events`, adds uniqueness/not-null tests
- `models/marts/fct_events.sql` — clean event fact table (pass-through from staging for now)
- `models/marts/dim_visitors.sql` — one row per visitor with first/last seen, device/geo from latest event

Still need: `metrics_daily.sql` (daily aggregates for the analytics page), mart schema.yml.

**dbt MCP:** Tried to set up the dbt MCP server (https://docs.getdbt.com/docs/dbt-ai/about-mcp) which would give Claude tools to generate sources, staging models, and run dbt directly. Installed `uv` via Homebrew, created `.mcp.json` with config pointing to the dbt project. The MCP didn't connect on reload — may need a full Claude Code restart or a different config approach. Worth trying again next session.

### Environment
- Conda env: `reflection` (Python 3.12)
- Run app: `conda activate reflection && cd /Users/annamatlin/repos/reflection && uvicorn app.main:app --reload --port 8000`
- GCP project: `reflection-data`
- BigQuery dataset: `reflection-data.reflection`
- Service account key: `~/reflection-bq-key.json`
- dbt project: `pipeline/dbt/`
- PostHog batch export: configured, hourly, events → BigQuery `posthog_events` table

## 2026-03-13 — Batch export failing: billing not enabled

PostHog batch export to BigQuery failed 3 runs with: `403 Billing has not been enabled for this project. DML queries are not allowed in the free tier.` BigQuery requires a billing account even for free-tier usage when running DML (INSERT) queries, which is what PostHog's export uses.

PostHog does have 41 events (confirmed via query with `filterTestAccounts: false`). The data is there, it just can't land in BigQuery yet.

Also: PostHog's default `filterTestAccounts: true` hides localhost traffic. Need to keep this in mind when querying — always set `filterTestAccounts: false` during local development.

## 2026-03-13 — GCP billing enabled, dbt models complete

Linked a billing account to GCP project `reflection-data` (required for BigQuery DML even on free tier). dbt MCP now connected and working.

Completed the dbt mart layer:
- **`metrics_daily.sql`** — daily aggregates: volume (events, visitors, sessions), event mix (pageviews, clicks, custom), device split, geo reach, derived ratios (events/visitor, pages/session, CTR)
- **`schema.yml`** for all three mart models — documents columns, adds uniqueness and not-null tests
- Added dbt artifacts (`target/`, `logs/`, `.user.yml`) to `.gitignore`

Full DAG: `posthog_events` (source) → `stg_events` (view) → `fct_events` (table) → `metrics_daily` (table), with `dim_visitors` (table) also branching from `stg_events`.

4 models, 13 tests, 1 source — all compiling. Waiting for the next hourly PostHog batch export to land real rows in BigQuery.

## 2026-03-13 — Pipeline works end-to-end

PostHog batch export landed 5 rows in BigQuery after billing was enabled. Ran `dbt build` — all 4 models materialized, all 12 tests passed.

Two fixes were needed:
1. **JSON path syntax** — BigQuery's native JSON type requires quoted keys for `$`-prefixed properties: `'$."$current_url"'` not `'$.$current_url'`. Fixed all 15 `json_value()` calls in `stg_events.sql`.
2. **Source reference** — replaced hardcoded table name with `{{ source('posthog', 'posthog_events') }}` so dbt tracks lineage properly.
3. **Device mix bug** — `desktop_sessions` was counting events, not distinct sessions. Fixed with `count(distinct case when device_type = 'Desktop' then session_id end)`.

First real data in the marts:
- `metrics_daily`: 1 day, 5 events, 2 visitors, 2 sessions, 1 pageview, 4 clicks
- `dim_visitors`: 2 visitors, both Chrome/Mac/Desktop from New York

**Pipeline runner deferred.** Not worth setting up cron yet — only generating events locally, can run `dbt build` manually or via dbt MCP on demand. Pipeline runner becomes valuable when the site is deployed with real traffic.

## 2026-03-13 — Analytics page design decisions

Brainstormed the analytics page. Key decisions:

1. **Separate `/analytics` page** rather than below-the-fold on the homepage. Clean separation between live (event stream) and analytical (warehouse) views. Mirrors how real companies separate operational monitoring from BI. Two-way door — can combine later.

2. **Pre-built numbers, not a SQL playground.** The SQL playground is more true to the spirit (hand visitors the apparatus), but it's a bigger investment (editor component, safe query execution, cost limits). Ship the simpler version first; playground is planned for M4.

3. **Server-rendered with in-memory cache (Approach B).** Backend queries BigQuery, caches results for 1 hour (matching dbt refresh cadence). No frontend JS needed beyond styling. Considered three approaches:
   - A: Direct BigQuery query on every page load (too slow, ~1-2s per load)
   - **B: Query + in-memory cache** (fast, simple, matches current architecture) ← chosen
   - C: API endpoint + frontend JS (more moving parts than needed right now; sets up for SQL playground later)

4. **Presentation: just the numbers.** Volume, event mix, device split, geo, ratios — plainly labeled, no narrative framing. Consistent with the spirit: "Here is the data."

### Next steps
1. Build `/analytics` page (server-rendered, cached BigQuery queries, numbers from `metrics_daily` + `dim_visitors`)
2. Pipeline runner (cron or script for `dbt build`) — defer until deployment
3. SQL playground — defer to M4
