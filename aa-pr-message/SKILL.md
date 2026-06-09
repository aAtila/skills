---
name: aa-pr-message
description: Use whenever the user is about to open, draft, or describe a pull request — phrasings like "what should the title and message of this PR be", "PR title and message", "write a PR description", "open a PR", "I'm about to open a PR", "ready for PR", "PR copy", "PR body", or "merge this branch to main". Reads the branch's commit messages (and the diff shape when needed), groups changes thematically, and produces a PR title and a markdown PR body the user can paste straight into `gh pr create` or the GitHub UI. Stops at the clipboard — does not push or open the PR.
---

# PR Message

This skill stops at the clipboard on purpose. The user wants to read the title and body before pasting them into `gh pr create` or GitHub. Two siblings cover the adjacent jobs:

- **`aa-commit`** — generates the message for a single commit and copies it to the clipboard.
- **`aa-commit-clarity`** — advisory only. Use first when a branch contains genuinely separable concerns and you want to think about whether it should be one PR or several before drafting the body.

The body of a PR is a different artifact than a commit message. A commit explains one change; a PR explains a branch — usually multiple commits — to a human reviewer who has not been living inside it. The job here is reviewer comprehension, not change logging.

**Where the signal lives.** In a well-maintained branch the commit messages already are the human-readable summary of what changed and why — the author wrote them while context was fresh. Treat them as the primary source. The diff is a fallback for cases where the commit messages are thin, the branch is one big WIP commit, or you need to verify a specific claim. Don't burn tokens re-deriving the story from raw hunks when the author already wrote it down.

## Workflow

### Step 0: Setup

Three quick checks before drafting:

1. **Identify the base branch.** Try in order; use the first that succeeds:
   - `git symbolic-ref --quiet refs/remotes/origin/HEAD` (strip the `refs/remotes/origin/` prefix) — the repo's configured default.
   - `git rev-parse --verify --quiet origin/main`, then `origin/master`.
   - Ask Atila. Don't guess.

2. **Confirm we have a branch to PR.** If `git rev-parse --abbrev-ref HEAD` returns the base, stop and tell Atila — there's nothing to PR.

3. **Check for a PR template.** This shapes the body's sections, so it has to happen *before* you draft anything. Look for any of:
   - `.github/pull_request_template.md` (and case variants `PULL_REQUEST_TEMPLATE.md`)
   - `.github/PULL_REQUEST_TEMPLATE/` — a directory of multiple templates (pick the one that fits, or ask)
   - `docs/pull_request_template.md`
   - `pull_request_template.md` at repo root

   One-liner: `find . -maxdepth 3 -iname 'pull_request_template*' -not -path './node_modules/*' 2>/dev/null`. If a template exists, use its section headings in Step 4 instead of inventing your own. Fill in only the sections that genuinely have content — leave a section blank rather than fabricating filler.

### Step 1: Read the branch — commit messages first

The commit messages are the primary source. Read them in full, not just subjects:

```sh
git log <base>..HEAD --format=fuller
```

(or `git log <base>..HEAD --pretty=format:'%h %s%n%n%b%n---'` for a tighter view of subject + body per commit). Authors often put the *why* in the commit body where `--oneline` would hide it.

Then get the file shape so you can describe scope honestly:

```sh
git diff <base>...HEAD --stat
```

Note the **three** dots — that's branch-vs-merge-base, which is what reviewers actually see.

**When to read actual hunks.** Default: don't. The commit messages plus `--stat` are enough for 99% of branches. Reach for `git diff <base>...HEAD -- <path>` only when:

- The branch is one big "wip" / "fix" commit and the message tells you nothing.
- A commit message claims something specific (e.g. "fixes race in deviceId mint") and you want to confirm the body summary you're about to write reflects what actually changed.
- The user explicitly asks you to double-check.

When you do read hunks, prioritise files where the diff shape suggests semantic change — new files, large `+/-` deltas, files matching obvious feature names. Skip lockfiles, snapshots, and formatter-only churn.

Also surface anything dirty or untracked that looks related to the branch's theme — easy to forget before pushing. Frame as a heads-up, not a blocker:

> "Heads up — `docs/investigations/foo.md` is untracked. Want it in this PR before I copy the message?"

### Step 2: Cohesion check (non-blocking)

Before drafting, ask: **would a reviewer see this as one story, or several unrelated stories stapled together?**

If it's one story, keep going. If it spans a few independent concerns, **don't ask permission to proceed** — draft the PR anyway and add a single-line P.S. when you hand off:

> "FYI this branch looks like it spans a couple of independent concerns. If you want to think about splitting before opening, `aa-commit-clarity` is the tool. Otherwise the message below is ready to paste."

There are intentional reasons to bundle (end-of-sprint cleanup, related-but-separate fixes, feature plus its prep work). Surfacing the signal once, without blocking, respects Atila's time.

