# Invoking `/onboarding`

Operator notes — how to call this skill well. The agent doesn't need this file; you and your teammates do.

**The habit that matters most:** give the *why* along with the *what*. One clause ("for contributing", "I'm reviewing a PR touching it") steers the clarify questions, the exemplar emphasis, and what "Quick Wins" optimizes for — better than any flag would.

## Full form — area + goal in one line (skips the Step 1 question)

```
/onboarding the WorkflowMax Job change detection substrate — for contributing code
```

## Minimal form — let the skill ask

```
/onboarding donor drives
```

Step 1 fires with the goal question (contributing / reviewing / debugging / understanding).

## Refreshing an existing walkthrough

```
/onboarding refresh the job-photos walkthrough — the download path changed, I mostly care about the gallery/download flow
```

Same protocol; the existing doc is its own exemplar. The verification table and the stamp do the real work.

## In a repo without domain docs (no MODULES.md, no RepoPrompt)

```
/onboarding the payment webhooks in this repo — I need to review a PR touching them
```

The skill proceeds silently without CONTEXT.md/MODULES.md, maps the area by hand, and falls back to the bundled skeleton if `docs/onboarding/` is empty.
