---
name: qa-plan
description: Generate a QA / acceptance checklist that tests a just-built change against its intent — not against itself. Run AFTER implementing, when you'd ask "how do I QA what we built?". Derives steps intent-first (from the issue / acceptance criteria, before reading the diff) so it probes for gaps instead of rubber-stamping the code. Output is a human-or-agent-walkable checklist; executing it is a separate opt-in step. Use for a manual test plan, QA plan, or acceptance walkthrough. NOT verify (that drives the app — this writes the plan it drives), NOT tdd (automated, test-first — this is acceptance, test-after), NOT feature-spec / to-issues (those define intent before building — this consumes it after).
---

# QA Plan

Produce the document a human or an agent walks to confirm a just-built change does what the issue asked. The plan is the deliverable; running it is a separate, opt-in act.

> Test the **intent**, against the **build** — never the build against itself.

This skill owns the *acceptance artifact*. It does not run the app (`verify` does) and does not write automated tests (`tdd` does). See [Boundaries](#boundaries).

## When this runs

```
intent (issue / feature-spec) → implement [→ tdd] → qa-plan → [optional] execute
```

After implementation — ideally once automated checks are green — before you call it done. TDD is not a prerequisite.

## Two rules

**Intent-first, not diff-first.** Read the issue / acceptance criteria *first* and derive flows from what the change was supposed to do; *only then* read the implementation, to ground preconditions and selectors. Start from the diff and the plan inherits the code's blind spots; start from intent and you surface the criterion nobody implemented.

**Scope to THIS change.** Test only what this change put at risk — its claimed criteria plus the blast radius they threaten. Past ~a dozen steps, or covering features this change never touched, you're QA-ing the framework — cut back.

## The plan IS the contract

A plan is dual-executable (human *or* agent) only if every step states an **observable** outcome. "Check it works" is not a step; "URL is `/dashboard` and 'Welcome back' is visible within 2s" is.

The document has a fixed shape:

```
## Scope        — what this change put at risk; in scope / out
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
- human-eval:   <yes ONLY for subjective/visual judgement — else omit>
```

**The `human-eval` tag is load-bearing.** A person eyeballs "the modal looks right"; an agent can't — left untagged it will confidently false-pass. Tag every subjective/visual step `human-eval: yes` so an agent **skips and flags** it rather than faking a verdict. If a step *can* be made observable (screenshot + explicit criteria), do that instead of tagging.

## Process

1. **Anchor on intent.** Pull the acceptance criteria **verbatim** — paraphrase is where intent-drift sneaks back in. If there's no written intent, reconstruct it in a sentence — but this is the **weak mode** (the misreading that shipped in code can ship in the plan), so confirm with the user first.
2. **Ground in the build.** *Now* read the implementation — just enough for real preconditions, routes, selectors, inputs. Any criterion with no code path is a likely gap; record it under `## Gaps`.
3. **Enumerate flows**, in order: the **happy path(s)** from the criteria; **edges the spec named**; **edges the spec did NOT name but this change exposes** (empty/invalid input, auth boundaries, error + retry, concurrency, the regression surface this change threatens). The unnamed ones are the value-add over a mechanical criteria→steps transform.
4. **Write each step in contract format** — observable `Expected` for every one; `human-eval` on the subjective ones.
5. **Present and stop.** This is the primary output — **generate-only**. Do not execute.
6. **Offer execution as a separate step.** Ask once: walk it yourself, or hand to an executor (`verify` / `run` / `agent-browser`). Only on an explicit yes does anyone run it — and an agent executor must honor `human-eval` tags.

## Boundaries

| You actually want to… | Use | Relationship |
|---|---|---|
| Drive the app to observe the change | `verify` | It acts; this writes the plan it acts on. Composes: qa-plan → verify. |
| Launch / screenshot the app | `run` | Executor this plan feeds. |
| Browser-drive an execution | `agent-browser` | Executor this plan feeds. |
| Write automated unit/integration tests | `tdd` | Covers unit-contract in code; this covers intent-acceptance (incl. the `human-eval` surface). |
| Define what to build | `feature-spec` / `aa-design-spec` / `to-issues` | Produce the intent (before); this consumes it (after). |
| File the bugs a QA pass uncovers | `triage` / `to-issues` | qa-plan records pass/fail; it doesn't file. |
| Root-cause a failure | `diagnose` | — |
| Judge code quality of the diff | `code-review` / `aa-second-opinion` | Judges code against taste; this judges behavior against intent. |
| Transcribe reported bugs into the tracker | the deprecated `qa` | Different animal despite the shared name — that one's backward (bugs→issues); this is forward (intent→plan). |

## Before you hand over the plan

- [ ] Derived flows from **intent first**, then grounded in the build?
- [ ] **Every** step has an **observable** `Expected` (no "verify it works")?
- [ ] Each step **traces** to a criterion — and criteria with no code path flagged under `## Gaps`?
- [ ] Covered happy path, **named** edges, and the **unnamed** edges this change exposes?
- [ ] **Scoped to this change** (~a dozen steps, not fifty)?
- [ ] Every subjective/visual step tagged **`human-eval`**?
- [ ] **Stopped at the plan** and offered execution as a separate, explicit step?
