# TODO

Open work items for Reflection. The [lab notebook](LAB_NOTEBOOK.md) tracks what's been done; this tracks what's left.

## Outage recovery (2026-10-05)

- ~~Migrate hosting Railway → Cloud Run~~ (done)
- ~~Re-enable the `dbt build` GitHub Actions workflow~~ (done, re-triggered)
- ~~DNS/SSL for reflection.sh~~ (done, working on Cloud Run)
- Confirm dbt build succeeds and warehouse/analytics chips work
- Check PostHog → BigQuery batch export; re-enable if paused
- Confirm Supabase `events` table still has data
- Update architecture.md hosting sections; delete Railway project
- Add a `/health` endpoint that reports each service's status (Supabase, BigQuery freshness, PostHog export lag)
- Keep-alive plan so the stack survives long idle periods (dbt workflow and Supabase both stop when untouched)

## Reframing (2026-10-06)

- Replace Narcissus image with something new (slot exists in walkthrough step 1)
- Rewrite copy/ working files to match new educational tone
- Pick better / more interesting insight questions for the analytics strip
- Update architecture.md to remove art references
- Consider replacing hex visitor IDs with generated names

## Simulated traffic — AI agents

- Design 10-20 agent personas
- Build hybrid agent system (Playwright + Claude for decisions)
- Schedule agents to run daily with staggered timing
- Decide whether to tag agent traffic or leave it unlabeled

## Mobile

- Test on real iOS/Android devices (only verified via Playwright viewport resize)

## Payments

- Stripe sandbox to live mode
- End-to-end purchase test

## Modeling step (UMAP visualization)

Pipeline scaffolding is in place (embed_and_fit.py, /api/umap/coordinates endpoint). Placeholder shows response counter until 50+ exist. Agents should generate enough responses to unblock this.

- Frontend: D3 or Plotly scatter plot in the modeling strip (after 50 responses)
- Wire embed_and_fit.py to daily cron alongside dbt
- Content moderation strategy before showing user-submitted text
