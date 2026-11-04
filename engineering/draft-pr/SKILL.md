---
name: draft-pr
description: Draft a PR/MR title and description. Use for every PR message, whether the user asked ("what should the PR say?", "draft and open the PR") or you need one yourself.
---

# PR Message

This skill stops at the clipboard: the user reads the title and body before they go into a PR (GitHub) or merge request (GitLab) — via `gh`, `glab`, or the web UI. It opens the PR only on an explicit instruction — the user or an orchestrating workflow saying "draft and open it" (Step 6); an inferred intent to open is not one. ("PR" throughout means either; the job is identical.) Two siblings cover the adjacent jobs:

- **`commit-me`** — makes every commit: formats, writes the message, stages, commits.
- **`land-pr`** — reshapes and merges the branch after review: history cleanup, merge strategy, the merge. This skill describes the branch as it stands, so amends, rebases, squashes, and rewords all belong there.

The body of a PR is a different artifact than a commit message. A commit explains one change; a PR explains a branch — usually multiple commits — to a human reviewer who has not been living inside it. **The diff shows the *what*; the body supplies what the diff can't: the *why*, how it was verified, and what could break.** That principle drives every choice below — the job is reviewer comprehension, not change logging.

**Where the signal lives.** In a well-maintained branch the commit messages already are the human-readable summary of what changed and why — the author wrote them while context was fresh. Treat them as the primary source. The diff is a fallback for thin commit messages, one big WIP commit, or a specific claim the body rests on (Step 1 lists when). Don't burn tokens re-deriving the story from raw hunks when the author already wrote it down.

## Workflow

### Step 0: Setup

Four quick checks before drafting:

1. **Identify the base branch.** Try in order; use the first that succeeds:
   - `git symbolic-ref --quiet refs/remotes/origin/HEAD` (strip the `refs/remotes/origin/` prefix) — the repo's configured default.
   - `git rev-parse --verify --quiet origin/main`, then `origin/master`.
   - Ask Atila. Don't guess.

2. **Confirm we have a branch to PR.** If `git rev-parse --abbrev-ref HEAD` returns the base, stop and tell Atila — there's nothing to PR.

3. **Check for a PR/MR template.** This shapes the body's sections, so it has to happen *before* you draft anything. Look for any of:
   - GitHub: `.github/pull_request_template.md` (and case variant `PULL_REQUEST_TEMPLATE.md`), or `.github/PULL_REQUEST_TEMPLATE/` — a directory of multiple templates (pick the one that fits, or ask)
   - GitLab: `.gitlab/merge_request_templates/*.md` — a directory; the filename is the template name (e.g. `Default.md`). Pick the fitting one, or ask.
   - `docs/pull_request_template.md` or `pull_request_template.md` at repo root

   One-liner: `find . -maxdepth 3 \( -iname '*request_template*' -o -ipath '*/merge_request_templates/*' -o -ipath '*/pull_request_template/*' \) -not -path './node_modules/*' 2>/dev/null`. If a template exists, use its section headings in Step 4 instead of inventing your own. Fill in only the sections that genuinely have content — leave a section blank rather than fabricating filler.

4. **Check the branch is pushed.** `git status` won't tell you reliably — it only reports against a configured upstream. Check directly:

   ```sh
   git rev-parse --abbrev-ref --symbolic-full-name @{u} 2>/dev/null   # fails → no upstream
   git rev-list --count @{u}..HEAD                                     # > 0 → unpushed commits
   ```

   Either result means the remote lags the local branch: keep drafting and carry it to Step 6.

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

**When to read actual hunks.** Default: don't. The commit messages plus `--stat` are enough for most branches. Reach for `git diff <base>...HEAD -- <path>` only when:

- The branch is one big "wip" / "fix" commit and the message tells you nothing.
- A commit message claims something specific (e.g. "fixes race in deviceId mint") and you want to confirm the body summary you're about to write reflects what actually changed.
- The messages or `--stat` show a possible one-way door — a migration, a deletion, an outbound send, a removed export. Read those hunks so the Risk line (Step 4) rests on the code.
- You're drawing a Summary sketch (Step 4). Read the hunks the sketch shows.
- The user explicitly asks you to double-check.

When you do read hunks, prioritise files where the diff shape suggests semantic change — new files, large `+/-` deltas, files matching obvious feature names. Skip lockfiles, snapshots, and formatter-only churn.

