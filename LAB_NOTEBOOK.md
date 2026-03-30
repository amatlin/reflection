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
1. ~~Build analytics view (server-rendered, cached BigQuery queries, numbers from `metrics_daily`)~~ (done — see below)
2. Pipeline runner (cron or script for `dbt build`) — defer until deployment
3. SQL playground — defer to M4

## 2026-03-13 — Analytics view shipped

Built the analytics view as a tab on the homepage instead of a separate `/analytics` page. Design change: instead of navigating away from the live stream, visitors toggle between "Live Stream" and "Analytics" tabs in the right panel. This keeps both views one click away and preserves the stream's WebSocket connection regardless of which tab is active.

### What was built

**New file: `app/services/bigquery_client.py`**
- Singleton BigQuery client mirroring the `supabase_client.py` pattern
- `get_latest_metrics()` queries `metrics_daily` for the most recent row, returns it as a dict
- 1-hour in-memory cache (`_cache` dict with TTL check) — matches the PostHog batch export cadence
- `get_cache_age_minutes()` returns minutes since last fetch for the "Last updated" display
- Graceful degradation: returns `None` on any error, so the page still renders

**Modified: `app/routes/pages.py`**
- Calls `get_latest_metrics()` and `get_cache_age_minutes()` on every page load
- Passes `metrics` (dict or None) and `cache_age` (int or None) to the Jinja template

**Modified: `app/templates/index.html`**
- Replaced `.stream-header` + `#stream` with a tab bar + two tab content divs
- Tab bar: "Live Stream" (with green dot) | "Analytics"
- `#tab-stream` wraps the existing `#stream` div
- `#tab-analytics` shows four metric groups in a 2x2 grid: Today, Event Mix, Devices, Visitors
- Values are baked into the HTML at render time (no client-side fetching)
- Jinja conditional: shows "No analytics data yet." when metrics is None

**Modified: `app/static/style.css`**
- Replaced `.stream-header` styles with `.tab-bar` / `.tab` styles (border-bottom active indicator)
- Added `.tab-content` show/hide (display: none / flex)
- Added analytics styles: `.analytics-grid` (2-col CSS grid), `.metric-group`, `.metric-value` / `.metric-label`
- All colors from existing palette

**Modified: `app/static/stream.js`**
- Added tab switching at the top of the IIFE (before WebSocket setup)
- Click handler toggles `active` class on tabs and corresponding content divs
- WebSocket continues running regardless of which tab is visible

### Key learnings

1. **BigQuery OAuth scopes matter.** Used `bigquery.readonly` initially — queries fail with "insufficient authentication scopes" because running a query creates a Job, which requires write-like permissions. The correct scope is `bigquery` (full access). The `readonly` scope only works for reading table data directly, not for running queries.

2. **Cache TTL design.** The cache only stores data after a successful fetch. If BigQuery is down, subsequent requests retry the query (no negative caching). This is intentional — better to be slow than stale when the data source recovers.

3. **Tab design > separate page.** The original plan called for a separate `/analytics` route. The tab approach is better because: (a) visitors see both views exist immediately, (b) the WebSocket stays connected while browsing analytics, (c) no page navigation means no new PostHog event just for checking analytics.

4. **`datetime.date` in BigQuery results.** BigQuery's DATE type comes back as `datetime.date` in Python. Jinja renders it fine as a string, but if we ever serialize to JSON we'll need a custom encoder.

### Verified
- BigQuery query returns real data (5 events, 2 visitors from the test session)
- Cache works: first call ~1.2s, second call ~0.000002s
- Template renders correctly with both real metrics and None
- App loads without import errors
- Both tab states render correctly (confirmed via template rendering test)

### What's next
- Deploy the site so it gets real traffic (currently only generating data locally)
- Pipeline runner (cron for `dbt build`) — needed once deployed
- Start M3: meaningful flows (sign-up, checkout, review) to generate richer data for the analytics view

## 2026-03-13 — Ideas to brainstorm next session

### 1. Personalized visitor greeting + sign-up flow
Homepage shows "Welcome visitor {id}" (using the PostHog distinct_id or short hash). Visitors can sign up, choose a username, and then appear in the live stream by name instead of an anonymous hex fragment. This ties sign-up (an M3 flow) directly into the existing M1 experience — the incentive to sign up is seeing your name in the stream. Needs brainstorming: what does the sign-up flow look like? Where does the username live (Supabase users table)? How does the stream resolve visitor_id → username?

### 2. SQL playground — build vs. embed
Question: do we need to build a SQL playground from scratch, or can we embed an existing tool? Options to explore:
- **BigQuery's connected sheets or Looker Studio** — embeddable, but may not give raw SQL access
- **Observable** or **Evidence.dev** — notebook-style tools that can connect to BigQuery
- **Retool / Metabase embedded** — read-only SQL runners with embed support
- **Monaco editor + API endpoint** — build it ourselves with a code editor widget and a backend that proxies read-only queries to BigQuery
- Key constraint: must be read-only, must have cost limits (BigQuery bills by bytes scanned)

### 3. Architecture diagram — simplify scope
The live animated architecture diagram (events flowing through nodes in real time) may be over-engineered for what it adds. Alternative: a static architecture diagram in one of the M5 blog posts, or a simple SVG on the site that labels the components without live animation. The pipeline is interesting to explain, but it doesn't need to be interactive to be valuable. This frees up significant frontend effort for things that matter more (SQL playground, flows).

### 4. User-generated text — community participation as data
The site could invite visitors to contribute text — not just clicks and pageviews. This turns Reflection into something communal, not just observational. Ideas for the prompt:
- **Open-ended**: a text box on the homepage ("Say something"), no constraints. Maximum creative freedom, hardest to analyze.
- **Feedback on Reflection**: "What do you think of this?" — narrower, but risks feeling like a survey rather than art.
- **Specific prompt**: a rotating question that changes periodically. Gives structure without being a survey.
- **Meta-prompt**: "What do you think happens to what you type here?" — deeply on-brand. The answer is: it becomes data, and you can see it analyzed on the analytics page.

What makes this powerful for the project:
- **New data type**: natural language alongside behavioral events. Opens up NLP/unstructured analysis in the analytics layer (sentiment, topics, word frequency, embeddings).
- **Community feel**: visitors become participants, not just subjects. The site watches you, but you also get to speak back.
- **Structured survey angle**: could also include a short structured survey ("Did this site change how you think about data tracking? Y/N/unsure") — results aggregated and displayed on the analytics tab. This is measurable and ties directly to the project's purpose.
- **Self-referential loop deepens**: the text people submit about the site becomes part of the site's data, which other people then see analyzed. The content about Reflection becomes Reflection's content.

