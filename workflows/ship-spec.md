---
id: 938BD461-A83C-4983-AD85-EFC89197882B
name: "Ship Spec"
icon: "checklist"
tooltip: "Walk a spec's ticket graph and ship it as one PR"
description: "Coordinate a spec's dependent tickets through Build It, verify completion, and open one PR on GitHub or GitLab."
---

# Ship Spec

Spec reference: $ARGUMENTS

You are the orchestrator of a spec: a tracker issue whose tickets form a **task graph** with blocking edges, produced by `to-spec`/`to-tickets` or written by hand. Your job is coordination — fetch the graph, walk it, dispatch, verify. Implementation happens inside child agents running the **Build It** workflow. The run ends with one PR that closes the spec.

Three words carry this workflow:

- **The frontier** — the open tickets whose blockers are all closed. Always computed fresh from the tracker, never from memory: the tracker is the source of truth for done/not-done, which is what makes a killed run resumable.
- **The notes issue** — a tracker issue this run owns: run state, research notes, the ticket→seam table, and the run ledger. You write it; children and future resumed runs read it.
- **A pause** — ask the user for a decision and wait before the dependent action. Continue independent work when the checkout is safe. Pause sites below cover decisions that evidence and existing authorization cannot settle.

Communicate with children through **context pointers**: ticket refs, the notes issue, and commit SHAs. Include the checkout, branch, confirmed seam, and ownership rules requested by each brief template. Children read acceptance criteria, research, and findings through the pointers.

---

## Phase 0: Name the session

```json
{"tool":"set_status","args":{"session_name":"SPEC #<spec>: <short title>"}}
```

`SPEC` uppercase and first, `#<spec>` from the spec issue, then a few words in the codebase's own terms. Set once; helper agents you dispatch later reuse this prefix (`SPEC #<spec> · Explore`, `SPEC #<spec> · Triage #<ticket>`, `SPEC #<spec> · Review`). Build It children name themselves (`BUILD #<ticket>: …`) — leave their Phase 0 alone.

---

## Phase 1: Intake

All tracker commands come from the _Tracker adapter_ section at the end of this document. Resolve the tracker first (`git remote get-url origin`), then:

1. **Fetch the spec and its tickets.** Read the spec body, enumerate its tickets, and for each ticket read: state, labels, acceptance criteria, blocking edges. Tickets labeled `HITL` or `ready-for-human` are **human tickets** — they gate the graph like any other but are worked by the user, never dispatched.
2. **Validate the graph.** Every blocking edge resolves to a ticket in the spec; no cycles. Investigate malformed references; pause if repair requires choosing dependencies or scope for the user.
3. **Resume check.** Read any linked notes issue titled `Notes: <spec title>`. Its _Run_ section distinguishes `active`, `interrupted`, and `complete` runs. A complete run reports its existing PR and any pending retrospective; it does not restart implementation. For an unfinished run, recover the branch, baseline, gates, Ledger, and user decisions with their recorded sources. Current user instructions take precedence. Verify recorded code commits for closed tickets are reachable on the remote spec branch; human tickets use recorded tracker completion evidence instead. Investigate discrepancies before pausing for an unresolved tracker/branch mismatch. Older notes without a Run section require reconstruction from the ledger, tracker, and branch evidence; pause if a required baseline or ownership fact cannot be recovered. Every resumed implementation completes steps 4–5 before dispatch. Recover any active ticket and its child before selecting a new ticket.
4. **Checkout and branch.** Inspect `git op=status` and refresh the remote default and spec refs. Preserve unrelated dirty work by using a clean isolated checkout when needed; keep any existing work for this spec in its current checkout while establishing ownership. Pause only if continuing would overwrite work or ownership remains unclear. The run uses one checkout and one writer at a time. Create `spec/<number>-<slug>` from the remote default branch, or adopt the recorded spec branch after checking that every commit above its merge-base with the remote default belongs to this spec or its verified ledger. Investigate unexplained commits before adopting. Record the checkout path, branch name, base SHA, baseline HEAD, and any pre-existing changes excluded from this run. Use the recorded branch and checkout in every child brief.
5. **Baseline and gates.** Preserve the original run baseline on resume. Check the current environment and record required gate commands, when they apply (per ticket or final integration), and unavailable services with evidence. Read the repo's tracker issue labeled `caveats` if one exists. Entries are checkable claims: an exemption requires a matching failure signature, including suites and count; investigate differences. **Green** means all applicable gates pass except evidenced baseline exceptions. Record results with commit SHA, command, environment, and outcome. Reuse results only when the tested content and environment still match, including any uncommitted changes; after changes, rerun affected checks and any repo-required gates. Run broader checks for integration risk, new failures, or explicit repo requirements. Newly failing gates require diagnosis, not a new exemption.

