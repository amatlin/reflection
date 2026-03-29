# TODO

Open work items for Reflection. The [lab notebook](LAB_NOTEBOOK.md) tracks what's been done; this tracks what's left.

## Website cleanup

- Rewrite exhibit copy (step headings + body text to match new step names)
- Pick better / more interesting insight questions for the analytics strip
- Consider replacing hex visitor IDs with generated names
- Architecture diagram in exhibit step 1 (static SVG/HTML showing both data paths)
- `reflection.sh` DNS/SSL fix


## Mobile

Mobile exhibit redesigned as inline walkthrough (2026-03-29). Remaining:

- Test on real iOS/Android devices (only verified via Playwright viewport resize)

## Payments

- Stripe sandbox to live mode
- End-to-end purchase test

## UMAP visualization (replaces shop as final exhibit strip)

2D scatter plot of embedded questionnaire responses. Each dot is a response; hovering shows the text. The visitor submits a thought, it gets embedded and projected, and they see where it lands. Design documented in [lab notebook entry 2026-03-28](LAB_NOTEBOOK.md).

- Daily batch job: fetch responses from BigQuery, embed, fit UMAP, save coordinates + serialized model
- FastAPI: load fitted UMAP model on startup, serve batch coordinates
- Frontend: D3 or Plotly scatter plot in the exhibit strip
- Content moderation strategy before showing any user-submitted text
