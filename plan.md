# Reflection

A website whose sole purpose is to analyze itself.

## Concept

Reflection is a self-referential website — you visit it, interact with it, and those interactions become the data you can explore on the site. It's a mirror. The more people use it, the more interesting the data becomes.

The site exposes its own data infrastructure, modeled after how a real tech company's data stack works — without sharing proprietary details. A live operational database for near real-time event data, and ETL into an analytical layer for heavier queries and historical analysis.

## Why

Real, live behavioral data is hard to find outside of a job. Public datasets are static snapshots. Synthetic data never feels right. Reflection generates real data from real users doing real things — and the thing they're doing is looking at the data.

## Milestones

1. ~~Landing page with live event stream~~ (done)

2. Analytics layer on existing data
- Live architecture diagram: an animated SVG showing events flowing through the actual infrastructure (browser → API → Supabase → PostHog → warehouse → dashboard) in real time, triggered by visitor actions
- Dashboards showing aggregate patterns from M1 events (traffic, sessions, devices, geo)
- The diagram grows as new infrastructure is added in later milestones

3. Meaningful data model
- Add flows (sign-up, checkout, review) that generate richer data types: funnels, natural language, pricing
- Each new flow immediately enriches the analytics layer from M2
- Solid, extensible event schema

4. Offline data + deeper analytics
- ETL from operational layer to warehouse (dbt)
- SQL playground with suggested queries
- Expose the pipeline itself as content (last snapshot, rows loaded, transformation logic)

5. Write-up
- Written posts about the architecture, the art concept, the goal of the website, how to explore the data, example analyses
- Tutorial notebooks (colab?) showing what can be done with the data

6. Self-optimization
- Define business goals for a business that doesn't exist (north star metric, guardrails) and let the site optimize itself against them
- Run its own experiments: generate variants, assign visitors, measure results, deploy winners — automatically
- The visitor sees everything: the hypothesis, which variant they're in, the current results, the decision
- The site becomes the only website that shows you the experiments it's running on you
- Depends on M2–M4 being solid; this is the capstone

## Future Ideas

- Merch store to generate e-commerce and funnel data
- Open-source the infrastructure code
