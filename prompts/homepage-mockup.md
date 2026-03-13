# Prompt for claude.ai — Reflection full site mockup

Paste everything below the line into claude.ai to generate a visual artifact.

---

Create an HTML/CSS mockup of a website called "Reflection." This should be a multi-page feel (use anchor sections or tabs to simulate navigation) showing the full vision of the site.

**What Reflection is:** A website whose sole purpose is to analyze itself. Every visitor interaction is captured as structured event data, and visitors can explore that data on the site — both in real-time and through an analytics layer. It's a self-referential loop. The site exposes its own data infrastructure the way a real tech company's data stack works: a live operational database for real-time events, and an offline analytical layer for deeper exploration.

**The tone is straightforward.** The site presents what it is without editorializing. No winking, no cleverness, no explanation of why this is interesting. It just is what it is.

**Pages/sections to include:**

1. **Home**
   - The name "Reflection" at the top.
   - A short conceptual statement explaining what the site is. Not a tagline — a plain description. Something like: "This website exists to analyze itself. Everything you do here — every page you view, every button you click, every purchase you make — becomes data. That data is stored, transformed, and made available for you to explore. There is no other product. The data is the product."
   - Below the statement, a live event stream showing recent events with timestamps, event types, page paths, and anonymous visitor IDs in monospace:
     - `2026-03-08 14:23:01 | page_view    | /home       | visitor_7f2a`
     - `2026-03-08 14:22:58 | sign_up      | /register   | visitor_3b1c`
     - `2026-03-08 14:22:45 | click        | /merch      | visitor_9d4e`
     - `2026-03-08 14:22:30 | checkout     | /cart        | visitor_3b1c`
     - `2026-03-08 14:22:12 | review       | /merch/tee  | visitor_a8f1`
     - `2026-03-08 14:21:55 | query_executed | /sql      | visitor_7f2a`
   - Simulate a few entries appearing to make it feel alive.
   - The concept statement and the live stream should feel like one continuous thought: here's what this is, and here it is happening.

2. **Sign up / Subscribe**
   - A simple sign-up form (email, password). This exists to generate registration and conversion funnel data.
   - A subscription option — free tier and a paid tier. The tiers don't need to be fully designed; the point is generating pricing and conversion data.

3. **Merch**
   - A small store selling a few items (e.g. a t-shirt, a sticker). Keep it minimal.
   - Each item has a price and an "Add to cart" button.
   - A simple cart/checkout flow. This exists to generate e-commerce funnel data: browse → add to cart → checkout → purchase, with drop-off at each stage.

4. **Review**
   - A place where users can leave a text review or rating of the site itself. This generates natural language and rating data.

5. **Data Schema**
   - A navigable reference showing the event types the site tracks and their structured payloads. For example:
     - `page_view`: referrer, viewport_width, viewport_height
     - `click`: element_id, element_type, element_text
     - `sign_up`: method
     - `checkout`: item_id, item_name, price, currency
     - `review`: rating, review_text
     - `query_executed`: query_text, row_count, duration_ms
   - Present this as a clean schema reference, like documentation.

6. **Dashboard**
   - Mock business metrics: active users, sign-up conversion rate, checkout funnel, top pages, events over time.
   - Use simple charts (bar, line, funnel) with simulated data. These would be real in production.

7. **SQL Playground**
   - A code editor area with a sample query like `SELECT event_type, COUNT(*) FROM events GROUP BY 1 ORDER BY 2 DESC`
   - A mock results table below it.
   - A few suggested queries the user could try.

8. **Blog / Write-up** (simple placeholder)
   - A list of 3-4 article titles that suggest the kind of content that would live here:
     - "How Reflection works"
     - "The event schema, explained"
     - "Building a conversion funnel from raw events"
     - "What is Reflection?"
   - No need to write full articles. Just titles and one-line summaries.

9. **Tutorials**
   - A section listing interactive tutorial notebooks (e.g. hosted on Colab) that walk through analyses using Reflection's own data. Placeholder titles:
     - "Sessionization from raw events"
     - "Cohort retention analysis"
     - "Funnel drop-off: where and why"
     - "Text analysis on user reviews"
   - Each entry shows a title, one-line description, and a "Open in Colab" button.

**Navigation:** A header with: Home, Sign Up, Merch, Data Schema, Dashboard, SQL, Blog, Tutorials

**Design direction:**
- Color palette inspired by a reflection pool: soft blue-grays, muted slate tones, cool whites. Think still water, not bright sky.
- Monospace or semi-monospace typography for all data elements (events, schemas, SQL, results). Clean sans-serif for everything else.
- Generous whitespace. Nothing should feel crowded.
- No illustrations, no icons, no stock imagery. The data IS the visual interest.
- The overall feeling should be: calm, still, precise. Like looking into water.

Make it a complete, self-contained HTML file with inline CSS and minimal JS for the tab navigation and simulated event stream. It should look good at desktop width.
