---
name: tidy-first
description: Prepare the code for ONE specific, imminent change before you write it — Kent Beck's "make the change easy, then make the easy change." Run as the zero step of implementing a picked issue/ticket: after understanding its blast radius (via context_builder) and before the first failing TDD test, tidy ONLY what makes THIS change easier, on green, in its own commit separate from the behavioral change. Its primary output is a gated, change-scoped shortlist of tidyings you can either apply now or hand off for a fresh session to execute. Reach for it when you've picked an issue and are about to touch code, want to prefactor / tidy first before a feature, or need the surrounding code prepared so the change becomes trivial. NOT a codebase-wide refactor sweep (that's improve-codebase-architecture / improve-codebase-colocation) and NOT for splitting code you already mixed (that's aa-commit-clarity).
---

# Tidy First

Prepare the landing zone for a single imminent change, then make the change. The structural prep and the behavioral change are **two separate acts with two separate commits** — never one tangle.

> **Make the change easy, then make the easy change.** — Kent Beck

This skill owns the *sequencing and separation* of a tidy versus a behavioral change at the moment you're about to code. It does not hunt the codebase for cleanup — that's what separates it from the `improve-*` skills (see [Boundaries](#boundaries)). It is deliberately the tidy-***first*** quadrant of Beck's timing choices (first / after / later / never): tidy in the same cycle, immediately *before* the behavior change — tidy-*after* lives in `tdd`'s post-green refactor, tidy-*later* is the issue you file.

## When this runs

Per issue, as the **zero step of implementation** — after you've picked an issue, ahead of the first red of `tdd`:

```
pick issue → context_builder (curate blast radius + lock direction) → tidy-first → tdd (red → green → refactor)
```

Invoke it fresh for each issue, against that issue's concrete blast radius. Tidying for issues you haven't started is **speculative**: a tidy *buys an option* on a future change, and paying now for one you may never exercise — against a discounted, uncertain payoff — rarely covers its cost. Don't.

**Tidy on green only.** If the suite is red, get it green first — on a failing suite you can't tell a behavior-preserving move from a behavior-changing one, the one thing this skill exists to keep separate.

**No tests on the blast radius?** Then *green* is meaningless and a post-tidy test run catches nothing. Either write a characterization test to pin current behavior first, or limit yourself to mechanical, tool-verified tidyings (IDE rename/extract) that preserve behavior by construction.

## The two gates (this is the whole skill)

A candidate tidying may only be done when it passes both:

1. **Change-scope gate (the stop-rule).** Tidy *only what makes THIS change easier*. If you're not about to touch that code for this issue, you don't tidy it here — no matter how messy. A tidy with no behavioral change waiting behind it is a sweep, not tidy-first.
2. **Direction gate.** Tidy *only what is stable across your chosen approach*. If approach A and approach B would tidy different things, your direction isn't locked — resolve the fork first (a quick `grill-me` or spike), then tidy.

If a candidate fails either gate, drop it. If it's a real problem but out of scope, make the decision *explicit*: file it now if it's actionable and worth tracking (route to `improve-codebase-architecture` / `improve-codebase-colocation` or the tracker), otherwise consciously drop it. What you must not do is leave it as invisible "later" — that's how a codebase accrues chronic under-tidying.

## Process

**0. Restate the change in one sentence.** *"I am about to change X so that Y."* This is the target both gates bite on. If you can't write it yet, that's a `context_builder` / `grill-me` problem, not a tidying one.

**1. Curate the blast radius with `context_builder` — not a plan.** Run it in **context / clarify** mode (or a directional `question`) to surface the **blast radius** (the files, functions, seams this lands on) and enough **direction** to evaluate the direction gate. `context_builder` is the canonical tool here — use it whenever it's available; fall back to direct inspection (`file_search` + `read_file`) only when it's genuinely unavailable or the change lands in a single function you can already see whole. **Do NOT use `plan` mode** — a line-level plan built against messy code bakes in the hard version of the change and defeats the skill. Hold the split: **directional** thinking (which approach?) belongs here, before the tidy; **detailed** thinking (the steps, the diff) comes *after*, emerging from the now-easier code. Defer the detailed, never the directional — conflating the two is the most common way to get this wrong.

**2. Find candidate tidyings inside the blast radius** — small, behavior-preserving legibility moves only:

- **Guard clauses** — flatten nested conditionals into early returns.
- **Dead code** — delete unreached branches, unused params, stale flags.
- **Normalize symmetry** — make things that do the same thing look the same.
- **Reading / cohesion order** — reorder so it reads as a reader needs it; put things that change together next to each other.
- **Extract helper** — pull a confusing chunk into a named function.
- **Explaining variable / constant** — name a magic value or dense subexpression.
- **Rename** — give a vague name the domain word for what it does.
- **Chunk statements** — blank-line a long run into labelled paragraphs.
- **Delete redundant comments** — when a rename or extract made them noise.

Run each through **both gates**. Keep the short list that survives.

**3. Present the shortlist — and stop.** Each item with one line: *why it makes THIS change easier* (not "cleaner"). If you can't articulate that link, it fails the change-scope gate. Keep it short; fifteen candidates is a sweep. **This shortlist is the skill's primary output. Do not edit yet** — stop here and let the user decide what happens next (step 4).

**4. Apply now, or hand off — the user's call.** Tidying the code in this session is *optional*. Offer both, and wait:
- **Execute now.** Behavior must not change: same inputs, outputs, side effects. **Run the existing tests/checks after tidying** to confirm before you commit. The tidy lands in **its own commit, separate from the behavioral change** — non-negotiable: it lets a reviewer read structure and behavior independently and revert either alone (squash-on-merge at the PR boundary is fine; the discipline is in how you author it, not the merge artifact). To sanity-check commit boundaries, `aa-commit-clarity`. Then continue to step 5.
- **Hand off instead.** Don't touch code. Use the `handoff` skill to capture the one-sentence change, the curated blast radius, and the approved shortlist — each item with its rationale and the execution discipline (green-only, own commit, run tests) — into a document the user can save for later or pass to a fresh agent/session to execute. This ends the skill; step 5 doesn't apply.

**5. Hand off to `tdd`** (only if you executed in step 4). End by saying: *"Structural prep committed separately — the change is now easy. Starting TDD."* Then make the easy change through red → green → refactor against the tidied code.

## Worked examples

Same scenario throughout — *"I am about to add a `priorityFee` to the checkout total."*

- **Good tidy (passes both gates).** `calculateTotal()` is 40 lines of interleaved subtotal/tax/discount math; your change adds one term. Extract `applyDiscounts(subtotal)` so the slot for `priorityFee` becomes obvious and isolated. → Makes *this* change easier, stable across any approach. **Do it.**
- **Speculative tidy (fails change-scope).** You notice `formatReceipt()` has the same interleaving — but your change never touches it. → No behavioral change behind it. **Drop it; file an issue only if genuinely worth it.**
- **Too-large move (fails scope; wrong skill).** The real friction is pricing spread across three modules that "should" be one `Pricing` service. True, but that's a risky depth/placement refactor. → **File it, route to `improve-codebase-architecture`. Don't smuggle it in.**

## Boundaries

- **Codebase-wide depth review** (shallow → deep modules): `improve-codebase-architecture` — a standalone sweep; tidy-first is bound to one imminent change.
- **Codebase-wide placement / colocation**: `improve-codebase-colocation` — also a sweep; tidy-first doesn't relocate features.
- **Splitting code you already mixed** *after the fact*: `aa-commit-clarity` — reactive; tidy-first is proactive, sequencing the work so structure and behavior are never mixed to begin with.
- **The refactor step *after* green**: that's `tdd`. tidy-first tidies *before* the first red; the two bookend the TDD loop.

## Checklist before you tidy

- Have I written the **one-sentence change** this tidy serves?
- Is the suite **green**?
- Is there a **specific behavioral change** this makes easier, one I'm about to make now? (change-scope gate)
- Is my **direction locked** enough that this survives regardless of implementation detail? (direction gate)
- Can I state, in one line, *why this makes the change easy* — not just "cleaner"?
- Is it **behavior-preserving**, and did I **run the tests** to confirm?
- Will it land in **its own commit**, separate from the behavioral change?
- Is the list **short**? (If it sprawls, it's a sweep — stop.)
- Is a candidate really a depth/placement/large-refactor problem? → file or consciously drop, don't smuggle it in.
