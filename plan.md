# Reflection

A website whose sole purpose is to analyze itself.

## Concept

Reflection is a self-referential website — you visit it, interact with it, and those interactions become the data you can explore on the site. It's a mirror. The more people use it, the more interesting the data becomes.

The site exposes its own data infrastructure, modeled after how a real tech company's data stack works — without sharing proprietary details. A live operational database for near real-time event data, and ETL into an analytical layer for heavier queries and historical analysis.

## Why

Real, live behavioral data is hard to find outside of a job. Public datasets are static snapshots. Synthetic data never feels right. Reflection generates real data from real users doing real things — and the thing they're doing is looking at the data.

## Milestones

1. ~~Landing page with live event stream~~ (done)

2. ~~Analytical backbone (pipeline + analytics view)~~ (done)
- ~~PostHog batch export → BigQuery warehouse (hourly)~~
- ~~dbt Core models: staging, facts, dimensions, daily metrics~~
- ~~Analytics tab on homepage showing numbers from `metrics_daily` mart~~
- ~~Server-rendered with 1-hour in-memory BigQuery cache~~

3. ~~Frontend redesign + deployment~~ (done)
- ~~Light "reflection pool" theme replacing dark terminal aesthetic~~
- ~~Deployed to Railway at reflection.sh~~
- ~~Public BigQuery dataset — visitors can query the data themselves~~

4. ~~Livestream UX overhaul~~ (done)
- ~~Humanized event names: `$pageview` → "viewed the page", `$autocapture` → `clicked "Button"`, hide `$pageleave`~~
- ~~"Everyone" / "You" tabs replacing Live Stream / Analytics~~ → tabs removed; stream is now a collapsible panel, journey card moved to left panel
- ~~Single "Fire an event" button replacing three action buttons~~
- ~~Journey card: real-time confirmations (captured → stored → streamed) with staggered animations~~
- ~~Journey card: dbt transformation preview (event_name, device, browser, os) computed client-side~~
- ~~Journey card: metrics contribution showing which `metrics_daily` aggregates the event affects~~
- ~~Pipeline countdowns in header (warehouse export + dbt refresh)~~
- ~~"you" label on your own events in the stream~~
- ~~Mobile responsive layout~~

5. Museum exhibit funnel
- Restructure site as a guided walkthrough: Homepage → Exhibit (8 steps) → Conclusion
- Each exhibit step explains one stage of the data pipeline (logging, streaming, export, transformation, metrics, analysis)
- Conclusion screen: thank-you note, questionnaire (text box → `questionnaire_response` event), gift shop (Stripe → `checkout_started` / `purchase_complete` events)
- Single-page hash routing (`#home`, `#exhibit-intro`, ..., `#exhibit-conclusion`), WebSocket stays alive across screens
- Generates `funnel_step` events on every navigation — enables funnel analysis of the exhibit itself
- See `museum_idea.md` for full design

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
- Sandbox: built-in SQL runner for on-site exploration
- Architecture diagram showing data flowing through the infrastructure
- Self-optimization: define business goals, run experiments, show visitors which variant they're in
- ML model serving on dbt marts
