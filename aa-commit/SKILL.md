---
name: aa-commit
description: Use whenever the user asks to commit, save changes, prepare a commit, wrap up work, or finish up a chunk of code — even if they don't say the word "commit" explicitly. Formats code if a formatter is configured, generates a conventional commit message, stages files, and copies the message to the clipboard so the user can review and paste it before committing.
---

# Commit

This skill stops at the clipboard on purpose. The user wants a chance to review the message and paste it themselves before the commit lands. Two siblings cover adjacent jobs:

- **`aa-commit-direct`** — same workflow, but commits directly without the clipboard step. Manual invocation only.
- **`aa-commit-clarity`** — advisory only. Use first when the diff feels mixed, to decide whether the changes belong in one commit or several.

## Workflow

### Step 0: Format the code

Detect the project's formatter and run it. Check in this order and use the first match:

- **Node** — if `package.json` exists and has a `format` script: run it via the matching package manager (`pnpm format` if `pnpm-lock.yaml`, `yarn format` if `yarn.lock`, `bun run format` if `bun.lockb`, otherwise `npm run format`).
- **Rust** — `cargo fmt` if `Cargo.toml` exists.
- **Go** — `gofmt -w .` if `go.mod` exists.
- **Python** — `ruff format .` if `pyproject.toml` or `ruff.toml` exists; otherwise `black .` if it's available.
- **Otherwise** — skip silently.

If a formatter is configured but the run fails (not just missing), briefly tell the user it failed and continue. Don't block the commit on formatter trouble.

### Step 1: Review changes

Run `git diff` and `git status` to understand everything staged and unstaged.

Before staging, scan for files that probably shouldn't be committed: `.env*`, `credentials.json`, `*.key`, `*.pem`, `*.p12`, secret-looking paths, large binaries, build artifacts. If any are present and unignored, surface them to the user and confirm before including them.

After the secrets scan, do a quick read of the diff for commit cohesion: does this span multiple independent concerns? Common signals — a refactor mixed with an unrelated behaviour change, formatting noise mixed with semantic edits, an obvious bugfix tucked into a feature commit, two changes that just happen to be sitting in your working tree together. If you spot a mix, pause before generating the message and surface a one-liner:

> "This diff looks like it might benefit from `aa-commit-clarity` before I write the message. Want me to run it, or just commit as-is?"

If the user says "just commit" (or anything that means proceed), don't push back further — they may have intentional WIP, end-of-day snapshots, or other legitimate reasons to commit a mixed diff. If the diff reads as cohesive, skip this check entirely and proceed straight to message generation.

### Step 2: Create the commit message

Use this conventional-commit shape. Treat it as a **maximum, not a minimum** — size the message to the change. A typo fix is one line. A multi-file refactor may need bullets and a paragraph. Use what genuinely adds information.

```
<type>(<scope>): <short description>

- <key technical change, if it adds info the diff doesn't already show>
- <another, only if useful>

<Optional paragraph explaining the WHY: what problem this solves and how>
```

Rules:

- Conventional types: `feat`, `fix`, `refactor`, `docs`, `style`, `test`, `chore`.
- Scope is short and concrete (`auth`, `api`, `ui`, `seo`, etc.). Omit scope if there isn't a meaningful one.
- Short description: imperative mood, lowercase, no period.
- The body explains **why**, not what — the diff already shows what.
- **Do not** list modified files in the body. Git already tracks this via `git show --stat`, `git log --name-status`, and `git diff --stat`. Duplicating it goes stale and bloats history.
- **Do not** include `Co-Authored-By`, "Generated with…", or any other attribution footer.

For multi-line messages, prefer a HEREDOC when invoking `git commit -m` later, so newlines survive shell quoting:

```sh
git commit -m "$(cat <<'EOF'
feat(auth): add JWT refresh flow

- introduces /auth/refresh endpoint
- swaps in-memory session store for signed cookies

Refresh tokens were never rotated, so a leaked token stayed valid
until expiry. The new flow rotates on every refresh.
EOF
)"
```

(For this skill the user does the actual commit themselves, but the message you generate should be HEREDOC-ready.)

### Step 3: Stage and copy

Stage the files that belong to this commit (don't use `git add -A` — be specific so secrets and unrelated edits don't slip in).

Then copy the commit message to the clipboard using whatever's available on the platform:

- macOS: `pbcopy`
- Linux: `xclip -selection clipboard` or `wl-copy` (Wayland)
- Windows: `clip`

Tell the user the message is on their clipboard, ready to paste into `git commit -m "$(pbpaste)"` (or however they prefer).

## Comment Guidelines

This section lives in the skill rather than only in a project's `CLAUDE.md` because this skill is used across many projects, and not all of them document comment conventions.

When adding comments to code, focus on explaining **why** code works the way it does, not what changed.

Good comments explain:

- Complex logic or algorithms
- Non-obvious design decisions
- Business rules or constraints
- Purpose of functions/classes
- Edge cases being handled

Comments should help someone understand the code 6 months later, not track edit history.
