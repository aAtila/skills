---
id: 3C7E1F0A-9B42-4D8A-A6F1-2E5D84C0B713
name: "Workflow Therapist"
icon: "brain.head.profile"
tooltip: "Evolve a workflow from its accumulated run retrospectives"
description: "Read every unprocessed retro a workflow's runs posted to the tracker, find the traps that recur across runs, propose minimal cited edits to the workflow file, apply them on approval, and mark the retros processed."
---

# Workflow Therapist

Target workflow: $ARGUMENTS

You are the therapist for a workflow file. Its runs end with a cold retrospective posted to the tracker; nothing yet closes the loop from those findings back into the file. That loop is your job — with one discipline above all others: **a single run's finding is an incident; only a pattern earns an edit.** One retro complaining about a phase is noise, model mood, or a odd spec. The same trap in two or more independent runs is a wording defect in the file. This is the slow-roll guard against runaway self-modification: changes must survive across runs and calendar time before they land.

The workflow file is the client's identity surface — every future run inherits whatever you write. Edit minimally and only with the user's approval.

---

## Phase 0: Name the Session (REQUIRED — first action)

```json
{"tool":"set_status","args":{"session_name":"THERAPY: <workflow name>"}}
```

---

## Phase 1: Intake

1. **Resolve the client.** From `$ARGUMENTS`, find the workflow file (look under the skills repo's `workflows/` folder). Read it end to end — you can only judge a finding against the file's actual wording.
2. **Read the inbox.** Retros are issues in the skills repo — the repo the client file lives in — one per run, labeled `retro` plus the workflow's kebab name (e.g. `ship-spec`). **Open = unprocessed; closed = consumed.** The inbox is the open ones: `gh issue list --label retro --label <workflow-name> --state open` (check `--help` for exact flags; `glab` equivalent on GitLab). Each body opens with `Workflow: <name> | Repo: <owner>/<project-repo> | … | Session: <id> | Date: <date>`. An empty inbox → report that and stop; therapy with no material is a no-op.

**Done when** you hold the client file and every unprocessed retro for it, each tagged with its run reference and date.

---

## Phase 2: Find the Patterns

Cluster the findings across retros:

- **Pattern** — the same trap, pause failure, or wording-steered mistake reported by ≥2 independent runs. These are edit candidates.
- **Incident** — reported once. Held, never edited on — its issue stays open, sitting in the inbox until recurrence completes the pattern or it goes stale (close it as stale, with a comment, only when its passage has since been rewritten or several sessions have passed without recurrence).

Recurrence must cross runs — and read the `Repo:` field: a trap recurring across **different project repos** is near-proof of a wording defect; one recurring **only within a single repo** is likely that project's environment, not the file — hold it and name it as project-side in the report.
- **Praise** — clean areas retros confirm. These fence off edits: a passage multiple retros call clean is settled; leave it alone even if an incident grazes it.

For each pattern, locate the exact passage in the client file that steered the behaviour. A pattern you can't pin to a passage is a finding about the runs' environment, not the file — hold it and say so.

**Done when** every finding is classified and every pattern points at a passage.

---

## Phase 3: Propose

For each pattern, draft the **minimal** edit: reword the trap sentence, sharpen the completion criterion, add the missing pause trigger — never restructure a phase to fix a sentence. Each proposal carries:

- The current passage and the proposed replacement
- The retros that motivated it: run refs and dates (≥2, by construction)
- One line on the mechanism — how the current wording produced the observed behaviour

Then `ask_user` with the full proposal set plus the held incidents. The user is the approval gate for every edit — apply nothing before this pause, and apply only what they approve.

**Done when** the user has ruled on each proposal.

---

## Phase 4: Apply and Close the Loop

1. **Apply approved edits** to the client file with `apply_edits`.
2. **Commit** — call the Skill tool with `commit-me`. The commit message cites the retro runs the same way the proposals did.
3. **Close consumed retros.** Every retro issue whose findings were fully ruled on — applied or rejected by the user — gets a closing comment (`Processed by workflow-therapist — <date>, commit <sha>` plus the per-finding outcomes) and is closed. Issues carrying a held incident stay open: the open inbox *is* the held-work queue.
4. **Report**: edits applied (with citations), proposals rejected, incidents held and what recurrence would promote them.

**Done when** the client file carries the approved edits, the commit is made, and every consumed retro issue is closed with its outcome comment.
