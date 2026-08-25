# Engineering skills

The day-to-day coding companions. One line each; the SKILL.md is the source of truth for protocol and triggers.

## Commit → PR flow

| Skill | What it does | Canonical invocation |
|---|---|---|
| `aa-commit-clarity` | Decides whether a mixed diff is one commit or several. | "should this be one commit or two?" |
| `commit-me` | Formats, stages, writes a conventional message, commits. | "commit this" |
| `draft-pr` | Drafts PR title + body from the branch's commits; stops at the clipboard. | "what should the PR title and message be?" |

## Review & second passes

| Skill | What it does | Canonical invocation |
|---|---|---|
| `aa-second-opinion` | Sends the diff to the Oracle for external review, adds a contrasting take. Read-only. | "gut check this" |
| `aa-simplify` | Critical pass biased toward removal — YAGNI, premature abstraction, dead branches. | "did I overdo it?" |
| `apply-review` | Triages an incoming review's findings: applies what holds up, defends the rest with facts. | "apply this review" |
| `test-review` | Audits existing tests for false greens and coverage gaps. Read-only; hands gaps to tdd. | "are these tests any good?" |
| `qa-plan` | Post-build acceptance checklist derived from intent, not the diff. | "how do I QA what we built?" |

## Code placement & prep

| Skill | What it does | Canonical invocation |
|---|---|---|
| `colocation-first` | Where new files and modules go — apply before writing code. | (fires when placing code) |
| `improve-codebase-colocation` | The audit counterpart: finds placement drift in existing code. | "make this codebase more colocated" |
| `tidy-first` | Prepares the landing zone for one imminent change (Kent Beck's prefactoring). | "tidy before this change" |

## Documentation

Both user-invoked only — they fire when you type them, never autonomously. Each has a `references/invocations.md` with fuller usage examples.

| Skill | What it does | Canonical invocation |
|---|---|---|
| `onboarding` | Writes a verified onboarding walkthrough for one codebase area into `docs/onboarding/`. Mirrors the repo's existing walkthrough as exemplar, verifies every claim, ends with a `Verified:` stamp. | `/onboarding <area> — for <goal>` |
| `doc-sync` | Syncs a repo's docs with a code diff: changed paths → owning docs via the module map, verify, fix, bump stamps. Scope is a kind boundary (all docs, wherever they live), not `docs/` only. | `/doc-sync <change> — since <baseline>` |

How they compose: `onboarding` creates walkthroughs born with a `Verified: <date> against <commit>` stamp; `doc-sync` uses that stamp to scope re-verification to the diff since it. They share one verification table — it lives in `onboarding`'s SKILL.md, and `doc-sync` points at it. A repo's own contract (e.g. r3pulse's `docs/agents/onboarding.md`) overrides both skills' defaults.

## Targeted

| Skill | What it does | Canonical invocation |
|---|---|---|
| `semantic-html` | Catches div-soup, heading skips, a11y failures in HTML/JSX. | (fires when writing markup) |
| `sentry-quick-wins` | Ranks unresolved Sentry issues into a quick-win approval table. Triage only. | "triage Sentry" |
