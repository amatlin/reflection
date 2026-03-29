# Reflection

A website whose sole purpose is to analyze itself.

## Concept

Reflection is a self-referential website — you visit it, interact with it, and those interactions become the data you can explore on the site. It's a mirror. The more people use it, the more interesting the data becomes.

The site exposes its own data infrastructure, modeled after how a real tech company's data stack works — without sharing proprietary details. A live operational database for near real-time event data, and ETL into an analytical layer for heavier queries and historical analysis.

## Why

Real, live behavioral data is hard to find outside of a job. Public datasets are static snapshots. Synthetic data never feels right. Reflection generates real data from real users doing real things — and the thing they're doing is looking at the data.

## Milestones

1. Landing page with live event stream (done)

2. Analytical backbone — pipeline + analytics view (done)
- PostHog batch export → BigQuery warehouse (hourly)
- dbt Core models: staging, facts, dimensions, daily metrics
- Analytics tab on homepage with server-rendered metrics from `metrics_daily`

3. Frontend redesign + deployment (done)
- Light "reflection pool" theme
- Deployed to Railway at reflection.sh

4. Livestream UX overhaul (done)
- Humanized event names, journey card with real-time confirmations
- Pipeline countdowns, "you" labels, mobile responsive layout
- Collapsible stream panel with fire-an-event button

5. Museum exhibit funnel (done — polish items in [TODO.md](TODO.md))
- Dark overlay exhibit with 5 steps: Welcome → Stream → Warehouse → Analytics → Shop
- Collapsible strips (stream + warehouse + analytics + shop) with horizontal accordion
- Hash routing (`#exhibit-1` through `#exhibit-5`), direct URL load supported
- "Fire an event" button + journey card in step 2
- Strips fade in at correct steps (stream at 2, warehouse at 3, analytics at 4, shop at 5)
- `funnel_step` events on navigation, `questionnaire_response` on submit, `checkout_started` on buy
- Interactive warehouse strip: SQL textarea + 3 query chips + results table
- Interactive analytics strip: 7-day server-rendered metrics + 3 insight chips with hardcoded SQL + Claude result summaries
- `exhibit_funnel` dbt model with step completion rates
- Daily dbt cron via GitHub Actions (6am UTC)
- Gift shop with Stripe Checkout (pay-what-you-wish donation)
- Deployed to Railway
- See `museum_idea.md` for original design

6. Sandbox
- Gallery page at `/sandbox` featuring analyses of Reflection's public BigQuery data
- Featured analyses seeded by the developer — each with a title, description, and link to a hosted notebook or visualization
- Accessible from homepage navigation and linked from the museum exhibit conclusion
- Positions the dataset as an educational resource for students and others learning about production data ecosystems

7. Blog post
- Write-up hosted on the site at `/blog` and cross-posted externally
- Covers the concept, architecture, art angle, and a link to explore the data

## Future Ideas

- Sandbox: community submissions — open contributions from visitors
- Self-optimization: define business goals, run experiments, show visitors which variant they're in
- UMAP visualization of embedded questionnaire responses (design in lab notebook)
