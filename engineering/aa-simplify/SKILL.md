---
name: aa-simplify
description: Cut-focused review of recent changes: what to delete, inline, or collapse. Use when the user asks to simplify or trim, or doubts a change ("over-engineered?", "did I overdo it?").
---

# Simplify

A second pass on recent changes, biased toward **removal**. Read the change **cold**: history, passing tests, and plans are context, not justification.

## 1. Scope

Use the target the user named (a branch, commits, a path, a PR). Otherwise: uncommitted changes (`git diff` + `git diff --staged`); if none, the latest commit. If the branch is ahead of trunk and the uncommitted diff is trivial, offer branch-vs-trunk. Ask only if the target is genuinely ambiguous.

## 2. Examine

Run every hunk through every question below.

1. **Abstraction**: does this helper/type/layer have a distinct responsibility, or more than one caller now? (A deliberate boundary can earn its place with one caller; say why.)
2. **Defense**: name the concrete, reachable scenario where this guard or fallback fires.
3. **Configuration**: does any caller pass a non-default value?
4. **State**: could this stored or synced value be derived at the use-site? Is there a second authority for the same fact? In async or stateful code, ownership, ordering, and cancellation facts are load-bearing; only redundant bookkeeping is a cut.
5. **Wrapper**: does it add behavior, or just rename?
6. **Consolidation**: do the callers solve the same problem, or just look alike?
7. **Dead code**: can this branch, compat path, or block actually run?
8. **Orphaned by the change**: does any replaced or rerouted path still have a caller? Authors miss this class most.
9. **Tests**: does each test pin a behavior no other test pins, using only the setup that behavior needs?

Answer every caller and reachability claim from the codebase, never from the diff alone.

**Engine (RepoPrompt available):** run `context_builder` with `response_type: "review"`; its discovery pulls in out-of-diff callers. Put the confirmed scope in `<context>`, and the nine questions verbatim in `<task>` plus:

> Bias toward removal. Report only cuts: code to delete, inline, or collapse.

The oracle proposes, you confirm: verify every finding against the actual code before reporting it. Follow up in the same chat (`ask_oracle`, `new_chat: false`) for anything unclear.

**Fallback (no RepoPrompt):** run the questions yourself, with a search for every caller count.

Done when every hunk has faced every question and every finding is verified against the code.

## 3. Classify

Sort what the change does into **load-bearing** (required behavior, including compatibility guarantees) and **discretionary** choices. Then:

- **CUT**: load-bearing behavior unchanged; equivalence shown by callers, contracts, or tests.
- **CONSIDER**: plausible, but equivalence needs judgment or more proof.
- **SCOPE DECISION**: drops or changes load-bearing behavior. A product call, not cleanup.

## 4. Report

One-line verdict first: clean, or N CUT / M CONSIDER / K SCOPE DECISION. Then up to ten findings, highest value first:

- **Location**: `file:line`
- **Cut**: delete / inline / collapse into X
- **Evidence**: which question it fails, with callers, contracts, or tests cited
- **Must preserve**: the behavior and invariants the cut keeps
- **Class**: CUT / CONSIDER / SCOPE DECISION

> **Location:** `src/hooks/use-user-display.ts:1-12`
> **Cut:** Inline `user.name || user.email` at the call site; delete the hook.
> **Evidence:** Abstraction, one caller (`ProfileCard.tsx:14`); the `useMemo` guards a string OR.
> **Must preserve:** name-then-email fallback.
> **Class:** CUT

Then: the order to apply the CUTs, independent ones first; substantial mechanisms you examined and kept, each with its concrete reason; and coverage gaps.

A clean result, with its kept mechanisms listed, is a complete review. The report is the deliverable; the run ends when it's delivered.

## Other asks

This skill reduces surface area. For other reviews:

- Bugs, correctness, security → `aa-second-opinion`
- Commit boundaries → `aa-commit-clarity`
- Architecture or design critique → Oracle in `plan` mode