Needs brainstorming: where does the text box live on the homepage (left panel? its own tab?)? How is text stored (Supabase table)? What NLP analysis is feasible and interesting? How to handle moderation/abuse?

### 5. Display the cost of running the site
Show visitors what it costs to operate Reflection — hosting, BigQuery, Supabase, PostHog, domain, etc. This is peak self-referential: the site doesn't just show you its data, it shows you the bill. Options to explore:
- **Static cost breakdown**: manually maintained list of monthly costs per service. Simple, honest, easy to start with.
- **Live cost tracking**: pull actual usage/billing data from GCP, Supabase, and PostHog APIs. More impressive but more complex.
- **Cost-per-visitor or cost-per-event**: derived metric that gets more interesting as traffic grows. "Your visit cost $0.0003."
- **Where to display**: could be a metric group on the analytics tab, a footer on the homepage, or part of a blog post about the infrastructure.

Why this works: most websites hide their costs. Reflection showing its own bill is consistent with the spirit of radical transparency — the apparatus is the art, and the economics of the apparatus are part of the story.

## 2026-03-15 — Scope trimmed to MVP

Came back after a couple days and decided the project was getting too sprawling. Trimmed the roadmap to minimum viable: restyle the frontend, deploy, add BigQuery public access, write a blog post. Moved the richer data model, SQL playground, architecture diagram, and self-optimization to future ideas.

## 2026-03-15 — Frontend redesign: "reflection pool" theme

