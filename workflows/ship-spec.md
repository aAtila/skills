---
id: 938BD461-A83C-4983-AD85-EFC89197882B
name: "Ship Spec"
icon: "checklist"
tooltip: "Walk a spec's ticket graph and ship it as one PR"
description: "Ship a spec's ticket graph as one PR: walk the dependency frontier on GitHub or GitLab, dispatch each ticket through Build It, cold-verify and close tickets as they land, then cold-review the branch, open the PR, and post a run retrospective."
---

# Ship Spec

Spec reference: $ARGUMENTS

You are the orchestrator of a spec: a tracker issue whose tickets form a **task graph** with blocking edges, produced by `to-spec`/`to-tickets` or written by hand. Your job is coordination — fetch the graph, walk it, dispatch, verify. Implementation happens inside child agents running the **Build It** workflow. The run ends with one PR that closes the spec.

Three words carry this workflow:

- **The frontier** — the open tickets whose blockers are all closed. Always computed fresh from the tracker, never from memory: the tracker is the source of truth for done/not-done, which is what makes a killed run resumable.
- **The notes issue** — a tracker issue this run owns: research notes, the ticket→seam table, and the run ledger (per-ticket status, commit SHAs, file manifest). You write it; children and future resumed runs read it.
- **A pause** — stop, `ask_user`, idle until answered; resolve nothing marked _pause_ on your own. Pause sites are marked inline where they arise; the _Pause triggers_ list at the end holds the ones with no phase home. The user would rather be asked than surprised.

Communicate with children through **context pointers** — ticket refs, the notes issue, commit SHAs — plus the operational envelope a brief template explicitly asks for: branch, confirmed seam, scope and ownership rules. Never restate what a pointer already reaches — no acceptance criteria, research notes, or review findings copied into a brief; the template's inline seam is the one sanctioned duplication.

---

## Phase 0: Name the Session (REQUIRED — first action)

```json
{"tool":"set_status","args":{"session_name":"SPEC #<spec>: <short title>"}}
```

`SPEC` uppercase and first, `#<spec>` from the spec issue, then a few words in the codebase's own terms. Set once; helper agents you dispatch later reuse this prefix (`SPEC #<spec> · Explore`, `SPEC #<spec> · Triage #<ticket>`, `SPEC #<spec> · Review`). Build It children name themselves (`BUILD #<ticket>: …`) — leave their Phase 0 alone.

---

## Phase 1: Intake

All tracker commands come from the _Tracker adapter_ section at the end of this document. Resolve the tracker first (`git remote get-url origin`), then:

1. **Fetch the spec and its tickets.** Read the spec body, enumerate its tickets, and for each ticket read: state, labels, acceptance criteria, blocking edges. Tickets labeled `HITL` or `ready-for-human` are **human tickets** — they gate the graph like any other but are worked by the user, never dispatched.
2. **Validate the graph.** Every blocking edge resolves to a ticket in the spec; no cycles. A malformed graph is a pause.
3. **Resume check.** Look for a notes issue linked from the spec (titled `Notes: <spec title>`). Finding one means a previous run was interrupted: read its ledger and _Decisions_ section back (decisions bind this run as if the user just said them), verify integrity — every closed ticket's recorded commit SHA is reachable on the remote spec branch — then adopt the branch and skip to Phase 3. An integrity mismatch (ticket closed, commit missing) is a pause: tracker and branch disagree, the user decides.
4. **Baseline.** `git op=status`. A dirty working tree is a pause. The clean baseline is what the abort path diffs against. Record which quality gates are runnable in this environment (full suite, typecheck, lint; note suites needing unavailable services). That recorded list — not a child's judgment or yours — is what **green** means for every sanity pass and dispatch: unavailable-by-baseline suites don't block, newly-failing ones do.
5. **Spec branch.** The run lives on `spec/<number>-<slug>`, branched off the **remote** default branch — record that base SHA now; it goes into the notes issue when Phase 2 creates it. Already on a branch carrying the spec number → adopt it only after checking ancestry: every commit above the merge-base with the remote default branch must belong to this spec or a verified resume ledger; foreign commits would ship in the PR — that's a pause. Record the adopted name as the run's `<spec-branch>` and use it wherever later phases say `spec/<number>-<slug>`. Otherwise create and check it out.

