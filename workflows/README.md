# Workflows

RepoPrompt loads workflows from its own application-support directory, not from this repo:

```
~/Library/Application Support/RepoPrompt CE/Workflows/
```

A workflow only runs from there. A file edited here and left uncopied changes nothing.

Two application-support directories exist — `RepoPrompt` and `RepoPrompt CE`. **CE is the live one**; the other holds a stale copy that tab-completion will offer first.

## Symlink each workflow into the live directory

```sh
  ln -sf /Users/atilaalacan/CODE/SKILLS/aAtila/skills/workflows/orchestrate-tdd.md \
    ~/Library/Application\ Support/RepoPrompt\ CE/Workflows/orchestrate-tdd.md
```

Now the repo file _is_ the live workflow: edits take effect on the next run, and every change is versioned by construction.

Copying instead leaves two files that drift. When `orchestrate-tdd.md` produced a surprising run, the first question was which copy had executed — answerable only by comparing the live file's mtime against the run's start time and the repo's commit timestamps. A symlink makes the question unaskable.

Keep the filename and the frontmatter `id` and `name` matching the live entry. RepoPrompt keys workflows on `id`; a fresh one registers a second, competing workflow in the picker.

**Verify after linking**: restart RepoPrompt and confirm the workflow still appears in the picker (`agent_manage op=list_workflows`). If it doesn't, RepoPrompt isn't following symlinks in that directory — `cp` the file back and sync by hand.

## Built-in workflows are read-only — clone to customize

Deep Plan, Review, Orchestrate, Optimize, Refactor, and Investigate ship with RepoPrompt and can't be edited in place. Customizing one means cloning it: the clone lands in the live directory as an ordinary file with a fresh `id`, and from there it's yours to edit, rename, and symlink back here.

`orchestrate-tdd.md` is a clone of built-in Orchestrate — it arrived named `Orchestrate (Clone)` and was renamed after. The original stays untouched and still appears in the picker alongside it.

## Workflows still living only in the live directory

`autoloop.md`, `catch-up.md`, `doc-sync.md`, `onboarding.md`, and `worktree-orchestrate-custom.md` are unversioned. Bring one into the repo and symlink it before editing it.

## Auditing a run

A finished run is stored as one JSON file per session:

```
~/Library/Application Support/RepoPrompt CE/Workspaces/Workspace-<name>-<uuid>/AgentSessions/AgentSession-<session-id>.json
```

Read that file when you need ground truth. The `history` MCP tool indexes tool _summaries_ only — never arguments or results — so searching a session for a tool name returns nothing even when the call was made. A zero-match search reads exactly like absence, which is how the #191 audit first concluded the closing `ask_oracle` review had been skipped; the session JSON showed it running 2,536s into a 2,672s run. Grep the JSON before believing a negative.

Orchestrate's housekeeping dismisses sub-agent sessions once their output is recorded, and dismissal deletes their files. Since a sub-agent's first message _is_ its dispatch brief, that's the record of what each agent was actually told — gone. Skip the cleanup on a run you intend to audit.

## Plans arrive from a workflow you can't edit

Deep Plan is built in, so its work-item convention — `Goal` / `Done when` / `Key files` / `Dependencies` / `Size` — is fixed, and **Seam** isn't in it. Orchestrate closes that gap in Phase 2 by naming the missing seam itself and writing it into the plan file. That fallback is the primary path, not a safety net: expect every deep-planned plan to arrive seamless.
