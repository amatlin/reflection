# Museum Exhibit Funnel

Working document for the museum exhibit restructure.

## Concept

Restructure the site as a museum exhibit: **Homepage → Exhibit (multi-step) → Conclusion/Gift Shop**. This creates an analyzable funnel and gives the site its first structured user journey.

The exhibit content IS the infrastructure walkthrough — each screen explains one stage of the data pipeline that's tracking the visitor as they move through it. Educational and self-referential.

## Structure

### Homepage (existing, modified)
- Keeps the live stream visible — it piques curiosity
- Adds a single "Enter the exhibit" button
- Analytics tab stays accessible

### Exhibit (8 steps with ← Back / Next → navigation)

| # | Screen | Content |
|---|--------|---------|
| 1 | Introduction | The concept: a website that analyzes itself. Duchamp/Warhol/Seinfeld lineage. |
| 2 | Logging | PostHog captures your behavior — clicks, pageviews, sessions. |
| 3 | Streaming | Events sent to API → Supabase → WebSocket → the live stream you just saw. |
| 4 | Export | PostHog batch exports to BigQuery hourly. |
| 5 | Transformation | dbt cleans, deduplicates, aggregates the raw data. |
| 6 | Metrics | Daily aggregates: visitors, events, devices, geography. |
| 7 | Analysis | The analytics tab displays the pipeline's output. |
| 8 | Conclusion | Thank you + questionnaire + gift shop. |

### Conclusion (final exhibit step, three sections)
- **Thank you** — short closing note
- **Questionnaire** — single text box ("Leave a thought", max 500 chars), submitted as `questionnaire_response` event
- **Gift shop** — real Stripe purchases (laptop sticker ~$5, buy the developer a coffee ~$3)
- **Sandbox link** — "Now explore the data yourself" → links to `/sandbox` (the analysis gallery, built in M5)

## Technical Approach

Single-page with hash routing. All screens in one `index.html`, show/hide with JS, update `location.hash` (`#home`, `#exhibit-intro`, `#exhibit-logging`, ..., `#conclusion`). WebSocket stays alive across all screens.

Hash is included in `page_path` for every event sent to the API, enabling funnel analysis.

## Event Tracking

| Event | Trigger | Properties |
|---|---|---|
| `funnel_step` | Each screen navigation | `step` (screen name) |
| `questionnaire_response` | Text box submit | `response_text` |
| `checkout_started` | Buy button → Stripe | `item_id`, `item_name`, `price` |
| `purchase_complete` | Stripe webhook confirms payment | `item_id`, `item_name`, `price`, `stripe_session_id` |

## What makes this work for Reflection

- The funnel is analyzable — the site can show its own conversion rates
- The exhibit content IS the infrastructure walkthrough
- The gift shop generates real e-commerce data (richest event type in analytics)
- The questionnaire generates natural language data (opens up NLP)
- Every new event type immediately enriches the existing pipeline