**Done when** the graph validates, the ticket table is complete, and the spec checkout, baseline, and gates are established. On resume, persist refreshed run metadata, repair missing shared context through Phase 2 as needed, then continue from the recorded phase.

---

## Phase 2: Shared context and seams

1. **Dispatch one explore agent** to research the codebase for the whole spec:

```json
{"tool":"agent_run","args":{
	"op":"start",
	"model_id":"explore",
	"session_name":"SPEC #<spec> · Explore",
	"message":"Read spec <ref> and its tickets via `gh`/`glab` first. In checkout <checkout> on branch <spec-branch>, map the codebase areas they touch: relevant modules, existing patterns to follow, gotchas. For each code ticket, propose the seam — the public boundary its tests should be written against. Return markdown: research notes, then a ticket→seam table."
}}
```

2. **Decide TDD per ticket.** A ticket delivering testable behaviour (logic, API, data flow — most tracer bullets by construction) is a **TDD ticket** and needs a seam. Config, tooling, docs, and pure visual polish tickets are exempt.
3. **Confirm the seams.** Review the proposals against the tickets and code, fix what's wrong, and proceed once settled. Resolve later child objections the same way and update the table before steering the child. Pause only when choosing a seam requires an unresolved product or architectural decision.
4. **Create or update the notes issue** on the tracker, titled `Notes: <spec title>` and linked from the spec, with these sections:

   - _Run_: state (`active`, `interrupted`, `complete`), current phase and active ticket/session, checkout, branch, base SHA, original baseline and exclusions, gate inventory and result evidence, PR URL, retrospective status/link or saved path.
   - _Research notes_: the explore output.
   - _Seams_: confirmed ticket→seam table with TDD/exempt/human classification.
   - _Ledger_: per-ticket status, correction count, commit SHAs, files changed, and verification evidence. Preserve existing entries on resume.
   - _Decisions_: user decisions with source references, including pause resolutions and mid-run steering.

Update phase and ticket state as work advances. Record a failure before selecting another ticket, and record decisions before taking the action they authorize.

**Done when** the notes issue contains the run metadata, shared context, and settled seams needed to dispatch the next ticket.

---

## Phase 3: Walk the frontier

One ticket in flight at a time. Children share the run checkout, so concurrent writers would race commits.

Repeat until every ticket is closed:

### 1. Compute the frontier

Query the tracker: open tickets whose blockers are all closed. Consult the notes Ledger and exclude failed tickets and their downstream subtrees from dispatch. A failed ticket stays excluded across resumes until a user decision authorizes retry or resolves its scope. Pick the next agent-workable ticket, preferring those that unblock the most others.

**Human tickets**: the moment one enters the frontier, tell the user — they can work it while you keep dispatching agent tickets. When the frontier holds *only* human tickets (or is empty while human tickets remain open), pause with `ask_user`; when the user reports done, confirm the ticket is closed on the tracker before recomputing. If the frontier is empty and open tickets remain, the graph is stuck — that's a pause with the blocked subtree named.

### 2. Dispatch a Build It child

Record the active ticket and its starting HEAD in the Ledger before dispatch; record the returned session id so a resumed run can recover the child.

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
> _(TDD tickets only:)_ Call the Skill tool with `tdd`. Follow it before you start. Build at this seam: `<seam>`. It's already confirmed — treat it as settled. If it looks wrong, stop and report back rather than choosing another one.
> Work in checkout `<checkout>` on branch `<spec-branch>`. Commit your work there as Build It directs. Pushing and PRs belong to the orchestrator.
> If you stop to report, leave your working tree exactly as it stands — the orchestrator owns any decision about uncommitted work.
> Read the Run section for applicable gates. Done when the ticket's acceptance criteria are implemented, applicable gates pass, and the work is committed. Report commit SHAs, files changed, and gate evidence.

