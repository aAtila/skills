---
name: apply-review
description: Act on a code review that came back from any reviewer — another agent, the Oracle, a human PR comment. Triages each finding against the actual implementation, applies what holds up, and defends what doesn't, with rejections required to cite a concrete fact rather than a preference. Explicit invocation only.
disable-model-invocation: true
---

# Apply Review

A review has come back on code you (or another agent) wrote. Your job is **not** to implement it. Your job is to judge it, finding by finding, and then act.

The reviewer read the diff. You have the implementation context: the constraints you hit, the callers you checked, the approaches you tried and abandoned, the decisions you made deliberately. A suggestion can be perfectly reasonable from outside and still wrong from inside. That asymmetry is the entire reason this skill exists.

But the asymmetry cuts both ways, and the second edge is sharper: **"I had my reasons" is cheaper than editing.** An agent told it has superior context will rationalize away legitimate findings, confidently, at no cost. Guard against that harder than against over-compliance.

## Scope

Works with any reviewer — another agent, the Oracle, Codex, a human PR comment, a pasted list. Source doesn't matter; the method is the same.

Reviewer credibility does **not** factor into triage. A finding from a senior human and a finding from a subagent get the same test. Judge the claim, not the claimant.

If you did not write the code under review, say so before starting — you don't have the implementer's context and your rejections carry much less weight. Prefer `apply` or `defer` in that case.

## Method

### 1. Decompose

Split the review into discrete, individually-decidable findings. Do not work from prose. Reviews arrive as paragraphs that bundle three claims into one sentence; a bundled finding gets accepted or rejected as a unit, which is how bad suggestions ride in on good ones.

Number them. If the review is vague ("consider tightening the error handling"), turn it into the concrete change it implies, or mark it `unclear` and ask.

### 2. Verify before judging

For each finding: **go look.** Read the actual code, the callers, the tests. Do not triage from memory of what you wrote — that memory is exactly what the reviewer is challenging.

Reviewers hallucinate. A finding that references a function, prop, or file that doesn't exist, or describes behavior the code doesn't have, is `invalid` — not `reject`. Distinguish the two: `invalid` means the reviewer was factually wrong, `reject` means they were factually right and you still disagree.

### 3. Triage

Assign every finding exactly one verdict:

| Verdict | Meaning |
| --- | --- |
| `apply` | Correct and the fix fits. Do it. |
| `reframe` | The problem is real, the proposed fix isn't right. Fix the problem your way. |
| `reject` | Wrong, or right in the abstract but wrong for this code. |
| `defer` | Real, but out of scope for this change — bigger refactor, separate concern, product decision. |
| `invalid` | Reviewer is factually mistaken about the code. |
| `unclear` | Can't tell what's being asked. Ask the user. |

**The rejection rule — this is the load-bearing part:**

> A `reject` must be justified by a **concrete, checkable fact about this codebase**: a constraint, a specific caller, a test, a performance measurement, a documented decision, an approach you tried that failed, a requirement from the task.
>
> Not sufficient: "this is intentional", "I prefer it this way", "the current approach is fine", "it's more readable", "consistent with the existing style" (unless you name the existing code).
>
> **If you cannot name the fact, you don't have context the reviewer lacks — you have a preference. Apply the fix.**

`reframe` is the most common honest outcome and is underused. Reviewers are much better at spotting problems than prescribing fixes. Reaching for `reject` when the reviewer correctly identified a real problem is the most damaging failure mode of this skill — it discards a true finding on a technicality about the proposed solution.

### 4. Report the triage

Print the table **before making any edits**:

```
| # | Finding | Verdict | Reason |
```

Keep reasons to one line. Then:

- **All `apply` (and nothing else)** — proceed straight to step 5. No confirmation needed; there's nothing to disagree with.
- **Any `reject`, `defer`, `invalid`, or `unclear`** — stop. Wait for the user. Those are the calls where you're claiming knowledge the user can't verify from the table alone, and they're cheap to correct now and expensive to correct after edits.
- **Any `apply` that touches something risky** — auth, payments, migrations, data deletion, public API shape — stop regardless.

### 5. Apply

Make the accepted changes. Then verify: run the tests, typecheck, build — whatever the project uses. A review-driven fix that breaks the build is worse than the original finding.

If applying a change reveals the reviewer was right about more than they knew, say so. If it reveals they were wrong, revert it and move that finding to `reject` with the new evidence — you now have the concrete fact the rejection rule wants.

### 6. Close out

Report:

- **Applied** — what changed, per finding.
- **Held** — rejected/deferred, one line each, so the user can push back.
- **Verification** — what you ran and the result.
- **New** — anything the review surfaced indirectly that nobody flagged.

Do not commit unless asked.

## Anti-patterns

- **Blanket agreement.** A triage table of all-`apply` on a substantive review usually means you didn't judge, you complied. Check whether you actually opened the files.
- **Blanket defense.** All-`reject` means you're protecting your work. Re-read the rejection rule and test each reason against it.
- **Silent scope creep.** Applying a finding, noticing something adjacent, and fixing that too. Note it under **New**; don't fold it in.
- **Deferring to avoid work.** `defer` means genuinely out of scope, not "annoying to do".
- **Triaging from memory.** See step 2.

## When this is the wrong fit

- Getting a review in the first place → `aa-second-opinion`, `aa-review-codex`, `autoreview`
- Cutting over-engineering → `aa-simplify`
- Review findings that amount to a redesign → stop and consult Oracle in `plan` mode; this skill applies changes, it doesn't re-architect
