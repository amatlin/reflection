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

## Modeling step (UMAP visualization)

2D scatter plot of embedded questionnaire responses. Each dot is a thought; clusters form where people said similar things. Placeholder shows a counter until 50+ responses exist. Design documented in [lab notebook entry 2026-03-28](LAB_NOTEBOOK.md).

- Daily batch job: fetch responses from BigQuery, embed (OpenAI text-embedding-3-small), fit UMAP, save coordinates
- FastAPI: serve precomputed coordinates JSON
- Frontend: D3 or Plotly scatter plot in the modeling strip (only renders when 50+ responses)
- Content moderation strategy before showing any user-submitted text