### Step 3: Draft the title

The title is the single most-read line in the PR. Rules:

- Short, imperative, no trailing period.
- Match the repo's recent merged PR style — sample with `gh pr list --state merged --limit 8 --json title` if `gh` is available and authed. Some repos use conventional-commit prefixes (`feat(scope): …`), some use plain imperative ("Add JWT refresh flow"). Match what's already there.
- Conventional-commit scope at the PR level is fine but **not required**. PR titles are read by humans skimming a PR list, not by a changelog generator.
- If the branch is one commit, the PR title is usually that commit's subject. Don't reinvent it.
- If the branch is many commits serving one theme, name the theme. Don't list the commits.

Examples (the same change, different repo styles):

- `Make recommended ads client-side and cache-safe`
- `feat(recommender): move fetching to client and harden device-id reads`

Pick the style the repo already uses.

### Step 4: Draft the body

If a PR template exists (Step 0), use its sections. Otherwise this template is a **maximum, not a minimum** — size the body to the change. A one-line bugfix doesn't need a `## Why` section; a 30-file refactor probably does.

```markdown
## Summary

<One short paragraph naming the user-visible or system-visible outcome. Not "this PR does X" — say what now works differently.>

## Changes

- <Thematic bullet 1 — group related edits, not file lists>
- <Thematic bullet 2>
- <…>

## Why

<Optional paragraph. Skip this section unless the WHY adds something the Summary didn't. The body of a PR exists for the reviewer's benefit — if they'd ask "why?" while reading, answer it here. If they wouldn't, don't pad.>
```

Rules:

- **Group by theme, not by file.** "Adds `useDeviceId` hook" beats "modifies `src/lib/device/use-device-id.ts`". The diff already lists the files.
- **Explain why, not what.** The diff shows what. The body's job is to give the reviewer enough context to evaluate whether the what is the right what.
- **No attribution footers.** No `Co-Authored-By`, no `Generated with…`, no `🤖`. The PR author is the human pushing it.
- **Don't enumerate every commit.** Reviewers can click "Commits" if they want that. The body is the human summary.

### Worked example

Branch: 3 commits adding a `useDeviceId` hook and migrating two call sites.

Commit log:

```
feat(device): add useDeviceId hook with client-side mint
refactor(recommender): use useDeviceId hook
refactor(search): use useDeviceId hook
```

Output:

**Title:** `feat(device): add useDeviceId hook and migrate consumers`

**Body:**

```markdown
## Summary

Centralises device-id reads behind a `useDeviceId` hook so consumers no longer have to remember the mint-if-missing dance.

## Changes

- New `useDeviceId` hook that mints client-side on first read and reuses thereafter.
- Recommender and search now read through the hook instead of touching cookies directly.

## Why

Pulls device-id handling out of feature code so the Varnish-prep work (client-first mint) can land in one place rather than being duplicated at every call site.
```

Notice what's *not* there: no file paths, no per-commit bullets, no "this PR does X" phrasing. `## Why` is included only because the surrounding context (Varnish prep) isn't obvious from the diff alone.

### Step 5: Hand off

Write the body to a temp file first — this avoids shell-quoting corruption when the body contains code blocks, backticks, or `$`. Direct `printf "$BODY" | pbcopy` works for plain text but silently mangles realistic PR bodies.

```sh
cat > /tmp/pr-body.md <<'EOF'
<the body verbatim>
EOF
pbcopy < /tmp/pr-body.md
```

(On Linux: `xclip -selection clipboard < /tmp/pr-body.md` or `wl-copy < /tmp/pr-body.md`. On Windows: `clip < /tmp/pr-body.md`. If no clipboard utility is available, just leave the file in place and tell Atila where it is.)

Print the title and body to the chat too, so Atila can grab either independently. Suggest the file-based `gh` invocation as primary — it survives any body content:

```sh
gh pr create --title "<title>" --body-file /tmp/pr-body.md
```

The clipboard form (`gh pr create --title "<title>" --body "$(pbpaste)"`) is fine as a fallback for short bodies without quotes or backticks, but don't recommend it for bodies that contain code blocks.

**Check that the branch is pushed.** `git status` won't tell you this reliably — it only reports against the configured upstream. Use:

```sh
git rev-parse --abbrev-ref --symbolic-full-name @{u} 2>/dev/null
```

If that command fails (no upstream configured), mention it — *"Branch isn't pushed yet — `git push -u origin <branch>` first."* — but don't run `git push` yourself. Atila pushes on his own terms.

## What this skill does NOT do

- Does not run `gh pr create`. Atila pastes it himself.
- Does not push the branch. If the branch has no upstream, mention it — but let Atila run `git push` on his own terms.
- Does not amend, rebase, squash, or reword commits. The branch is what it is; the skill describes it.
- Does not block on cohesion concerns. It surfaces them once and moves on.
