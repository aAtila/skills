---
name: slice-check
description: Audit a spec's ticket slicing with cold-read probes before dispatching implementation. Run by hand after to-tickets.
disable-model-invocation: true
---

# Slice check

Audit the tickets cut from a spec before implementation. Use one independent cold-read probe per open ticket to rehearse a fresh implementation session; combine its evidence with your whole-graph review.

The deliverable is a verdict table with proposed remedies. Applying ticket changes is a separate task requiring user authorization.

**Cold read** means fresh context containing one ticket and access to the codebase, with no parent conversation, spec, or sibling tickets.
**Context budget** is a planning heuristic for source material needed together, with room left to plan, edit, and verify. Default to **50k tokens** for that material unless the user supplies a budget. An estimate above it warrants investigation, not an automatic split.

## Verdicts

Assign evidence-backed verdicts:

| Verdict | Meaning | Evidence required |
| --- | --- | --- |
| `fits` | Context needs and implementation work are manageable in a fresh session | sufficient cold-start context, justified footprint, meaningful falsifiable criteria, independently verifiable contribution |
| `split` | Too much work or context for one session | footprint or implementation complexity explaining the limit, plus a viable split boundary |
| `merge` | Over-decomposed; name the sibling(s) to absorb it into | the sibling refs and the shared demo path |
| `horizontal` | No independently verifiable contribution after declared prerequisites are satisfied | the missing contribution and the later ticket needed to demonstrate it |
| `criteria` | Acceptance criteria fail to distinguish success from failure | the missing or unfalsifiable criterion, or evidence that it passes at base without checking the intended change |
| `unclear` | Missing context or evidence prevents a supported verdict | the unresolved decision, unavailable material, or uncertain claim and what would resolve it |

A ticket can carry multiple findings, such as `split` + `criteria`. Use `fits` only when all its evidence requirements are met and no unresolved finding remains.

## Steps

### 1. Fetch the graph

Resolve the spec from the argument or conversation and enumerate its tickets: ref, state, blocking edges. Read their bodies for the graph review. Record the implementation start commit as a SHA; inspect repository files and cited documents at that revision. Keep completed-prerequisite assumptions distinct from what exists at this baseline.

### 2. Dispatch cold probes

Use read-only subagents with conversation inheritance disabled. Choose available tools and scheduling to suit the environment; each ticket needs a fresh reader, including when probes run sequentially. If isolated probes are unavailable, report the cold-read check as unverified.

Give each probe:

1. The ticket ref (or the ticket's verbatim body, when the probe has no tracker access).
2. The repo root and start commit.
3. The context budget.
4. This checklist and report format:

```
You are rehearsing a fresh implementation session for one ticket. Grade it
on the context it supplies and what you can establish from the codebase.

Inspect files and cited repository documents at the supplied start SHA.

1. FOOTPRINT: Estimate source context needed together, using relevant file
   sections where sufficient. Explain the estimate, uncertainty, and work
   complexity. If too large, identify a viable split boundary.
2. COLD START: Identify decisions or information the ticket leaves unresolved
   after repository inspection. Record missing references and assumptions
   about declared prerequisites separately from observed baseline facts.
3. CRITERIA: For each criterion, give a falsifying observation and its status
   at the start SHA: passes, fails, or unknown. Cite file locations or check
   results; distinguish an intentional regression guard from a criterion
   that passes without checking the intended change.
4. CONTRIBUTION: State the behaviour that can be demonstrated after declared
   prerequisites are satisfied. For prefactoring, name the structural
   outcome and how preserved behaviour can be verified.

Return a concise report containing:
- Assessment and unresolved concerns.
- Estimated tokens, estimation method, file sections, complexity, and any
  proposed split boundary.
- Missing cold-start context and prerequisite assumptions.
- Each criterion, its falsifying observation, baseline status, evidence,
  and any reason verification was unavailable.
- The demo or verification path for this ticket's contribution.
```

You assign final verdicts from probe evidence and the whole graph.

### 3. Review the graph

Check the ticket bodies and incorporate probe findings as they arrive:

- Every blocking edge resolves to a ticket in the spec; no cycles.
- Each ticket adds an independently verifiable contribution once declared prerequisites are satisfied. Depending on earlier work alone does not make a ticket `horizontal`.
- Adjacent tickets whose demo paths only make sense together → `merge` candidates.
- Prefactoring precedes the work it prepares and has a verifiable structural outcome with preserved behaviour.

### 4. Resolve consequential uncertainty

Verify uncertain or conflicting claims that could change a verdict, using evidence at the recorded SHA. For example, inspect the selected sections behind a borderline footprint or check a disputed criterion at baseline. Accept supported observations without a fixed recheck quota. Carry unresolved uncertainty into `unclear` with the evidence needed to resolve it.

### 5. Report

One table: ticket ref, verdict(s), evidence, one-line remedy (`split along <seam>`, `merge into #N`, `rewrite criterion 2`). Below it, give the baseline SHA, graph findings, and verification limits. Done when **every open ticket has a supported verdict or an explicit `unclear` finding naming what is needed**. End with the most consequential finding, or state that no dispatch-blocking finding remains.
