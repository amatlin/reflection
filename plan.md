# Reflection

A website that tracks and analyzes its own usage, then shows you how it did it.

## Concept

Reflection is a self-referential website — you visit it, interact with it, and those interactions become the data you can explore on the site. The more people use it, the more interesting the data becomes.

The site exposes its own data infrastructure, modeled after how a real tech company's data stack works. A live operational database for near real-time event data, and ETL into an analytical layer for heavier queries and historical analysis.

## Why

Real, live behavioral data is hard to find outside of a job. Public datasets are static snapshots. Synthetic data never feels right. Reflection generates real data from real users doing real things — and the thing they're doing is looking at the data.

## Milestones

1. Landing page with live event stream (done)

2. Analytical backbone — pipeline + analytics view (done)
- PostHog batch export → BigQuery warehouse (hourly)
- dbt Core models: staging, facts, dimensions, daily metrics
- Analytics tab on homepage with server-rendered metrics from `metrics_daily`

3. Frontend redesign + deployment (done)
- Light theme, deployed to Cloud Run at reflection.sh

4. Livestream UX overhaul (done)
- Humanized event names, journey card with real-time confirmations
- Pipeline countdowns, "you" labels, mobile responsive layout
- Collapsible stream panel with fire-an-event button

5. Guided walkthrough (done — polish items in [TODO.md](TODO.md))
- Dark overlay walkthrough with 5 steps: how it works → stream → warehouse → analytics → modeling
- Collapsible strips (stream + warehouse + analytics) with horizontal accordion; shop is a homepage strip
- Hash routing (`#exhibit-1` through `#exhibit-5`), direct URL load supported
- "Fire an event" button + journey card in step 2
- Strips fade in at correct steps (stream at 2, warehouse at 3, analytics at 4)
- `funnel_step` events on navigation, `questionnaire_response` on submit, `checkout_started` on buy
- Interactive warehouse strip: SQL textarea + 3 query chips + results table
- Interactive analytics strip: 7-day server-rendered metrics + 3 insight chips with hardcoded SQL + Claude result summaries
- Modeling step: questionnaire + response counter, UMAP visualization after 50 responses
- `exhibit_funnel` dbt model with step completion rates
- Daily dbt cron via GitHub Actions (6am UTC)
- Gift shop with Stripe Checkout (pay-what-you-wish donation) — homepage strip only
- Deployed to Cloud Run

6. Simulated traffic — AI agents
- 10-20 agents with distinct personas that browse the site via headless browsers
- Agents navigate the walkthrough at different speeds, click different chips, leave questionnaire responses
- Hybrid approach: Playwright handles browser mechanics, Claude decides what to do at each step
- Generates realistic traffic patterns and meaningful text data for the UMAP visualization

7. Sandbox
- Gallery page at `/sandbox` featuring analyses of Reflection's public BigQuery data
- Featured analyses seeded by the developer
- Accessible from homepage navigation and linked from the walkthrough conclusion
- Positions the dataset as an educational resource for students and others learning about production data ecosystems

8. Blog post
- Write-up hosted on the site at `/blog` and cross-posted externally
- Covers the concept, architecture, and a link to explore the data

## Future Ideas

- Sandbox: community submissions — open contributions from visitors
- Self-optimization: define business goals, run experiments, show visitors which variant they're in
- UMAP visualization of embedded questionnaire responses (pipeline scaffolded, awaiting 50+ responses)