**Done when** you hold the full ticket table (id, title, ACs, blockers, human/agent), the graph validates, and HEAD is on the spec branch.

---

## Phase 2: Shared Context and Seams

1. **Dispatch one explore agent** to research the codebase for the whole spec:

```json
{"tool":"agent_run","args":{
	"op":"start",
	"model_id":"explore",
	"session_name":"SPEC #<spec> · Explore",
	"message":"Read spec <ref> and its tickets via `gh`/`glab` first. Map the codebase areas they touch: relevant modules, existing patterns to follow, gotchas. For each code ticket, propose the seam — the public boundary its tests should be written against. Return markdown: research notes, then a ticket→seam table."
}}
```

2. **Decide TDD per ticket.** A ticket delivering testable behaviour (logic, API, data flow — most tracer bullets by construction) is a **TDD ticket** and needs a seam. Config, tooling, docs, and pure visual polish tickets are exempt.
3. **Confirm the seams.** You are the seam authority: review the explore agent's proposals against the tickets, fix what's wrong. A seam you can't settle is a pause.
4. **Create the notes issue** on the tracker: title `Notes: <spec title>`, linked from the spec, body with four sections — _Research notes_ (the explore output), _Seams_ (the confirmed ticket→seam table), _Ledger_ (one row per ticket: status · commit SHAs · files changed, all empty for now), _Decisions_ (empty for now). From here on the notes issue is the run's persistent memory — update the Ledger after every ticket, and append every pause resolution and mid-run user steer to _Decisions_ as it lands, so a resumed run can reconstruct everything — work and corrections — from the tracker alone.
5. **Seam-table checkpoint** — `ask_user`, showing the ticket→seam table and which tickets are TDD/exempt/human. This is the run's one scheduled pause; dispatch nothing until the user confirms.

**Done when** the notes issue exists with all four sections in place and the user has approved the seam table.

---

## Phase 3: Walk the Frontier

Strictly sequential: one ticket in flight at a time. Parallelism arrives with worktrees in a later version of this workflow — on a shared branch, concurrent children racing commits is the failure mode, so wide frontiers queue.

Repeat until every ticket is closed:

### 1. Compute the frontier

Query the tracker: open tickets whose blockers are all closed. Pick the next agent-workable ticket (prefer unblocking-heavy tickets — the ones the most others wait on).

**Human tickets**: the moment one enters the frontier, tell the user — they can work it while you keep dispatching agent tickets. When the frontier holds *only* human tickets (or is empty while human tickets remain open), pause with `ask_user`; when the user reports done, confirm the ticket is closed on the tracker before recomputing. If the frontier is empty and open tickets remain, the graph is stuck — that's a pause with the blocked subtree named.

### 2. Dispatch a Build It child

```json
{"tool":"agent_run","args":{
	"op":"start",
	"model_id":"pair",
	"workflow_name":"Build It",
	"message":"<brief>"
}}
```

The brief is pointers plus scope:

> Your task is ticket <ref> — read it first (`gh issue view <n>` / `glab issue view <n>`), including its acceptance criteria. Implement exactly that ticket; other tickets in the spec are handled separately.
> Fetch the notes issue <ref> the same way: research notes for context, the Ledger section for what previous tickets already landed.
> _(TDD tickets only:)_ Call the Skill tool with `tdd` and follow it before you start. Build at this seam: `<seam>`. It's already confirmed — treat it as settled. If it looks wrong, stop and report back rather than choosing another one.
> You are on branch `spec/<number>-<slug>` — commit your work there as Build It directs. Pushing and PRs belong to the orchestrator.
> If you stop to report, leave your working tree exactly as it stands — the orchestrator owns any decision about uncommitted work.
> Done when the ticket's acceptance criteria are implemented and committed. Report your commit SHAs and files changed.

Use `engineer` instead of `pair` when the ticket is small and its path is obvious from the ACs alone.

### 3. Sanity pass

When the child returns: new commits exist on the branch, the Phase-1 recorded gates are green, and the reported files-changed manifest matches `git op=diff`. Record SHAs and manifest in the Ledger. Gaps → steer the same child (it holds the context); after **two** failed corrections, the ticket is **failed** — comment the state of things on the ticket, and continue with frontier tickets outside its downstream subtree. Dispatch onto a green tree only: a red tree halts the loop (pause).

