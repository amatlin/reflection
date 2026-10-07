# Spirit

Reflection is a website that tracks and analyzes its own usage, then shows you how it did it.

## The Concept

Every website you visit tracks your behavior. Most of them never show you what they collect, how they store it, or what they do with it. Reflection does all three.

You visit the site. Your clicks, page views, and interactions are captured by a real event tracking system. Those events flow through a real data pipeline — ingestion, storage, transformation, aggregation — and come out the other side as metrics and insights that you can see on the same site that generated them.

The self-referential loop is the core idea. The site's only content is its own data.

## Who It's For

- **Anyone curious about tracking.** If you've ever wondered what happens when you click something on a website, this shows you the full path — from the click to the database row to the chart.
- **Students and junior data scientists.** The pipeline is production-grade: PostHog for event capture, BigQuery for warehousing, dbt for transformation, daily cron jobs for orchestration. It's a working example of the modern data stack, not a diagram of one.
- **People who know part of the stack.** A data engineer might skip the event capture section and go straight to the dbt models. A frontend developer might be more interested in how PostHog hooks into the page. The walkthrough lets you focus on what's new to you.

## The Tone

Warm but matter-of-fact. The site explains what's happening clearly and without jargon where possible. Technical terms are used when they're the right words, and explained when they're not obvious. No hype, no cleverness for its own sake. The goal is for someone to leave understanding something they didn't before.

## What a Visitor Should Walk Away With

A high-level picture of how data flows through a modern analytics pipeline: capture → store → transform → analyze. And the option to dig deeper into any piece — click a query chip to see the actual SQL, read the dbt model that built the table, watch your own events arrive in real time.

The depth is up to the visitor. The surface should be accessible to anyone.
