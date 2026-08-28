---
name: slice-check
description: Audit a spec's ticket slicing with cold-read probes before dispatching implementation. Run by hand after to-tickets.
disable-model-invocation: true
---

# Slice Check

Audit the tickets cut from a spec, before any implementation session is spent on them. You are the orchestrator; verdicts on individual tickets come from **cold-read probes** — one subagent per ticket, each seeing only its ticket, because that is exactly what the implementing session will see. Fan out even on small specs: the fan-out is what keeps every read cold, including yours after ticket one.

The deliverable is a verdict table. Stop there — splitting, merging, and rewriting tickets is the user's call.

**Cold read** — a reader with no spec, no grilling thread, no sibling tickets. The probe is a rehearsal of the implementer: fresh context, one ticket, the codebase.
**Smart zone** — the front portion of a context window where the agent still reasons well. A ticket "fits" when its relevant files plus room to plan, edit, and verify stay inside it. Default budget for the files alone: **50k tokens**; the user's number wins if they gave one.

## Verdicts

One per ticket, evidence attached:

| Verdict | Meaning | Evidence required |
| --- | --- | --- |
| `fits` | A fresh session can finish it in the smart zone | selection footprint under budget, criteria falsifiable, demo path named |
| `split` | Too big for one window | selection footprint (tokens) or seam count |
| `merge` | Over-decomposed; name the sibling(s) to absorb it into | the sibling refs and the shared demo path |
| `horizontal` | A layer, not a tracer bullet — nothing demoable alone | the criterion that depends on another ticket's work |
| `criteria` | Acceptance criteria grade nothing | each unfalsifiable criterion, and why it passes at the start commit |

A ticket can carry two verdicts (`split` + `criteria`). `fits` requires all three pieces of evidence — "probably fine" is not a verdict.

## Steps

### 1. Fetch the graph

Resolve the spec (argument, or the tracker issue the conversation names) and enumerate its tickets: ref, state, blocking edges. Read the ticket bodies yourself — you need them for the graph checks in step 3, and you are allowed to be warm; the probes are the cold readers. Note the start commit the implementers will branch from.

### 2. Dispatch cold probes

One probe per open ticket, in parallel (`agent_run` with `model_id="explore"`, `detach: true`, then one `wait` on the batch — or this environment's equivalent read-only subagent).

The brief contains exactly four things — a bare pointer, so the probe stays cold:

1. The ticket ref (or the ticket's verbatim body, when the probe has no tracker access).
2. The repo root and start commit.
3. The budget: 50k tokens (or the user's figure).
4. This checklist and report format:

```
You are rehearsing a fresh implementation session for one ticket. You know
nothing about the wider feature — grade the ticket on what it alone gives you.

1. FOOTPRINT — Find every file you would need loaded to implement this.
   Estimate their total tokens. Over budget → oversized.
2. COLD START — List what the ticket assumes you know but doesn't say
   (vocabulary, decisions, file locations). Anything you had to guess.
3. CRITERIA — For each acceptance criterion, name the observation that would
   show it false, and whether it already passes at the start commit.
4. DEMO — State what can be demoed when this ticket is done. Behaviour, not
   a layer.

Return only:
{ verdict: fits|oversized|unclear, est_tokens, files: [...],
  missing_for_cold_start: [...], criteria: [{text, falsifiable, passes_at_base}],
  demo_path: "..." }
plus at most two sentences of commentary.
```

Probes report `oversized`/`unclear`; you own the final verdict vocabulary — `merge` and `horizontal` are yours to assign, since only you see the whole graph.

### 3. Graph checks (while probes run)

From the ticket bodies, warm and whole-graph:

- Every blocking edge resolves to a ticket in the spec; no cycles.
- No criterion is satisfied by work another ticket owns (the `horizontal` tell).
- Adjacent tickets whose demo paths only make sense together → `merge` candidates.
- Prefactoring tickets sit at the front of the order.

### 4. Spot-check

Probes report what they intended to find, not what they saw. Before a claim decides a verdict, verify it yourself: re-count one `oversized` footprint with your own file reads; run one `passes_at_base` claim against the start commit. One spot-check per verdict class that appears.

### 5. Report

One table: ticket ref, verdict(s), evidence, one-line remedy (`split along <seam>`, `merge into #N`, `rewrite criterion 2`). Below it, the graph findings. Done when **every open ticket has a verdict backed by its required evidence**. End with the single most consequential finding — the one to fix before dispatching anything.
