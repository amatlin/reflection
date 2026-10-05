# TODO

Open work items for Reflection. The [lab notebook](LAB_NOTEBOOK.md) tracks what's been done; this tracks what's left.

## Outage recovery (2026-10-05)

Site down since Railway trial expired 2026-04-15. See [`cloud_run_migration.md`](cloud_run_migration.md).

- Migrate hosting Railway → Cloud Run (runbook steps 3–9)
- Confirm Supabase finished restoring (resumed 2026-10-05) and the `events` table still has data
- Check PostHog → BigQuery batch export; re-enable if paused
- Re-enable the `dbt build` GitHub Actions workflow (disabled for inactivity 2026-05-30)
- Update README.md / architecture.md hosting sections once migrated; delete Railway project
- Add a `/health` endpoint that reports each service's status (Supabase, BigQuery freshness, PostHog export lag)
- Keep-alive plan so the stack survives long idle periods (dbt workflow and Supabase both stop when untouched)

## Website cleanup

- Revisit spirit.md to reflect new exhibit voice (first person, water metaphor, Narcissus)
- Pick better / more interesting insight questions for the analytics strip
- Consider replacing hex visitor IDs with generated names
- `reflection.sh` DNS/SSL fix


## Mobile

Mobile exhibit redesigned as inline walkthrough (2026-03-29). Remaining:

- Test on real iOS/Android devices (only verified via Playwright viewport resize)

## Payments

- Stripe sandbox to live mode
- End-to-end purchase test

## Modeling step (UMAP visualization)

Pipeline scaffolding is in place (embed_and_fit.py, /api/umap/coordinates endpoint). Placeholder shows response counter until 50+ exist. Blocked on collecting responses.

- Frontend: D3 or Plotly scatter plot in the modeling strip (after 50 responses)
- Wire embed_and_fit.py to daily cron alongside dbt
- Content moderation strategy before showing user-submitted text
