---
name: aa-commit-clarity
description: Use whenever the diff feels mixed and you want to think about commit boundaries — phrasings like "should this be one commit or several", "how should I commit this", "this feels mixed", "is this one commit or two", "help me split this up", "what's the right way to commit this", or before running `aa-commit`/`aa-commit-direct` on a large or multi-concern change. Analyzes conceptual cohesion, separability, and diff hygiene to recommend a single commit or a logical split.
---

# Commit Clarity

Advisory only. Sits in front of `aa-commit` (clipboard) and `aa-commit-direct` (autocommit) — use this first when the diff spans more than one obvious concern and you want to decide one-vs-many before committing.

## Step 1: Read the actual diff

Run `git status` and `git diff` first. The recommendation has to be grounded in the hunks, not the file list — files can look related and have unrelated changes inside, or look unrelated and turn out to be one cohesive edit. The whole skill is worthless if the recommendation is based on guesses about file names.

For large diffs, run `git diff --stat` to get the shape, then read the most concerning hunks in full.

## Step 2: Apply the primary test

**Can the change be honestly described in one imperative sentence with no "and also"?**

- Yes → probably one commit.
- No → probably more than one.

This single test catches most cases. "Honestly" is load-bearing — don't let the model rationalise an awkward conjunction as a single sentence. The lenses below are for the harder calls where the primary test is genuinely unclear.

## Step 3: Apply the lenses (only when the primary test is unclear)

### Conceptual cohesion
Do all changes serve a single, clearly articulable purpose?

### Logical separability
Are there independent concerns (refactor + feature, behaviour change + formatting, infra + product)? Could any subset be reverted independently without breaking intent?

### Reviewer comprehension
Would a future developer understand *why* this change exists from the commit history? Would splitting improve narrative clarity, or fragment a story that reads better as one?

### Diff hygiene
Are mechanical changes (renames, formatting, generated output) mixed with semantic ones? Are there preparatory refactors that would be clearer on their own?

### Anti-fragmentation guard
Do not split unless it clearly improves understanding or safety. Tightly coupled changes that are meaningless in isolation belong together — splitting them creates broken intermediate commits and makes bisecting harder, not easier.

## Calibration examples

- **Refactor touching 30 files + an unrelated one-line bugfix** → split. The bugfix is an independent concern; it should be reviewable and revertable on its own.
- **Renaming a function across all its call sites** → single. The call-site changes are meaningless without the rename.
- **Adding a feature + the small refactor that made it possible** → judgment call. Split if the refactor stands on its own merits (clearer code regardless of the feature). Single if the refactor only makes sense in service of this feature.
- **Whole-file formatting + one semantic change in the same file** → split. The semantic change drowns in the formatting noise; the reviewer can't see what actually changed.
- **Adding a feature + the tests for it** → single. The tests are part of the feature.
- **A feature touching many files (migration + types + API + UI + tests) where each change is small** → single. The files all serve one purpose ("add the X field to Y"). Splitting per-file creates broken intermediate commits and serves nobody.

## Output

Start with a one-line verdict: **"Single commit"** or **"Split into N commits"**.

Then a short rationale (bullets).

If splitting:
- Propose commit boundaries — name the files (or hunks) that go in each.
- Suggest a one-line conventional-commit title for each.
- Briefly say what goes in each and why.

Do not suggest changes to the code itself unless the commit structure depends on it (e.g. "the formatting noise in `foo.ts` needs to be reverted before this can be a clean refactor commit"). Focus on commit strategy.

## After the recommendation

Wait for the user to decide.

If they accept a split, hand off to `aa-commit` (or `aa-commit-direct` if they prefer the autocommit path) for each chunk in turn. Stage only the files belonging to the current commit — never `git add -A`. Repeat until the working tree is clean.

If they accept a single commit, hand off once to `aa-commit`.
