---
name: sentry-quick-wins
description: Use when the user wants to triage the easy bugs from Sentry — "triage Sentry", "find quick wins", "what should I fix first from Sentry", "pull the top fixable bugs", "clear the easy ones before the hard ones". Fetches unresolved issues, ranks by impact while filtering noise, and triages the best quick wins into an approval table. Triage only — stops at the table.
---

# Sentry Quick Wins

Find the **quick wins** in Sentry — real user-facing bugs with a clear root cause and a small, low-risk fix — and surface them in a ranked table so they can be cleared ahead of the complex issues. This skill triages only; fixing is a separate step the user drives later.

A **quick win** is:
- a likely real, user-facing bug (not noise)
- root cause clear from the stack trace, breadcrumbs, route, request data, or surrounding code
- fixable with a small, low-risk change touching no more than ~2 files
- no API, schema, architecture, design, or product decision needed
- reproducible, or at least verifiable via the Sentry failing path plus a regression test
- low risk of expanding in scope

## Step 0: Confirm Sentry access

The Sentry MCP must be connected to *this* session — it is not always exposed even when configured globally. Make one small test call (search unresolved issues, limit a handful) and report how many unresolved issues you can see.

If no Sentry tool is available, stop and tell the user to connect the Sentry MCP. Do not fall back to anything else.

## Step 1 — Triage

Fetch unresolved issues from the last 30 days. Scope to the project the user is working in if the MCP exposes more than one.

Rank by `event count × users affected` as the starting signal, then **down-rank noise**:
- bots, crawlers, browser extensions, third-party scripts (ads, analytics, pixels)
- flaky network errors, cancelled requests
- `ResizeObserver` / chunk-load / hydration errors with no actionable trace
- issues with no actionable stack trace

Select the **5 best quick wins** against the criteria above. For each candidate, call the issue-detail tool, inspect the stack trace and events, and map it to this repo's files and route/component.

Return a ranked table with these columns:

`rank` · `issue title` · `Sentry link` · `events` · `users affected` · `route/component` · `suspected root cause` · `repo files` · `proposed one-line fix` · `confidence (H/M/L)` · `hidden-complexity notes`

Then a **Skipped** section: issues that looked relevant but were rejected as noise, too vague, too risky, or not quick wins — one-line reason each. This is the audit trail; it proves the noise was examined, not silently dropped.

<HARD-GATE>
Stop after the table. This skill ends at triage — do NOT edit code, reproduce, or fix anything. Fixing is a separate step the user drives later.
</HARD-GATE>
