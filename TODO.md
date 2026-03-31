# TODO

Open work items for Reflection. The [lab notebook](LAB_NOTEBOOK.md) tracks what's been done; this tracks what's left.

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