**Gather verification.** Collect every check you saw run on this branch: commands run in this session, results the invoker hands you, and — when Step 0 found the branch pushed — CI on its head (`gh run list --branch <branch> --limit 5`; GitLab: `glab ci status`). Note each one's result and the short SHA it ran on. These are Step 4's only Verification sources.

Also surface anything dirty or untracked that looks related to the branch's theme — easy to forget before pushing. Frame as a heads-up, not a blocker:

> "Heads up — `docs/investigations/foo.md` is untracked. Want it in this PR before I copy the message?"

### Step 2: Cohesion check (non-blocking)

Before drafting, ask: **would a reviewer see this as one story, or several unrelated stories stapled together?**

If it's one story, keep going. If it spans a few independent concerns, **don't ask permission to proceed** — draft the PR anyway and add a single-line P.S. at handoff that names the concerns:

> "FYI this branch spans independent concerns — the device-id hook and the unrelated search-copy fix. Worth splitting before opening? Otherwise the message below is ready to paste."

There are intentional reasons to bundle (end-of-sprint cleanup, related-but-separate fixes, feature plus its prep work). Surfacing the signal once, without blocking, respects Atila's time.

### Step 3: Draft the title

The title is the single most-read line in the PR. Rules:

- Short, imperative, no trailing period.
- Match the repo's recent merged PR/MR style — sample with `gh pr list --state merged --limit 8 --json title` (on GitLab: `glab mr list --merged`) if the CLI is available and authed. Some repos use conventional-commit prefixes (`feat(scope): …`), some use plain imperative ("Add JWT refresh flow"). Match what's already there.
- Conventional-commit scope at the PR level is fine but **not required**. PR titles are read by humans skimming a PR list, not by a changelog generator.
- If the branch is one commit, the PR title is usually that commit's subject. Don't reinvent it.
- If the branch is many commits serving one theme, name the theme. Don't list the commits.

Examples (the same change, different repo styles):

- `Make recommended ads client-side and cache-safe`
- `feat(recommender): move fetching to client and harden device-id reads`

Pick the style the repo already uses.

### Step 4: Draft the body

If a PR template exists (Step 0), use its sections; Verification and Risk content goes under its matching headings (testing, risk, deployment notes), or into short sections appended at the end when it has none. Otherwise this template is a **maximum, not a minimum** — size the body to the change. A one-line bugfix doesn't need a `## Why` section; a 30-file refactor probably does. Verification and Risk carry what the diff can't show, so they're the last to cut: every body keeps both, except docs- or comment-only changes.

```markdown
## Summary

<One short paragraph naming the user-visible or system-visible outcome. Not "this PR does X" — say what now works differently.>

<Optional sketch of the change's shape — see the rules below.>

## Changes

- <Thematic bullet 1 — group related edits, not file lists>
- <Thematic bullet 2>
- <…>

## Why

<Optional paragraph. Skip this section unless the WHY adds something the Summary didn't. The body of a PR exists for the reviewer's benefit — if they'd ask "why?" while reading, answer it here. If they wouldn't, don't pad.>

## Verification

- <check → result @ short SHA, e.g. `pnpm test` → 214 passed @ `a1b2c3d`>

## Risk

<Two-way or one-way door, then the blast radius: what breaks, and for whom, if this is wrong.>
```

Rules:

- **Group by theme, not by file.** "Adds `useDeviceId` hook" beats "modifies `src/lib/device/use-device-id.ts`". The diff already lists the files.
- **Sketch the shape when a paragraph can't carry it.** A new call path, a moved boundary, or a reorganised folder reads faster as a picture: a call tree, a file tree, or a `diff`-fenced sketch whose `+`/`-` lines mark what changed inside the shape that already exists. One sketch, holding only the calls, files, or states the change touches; plain text, so it reads the same in chat, terminal, and the forge. When the sketch already shows what Changes would list, drop Changes.
- **Verification lists only observed runs** — the sources gathered in Step 1. A run over uncommitted changes gets no SHA. For a behaviour fix, the strongest line is a before/after: the test that failed before the fix and passes after, when you saw both. For a visual change, name the screen and state to capture; Atila attaches the screenshot. When nothing has run, the section says `Not run yet` and names what's pending.
- **Risk names the door, then the blast radius.** A one-way door is a change a revert doesn't undo: a destructive or data-rewriting migration, deleted data, an outbound send (emails, webhooks, payments), a removed public API or contract field, a published package. Everything else is a two-way door. Judge from what the change writes, sends, and deletes, not from how small the diff looks — you're grading your own work, so a "two-way, small" call needs the firmest grounds. When the branch carries a deployment-impact signal (a migration, a new env var, a cron/worker/queue/cache change, an API contract change), name it on the Risk line; `land-pr` runs `deploy-check` on it before merge. A `deploy-check` verdict the invoker supplies goes on the Risk line.
- **No attribution footers.** No `Co-Authored-By`, no `Generated with…`, no `🤖`. The PR author is the human pushing it.
- **Don't enumerate every commit.** Reviewers can click "Commits" if they want that. The body is the human summary.
- **Issue reference (optional):** if the branch's parent issue can be confidently determined — the user mentioned it, the branch name encodes it (`spec/252-…`, `123-fix-login`, `feature/GH-123`), or the commits carry `Refs #123` — end the body with `Closes #<n>` on its own line (`Closes` here, unlike commits' `Refs`: merging the PR is exactly when the issue should close). If it can't be confidently determined, skip the line silently — don't ask and don't guess.