Replaced the dark terminal aesthetic with a light, calm theme inspired by a reflection pool. Key changes:
- Color palette: light blue-gray background (#f4f7fb), white cards, slate text, blue accent
- Typography: DM Serif Display for the title, DM Sans for body, JetBrains Mono for data
- Kept the split-screen layout (left panel concept, right panel stream/analytics tabs)
- Added ripple effect: each new event in the stream triggers a subtle radial blue glow that fades out over ~1.4s, like a drop on still water
- Simplified the copy to: "Welcome to Reflection. Stay for a second or for a while. Every action you take here is recorded and visible to everyone."
- Added footer with blog and GitHub links
- Added BigQuery link in the analytics tab

Process: built a standalone mockup.html first, iterated on copy and layout there, then applied to the real templates.

## 2026-03-15 — Deployed to Railway

Deployed the FastAPI app to Railway. Key setup:
- **Dockerfile**: Python 3.12 slim, installs web deps only (split dbt into `requirements-pipeline.txt`)
- **BigQuery credentials**: added `BIGQUERY_KEY_JSON` config field — accepts the full service account JSON as an env var string, since Railway can't mount key files. Falls back to `BIGQUERY_KEY_PATH` for local dev.
- **dbt profiles.yml**: added `prod` target using `service-account-json` method
- **Custom domain**: reflection.sh (Namecheap) → CNAME to Railway, with root redirect to www
- **Railway URL**: courageous-expression-production.up.railway.app

Skipping dbt cron for now — running `dbt build` manually until there's real traffic.

### Environment
- Railway project: courageous-expression
- Domain: reflection.sh (www.reflection.sh)
- Railway CLI: `brew install railway`, `railway login`

### Next
- Wait for DNS propagation, verify reflection.sh works
- Phase 3: Grant BigQuery `dataViewer` to `allAuthenticatedUsers`
- Phase 4: Blog post at `/blog`

## 2026-03-15 — Museum exhibit funnel design

Designed a restructure of the site as a museum exhibit: **Homepage → Exhibit (8 steps) → Conclusion/Gift Shop**. This maps to M3's goal of "meaningful data model / richer event types" and gives the site its first structured user journey with real e-commerce data.

### Why a museum exhibit

The original M3 plan called for sign-up, checkout, and review flows — but those felt bolted-on. A museum exhibit reframes the same infrastructure walkthrough the site already does as a guided, step-by-step experience. Each exhibit screen explains one stage of the pipeline that's tracking the visitor as they move through it. The funnel IS the content.

### Structure

8 exhibit steps, each its own screen with back/next navigation:
1. Introduction (the concept, Duchamp/Warhol/Seinfeld lineage)
2. Logging (PostHog captures behavior)
3. Streaming (API → Supabase → WebSocket → live stream)
4. Export (PostHog batch export to BigQuery, hourly)
5. Transformation (dbt cleans and aggregates)
6. Metrics (daily aggregates in `metrics_daily`)
7. Analysis (analytics tab displays the pipeline's output)
8. Conclusion (thank you + questionnaire + gift shop)

### New event types

| Event | Trigger | What it adds |
|---|---|---|
| `funnel_step` | Each screen navigation | Funnel analysis — conversion rates through the exhibit |
| `questionnaire_response` | Text box submit on conclusion | Natural language data — opens up NLP in analytics |
| `checkout_started` | Buy button → Stripe | E-commerce funnel start |
| `purchase_complete` | Stripe webhook | Real revenue data — richest event type in analytics |

### Technical approach

Single-page with hash routing — all screens in one `index.html`, show/hide with JS, update `location.hash`. WebSocket stays alive across all screens. Hash included in `page_path` for every event, so PostHog and the Supabase events table both capture which screen the visitor is on.

### What makes this work for Reflection

- The funnel is analyzable — the site can show its own conversion rates
- The exhibit content IS the infrastructure walkthrough — educational and self-referential
- The gift shop generates real e-commerce data (the richest event type in any analytics stack)
- The questionnaire generates natural language data (opens up NLP in the analytics layer)
- Every new event type immediately enriches the existing pipeline

### Files created
- `museum_idea.md` — working document with full design spec
- `plan.md` — updated milestones: museum exhibit is M4, blog post pushed to M5

### Next session
- Implement the museum exhibit: restructure `index.html`, add hash routing in `stream.js`, exhibit styles in `style.css`
- Add questionnaire validation in `events.py`
- Create `checkout.py` for Stripe integration
- Set up Stripe account and add keys to config

## 2026-03-16 — Sandbox idea: analysis gallery

New idea: a gallery of featured analyses built on Reflection's public BigQuery data. Called "Sandbox" — the name signals exploration and grows into itself if we add interactive tools later.

### What it is

A curated gallery page at `/sandbox` showcasing analyses of the dataset. Each entry has a title, description, and link to a hosted notebook or visualization. Seeded with developer-created examples to establish the format and quality bar.

### Why it matters

- **Educational resource.** Real production-quality behavioral data is hard to find outside a job. University students, bootcamp learners, and anyone curious about data ecosystems can use this dataset to practice on real data with real infrastructure behind it.
- **Community potential.** Starts curated, but the format naturally opens up to community contributions later (Observable notebooks, Colab, visualizations, SQL queries).
- **Self-referential.** Analyses of the site become content on the site. The sandbox deepens the loop.

### How it fits into the roadmap

- M5 (separate from the museum exhibit in M4)
- Museum exhibit conclusion links to the sandbox: "Now explore the data yourself"
- Also accessible from homepage navigation
- Format for seeded analyses TBD (Observable, Colab, static write-ups, or a mix)

### Naming decision

Considered: Sandbox, Lab, Analysis, Library. Went with **Sandbox** — it's direct, implies hands-on exploration, and the name earns itself over time if we add a built-in SQL runner or other interactive tools.

### Next session
- Implement the museum exhibit (M4)
- Or: start on sandbox gallery design

## 2026-03-16 — Frontend shipped, site deployed

### What happened
- Built HTML mockup for the "reflection pool" redesign, iterated on copy and layout
- Applied the new theme to the real site: light palette, Lora italic title, lowercase "reflection", personalized visitor greeting ("welcome, visitor a3fb9d2c."), ripple animation on stream events, green bold visitor ID matching the stream
- Deployed to Railway with Docker, set up env vars, BigQuery JSON credentials
- Set up reflection.sh domain on Namecheap → Railway
- Removed BigQuery link from analytics tab (moving to sandbox milestone)
- Split dbt deps into `requirements-pipeline.txt` to keep the Docker image lean

### Open issue
- **SSL cert for www.reflection.sh not provisioning.** DNS is correct (CNAME `www` → `hi6tzv2n.up.railway.app`, TXT `_railway-verify.www` set). Railway domain status may need checking in the dashboard. The Railway default URL (`courageous-expression-production.up.railway.app`) works fine.

## 2026-03-16 — Grant updated, CLAUDE.md refined

### What was done

1. **CLAUDE.md: "Ideas before code" guidance.** Added a line to the Development section establishing the project's pattern: new features start as working documents and milestone entries in `plan.md` before any code is written. This came from a session where Claude jumped to code prematurely — the pattern was clear but wasn't written down.

2. **Grant rewritten around museum exhibit + sandbox.** All five grant files (`project_description.md`, `artistic_merit.md`, `public_engagement.md`, `budget.md`, `bio.md`) updated to replace the self-optimization capstone with the museum exhibit and sandbox as the project's direction. The grant now frames the work as curation and education — walking visitors through the data pipeline, then handing them the tools to explore the data themselves.

   Key shifts:
   - **Project description**: replaced self-optimization paragraph with museum exhibit walkthrough + sandbox as educational resource. Added personal motivation: the gap between what tracking systems do and what people imagine they do.
   - **Artistic merit**: added paragraph about walking through the apparatus (not just seeing it). Reframed the closing around genuine affection for the craft — the project as an invitation to share what the developer sees in data work.
   - **Public engagement**: expanded from 2 paragraphs to 4 — exhibit as structured engagement, sandbox as path from passive visitor to active analyst, educational framing for students.
   - **Budget milestones**: replaced data model → analytics → write-up → self-optimization → polish with museum exhibit → sandbox → curation/refinement → blog → polish.
   - **Bio**: added museum exhibit and educational resource framing.

## 2026-03-16 — Mobile responsive layout

The site wasn't usable on phones — the 42%/58% side-by-side split rendered as two squished columns with no media queries. Added a `@media (max-width: 768px)` breakpoint to `style.css` that stacks the panels vertically, makes the divider horizontal, switches the analytics grid to single-column, and tightens padding. ~54 lines of CSS, no HTML changes.

Verified with Playwright at 375×812 (iPhone size) — layout stacks cleanly, stream scrolls naturally.

**Deployment gotcha:** `git push` alone didn't update Railway — Docker layer caching served stale static files. `railway up` (direct upload) forced a fresh build. Also discovered the `@keyframes eventRipple` block (which used `radial-gradient` inside keyframes) was breaking CSS parsing in some browsers — the `@media` block after it was silently dropped. Removed the ripple animation entirely and added `?v=2` cache-busting param to the stylesheet link. The ripple was likely never working for the same reason.

### Next session
- Implement the museum exhibit (M4) — full design spec in `museum_idea.md`
- The livestream remains the homepage front page, including for the exhibit

## 2026-03-16 — UI cleanup: removed You tab, collapsible stream

Clearing the decks before the museum exhibit redesign. Three changes:

1. **Moved journey card to left panel.** The journey card (real-time pipeline confirmation) now renders directly below the "Fire an event" button instead of in a separate tab. `renderJourneyCard()` already targeted `#journey-container` by ID, so moving the div was all it took.

2. **Removed the tab bar entirely.** The "Everyone" / "You" tab paradigm was replaced with a simple stream header: green dot + "LIVE STREAM" label + presence count + collapse chevron. All tab-switching JS (`switchTab()`, tab click handlers) deleted.

3. **Collapsible stream panel.** Clicking the stream header collapses the entire right panel to a 36px vertical strip showing the green dot, rotated "LIVE STREAM" text, and presence count. The left panel expands via flex to fill the freed space. Smooth CSS transitions on flex/padding. On mobile, the collapsed state hides the stream content but keeps the header horizontal (since the layout is stacked vertically).

Verified with Playwright: expanded view shows full stream, collapsed view shows narrow strip with left panel filling the page, re-expanding restores the stream.

### Next session
- Implement the museum exhibit (M5) — full design spec in `museum_idea.md`
- Read `museum_idea.md` and `plan.md` M5 for the full design before starting
- The collapsible livestream is the homepage; the exhibit builds on top of it

## 2026-03-16 — Museum exhibit implemented

Built the museum exhibit as a dark overlay with 4 steps, two side-by-side collapsible strips, hash routing, and new event types. This was a large change touching 5 files.

### What was built

**Phase 1: Two side-by-side strips**

Replaced the single `.panel.right` with a `.strips-container` holding two `.strip` elements — "live stream" and "analytics". Each strip has a header (label + chevron) and content area. Clicking one expands it and collapses the other (horizontal accordion). When both are collapsed, the left panel expands to fill the space. On mobile, strips stack vertically.

**Phase 2: Dark exhibit overlay + hash routing**

- New `exhibit.js` handles hash routing (`#exhibit-1` through `#exhibit-4`), dark overlay transitions, step navigation, and strip visibility
- "Enter the exhibit" button on homepage replaces the "Fire an event" button (which moved into exhibit step 2)
- `body.exhibit-mode` class triggers dark theme overrides for strips, stream text, journey card
- Strips are hidden by default in exhibit mode, fade in at the correct step (stream at step 2, analytics at step 3)
- Direct URL load (e.g., `/#exhibit-3`) works — exhibit opens at that step
- Back/Next navigation with step counter; Next becomes "Exit" on step 4

**Phase 3: Content, questionnaire, new events**

4 exhibit steps:
1. **Welcome** — "this site analyzes itself." Concept intro.
2. **The Loop** — explains real-time capture. "Fire an event" button + journey card here. Stream strip fades in.
3. **The Pipeline** — explains hourly export, dbt, daily metrics. Analytics strip fades in.
4. **The Apparatus** — closing note + questionnaire textarea (500 char max) + tip jar placeholder.

New event types:
- `funnel_step` — fired on each step navigation with `step` property (welcome, the-loop, the-pipeline, the-apparatus). Humanized in stream as "entered exhibit step: {step}".
- `questionnaire_response` — fired on questionnaire submit with `response_text` property. Humanized as "left a thought". Backend validation: `response_text` required, max 500 chars.

**`_onCapture` fixes:**
- `page_path` now includes `window.location.hash` so PostHog and Supabase both capture which exhibit step the visitor is on
- Custom properties (non-`$` prefixed) now forwarded to `raw_properties` (was always `{}` before)

### Files modified

| File | Changes |
|------|---------|
| `app/templates/index.html` | Two-strip layout, exhibit overlay HTML, moved fire button + journey card to step 2, `_onCapture` fixes, added `exhibit.js` script tag |
| `app/static/style.css` | Complete rewrite: strip layout + accordion, dark overlay, exhibit-mode theme, strip visibility transitions, questionnaire styles, mobile responsive |
| `app/static/stream.js` | Replaced collapse toggle with strip accordion (`toggleStrip()`), added `funnel_step` and `questionnaire_response` to `humanizeEvent()` |
| `app/static/exhibit.js` | **New file.** Hash routing, overlay management, step navigation, strip reveal, questionnaire handler, funnel_step events |
| `app/routes/events.py` | Added `questionnaire_response` validation (response_text required, max 500 chars) |
| `CLAUDE.md` | Added Environment section: always use conda |

### Verified with Playwright

1. Homepage loads — light theme, two strips, stream receiving events
2. Click "Enter the exhibit" — dark overlay, step 1, strips hidden, URL `#exhibit-1`
3. `funnel_step` events appear in stream with step names
4. Next → step 2 — "Fire an event" button, click → stream strip fades in, journey card confirms all 3 pipeline steps
5. Next → step 3 — analytics strip fades in (collapsed, vertical label)
6. Next → step 4 — questionnaire visible, submit → "Recorded.", "left a thought" in stream, textarea disabled
7. Exit → light theme returns, URL back to `/`
8. Direct load `/#exhibit-3` — exhibit opens at step 3
9. Strip accordion — clicking analytics expands it, collapses stream
10. Mobile (375×812) — exhibit stacks content above strips, homepage stacks vertically
11. Backend validation — empty `response_text` returns 422, >500 chars returns 422

### Deployed to Railway

Pushed to main and ran `railway up`. Verified:
- HTML contains exhibit markup (curl check)
- `exhibit.js` served correctly
- Questionnaire validation returns 422 on prod
- Railway URL: `courageous-expression-production.up.railway.app`
- SSL issue with `www.reflection.sh` persists from earlier (pre-existing)

### What's not done yet
- Tip jar is a placeholder link (`href="#"`) — Stripe integration deferred
- Analytics strip just shows "coming soon" — content TBD
- Test with real multi-visitor traffic

### TODO: Architecture diagram in exhibit step 1
Add a static diagram to the Welcome step showing the two data paths:
- **Real-time:** Browser → PostHog → FastAPI → Supabase → WebSocket → Stream
- **Analytical:** PostHog → BigQuery → dbt → metrics

Sets the stage before the visitor walks through each piece in steps 2-4. Simple SVG or styled HTML — no animation needed.

### Next session
- Build the architecture diagram for step 1
- Test with real traffic on the deployed site
- Consider: what goes in the analytics strip?
- Update `museum_idea.md` to reflect what was actually built vs. planned

## 2026-03-16 — Three-strip layout + warehouse strip content

Added a third strip (warehouse) between stream and analytics. Reworked strip content: warehouse strip shows a static SQL query + link to BigQuery console. Analytics strip shows server-rendered metrics from `metrics_daily`. Auto-expand logic: stream at exhibit step 2, warehouse at step 3, analytics at step 4+. All three strips visible at step 5.

## 2026-03-16 — Interactive warehouse/analytics + exhibit chips + /api/query and /api/ask

Major feature session: made the exhibit genuinely interactive. Visitors can now run SQL and ask natural-language questions about Reflection's data.

### What was built

**Backend (3 new files):**
- `app/routes/query.py` — `POST /api/query` (run SQL against BigQuery) and `POST /api/ask` (natural language → Claude → SQL → BigQuery). Validation: SELECT-only, DDL/DML rejection, dataset restricted to `reflection-data.reflection.*`, auto LIMIT 100, 10s timeout, 100MB billing cap.
- `app/services/claude_client.py` — Claude API client with system prompt containing full schema for `fct_events`, `dim_visitors`, `metrics_daily`, and `exhibit_funnel`. Uses `claude-sonnet-4-20250514`.
- `pipeline/dbt/models/marts/exhibit_funnel.sql` — new dbt model: exhibit step completion rates from `stg_events` raw_properties.

**Frontend changes:**
- Warehouse strip: replaced static `<pre>` with editable `<textarea>` + "Run query →" button + results area
- Analytics strip: added "ask a question" divider + text input + "Ask" button + collapsible SQL display + results below the metrics grid
- Exhibit step 3: query chips in left panel ("events by type", "visitors today", "exhibit completion") — click auto-populates textarea and runs query
- Exhibit step 4: question chips ("how many visitors complete the exhibit?", "what's the most common event?", "what percentage of visitors are on mobile?") — click auto-fills input and submits
- Exhibit close button (×) — positioned top-left, works on desktop and mobile
- Removed `renderMetricsSection` from journey card (metrics story moved to step 4)

**Bug fixes:**
- Template referenced `total_sessions` and `events_per_session` but dbt outputs `unique_sessions` and `pages_per_session`. Fixed.
- Added `anthropic_api_key` to config, `anthropic` to requirements.

### Verified with Playwright

| Test | Result |
|------|--------|
| Homepage loads, three strips visible | Pass |
| Warehouse strip: textarea + Run query button | Pass |
| Click "Run query" → real BigQuery results table (2 rows, 0.7s) | Pass |
| Analytics strip: metrics grid with real data | Pass |
| Analytics strip: ask input + Ask button present | Pass |
| /api/ask without API key → graceful error message | Pass |
| Exhibit step 1 → 2 → 3 → 4 navigation | Pass |
| Exhibit step 3: query chips visible | Pass |
| Click "events by type" chip → auto-runs query → results in warehouse strip | Pass |
| Exhibit step 4: question chips visible, analytics strip expanded | Pass |
| Exhibit close button (×) clickable | Pass |

### TODO
- **Deploy with `ANTHROPIC_API_KEY`** set in Railway so `/api/ask` works in production.
- **Run `dbt build`** after deploy to materialize the new `exhibit_funnel` model.
- **AI-generated insight** summarizing query results at step 4 (fast-follow from plan).

---

## 2026-03-16 — Exhibit close button + mobile nav fix

Fixed two z-index stacking issues with the exhibit overlay:

1. **Close button (×):** Moved from `left: calc(42% - 3rem)` (overlapping with strips) to `left: 1.25rem` (top-left corner, inside the overlay's left panel area). No more z-index conflict with the strips-container.

2. **Mobile Next/Back buttons:** On mobile, the strips-container was `position: fixed; z-index: 200` at the bottom of the screen, sitting above the exhibit overlay (`z-index: 100`). The nav buttons inside the overlay were unreachable. Fix: lowered mobile strips z-index to 90 during exhibit mode so the overlay's nav buttons are tappable.

### Verified with Playwright (mobile 375×812)
- Next button works at every step (1→2→3→4→5)
- Exit button works at step 5
- × close button works from step 1
- Desktop close button also works (tested from steps 1 and 3)

### Key design decisions
- Interactive controls live **in the strips** (not the exhibit overlay) so they work on the homepage without the exhibit. The exhibit just adds context and suggested chips.
- SQL validation is regex-based, not a full parser — BigQuery permissions are the real security boundary. The validation catches obvious mistakes and abuse.
- Results rendering uses safe DOM methods (`textContent`, `createElement`) — no `innerHTML` with user-controlled content.

## 2026-03-16 — Replace freeform SQL/NL→SQL with fixed chips + daily cache

Replaced the open-ended warehouse SQL textarea and analytics "ask a question" input with fixed clickable chips, cached daily server-side. Motivation: the freeform interfaces created jailbreak/prompt injection risk (analytics NL→SQL) and unbounded BigQuery cost (both).

### What changed

**Backend (`app/routes/query.py`):**
- Removed `POST /api/query` and `POST /api/ask` entirely
- Added `GET /api/warehouse/{key}` — 3 fixed SQL queries (`events-by-type`, `visitors-today`, `exhibit-completion`) with 24-hour in-memory cache
- Added `GET /api/insights/{key}` — 3 fixed insight questions (`exhibit-completion`, `most-common-event`, `mobile-percentage`) with Claude NL→SQL translation, also 24-hour cached
- Errors are NOT cached — next request retries
- Removed `QueryRequest`, `AskRequest` models and SQL validation helpers (no longer needed since queries are hardcoded)

**Frontend:**
- Warehouse strip: 3 clickable `warehouse-chip` buttons above a readonly textarea. Clicking a chip fetches the cached result, populates the textarea with the SQL, and renders results below. No "Run query" button.
- Analytics strip: replaced text input + Ask button with 3 `insight-chip` buttons. Click → "thinking..." → collapsible SQL + results table.
- Exhibit steps 3 & 4: removed duplicate chip divs from the overlay. Text now directs visitors to the chips in the strips ("click one of the chips in the warehouse panel on the right").

**CSS:**
- Added `.chip-row`, `.warehouse-chip`, `.insight-chip` styles (light theme + dark exhibit-mode overrides)
- Made textarea `readonly` with `resize: none`, dimmed opacity
- Removed `.btn-query`, `.ask-row`, `.ask-input`, `.exhibit-chips` styles
- Mobile: chips wrap naturally, slightly smaller font/padding

### Verified with Playwright

| Test | Result |
|------|--------|
| Homepage: 3 warehouse chips + readonly textarea (empty placeholder) | Pass |
| Homepage: 3 insight chips (no text input) | Pass |
| Click warehouse chip → textarea fills with SQL → results appear | Pass |
| Click same chip again → instant, shows "cached" in meta | Pass |
| Click insight chip → error (no API key locally, expected) | Pass |
| Textarea is readonly | Pass |
| Exhibit step 3 → no duplicate chips, text references strip | Pass |
| Exhibit step 4 → no duplicate chips, analytics strip visible | Pass |
| `POST /api/query` → 404 | Pass |
| `POST /api/ask` → 404 | Pass |
| Mobile (375×812) → chips wrap, tappable, results render | Pass |

### Docs updated
- `architecture.md`: updated route descriptions, caching section, frontend description
- `README.md`: updated interactive feature descriptions

### Deployed and verified on prod

Set `ANTHROPIC_API_KEY` in Railway. Initial key had no credits — added $5 to the Anthropic account, then rotated the key (old one was exposed in conversation). All three insight chips working end-to-end on prod: Claude generates SQL → BigQuery runs it → results cached 24h.

Prod verification (Playwright against Railway URL):
- Warehouse chip "events by type" → results table with real data (2 rows, 0.9s)
- Insight chip "most common event" → `$autocapture` with 4 events (1.1s, then cached)
- 3 visitors online during testing

### Next session

**Exhibit:**
- Consider adding a "modeling" step between "analytics" and the conclusion — what would be modeled? Prediction, forecasting, etc.
- Consider adding visualizations to the analytics step now that queries are limited to 3 fixed questions
- Mobile exhibit UX: Next button works but query results/metrics are grayed out and too small — rethink how to make the complex exhibit mobile-friendly
- "Visitors today" warehouse query returns zero rows — fix the query
- Syntax highlighting for the readonly SQL textarea
- Consider renaming "welcome" step → "concept" (where the artistic concept/copy will live)
- Consider renaming steps with numerical indices (risky for long-term)
- Tip jar vs. gift shop: selling prints of the website via Printful leans into the LACMA grant's artistic angle. A gift shop could be its own strip at the final exhibit step (currently showing analytics, which feels stale)
- Add NL interpretation of warehouse query results — the NL→SQL works but results should get back to NL

**Frontend:**
- Rename "live stream" → "streaming"
- Coordinate visitor ID color on homepage with color in the stream
- Consider replacing visitor IDs with cute generated names (like Railway's app naming — more memorable/fun)

**Other:**
- Run `dbt build` to refresh marts with new traffic data

## 2026-03-17 — Brainstorm: modeling step for the exhibit

### Rationale

From a DS perspective, the exhibit's pipeline narrative (capture → store → transform → analyze → reflect) is missing a step that any real company's data stack would have: **modeling**. After analytics, you build models on the data. Adding this step makes the exhibit a more complete representation of a production data stack.

### Options considered

- **Real-time scoring** (e.g., predict next click): ruled out — the exhibit's analytical path is batch, and real-time ML would require a serving layer that doesn't fit the current architecture.
- **Predictive modeling** (e.g., churn, return visit): not enough data volume yet to make this meaningful.
- **Text analysis on questionnaire responses**: NLP on the free-text responses visitors leave at the end of the exhibit. Topic clustering, sentiment distribution, and/or Claude summarization of what visitors have said.

### Direction chosen: text analysis on questionnaire responses

**Why this fits:**
- **Self-referential.** Visitors leave their thoughts about the site, and the site models those thoughts back at them. The loop deepens.
- **Batch-native.** Runs daily on accumulated `questionnaire_response` texts — fits the existing analytical path (BigQuery + dbt + daily refresh).
- **Gets richer with more data.** Unlike behavioral event modeling, text analysis becomes more interesting as more visitors contribute. Topic clusters emerge, sentiment shifts over time.
- **Completes the pipeline narrative.** The exhibit would become: capture → store → transform → analyze → **model** → reflect.

### Status

Idea stage — not ready for implementation. Added to `plan.md` under Milestone 5 as a tracked TODO. Design decisions (which NLP techniques, how to display results, whether to use Claude or a dedicated NLP pipeline) are all TBD.

## 2026-03-17 — Gift shop strip

Added a shop strip to the exhibit as the fifth collapsible panel (stream → warehouse → analytics → modeling → shop). The shop appears at step 6 and auto-expands when the visitor reaches it.

Three items:
1. **"keep the lights on"** — pay-what-you-wish contribution toward hosting (BigQuery, Railway, Supabase, PostHog). Text input for amount.
2. **"a visualization"** — a print of the site's data. Price TBD, button disabled.
3. **"buy the developer a coffee"** — fixed $5.

All buy buttons fire a `checkout_started` event with `item_id`, `item_name`, and `price` properties. The event is validated server-side and humanized in the stream as "started checkout: {item_name}". Buttons are marked "coming soon" — Stripe integration is deferred.

Replaced the old tip jar link in step 6 with text directing visitors to the shop strip on the right.

Also renamed the step 6 funnel step from `"the-apparatus"` to `"the-shop"` in the exhibit's `stepNames` array (the exhibit heading still says "the apparatus").

### Files changed
- `app/templates/index.html` — shop strip HTML, removed tip jar, updated step 6 copy, cache-busted JS/CSS to v15
- `app/static/style.css` — shop card styles (light + dark), removed `.exhibit-tip-jar`
- `app/static/exhibit.js` — shop strip visibility/auto-expand, buy button event handlers, updated stepNames
- `app/static/stream.js` — humanize `checkout_started`
- `app/routes/events.py` — `checkout_started` validation

### Next steps
- Wire up Stripe for actual payments
- Design the visualization print
- Modeling step content (NLP on questionnaire responses)

## 2026-03-17 — Stripe integration for "keep the lights on"

Wired up Stripe Checkout so the "keep the lights on" donation in the shop strip actually processes payments. The visualization card keeps its "coming soon" overlay.

**How it works:** Visitor enters an amount → clicks Buy → frontend POSTs to `/api/checkout/create-session` → backend creates a Stripe Checkout Session → visitor is redirected to Stripe's hosted payment page → after payment, Stripe sends a `checkout.session.completed` webhook to `/api/stripe/webhook` → webhook handler inserts a `purchase_complete` event into Supabase and broadcasts it via WebSocket to the live stream.

The self-referential loop is preserved: purchase events flow through the same pipeline as all other events (Supabase → BigQuery → dbt), so they show up in warehouse queries, analytics, and the live stream.

**Key decisions:**
- Used Stripe Checkout (hosted page) rather than Stripe Elements (embedded form) — simpler, PCI compliant out of the box, no need to handle card inputs ourselves.
- Redirect URLs are built dynamically from the incoming request origin, so they work on both the Railway URL and `reflection.sh` without code changes.
- The `purchase_complete` event is inserted server-side by the webhook (not the frontend) so it's authoritative — only fires on actual completed payments.
- Default donation amount is $5 (set as `value`, not `placeholder`, so clicking Buy without changing it works).

**Stripe setup (sandbox/test mode):**
- Created webhook endpoint pointing to Railway URL (`/api/stripe/webhook`), listening for `checkout.session.completed`
- Three env vars in Railway: `STRIPE_SECRET_KEY`, `STRIPE_PUBLISHABLE_KEY`, `STRIPE_WEBHOOK_SECRET`
- `reflection.sh` DNS wasn't resolving, so webhook uses the Railway URL for now

### Files changed
- `requirements.txt` — added `stripe>=8.0.0`
- `app/config.py` — added Stripe settings
- `.env.example` — added Stripe env vars
- `app/routes/checkout.py` — new file, checkout session + webhook endpoints
- `app/main.py` — registered checkout router
- `app/templates/index.html` — removed "coming soon" from keep-the-lights-on card, set default amount to $5, cache-busted to v16/v18
- `app/static/exhibit.js` — buy button redirects to Stripe, success toast on return, error handling
- `app/static/stream.js` — humanize `purchase_complete` events
- `app/static/style.css` — checkout error + success toast styles
- `architecture.md` — Stripe section, new event type, new API routes
- `plan.md` — marked Stripe integration as complete

### Also in this session

**PostHog server-side capture (`f8b7b08`):** The Stripe webhook inserts `purchase_complete` into Supabase but that doesn't flow to PostHog (PostHog capture happens client-side via `_onCapture`). Added server-side `posthog.capture()` in the webhook handler so purchase events reach BigQuery through the PostHog → BigQuery pipeline. Required adding `posthog-python` to requirements and initializing the PostHog client in the checkout router.

**`fct_purchases` mart + metrics_daily purchase columns (`52ff5f2`):** Created `pipeline/dbt/models/marts/fct_purchases.sql` — extracts purchase events from `stg_events` with amount, item_id, item_name parsed from `raw_properties`. Added purchase columns to `metrics_daily`: `total_purchases`, `total_revenue`, `unique_purchasers`. Updated `schema.yml` with documentation for both.

**Copy fix (`69e34e1`):** Removed directional "on the right" from exhibit step copy — it's wrong on mobile where strips stack below.

### Additional files changed
| File | Changes |
|------|---------|
| `app/routes/checkout.py` | PostHog server-side capture in webhook handler |
| `app/templates/index.html` | Removed "on the right" from exhibit copy |
| `pipeline/dbt/models/marts/fct_purchases.sql` | New mart: purchase events with amount/item/visitor |
| `pipeline/dbt/models/marts/metrics_daily.sql` | Added purchase columns (total_purchases, total_revenue, unique_purchasers) |
| `pipeline/dbt/models/marts/schema.yml` | Documentation for fct_purchases and new metrics_daily columns |

### Next steps

**Exhibit content:**
- **Modeling step (step 5) — open question.** The NLP-on-questionnaire-responses idea has a sequencing problem: step 5 comes *before* step 6 (the apparatus), which is where visitors leave their thoughts. So at step 5 the current visitor hasn't contributed yet. Need to rethink what goes here — maybe show results from *previous* visitors' responses, or find a different modeling concept entirely. Leaving as TODO.
- Architecture diagram for step 1 (the two data paths: real-time and analytical)
- AI-generated insight summarizing query results at step 4
- NL interpretation of warehouse query results (SQL results → natural language)

**Shop / Stripe:**
- Fix `reflection.sh` DNS so the custom domain works again
- Switch Stripe from sandbox to live mode when ready
- Design the visualization print (item 2 in shop, currently "coming soon")
- End-to-end purchase test: buy → webhook → stream → BigQuery → dbt → metrics

**Frontend polish:**
- Mobile exhibit UX: query results/metrics are grayed out and too small — rethink for mobile
- "Visitors today" warehouse query returns zero rows — fix the query
- Coordinate visitor ID color on homepage with color in the stream
- Consider replacing visitor IDs with cute generated names (like Railway's app naming)

**Pipeline:**
- `questionnaire_responses` model (staged but not committed — in `pipeline/dbt/models/marts/`)
- Run `dbt build` to materialize all new marts with real traffic data

**Future milestones:**
- Sandbox mode (plan.md Milestone 6) — let visitors write and run their own dbt models
- Blog / write-up of the project

## 2026-03-27 — Fixed "visitors today" query + daily dbt cron

### What was done

1. **"Visitors today" → "visitors this week"**: The warehouse chip query returned zero rows because `fct_events` is a dbt-materialized table and the query used `CURRENT_DATE()`. Changed to query last 7 days with daily breakdown (`DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY)`, grouped by day). Renamed chip label and query key from `visitors-today` to `visitors-this-week`.

2. **Daily dbt build via GitHub Actions**: Created `.github/workflows/dbt-build.yml` — runs `dbt build --target prod` daily at 6am UTC with manual `workflow_dispatch` trigger. Uses `BIGQUERY_KEY_JSON` GitHub secret written to a temp file (`/tmp/bq-key.json`), since dbt's `service-account-json` method doesn't reliably parse JSON from env vars.

3. **dbt profiles.yml prod target**: Changed from `method: service-account-json` with `keyfile_json` (broken — dbt expects a YAML dict, not a JSON string from `env_var()`) to `method: service-account` with `keyfile: /tmp/bq-key.json` (written by the GitHub Actions workflow step).

### Key learning

dbt's `service-account-json` with `env_var()` is fragile — the env var returns a string but dbt expects a parsed dict. Writing the JSON to a temp file and using `service-account` with `keyfile` is more reliable and works identically.

### Files changed
- `app/routes/query.py` — new query SQL and key name
- `app/templates/index.html` — chip label updated
- `.github/workflows/dbt-build.yml` — new file
- `pipeline/dbt/profiles.yml` — prod target switched to keyfile method

### Deployed
- Railway: `railway up` for the query fix
- GitHub Actions: dbt build #2 succeeded (1m 22s), all marts refreshed

## 2026-03-28 — Hardcode insight SQL, Claude summaries, remove modeling step

### What was done

1. **Replaced Claude NL→SQL with hardcoded SQL + Claude summaries.** The 3 insight chips ("how many visitors complete the exhibit?", "what's the most common event?", "what percentage are on mobile?") now use hardcoded SQL instead of asking Claude to generate it. Claude now summarizes the query results in 1-2 sentences, shown above the results table. If the API key is missing, results still display — just without a summary. `claude_client.py` rewritten: `summarize_results()` replaces `question_to_sql()`.

2. **Removed the modeling step and strip.** The empty "the model" step (step 5) and the modeling strip ("Coming soon.") are gone. Exhibit is now 5 steps instead of 6.

3. **Renamed exhibit steps to match strip names.** Funnel step events changed from `the-loop`, `the-warehouse`, `the-pipeline`, `the-model`, `the-shop` to `welcome`, `stream`, `warehouse`, `analytics`, `shop`. The `exhibit_funnel` dbt model maps both old and new names to the same step numbers so historical data still works.

### Key decisions

- Claude is more useful summarizing data than generating SQL for fixed questions. The SQL never changes, but the data does — so the summary is the part that should be dynamic.
- Step names now match strip names exactly — simpler mental model, no "the-" prefix naming convention to maintain.

### Files changed
- `app/routes/query.py` — `INSIGHT_QUERIES` dict with hardcoded SQL, endpoint calls `summarize_results()`
- `app/services/claude_client.py` — rewritten for result summarization
- `app/templates/index.html` — removed modeling strip + step, renumbered, "insights" divider
- `app/static/exhibit.js` — updated stepNames, removed modeling logic
- `app/static/stream.js` — shows summary paragraph, updated SQL label
- `app/static/style.css` — replaced modeling styles with insight-summary styles
- `pipeline/dbt/models/marts/exhibit_funnel.sql` — maps both old + new step names
- `pipeline/dbt/models/marts/schema.yml` — updated step name description
- `architecture.md`, `README.md` — updated

### Verified
- Desktop: all 5 exhibit steps work, strips appear at correct steps
- Mobile (375×812): exhibit navigable, all buttons accessible
- New funnel step names appear in live stream ("entered exhibit step: stream")
- Deployed to Railway

### TODO (deferred)
- Rewrite exhibit copy (step headings + body text)
- Pick better insight questions
- Mobile exhibit UX improvements (query results/metrics still small)
- `reflection.sh` DNS/SSL fix
- Stripe sandbox → live
- UMAP visualization of questionnaire responses (see below)

## 2026-03-28 — Idea: UMAP visualization of questionnaire responses

Replace the shop as the final exhibit strip with a 2D UMAP scatter plot of embedded questionnaire responses. Each dot is a response; hovering shows the text. The visitor leaves a thought at the last exhibit step and sees where it lands in the space of everyone else's thoughts. The shop moves to appear only when the user exits the exhibit.

### Why this fits

The self-referential loop deepens: you contribute text, it gets embedded and projected alongside everyone else's contributions, and you see the result immediately. It's the modeling step that was missing — not ML for ML's sake, but a genuine use of embeddings that makes the data visible in a new way.

### Architecture sketch

**Daily batch (GitHub Actions cron):**
1. Fetch questionnaire responses from BigQuery
2. Embed with external API (OpenAI or Voyage — cheap at this scale)
3. Fit UMAP on all embeddings
4. Save 2D coordinates to a BigQuery table (or Supabase)
5. Pickle the fitted UMAP model → upload to Supabase Storage

**FastAPI server:**
1. On startup: download fitted UMAP model from Supabase Storage, cache in memory
2. Serve batch coordinates from BigQuery (cached) for the scatter plot

**Live path (on questionnaire submit):**
1. Embed the new response via external API
2. `umap_model.transform([embedding])` → get 2D coordinates
3. Broadcast coordinates + text via WebSocket → dot appears live on everyone's screen

**Frontend:**
- 2D scatter plot (D3 or canvas) showing all responses
- Hover/click shows response text
- New responses animate in via WebSocket

### Open questions
- Which embedding API? OpenAI `text-embedding-3-small` is cheap and good enough.
- UMAP parameters (n_neighbors, min_dist) — need to experiment once there's enough data.
- How many responses before the visualization is interesting? Probably need 20-30 minimum for clusters to emerge.
- Color coding? Could color by sentiment, time period, or just use a single color.
- What happens with very few responses? Show a message like "N more thoughts needed before the map appears."

---

## 2026-03-29 — Mobile exhibit redesign + cleanup

### Problem

The desktop exhibit uses a split layout — exhibit text on the left, interactive strips on the right. On mobile this was completely broken: the overlay sat at z-index 100 blocking all strip interaction, strip content bled through the semi-transparent background, and query/insight chips were untappable.

### Solution

On mobile (≤768px), the exhibit is now a self-contained vertical walkthrough. Each step inlines the relevant strip content directly:
- **Step 2 (stream):** Mini-stream showing last 8 events, updated live via WebSocket
- **Step 3 (warehouse):** Query chips + SQL textarea + results table, all inline
- **Step 4 (analytics):** Metrics grid + insight chips with Claude summaries, all inline
- **Step 5 (shop):** "Keep the lights on" donation card with working Buy button

Desktop is unchanged — strips still appear alongside the overlay as before.

### Implementation details
- Added `exhibit-mobile-content` divs inside each exhibit step, hidden on desktop via CSS (`display: none`)
- On mobile during exhibit, strips container is `display: none` — no z-index conflicts
- Warehouse/insight chip click handlers use `closest()` to find their result container, so the same handler works for both strip-based and inline chips
- Stream strip no longer auto-expands on mobile homepage — all four strip headers visible

### Other changes
- Created `TODO.md` as a living checklist (separate from lab notebook history)
- Cleaned up `plan.md` — removed strikethrough noise, condensed done milestones, linked TODO
- Fixed stale exhibit copy: step 4 now says "last 7 days" instead of "today's metrics"
- Added `CLAUDE.md` instruction to propose `TODO.md` additions when new work surfaces

---

## 2026-03-29 — Exhibit restructure + website cleanup

### Exhibit restructure
Replaced the shop as exhibit step 5 with "modeling." The exhibit is now: welcome → stream → warehouse → analytics → modeling. The shop strip stays on the homepage sidebar but is no longer part of the guided walkthrough.

The modeling step shows a questionnaire ("leave a thought") and a counter of total responses. Once 50+ responses exist, a UMAP visualization will render — each dot is a thought, clusters form where people said similar things. Decided against seeding with synthetic data because it contradicts the site's spirit of authenticity, and fake thoughts could prime real ones.

UMAP pipeline scaffolding is in place (`pipeline/umap/`, `/api/umap/coordinates` endpoint) but won't produce output until the response threshold is met.

### Website cleanup
- **Exhibit funnel fix:** Old step names (`the-loop`, `the-warehouse`, etc.) and new names (`stream`, `warehouse`, etc.) were showing as separate rows in the funnel query. Consolidated in the dbt model by grouping on step number and mapping to canonical names.
- **Exit button:** Styled with amber border/text to distinguish from Back/Next.
- **Pipeline countdown:** Was showing "metrics refresh in Xm" assuming hourly dbt runs. Fixed to show daily countdown (6am UTC). Split the single status line across three strips — streaming shows export timing, warehouse shows raw data freshness + pipeline refresh, analytics shows next dbt refresh.

### Files changed
| File | Change |
|---|---|
| `app/templates/index.html` | Step 5 → modeling with response counter, pipeline status in warehouse/analytics strips |
| `app/static/exhibit.js` | stepNames updated, shop strip toggling removed, exit button class toggle |
| `app/static/stream.js` | Pipeline countdown split across three strips, daily dbt schedule |
| `app/static/style.css` | `.exhibit-btn-exit` amber styling |
| `app/config.py` | `dbt_cron_hour_utc` replaces `dbt_cron_minute`, added `openai_api_key` |
| `app/routes/pages.py` | Passes `response_count` and `dbt_cron_hour_utc` to template |
| `app/services/bigquery_client.py` | Added `get_response_count()` |
| `app/routes/umap.py` | New — serves precomputed UMAP coordinates |
| `app/main.py` | Registered umap router |
| `pipeline/dbt/models/marts/exhibit_funnel.sql` | Consolidated old/new step names, added "modeling" |
| `pipeline/umap/` | New — seed_responses.py, embed_and_fit.py (scaffolding for future use) |