Use `engineer` instead of `pair` when the ticket is small and its path is obvious from the ACs alone.

### 3. Sanity pass

When the child returns, verify its commits exist on the branch, applicable gates are green under Phase 1, and its file manifest matches the diff from the ticket's starting HEAD to the returned HEAD. Before another ticket starts, finish and commit the active ticket's work. If run-owned uncommitted changes remain after its correction budget is exhausted, preserve them and pause for a disposition; identifying their owner alone does not make the checkout ready. Record SHAs, files, and gate evidence in the Ledger.

For a sanity failure or unmet acceptance criterion from step 5, steer the same implementing child. Allow two correction attempts per ticket across both kinds of failure, recording each attempt before dispatch so resumes preserve the count. Every corrected result returns through steps 3–5, including pushing before verification. After the second unsuccessful correction, mark the ticket failed in the Ledger and comment its state on the ticket. Continue outside its downstream subtree only when no run-owned uncommitted changes remain and the applicable gates are green. If repair cannot restore that state within the correction budget, preserve the work and pause for a decision. A first test failure starts diagnosis; it does not itself require approval.

Two child-session mechanics:

- **A child that pauses with its own question**: answer with `agent_run op=respond` when an advertised option fits the evidence and existing authorization. If none fits, keep the child paused and steer with the needed instruction; use `ask_user` only for a decision the orchestrator cannot settle. Never select an inaccurate option just to advance the session.
- **A steer/wait handle can expire while its session is still alive.** On `Expired`, re-acquire via `agent_manage op=list_sessions` and steer the same session id — a live session keeps its context; re-dispatching a replacement loses it.

### 4. Push

Push the spec branch. A closed ticket must always point at commits that exist on the remote — push before anything closes.

### 5. Cold verification closes the ticket

```json
{"tool":"agent_run","args":{
	"op":"start",
	"model_id":"engineer",
	"session_name":"SPEC #<spec> · Triage #<ticket>",
	"message":"Read `~/.agents/skills/triage/SKILL.md` (or its Claude skills counterpart) and follow its verification process. Read ticket <ref> and notes issue <ref>. Implementation at <head SHA> is committed and pushed on branch <spec-branch> in checkout <checkout>. Verify all acceptance criteria are met at that commit. Close the ticket if everything checks out; report any unmet AC instead of closing."
}}
```

The verifier closes on pass, advancing the frontier. Unmet ACs enter the correction loop in step 3. The sanity pass checks mechanics; the independent verifier judges acceptance.

### 6. Bookkeeping

Update the notes-issue Ledger row (status, SHAs, files) and comment the commit SHAs on the closed ticket. Keep all child sessions — implementers and verifiers — until the end of Phase 4: the retrospective reads them and a later steer may need them. Then recompute the frontier.

**Done when** every ticket in the current spec is closed, with code commits pushed and human completion confirmed on the tracker. Failed or blocked work is an interrupted run requiring a user decision, not a completed spec. If the user changes scope, update the spec and graph before close-out; a partial PR must not claim to close an unmet spec.

---

## Phase 4: Close-out

1. **Cold review** of the whole branch catches cross-ticket drift. Run the applicable final integration gates, refresh the remote default ref, and record the review base (merge-base with that ref) and head SHAs. Give a fresh reader the exact range and the spec:

```json
{"tool":"agent_run","args":{
	"op":"start",
	"model_id":"design",
	"workflow_name":"Review",
	"session_name":"SPEC #<spec> · Review",
	"message":"Read spec <ref> and its tickets. Independently review the diff from <base SHA> to <head SHA> on branch <spec-branch> in checkout <checkout> for correctness and compliance with the spec.",
	"detach":true
}}
```

Supply authoritative requirements as pointers and let the reviewer form its own conclusions. Wait with `agent_run op=wait`.

