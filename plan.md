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

4. Blog post
- Write-up hosted on the site at `/blog` and cross-posted externally
- Covers the concept, architecture, art angle, and a link to explore the data

## Future Ideas

- Meaningful data model: sign-up, checkout, review flows generating richer event types
- SQL playground with suggested queries
- Architecture diagram showing data flowing through the infrastructure
- Self-optimization: define business goals, run experiments, show visitors which variant they're in
- Merch store to generate e-commerce and funnel data
- ML model serving on dbt marts
