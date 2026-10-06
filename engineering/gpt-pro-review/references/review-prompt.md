# Review prompt

Sent verbatim by Step 3 of `gpt-pro-review`, with `<PR URL>`, `<HEAD SHA>`, and `<REVIEW ID>` substituted. The leading `@GitHub` mention makes ChatGPT open the PR and post the comment through its connector; keep it.

```
@GitHub <PR URL>

Review ID: <REVIEW ID>
Requested head SHA: <HEAD SHA>

Review the provided PR through GitHub, using full file context and any supplied plan/spec. Assess whether the changes are **correct, minimal, idiomatic, secure, performant, testable, maintainable, and biased toward one canonical current-state implementation**. Report concrete, evidence-backed risks that the diff causes or worsens, including regressions, fallback behavior that hides bugs, and disproportionate long-term complexity.

The diff is authoritative for what changed; the PR description, surrounding code, and plan/spec supply intent and any approved implementation boundary. If intent or scope is ambiguous, infer it from codebase patterns and state assumptions explicitly. A review finding is not authority to expand an approved scope: when a necessary remedy crosses that boundary, classify it as requiring scope or plan revision rather than presenting the expansion as ordinary remediation.

Judge the change on correctness, regressions, security, reliability, tests, and long-term maintainability, in that order. Prefer designs whose correctness is easy to see over designs whose deficiencies are merely hard to find, and apply that bar proportionally to the change.

## Canonical path doctrine

Prefer a clear current-state code path. Scrutinize speculative compatibility paths, redundant defenses, and silent fallbacks against requirements, existing behavior, persisted formats, external contracts, and demonstrated failures. Flag complexity when you can explain why it is unnecessary, and prefer removal when it preserves required behavior. Ordinary control flow should be judged on correctness and clarity.

A silent fallback substitutes different behavior when the primary path fails or data does not match expectations. Prefer specified recovery that detects and surfaces failures, such as retries with backoff on network I/O or timeouts. Preserve defenses at security, authorization, and untrusted-input boundaries.

For each new defensive check, ask whether the better fix is to strengthen the type, schema, constructor, parser, or state transition that produces the value. Validate at trust boundaries; downstream code relies on established invariants.

## Method

1. Summarize what the change does and which flows it touches.
2. Check proportionality: compare the diff footprint and new obligations with the stated requirement.
3. Identify applicable risk surfaces: APIs, persistence, concurrency, authorization, data models, and external contracts.
4. Walk each hunk: behavior before versus after, including edge and error paths; impact on identified risk surfaces; unnecessary complexity; alignment with existing patterns and utilities.
5. Cross-check tests: new and changed behavior covered, error paths covered, tests assert behavior rather than implementation.
6. Generate concrete fixes, preferring removal or simplification toward a single explicit path.

When a prior-finding ledger is supplied for a repeated review, verify the recorded corrections and assess regressions introduced by them. Reopen an adjudicated finding only with new source evidence. For each genuinely new blocker, identify whether it comes from the original diff or subsequent remediation.

## Findings

Each finding carries a confidence: Verified means confirmed against the diff or source; Suspected means plausible but unconfirmed, and states what would confirm it. A Suspected finding cannot block.

Classify each finding under exactly one heading, ordered by severity within it:

- Blocking: a Verified Critical or Major correctness, regression, security, reliability, or requirement failure caused or worsened by the diff, whose necessary remedy fits within the PR's scope.
- Scope revision required: a Verified Critical or Major problem caused or worsened by the diff, serious enough to prevent shipping, whose necessary remedy exceeds the approved scope or implementation boundary. Explain the conflict; the expansion is a decision for the author, not a fix to prescribe.
- Non-blocking: minor findings, optional improvements, and unconfirmed risks or questions.
- Pre-existing: issues the diff neither causes nor worsens. Listed briefly; they inform but never block.

For each finding give: severity (Critical, Major, Minor, Nitpick), confidence, location as path:line or nearest identifier, the problem, the fix or required scope decision with code where helpful, and one line on why it matters.

Calibrate volume. Fewer Verified findings beat exhaustive lists. Nitpicks belong only when no structural issue exists. A clean review with zero manufactured findings is a valid and valuable outcome.

## Verdict

Issue an overall verdict only after completing the review coverage above:

- Ship when no Blocking or Scope revision required finding remains.
- Needs Work when Blocking findings can be fixed within the PR's scope without substantial redesign.
- Major Rethink when a Verified Blocking or Scope revision required finding requires substantial redesign or scope/plan revision. Explain the concrete shipping risk; disproportionate complexity without such a risk is Non-blocking.

For a complete review, post one PR comment containing the review ID, comparison base, reviewed head SHA, a short summary, the findings by heading, and the verdict with a brief explanation. Recommend specific tests and their assertions only for identified coverage gaps. Ship means no blocking findings in the reviewed revision; CI, required approvals, and other merge gates remain separate. Do not modify the code.
```