Two child-session mechanics:

- **A child that pauses with its own question**: answer with `agent_run op=respond` choosing one of its advertised options. If none matches the user's decision, pick the least destructive option, then immediately steer with the full instruction. A question whose default discards work always gets an explicit answer, never a skip or timeout.
- **A steer/wait handle can expire while its session is still alive.** On `Expired`, re-acquire via `agent_manage op=list_sessions` and steer the same session id — a live session keeps its context; re-dispatching a replacement loses it.

### 4. Push

Push the spec branch. A closed ticket must always point at commits that exist on the remote — push before anything closes.

### 5. Cold verification closes the ticket

```json
{"tool":"agent_run","args":{
	"op":"start",
	"model_id":"engineer",
	"session_name":"SPEC #<spec> · Triage #<ticket>",
	"message":"Load the `triage` skill. Ticket <ref> — implementation is committed and pushed on branch `spec/<number>-<slug>`. Verify all acceptance criteria are met. Close the ticket if everything checks out; report any unmet AC instead of closing."
}}
```

The verifier closes on pass — that is what advances the frontier (and on GitHub, native blocked-by unblocks dependents automatically). Unmet ACs go back to the implementing child as a steer, then re-verify. You grade nothing yourself: the sanity pass checks mechanics, the verifier judges the work.

### 6. Bookkeeping

Update the notes-issue Ledger row (status, SHAs, files) and comment the commit SHAs on the closed ticket. Keep all child sessions — implementers and verifiers — until the end of Phase 4: the retrospective reads them and a later steer may need them. Then recompute the frontier.

**Done when** every ticket in the spec is closed and pushed, or the remaining open tickets are failed/blocked and the user has been paused for a decision.

---

## Phase 4: Close-out

1. **Cold review** of the whole branch — cross-ticket drift is invisible to the per-ticket warm reviews inside Build It, so a fresh reader takes the whole diff:

```json
{"tool":"agent_run","args":{
	"op":"start",
	"model_id":"design",
	"workflow_name":"Review",
	"session_name":"SPEC #<spec> · Review",
	"message":"Review the changes on branch spec/<number>-<slug> against its merge-base with the default branch.",
	"detach":true
}}
```

Keep the brief to that sentence — naming decisions or constraints warms up the reviewer and defeats the cold read. Wait with `agent_run op=wait`.

2. **Warm triage in this session** — call the Skill tool with `apply-review` (orchestrated mode). Interrogate the reviewer by steering its session — one finding, one specific question per steer. Expect one false-positive class: the cold reviewer cannot see intent, so a finding that contradicts an explicit spec decision is a challenge to answer with the spec's own text, not a defect to fix — have the reviewer amend its saved report when it withdraws one. Apply accepted fixes (narrow fresh agents for behavioural or multi-file fixes; directly for mechanical ones), verify against the affected modules' full test suites, and commit them as their own commit (call the Skill tool with `commit-me`). Record review-fix commits in a **Review fixes** Ledger row (SHAs, files) as they land; before opening the PR, push the branch, then reconcile the Ledger against `origin/<default>..HEAD` — every commit in the PR range must be accounted for, and an unexplained one is a pause. An architectural finding that invalidates closed tickets is a pause.

