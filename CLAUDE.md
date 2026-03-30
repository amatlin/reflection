# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Reflection is a self-referential website that analyzes its own usage. See `plan.md` for milestones, `spirit.md` for creative identity and tone, `architecture.md` for system design, and `LAB_NOTEBOOK.md` for decision history.

## Key Principles

- Read `spirit.md` before making design or copy decisions.
- The self-referential loop is the core feature. If it doesn't work, nothing else matters.
- Architecture should mirror a real company's data stack — not a toy.
- Events use structured, typed payloads. Validate at the API layer.
- **One-way doors** (get right early): event schema, data model, tracking contract.
- **Two-way doors** (pick what's fastest): frontend framework, hosting, database product, specific services.

## Developer Context

- The developer is a senior data scientist experienced in Python, SQL, and large-scale data infrastructure. Minimal frontend experience.
- Prefer Python backends and managed services. Minimize ops overhead.
- Frontend may be generated via AI tools, with manual customization as needed.
- **This is a learning project.** Always explain what you're doing and why — walk through commands, code, and infrastructure decisions in enough detail that the developer builds understanding as we go. Don't just do things silently.

## Environment

- **Always use conda** for virtual environments, not venv or pip virtualenvs. The conda environment for this project is `reflection`. Activate with `conda activate reflection`.

If you notice a tool permission being repeatedly approved for a safe, read-only, or routine operation, suggest adding it to `~/.claude/settings.json` under `permissions.allow`.

## Development

The project is built incrementally through milestones — each one should be demo-able. Speed over polish. Commit and push frequently — don't let work pile up locally.

**Ideas before code.** New features start as working documents (`museum_idea.md`, `LAB_NOTEBOOK.md`) and milestone entries in `plan.md`. Don't write code until the design is documented and the user asks for implementation.

On every commit and push, check whether `README.md` or `plan.md` need to be updated to reflect the changes.

**Track open work in `TODO.md`.** When new work surfaces during a session — bugs found, features deferred, ideas discussed but not implemented — propose adding them to `TODO.md`. When items are completed, remove them from `TODO.md` entirely — don't use checkboxes. Completed work goes in `LAB_NOTEBOOK.md`, not TODO. The lab notebook records history; `TODO.md` is the living checklist of what's left.

**Always test frontend changes with Playwright** before presenting them. Navigate to the page, verify the snapshot, click interactive elements, and test mobile (375×812). Don't share frontend work without verification.

## Session Start

At the beginning of every conversation, read these files in order before doing anything else:

1. `README.md` — what the project is and current state
2. `plan.md` — milestones and status
3. `LAB_NOTEBOOK.md` — what happened in recent sessions
4. `spirit.md` — creative identity and tone
5. `architecture.md` — system design

Summarize what you learn and what seems like the natural next step, then ask the user what they'd like to work on.

## Session Handoff

When the user is wrapping up a session, document what was done and what's next in `LAB_NOTEBOOK.md`. Include enough context that a fresh conversation can pick up without re-reading the full transcript.
