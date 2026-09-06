# Review prompt

Sent verbatim by Step 3 of `gpt-pro-review`, with `<PR URL>`, `<HEAD SHA>`, and `<REVIEW ID>` substituted. The leading `@GitHub` mention makes ChatGPT open the PR and post the comment through its connector; keep it.

```
@GitHub <PR URL>

Review ID: <REVIEW ID>
Requested head SHA: <HEAD SHA>

Review this revision and confirm the diff and source you inspect correspond to the requested head SHA. If you cannot establish that, return an incomplete-review response explaining the limitation instead of a verdict. Include the review ID and actual reviewed head SHA in your response and PR comment so the caller can verify delivery and revision coverage.

Review this PR through GitHub. The diff is authoritative for what changed; the PR description and the surrounding code supply intent. Where intent is thin, infer it from codebase patterns and state your assumptions.

Judge the change on correctness, regressions, security, reliability, tests, and long-term maintainability, in that order. Prefer designs whose correctness is easy to see over designs whose deficiencies are merely hard to find, and apply that bar proportionally to the change.

## Canonical path doctrine

Prefer a clear current-state code path. Scrutinize speculative compatibility paths, redundant defenses, and silent fallbacks against requirements, existing behavior, persisted formats, external contracts, and demonstrated failures. Flag complexity when you can explain why it is unnecessary, and prefer removal when it preserves required behavior. Ordinary control flow should be judged on correctness and clarity.

A silent fallback substitutes different behavior when the primary path fails or data does not match expectations. Prefer specified recovery that detects and surfaces failures, such as retries with backoff on network I/O or timeouts. Preserve defenses at security, authorization, and untrusted-input boundaries.

For each new defensive check, ask whether the better fix is to strengthen the type, schema, constructor, parser, or state transition that produces the value. Validate at trust boundaries; downstream code relies on established invariants.

## Method

1. Summarize what the change does and which flows it touches.
2. Check proportionality: compare the diff footprint and new obligations with the stated requirement.
3. Walk each hunk: behavior before versus after, including edge and error paths; unnecessary complexity; alignment with existing patterns and utilities.
4. Cross-check tests: new and changed behavior covered, error paths covered, tests assert behavior rather than implementation.
5. Generate concrete fixes, preferring removal or simplification toward a single explicit path.

## Findings

Each finding carries a confidence: Verified means confirmed against the diff or source; Suspected means plausible but unconfirmed, and states what would confirm it. A Suspected finding cannot block.

Classify each finding under exactly one heading, ordered by severity within it:

- Blocking: a Verified correctness, regression, security, reliability, or requirement failure caused or worsened by the diff.
- Scope revision required: a Verified problem serious enough to prevent shipping, whose remedy exceeds the PR's stated scope. Explain the conflict; the expansion is a decision for the author, not a fix to prescribe.
- Non-blocking: minor findings and optional improvements.
- Pre-existing: issues the diff neither causes nor worsens. Listed briefly; they inform but never block.

For each finding give: severity (Critical, Major, Minor, Nitpick), confidence, location as path:line or nearest identifier, the problem, the fix with code where helpful, and one line on why it matters.

Calibrate volume. Fewer Verified findings beat exhaustive lists. Nitpicks belong only when no structural issue exists. A clean review with zero manufactured findings is a valid and valuable outcome.

## Verdict

Ship when no Blocking or Scope-revision finding remains. Needs Work when Blocking findings can be fixed within the PR's scope. Major Rethink when the patch is disproportionate to the requirement or safe remediation needs redesign.

Post one PR comment containing the review ID, reviewed head SHA, a short summary, the findings by heading, and the verdict with a brief explanation. Recommend specific tests and their assertions only for identified coverage gaps. Ship means no blocking findings in the reviewed revision; CI, required approvals, and other merge gates remain separate. Do not modify the code.
```