3. **Draft and open the PR** — call the Skill tool with `draft-pr` (don't restate it), invoking its draft-and-open branch: this workflow's explicit instruction is to open. The branch name gives it the spec number for the `Closes` line (tickets are already closed — only the spec rides the PR). The user reviews the open PR on their own time; the run doesn't block here.

4. **Rollup.** Comment the rollup on the spec issue: per-ticket outcomes, failed/deferred work, review verdict table with held findings and one-line reasons.

5. **Retrospective** — always, and cold: the orchestrator grading itself is the one thing this workflow refuses everywhere else. Export your own transcript (`agent_manage op=extract_handoff`, `output_path` in a temp location outside the repo, `max_transcript_items` and `max_tool_args_characters` at their maximums). **Validate the export before dispatching**: it must show this run's pauses, dispatch briefs, and tracker queries as individual entries. A compacted or truncated export is not evidence — locate the provider's raw session transcript and pass both paths, or name the export-dark phases in the retro brief. Then dispatch a fresh agent whose brief is pointers only — this workflow file and the export(s):

> Read the Ship Spec workflow at `<workflow path>` and the run transcript at `<export path>`. Audit this run against the workflow's own contract: pauses honored, frontier computed from the tracker, briefs within the pointer-plus-envelope rule (see the intro), ledger complete. Report traps (where the wording steered behaviour wrong or nearly did, with turn references), clean areas, and proposed workflow edits.

Post the findings as a **retro issue in the skills repo** — the repo this workflow file lives in, not the project repo (resolve its `owner/repo` from the skills clone's remote and pass it explicitly, e.g. `gh issue create --repo <owner>/<skills-repo>`). One issue per run: title `Retro: Ship Spec — <project repo> — <date>`, labels `retro` and `ship-spec`, body opening with `Workflow: ship-spec | Repo: <owner>/<project-repo> | Spec: #<spec> | Session: <id> | Date: <date>` followed by the findings. Leave it **open** — open means unprocessed; the **Workflow Therapist** workflow closes it when its findings are consumed. If the skills repo is unreachable from this run (auth, host mismatch), that's a pause: hand the retro text to the user rather than dropping it or posting it into the project repo. Then close the notes issue and delete the transcript export — the notes issue stays about this run's work, and the sessions themselves stay disposable.

6. **Offer cleanup — never run it unprompted.** Final `ask_user`: "N child sessions from this run are still around — clean them up now, or leave them for a post-PR-review steer?" Default is leave them; the user can trigger cleanup later in one sentence. Also delete stale `prompt-exports/` files from this run.

**Done when** the PR is open, the notes issue is closed with the retro comment, and the rollup is posted.

---

## If the user stops the run

Abort is a first-class exit:

1. Cancel running children (`agent_run op=cancel`).
2. Diff against the Phase 1 baseline; the Ledger manifests scope exactly which files are this run's.
3. Offer a patch-backed revert of exactly those files; revert only on confirmation. Reverting work whose ticket already closed means reopening that ticket in the same breath — the tracker must not claim work the branch takes back.
4. Post the interruption state as a comment on the notes issue (leave it open) — the resume check in Phase 1 picks the run back up from there.

---

## Pause triggers

These have no phase home but pause all the same:

- Ambiguous or contradictory acceptance criteria on a ticket
- A child reporting its assigned seam looks wrong
- A failed ticket with no agent-workable frontier remaining
- Anything destructive or irreversible: force-push, data loss, deleting remote objects

Everything else — a flaky test, a missing file, an unclear module — you resolve yourself or by steering the child that owns the context.

---

## Tracker adapter

Resolve the tracker once from `git remote get-url origin` (github.com → GitHub, otherwise your GitLab host). Both CLIs are installed and authenticated; check `--help` for exact flags rather than trusting memory — the operations below are the contract, the commands are hints.

| Operation | GitHub (`gh`) | GitLab (`glab`) |
| --- | --- | --- |
| Read spec / ticket | `gh issue view <n> --json title,body,state,labels` | `glab issue view <n>` |
| Enumerate tickets | Sub-issues of the spec, via `gh api` GraphQL (`issue(number:N){ subIssues(first:50){ nodes{ number title state } } }`) | Task-list items in the spec description referencing issues (`- [ ] #12`) — parse the body |
| Blocking edges | Native blocked-by relationships via `gh api` (issue dependencies); fall back to a `Blocked by:` section in the ticket body | `Blocked by:` section in the ticket body (canonical — blocking links are Premium-only) |
| Ticket done? | `state == CLOSED` | `state == closed` |
| Create / edit notes issue | `gh issue create` / `gh issue edit <n> --body-file` | `glab issue create` / `glab issue update <n> --description` |
| Comment | `gh issue comment` | `glab issue note` |
| Open PR | `gh pr create --title … --body "Closes #<spec> …"` | `glab mr create --title … --description "Closes #<spec> …"` |

On either tracker, a `Blocked by:` body section always wins as fallback when native data is missing — specs written by `to-tickets` carry it by construction.
