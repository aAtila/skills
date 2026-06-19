---
name: aa-simplify
description: Use whenever the user wants a critical second-pass focused on cutting code — phrasings like "simplify this", "is this over-engineered?", "did I overdo it?", "what would you remove?", "feels bloated", "any cleanup opportunities?", "second look at this", "take another pass". Reviews recent changes for KISS/YAGNI violations, premature abstraction, defensive coding, unused configurability, and dead branches. Biased toward removal — outputs findings for discussion, not direct edits.
---

# Simplify

A critical second-pass on recent code changes, biased toward **removal**. The author just wrote this code and is biased toward keeping it; your job is to read it cold and ask what actually survives scrutiny. Treat the iteration history as a _liability_, not credit — early decisions ossify and stop being questioned.

## Scope

Look at what changed recently:

- Default: `git diff` + `git diff --staged` (uncommitted work)
- If both are empty, look at the most recent commit
- If still nothing or the user named a path/PR, use that

If the diff is large or you're unsure where to focus, ask the user before reading the whole thing.

## The method

Don't just run a rubric. For each change, ask the diagnostic questions below. If you can't answer "yes, definitely" to the question, it's a finding.

### 1. Premature abstraction

For each new function, hook, component, type, or file: **is it used in more than one place right now?** If not, is the second caller genuinely coming — not "might be useful someday"?

### 2. Defensive coding

For each null check, try/catch, optional chain, fallback, or guard: **name a specific scenario where this branch triggers.** If you can't, it's noise — it hides real bugs and inflates surface area.

### 3. Speculative configurability

For each prop, option, or parameter: **does any caller pass a non-default value?** If every caller passes the same thing, the option is dead weight.

### 4. Derived state pretending to be state

For each `useState` + `useEffect` pair that syncs from another value: **could this be a `useMemo`, a `key` prop, or just inline computation?** Effects that mirror props or other state are almost always wrong in React.

### 5. Wrapper layers

For each new wrapper around a library or utility: **does the wrapper add behavior, or just rename things?** Rename-only wrappers are pure indirection.

### 6. DRY against the grain

For each consolidation of "similar" code: **are the callers solving the same problem, or do they just look alike?** Coupling distinct concerns under one abstraction costs more than the duplication.

### 7. Dead branches and vestigial code

Code paths marked "shouldn't happen", legacy compatibility shims with no caller, commented-out blocks, TODOs with no owner — all candidates for removal.

## Output

Produce a findings list, **don't edit**. The user discusses architectural decisions before implementation (see their CLAUDE.md). Format each finding:

- **Location** — `file:line` or function name
- **Finding** — what's over-engineered, in one sentence
- **Why it's noise** — which diagnostic question it fails
- **Suggested cut** — concrete change (delete, inline, replace with X)
- **Severity** — `cut` (clearly dead), `consider` (judgment call), `flag` (worth a thought)

Group by severity, `cut` first. If nothing meaningful is wrong, say so plainly — don't manufacture findings to look thorough. A clean diff is a valid result.

## Example finding

> **Location:** `src/hooks/use-user-display.ts:1-12`
> **Finding:** New hook wraps `user.name || user.email` with `useMemo`, used in one component.
> **Why it's noise:** Premature abstraction (one caller) + unnecessary memoization (string OR, no measurable cost).
> **Suggested cut:** Inline the expression at the call site; delete the hook file.
> **Severity:** `cut`

## When this skill is the wrong fit

This skill is specifically for _reducing surface area_. Redirect when the ask is different:

- General review (bugs, correctness, security) → `aa-review-superpower` or `aa-second-opinion`
- Pre-commit polish on staged changes → `aa-commit-review`
- Architecture critique / design questions → consult Oracle in `plan` mode

The honest path: if you have nothing to cut, recommend a different skill or say "this is fine."
