---
name: qol-hunt
description: Hunt quality-of-life features for an app's day-to-day users, each grounded in friction observed in the codebase. Explicit invocation only.
disable-model-invocation: true
---

# QoL hunt

Find **quality-of-life** features for the people who use this app day to day: small friction-removals, sized S or M. An L-effort proposal needs one line justifying why it is still QoL rather than a headline feature.

The invocation text may name a **count** (default 5), a **scope** (a subtree or area; default the whole app), and whether to **write a report** (default chat only).

## 1. Orient (inline)

Establish the two facts every probe brief carries:

- **Audience**: who uses this app and for what. Read the README, `CONTEXT.md` or equivalent, and the routes themselves. Done when you can name each user role and its main workflows in a line.
- **Map**: the areas to survey. Lookup ladder: a capability/module doc (`MODULES.md`, `ARCHITECTURE.md`) → the routes/pages directory → a map you build from the file tree. Done when every route or user-facing area appears on it. A scope argument restricts the map; the audience stays whole-app.

Also glob `**/qol-hunt-*.md`: a prior report feeds the disqualification clause.

## 2. Survey (delegated)

Dispatch explore subagents: one per area on the map, one git-archaeology probe, and one tracker probe if an issue tracker is reachable (`gh`, Linear, a backlog doc). Without subagent dispatch, run the same probes yourself in sequence.

Every brief carries the audience, the area (whole app for git and tracker), the **Friction** reference below verbatim, and the return schema. Probes return **observations only**: workflow, what the user has to do, `file:line` or route path. Proposals form in Dig, from your own reading.

- Git probe target: user-facing areas with repeated small fixes — users hit them often and they are brittle.
- Tracker probe target: two separate lists — issues *reporting* pain (evidence) and issues *proposing or scheduling* a fix (disqualifiers).

Done when every map entry has a probe report.

## 3. Dig (inline)

Rank areas by observation density and severity. Working down the ranking, read the actual code of each area — the route, the form, the handler — and form candidate proposals. Verify each candidate's cited friction first-hand by opening the cited file yourself. Continue until the count is met by candidates that pass **Disqualification**, or the ranking is exhausted.

## 4. Propose

Rank survivors by impact-to-effort, where impact = how often the workflow runs × what the friction costs each time. Fewer proposals that all pass beats a full count with weak ones: report any shortfall and what was considered.

Open with one line stating your read of the audience, then per feature:

- **Workflow** — the route or module, by name
- **Friction observed** — with citations: file paths, routes, issue links
- **Proposed change**
- **Effort** — S / M / L

Chat by default. On request, write to `docs/analysis/qol-hunt-YYYY-MM-DD.md`, or the repo's existing analysis convention.

## Friction

Observable patterns probes look for:

- Multi-step flows that could be one step
- Re-entering data the app already holds
- Bulk work done one item at a time
- Actions with no feedback: silent saves, missing loading or error states
- Dead ends: the next obvious action is not offered where the user stands
- Forms without sensible defaults
- Data shown without the action that follows from it

## Disqualification

A feature counts toward the count only if all four hold:

- It names a workflow with observed friction, cited.
- You verified the cited friction first-hand in Dig.
- It does not already exist in the app, and no open issue proposes or schedules it.
- No prior qol-hunt report already proposed it.
