---
name: qa-plan
description: Generate a QA / acceptance test plan to check a just-implemented change against its intent — the checklist you (or an agent) walk to confirm it works. Run it AFTER implementing an issue/feature — when you'd ask "how should I QA what we built?". Derives steps from the issue / acceptance criteria FIRST (intent-first, not diff-first), so it probes for gaps instead of rubber-stamping the code it just wrote. Output is a human-walkable checklist — each step has a precondition, action, OBSERVABLE expected result, pass/fail box, and a human-eval tag for subjective checks an agent can't fake. Generate-only by default; executing it (manually or via verify / run / agent-browser) is a separate opt-in step. Use when you want a manual test checklist, QA plan, or acceptance walkthrough. NOT verify (that drives the app — this produces the plan it drives), NOT tdd (automated, test-first — this is acceptance, test-after), NOT feature-spec / to-issues (those define intent before building — this consumes it after).
---

# QA Plan

Produce the document a human or an agent walks to confirm a just-built change does what the issue asked. The plan is the deliverable — running it is a separate, opt-in act.

> Test the **intent**, against the **build** — never the build against itself.

This skill owns the *acceptance artifact*: a traceable, executable-by-anyone checklist generated after implementation. It does not run the app (`verify` does) and it does not write automated tests (`tdd` does). See [Boundaries](#boundaries).

## When this runs

After implementation — once the change is built and, ideally, automated checks are green; before you call it done. TDD is not a prerequisite — this is just as useful after non-TDD work:

```
intent (issue / feature-spec) → implement [→ tdd] → qa-plan → [optional] execute
```

## The two rules that make it work

**1. Intent-first, not diff-first.** Read the **issue / acceptance criteria first** and derive flows from *what the change was supposed to do*. Only *then* look at the implementation, to ground preconditions and selectors. Start from the diff and the plan inherits the code's blind spots and rubber-stamps it; start from intent and you surface the criterion nobody implemented and the edge case the code silently skips.

**2. Scope to THIS change.** Test only what *this change* put at risk — the criteria it claimed, plus the behavior its blast radius threatens. Not the whole app. If the plan runs past ~a dozen steps, or starts covering features this change never touched, you're QA-ing the framework, not the change — cut back. (The tidy-first instinct: a sprawling list is a sweep.)

## The plan IS the contract

A plan is dual-executable (human *or* agent) only if every step states an **observable** outcome, not a vibe. "Check it works" is not a step; "URL is `/dashboard` and 'Welcome back' is visible within 2s" is.

The document has a fixed shape:

```
## Scope        — what this change put at risk; what's in scope / out
## Acceptance   — the criteria, verbatim, each linked to its step(s)
## Gaps         — criteria with no code path, or risks with no coverage
## Checklist    — the steps below, grouped by flow
## Execution    — left empty by default; filled only on the opt-in run
```

Each step:

```
### [n] <short flow name>  ·  traces: <acceptance criterion / issue line>
- Precondition: <state/data/role needed before this step>
- Action:       <the concrete thing to do>
- Expected:     <an OBSERVABLE result — URL, visible text, value, state, error>
- Result:       [ ] pass  [ ] fail        (human ticks / agent fills)
- human-eval:   <yes ONLY for subjective/visual/aesthetic judgement — else omit>
```

**The `human-eval` tag is load-bearing.** A person eyeballs "the modal looks right"; an agent can't — left untagged it will confidently false-pass. Tag every subjective/visual step `human-eval: yes` so an agent **skips and flags** it rather than faking a verdict. If a step *can* be made observable (screenshot + explicit criteria), prefer that over tagging it.

## Process

1. **Anchor on intent.** Pull the acceptance criteria **verbatim** from the issue / spec — don't paraphrase (paraphrase is where intent-drift sneaks back in). List them as the trace target. If there's no written intent, reconstruct it in a sentence or two — but treat this as the **weak mode**: the same misreading that shipped in the code can ship in the plan, so confirm it with the user before going further.
2. **Ground in the build.** *Now* read the implementation — just enough to fill real preconditions, routes, selectors, and inputs. Note any criterion you can't find a code path for: that's a likely gap, call it out.
3. **Enumerate flows.** Cover, in order: the **happy path(s)** straight from the criteria; **edge cases** the spec named; **edge cases the spec did NOT name but the change exposes** (empty/invalid input, auth/permission boundaries, error + retry, concurrency, the regression surface *this change* threatens). The unnamed ones are the value-add over a mechanical criteria→steps transform.
4. **Write each step in the contract format.** Observable `Expected` for every one. Tag subjective steps `human-eval`.
5. **Present the plan and stop.** Group by flow, lead with a one-line scope ("what this does / doesn't cover"). This is the primary output — **generate-only**. Do not execute.
6. **Offer execution as a separate step.** Ask once: walk it yourself, or hand it to an executor (e.g. `verify` / `run` / `agent-browser`). Only on an explicit yes does anyone run it — and an agent executor must honor `human-eval` tags (skip + report, never fake).

## Boundaries

- **Driving the app to observe a change** → `verify`. It *acts*; this *produces the plan it acts on*. They compose: qa-plan → verify. Reach for **qa-plan** when you want a durable, traceable, handoff-able artifact; for a one-off "does it work?", just use `verify`.
- **Launching/screenshotting the app** → `run`. **Browser-driving an execution** → `agent-browser`. Both are executors this plan feeds; neither generates the plan.
- **Automated unit/integration tests** → `tdd`. That covers *unit-contract* correctness in code; this covers *intent-acceptance* — precisely what escapes automated tests: the `human-eval` surface, and whether an operator would agree the issue is *done*.
- **Defining what to build** → `feature-spec` / `aa-design-spec` / `to-issues`. Those produce the *intent* (before). This consumes that intent to verify the *result* (after).
- **Filing the bugs the QA pass uncovers** → `triage` / `to-issues`. **Root-causing a failure** → `diagnose`. qa-plan finds and records pass/fail; it does not fix or file.
- **Judging code quality of the diff** → `code-review` / `aa-second-opinion`. This judges *behavior against intent*, not code against taste.
- **Conversational bug-intake** (report bugs → file issues) → the deprecated `qa`, a different animal despite the shared name. `qa-plan` writes a *forward* test plan from intent; it doesn't transcribe reported bugs into the tracker.

## Checklist before you hand over the plan

- Did I derive flows from the **intent first**, and only then ground them in the build?
- Does **every** step have an **observable** `Expected` (no "verify it works")?
- Does each step **trace** to a criterion — and did I flag criteria with no code path?
- Did I cover happy path, **named** edges, and the **unnamed** edges the change exposes?
- Is the plan **scoped to this change** — not sprawling into the whole app (~a dozen steps, not fifty)?
- Is every subjective/visual step tagged **`human-eval`** so an agent won't false-pass it?
- Did I **stop at the plan** (generate-only) and offer execution as a separate, explicit step?