2. **Triage and fix.** Read `~/.agents/skills/apply-review/SKILL.md` (or its Claude skills counterpart). Select orchestrated mode. Resolve unclear findings by steering the reviewer; assess conflicts with spec decisions using that skill's evidence rule. Apply accepted fixes, using narrow agents for behavioural or multi-file changes and direct edits for mechanical ones. Verify under the Phase-1 gate policy. Call the Skill tool with `commit-me`. Record fixes in a **Review fixes** Ledger row with SHAs, files, and validation evidence. Have the reviewer check changed behaviour and affected findings at the new head; reuse unaffected findings from the original review. Pause if a fix requires an unresolved architecture or scope decision that invalidates closed tickets. Before opening the PR, push and reconcile every commit in the PR range against the Ledger. Investigate unexplained commits, and pause if ownership cannot be established. Record the final reviewed head and confirm it matches the pushed PR head.

3. **Draft and open the PR.** Call the Skill tool with `draft-pr`. Invoke its draft-and-open branch; this workflow explicitly instructs opening the PR. Reuse an existing PR for this branch on resume. Tickets are already closed; only the completed spec uses the PR's `Closes` line. The user reviews the open PR on their own time; the run does not block here.

4. **Rollup.** Comment the rollup on the spec issue: per-ticket outcomes, failed/deferred work, review verdict table with held findings and one-line reasons. Then settle the caveats ledger: append any environment quirk this run diagnosed that it doesn't list (create the issue if the repo lacks one: `gh issue create --label caveats --title "Known caveats"`, pinned if permissions allow), each entry stating symptom, repro command, expected signature, and date — and prune entries whose quirk didn't reproduce when its gate ran this run.

5. **Retrospective** — always, and cold: the orchestrator grading itself is the one thing this workflow refuses everywhere else. Export your own transcript (`agent_manage op=extract_handoff`, `output_path` in a temp location outside the repo, `max_transcript_items` and `max_tool_args_characters` at their maximums). **Validate the export before dispatching**: it must show this run's pauses, dispatch briefs, and tracker queries as individual entries. A compacted or truncated export is not evidence — locate the provider's raw session transcript and pass both paths, or name the export-dark phases in the retro brief. Then dispatch a fresh agent whose brief is pointers only — this workflow file and the export(s):

> Read the Ship Spec workflow at `<workflow path>` and the run transcript at `<export path>`. Audit this run against the workflow's own contract: pauses honored, frontier computed from the tracker, briefs within the pointer-plus-envelope rule (see the intro), ledger complete. Report traps (where the wording steered behaviour wrong or nearly did, with turn references), clean areas, and proposed workflow edits.

Post the findings as a **retro issue in the skills repo**, resolved from this workflow's source clone remote and passed explicitly to the tracker command. One issue per run: title `Retro: Ship Spec — <project repo> — <date>`, labels `retro` and `ship-spec`, body opening with `Workflow: ship-spec | Repo: <owner>/<project-repo> | Spec: #<spec> | Session: <id> | Date: <date>` followed by the findings. Reuse an existing issue for this run. Leave it open for **Workflow Therapist** to process. If publication is unavailable, save the exact retro text to a durable local file outside the project repo and give the user its path and the failure reason. Record publication as pending; delivery need not wait for skills-repo access. Comment the retro link or pending status and saved path on the notes issue, set Run state to `complete`, record the PR URL, and close the notes issue. Delete temporary transcript exports only once the findings are preserved.

6. **Retain child sessions** for later PR feedback. Report the retained count in the final handoff; cleanup runs only when requested. Delete only temporary prompt exports owned by this run, preserving any pending retro artifact.

**Done when** the completed spec's PR is open at the final reviewed and validated head, the rollup is posted, and the notes issue is closed with the PR and retrospective outcome recorded. Pending retro publication is reported separately with its saved artifact; it does not turn a delivered spec back into an implementation task.

---

## If the user stops the run

Abort is a first-class exit:

1. Cancel running children (`agent_run op=cancel`).
2. Compare the checkout against the original Phase-1 baseline, exclusions, and Ledger. Include the active child's uncommitted changes when establishing which edits belong to this run.
3. Offer a patch-backed revert of this run's changes; revert only on confirmation and preserve pre-existing edits even when they share a file. Reverting work whose ticket already closed means reopening that ticket in the same breath.
4. Set Run state to `interrupted` and record the current phase, active ticket, correction count, and uncommitted work on the notes issue; leave it open. If stopped before notes creation, report that state directly to the user.

---

## Pause triggers

These have no phase home but pause all the same:

- Acceptance criteria or seam choices that remain ambiguous after checking the spec and code, and require a user decision
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