### Worked example

Branch: 3 commits adding a `useDeviceId` hook and migrating two call sites. `pnpm test` and `pnpm typecheck` ran green on the head commit earlier in the session.

Commit log:

```
feat(device): add useDeviceId hook with client-side mint
refactor(recommender): use useDeviceId hook
refactor(search): use useDeviceId hook
```

Output:

**Title:** `feat(device): add useDeviceId hook and migrate consumers`

**Body:**

````markdown
## Summary

Centralises device-id reads behind a `useDeviceId` hook so consumers no longer have to remember the mint-if-missing dance. The hook mints client-side on first read and reuses the id after.

```diff
 RecommenderWidget
-  cookies.get('device_id')
+  useDeviceId()
 SearchResults
-  cookies.get('device_id')
+  useDeviceId()
```

## Why

Pulls device-id handling out of feature code so the Varnish-prep work (client-first mint) can land in one place rather than being duplicated at every call site.

## Verification

- `pnpm test` → 214 passed @ `a1b2c3d`
- `pnpm typecheck` → clean @ `a1b2c3d`

## Risk

Two-way door: the hook reads the same `device_id` cookie the call sites read before, so a revert restores direct reads and the ids it minted stay valid. Blast radius: recommender and search, the hook's only consumers.
````

Notice what's *not* there: no file paths, no per-commit bullets, no "this PR does X" phrasing. The sketch replaced `## Changes`, since it already shows both call sites moving to the hook. `## Why` is included only because the surrounding context (Varnish prep) isn't obvious from the diff alone.

### Step 5: Polish the body

If `unslop` is in your available skills, call the Skill tool with `unslop` on the drafted body; otherwise skip this step and hand off the draft as is. Keep template headings, code spans, sketches, identifiers, Verification results and SHAs, and the `Closes #<n>` line exactly as drafted; the title keeps the repo's format from Step 3. **Done when** `unslop` has run (or is unavailable) and every claim in the body still matches the commits and the observed runs.

### Step 6: Hand off

If Step 0 found the branch unpushed or behind its upstream, lead the handoff with it — *"Branch isn't pushed yet — `git push -u origin <branch>` first."* (or *"2 commits aren't pushed — `git push` first."*). Atila pushes on his own terms, so the push stays with him.

Write the body to a temp file first — this avoids shell-quoting corruption when the body contains code blocks, backticks, or `$`. Direct `printf "$BODY" | pbcopy` works for plain text but silently mangles realistic PR bodies.

```sh
cat > /tmp/pr-body.md <<'EOF'
<the body verbatim>
EOF
pbcopy < /tmp/pr-body.md
```

(No clipboard utility available? Just leave the file in place and tell Atila where it is.)

Print the title and body to the chat too, so Atila can grab either independently. Suggest the file-based invocation as primary — it survives any body content:

```sh
# GitHub
gh pr create --title "<title>" --body-file /tmp/pr-body.md

# GitLab — no file flag, but quoted command-substitution is safe even with backticks/$ in the body
glab mr create --title "<title>" --description "$(cat /tmp/pr-body.md)"
```

The clipboard form (`gh pr create --title "<title>" --body "$(pbpaste)"`) is fine as a fallback for short bodies without quotes or backticks, but don't recommend it for bodies that contain code blocks.

**If the invoker explicitly asked to open the PR**: re-run Step 0's push check, then run the file-based create command yourself instead of handing it off, and report the PR URL. A branch that isn't fully pushed stops you there — the user pushes. Everything else above still applies, including printing the title and body in full.
