---
id: 85A342DB-401C-4F47-9528-EA2AA00898F9
name: "Ship Spec (Seat)"
icon: "checklist.checked"
tooltip: "Ship a spec as one PR under an overseer seat"
description: "Under an r3call overseer seat: walk a spec's ticket graph in the seat's worktree through Build It, verify and close each ticket, review the branch twice, and open one PR on GitHub or GitLab."
---

# Ship Spec (Seat)

Spec reference: $ARGUMENTS

You orchestrate one spec: a tracker issue whose tickets form a **task graph** with blocking edges. Your job is coordination: fetch the graph, walk it, dispatch Build It children, verify each ticket, review the whole branch, and open one PR. Around the run, the seat owns the worktree, landing, the retro and retiring sessions.

Six words carry this workflow:

- **The seat** — the r3call overseer seat that started this lane and watches it. Its brief binds the run: **Where** names your worktree and branch, and its operational rules (gate commands, the DB lock, container cleanup, local gates standing in for CI, post attribution, the main checkout left alone) bind you and every child. A relayed instruction counts as Atila's when it quotes him. A notice that blocks nothing goes in the notes issue's *Run* section, followed by `agent_session_link op=request_attention`.
- **The frontier** — the open tickets whose blockers are all closed, computed fresh from the tracker every time. The tracker holds done and not-done, which is what makes a killed run resumable.
- **The notes issue** — `Notes: <spec title>`, linked from the spec: run state, research, seams, the Ledger and decisions. The run is its only writer; children and resumed runs read it, and the seat keeps a pointer to it.
- **A pause** — an `ask_user` question with your recommended option first, marked "(recommended)", and `timeout_seconds: 900`. Wait before the dependent action; independent work continues while the worktree is safe. The seat answers routine pauses and relays the rest to Atila. *Pauses*, near the end, lists every trigger.
- **The envelope** — what a child brief carries besides pointers: the task boundary, its refs (ticket, notes issue, spec), worktree, branch and SHA, the confirmed seam, role and ownership. Every child brief ends with the seat brief's operational rules, word for word, because a child inherits none of them. Criteria, research and findings reach children through the refs; a repair steer may name the failing criterion and point at its evidence.
- **A bounded wait** — every `agent_run op=wait` on a child or reviewer carries `timeout: 600`, and each return checks the session's last activity (`op=poll`). About 20 minutes silent is a **stall**: collect what the session finished, cancel it, and rerun the rest once in a fresh session. A second stall marks that work unavailable: a review axis unavailable, a ticket failed. An `Expired` handle means a live session: re-acquire it with `agent_manage op=list_sessions` and steer the same id, keeping its context.

## Phase 0: Name the session

The seat names this lane `SPEC #<spec>: <short title>`; if the name differs, set it once with `set_status`. Helpers reuse the prefix: `SPEC #<spec> · Explore`, `· Triage #<ticket>`, `· Review`, `· Standards`, `· Spec`. Build It children name themselves.

## Phase 1: Intake

Tracker commands come from the *Tracker adapter* at the end; resolve the tracker first (`git remote get-url origin`).

1. **Fetch the spec and its tickets.** For each ticket, read state, labels, acceptance criteria and blocking edges. Tickets labelled `HITL` or `ready-for-human` are **human tickets**: they gate the graph like any other, and Atila works them. A human ticket that accepts the integrated result (blocked by every code ticket, or with criteria that test the whole spec) is an **acceptance ticket**, worked in Phase 4 on the final head.
2. **Validate the graph.** Every blocking edge resolves to a ticket in the spec, with no cycles. Investigate malformed references; a repair that edits the spec is a pause, since the spec is Atila's.
3. **Resume check.** Read the notes issue if one is linked. A `complete` run reports its PR to the seat and stops. An `active` or `interrupted` run recovers the branch, baseline, gates, Ledger and decisions with their sources; a current instruction from Atila, direct or quoted by the seat, outranks the recorded ones. Recorded commits for closed code tickets must be reachable on the remote spec branch; human tickets use their recorded tracker evidence. Investigate discrepancies; pause on one you can't resolve, or on a baseline or ownership fact you can't recover. Recover the active ticket and its child first, and finish steps 4–5 before any dispatch.
4. **Adopt the worktree.** The seat created it, bound this session to it, and names it with the branch under **Where**. Refresh the remote default and spec refs, then check that `git op=status` shows that branch with a clean tree, and that every commit above its merge-base with the remote default belongs to this spec or its Ledger. Record the worktree path, branch, base SHA and baseline HEAD. A missing worktree, a wrong branch, a dirty tree or an unexplained commit is a pause; the seat fixes the checkout. If pushing needs Atila's direct consent (sandbox or auto-review), ask once now, for this branch and every later push to it, and record the consent in *Run*.
5. **Baseline and gates.** Take the gate commands, the DB lock and the CI stand-in from the seat's brief, and keep the original baseline on resume. Record each gate's scope (per ticket or final integration) and any unavailable service, with evidence. Read the repo's `caveats` issue if one exists: its entries are checkable claims, and an exemption needs a matching failure signature, suites and count included. Record the blocked, agent-ready and human-ready label names from the repo's triage-label doc (e.g. `docs/agents/triage-labels.md`). **Green** means every applicable gate passes except evidenced baseline exceptions. Record each result with commit SHA, command, environment and outcome, and reuse it only while the tested content (uncommitted changes included) and the environment still match. After a change, rerun the affected and repo-required gates, plus broader checks for integration risk. A newly failing gate needs diagnosis, never a new exemption.

**Done when** the graph validates, the ticket table is complete, and the worktree, baseline, gates, label names and push consent are recorded. On resume, persist the refreshed metadata, repair missing shared context through Phase 2, then continue from the recorded phase.

## Phase 2: Shared context and seams

1. **Dispatch one explore agent** for the whole spec, and collect it with a bounded wait:

```json
{"tool":"agent_run","args":{
	"op":"start",
	"model_id":"explore",
	"session_name":"SPEC #<spec> · Explore",
	"message":"Read spec <ref> and its tickets via `gh`/`glab` first. In worktree <worktree> on branch <spec-branch>, map the codebase areas they touch: relevant modules, existing patterns to follow, gotchas. For each code ticket, propose the seam: the public boundary its tests should be written against. Return markdown: research notes, then a ticket table with the columns seam, files touched, and stateful test resources (databases, ports)."
}}
```

2. **Decide TDD per ticket.** A ticket delivering testable behaviour (logic, API, data flow) is a **TDD ticket** and needs a seam. Config, tooling, docs and pure visual polish are exempt.
3. **Confirm the seams** against the tickets and code, and fix what's wrong. Settle later child objections the same way, updating the table before steering the child. A seam that hinges on a product or architecture choice the spec leaves open is a pause: the seat answers under its delegation or asks Atila.
4. **Create or update the notes issue,** linked from the spec, with these sections:
   - *Run*: state (`active`, `interrupted`, `complete`), phase, active ticket and session, worktree, branch, base SHA, baseline and exclusions, push consent, label names, gate inventory and result evidence, PR URL, and this run's IDs as separate fields: CE session ID, provider session or rollout ID, workspace ID, tab ID.
   - *Research notes*: the explore output.
   - *Seams*: the confirmed ticket table, each ticket classed TDD, exempt or human.
   - *Ledger*: one current row per ticket, rewritten after every event: status, start and final HEAD, every commit SHA, the exact file manifest, repair count, implementer and verifier session IDs, planning route, and pointers to criterion and gate evidence. History and the implementer's handoff notes sit below the row. Preserve existing rows on resume.
   - *Decisions*: each with its source: Atila directly, "Atila's words, relayed by the <seat>", or "the <seat>, under Atila's delegation". Pause answers and mid-run steering included.

Record a failure before selecting another ticket, and a decision before the action it authorizes.

**Done when** the notes issue holds the run metadata, shared context and settled seams the next dispatch needs.

## Phase 3: Walk the frontier

One ticket in flight at a time: children share the worktree, so concurrent writers would race commits. A *parallel group* (§1) is the only exception. Repeat until every ticket other than the acceptance tickets is closed:

### 1. Compute the frontier

Query the tracker, then exclude failed tickets and their downstream subtrees until a decision authorizes a retry. Pick the next agent-workable ticket, preferring the one that unblocks the most.

**Human tickets:** when one enters the frontier, send the seat a notice so Atila can work it, and keep dispatching; acceptance tickets wait for Phase 4. When the frontier holds only human tickets, or is empty while human tickets remain open, pause; once Atila reports one done, confirm it closed on the tracker before recomputing. An empty frontier with open tickets means the graph is stuck: pause, naming the blocked subtree.

**Parallel group:** frontier tickets with disjoint files touched, no shared stateful resource, and no pattern one would set for another (serial tickets reuse the first one's patterns; parallel ones invent their own). Pause once to propose the group; on yes, the seat creates and claims a worktree per ticket. Each child commits on `spec/<n>-<slug>/<ticket>` in its worktree. Integrate those branches into the spec branch one at a time, in frontier order, with the full gate after each; then push, verify and close. Suites on a shared resource run only on the integrated spec branch. Integration conflicts are yours to resolve.

### 2. Dispatch a Build It child

Record the active ticket and its starting HEAD in the Ledger before dispatch, then the returned session id. The child inherits this session's worktree binding. Use `engineer` instead of `pair` when the ticket is small and its path is obvious from the criteria alone.

```json
{"tool":"agent_run","args":{"op":"start","model_id":"pair","workflow_name":"Build It","message":"<brief>"}}
```

The brief is pointers plus the envelope:

> Your task is ticket <ref>: read it first (`gh issue view <n>` / `glab issue view <n>`), including its acceptance criteria. Implement exactly that ticket; the spec's other tickets are handled separately.
> Read notes issue <ref> the same way: research notes for context, the Ledger and earlier tickets' closing comments for what has landed.
> _(TDD tickets only:)_ Call the Skill tool with `tdd` and follow it. Build at this seam: `<seam>`. It is confirmed; if it looks wrong, stop and report.
> Work in worktree `<worktree>` on branch `<spec-branch>`. Commit there as Build It directs, each commit with `Refs #<ticket>`. Pushing, tracker writes and PRs belong to the orchestrator. If you stop to report, leave the working tree exactly as it stands. Write any ADR edit as a proposed amendment, marked as awaiting ratification.
> **Planning route.** `context_builder` can't read a worktree-bound session (`workspace_authority_superseded`); use it only if it returns real source (more than a handful of files). Otherwise read every file the ticket touches, plus the tests and docs that govern it, with your own `read_file`, `file_search`, `get_code_structure` and Bash against this worktree. Try `manage_selection op=set` with those files, skipping it if it fails, then plan with `ask_oracle`, mode `plan`, in a new chat, pasting load-bearing excerpts if the selection failed. When the Oracle asks for more source, gather it and continue in the same chat; stop only if it can't see source you've selected. The plan is done when it maps every acceptance criterion to code and a test; then continue with Build It's Phase 3.
> Read the notes issue's Run section for applicable gates. Done when the ticket's acceptance criteria are implemented, applicable gates pass, and the work is committed. Report commit SHAs, files changed, gate evidence, the planning route you used and any RepoPrompt tool that failed, and handoff notes: what later tickets need (patterns set, helpers added, gotchas).

### 3. Sanity pass

Collect the child with a bounded wait. Check that its commits are on the branch, applicable gates are green under Phase 1's policy, and its file manifest matches the diff from the ticket's starting HEAD to the returned HEAD. Record the SHAs, files, gate evidence, planning route and handoff notes in the Ledger. Finish and commit the active ticket's work before another starts.

**Repairs.** A sanity failure, or an unmet criterion from step 5, goes back to the same implementing child as a steer. One counter covers both: two repair attempts per ticket, each recorded before dispatch so a resume keeps the count. A planned TDD red, or a failure in the child's own throwaway tooling, is diagnosis and counts nothing. Every repaired result returns through steps 3–5. After a second failed repair, mark the ticket failed in the Ledger, comment its state on the ticket, and pause on it. Carry on outside its downstream subtree only while no run-owned change is uncommitted and the gates are green; otherwise preserve the work and pause for a disposition.

**Child pauses.** Answer with `agent_run op=respond` when an advertised option fits the evidence and the seat's brief. If none fits, keep the child paused and steer it with the needed instruction; a decision you can't settle becomes your own pause. Choose only an accurate option, even when a session is waiting.

### 4. Push

Push the spec branch before anything closes, so a closed ticket always points at commits on the remote.

### 5. Cold verification closes the ticket

Atila's standing yes lets this verifier close a ticket once it passes (overseer brief, 2026-10-24). Collect it with a bounded wait.

```json
{"tool":"agent_run","args":{
	"op":"start",
	"model_id":"engineer",
	"session_name":"SPEC #<spec> · Triage #<ticket>",
	"message":"Read `~/.agents/skills/triage/SKILL.md` and every file it points to, and follow its verification process. Read ticket <ref> and notes issue <ref>. Implementation at <head SHA> is committed and pushed on branch <spec-branch> in worktree <worktree>. Check every explicit acceptance criterion against the committed code at that commit, including criteria the baseline already appeared to meet, and link each to its evidence: the test that proves it, the code that implements it, or a command and its output. A green suite proves only what its tests assert. The notes issue's Run section records gate evidence by commit and environment: where it covers <head SHA> in an environment you can confirm matches, cite it instead of rerunning the broad gates. If every criterion passes, close the ticket with one comment: the per-criterion evidence, the ticket's commit SHAs, and the handoff notes from its Ledger entry. Otherwise leave it open and report each unmet criterion with its evidence."
}}
```

That closing comment is the ticket's one handoff comment. Unmet criteria go to step 3's repairs. The sanity pass checks mechanics; the verifier judges acceptance.

### 6. Bookkeeping

Rewrite the ticket's Ledger row. For each ticket this closure fully unblocks, swap the blocked label for the agent-ready one, or the human-ready one on a human ticket. Keep every child session: the seat's retro reads them, then the seat retires them. Then recompute the frontier.

**Done when** every ticket other than the acceptance tickets is closed, with code commits pushed and human completion confirmed on the tracker. Failed or blocked work leaves the run interrupted pending a decision. The spec body changes only by Atila's hand: a scope change is a pause, and close-out waits for the updated spec and graph, so the PR claims only what the spec now asks.

## Phase 4: Close-out

Review twice before opening the PR: first the whole branch, then a cold `code-review`. This phase is that rule's home.

1. **Integrate.** Run the final integration gates, refresh the remote default ref, and record the review base (the merge-base with `origin/<default>`) and head SHAs.
2. **First review: the whole branch.** A fresh reader catches cross-ticket drift. Give it the exact range and the spec as pointers, and collect it with a bounded wait:

```json
{"tool":"agent_run","args":{
	"op":"start",
	"model_id":"design",
	"workflow_name":"Review",
	"session_name":"SPEC #<spec> · Review",
	"message":"Read spec <ref> and its tickets. Independently review the diff from <base SHA> to <head SHA> on branch <spec-branch> in worktree <worktree> for correctness and compliance with the spec.",
	"detach":true
}}
```

3. **Triage and fix.** Read `~/.agents/skills/apply-review/SKILL.md` and every file it points to, and select orchestrated mode. Resolve unclear findings by steering the reviewer, and weigh conflicts with recorded decisions by that skill's evidence rule. Apply accepted fixes: narrow agents for behavioural or multi-file changes, direct edits for mechanical ones. Verify under Phase 1's gate policy, call the Skill tool with `commit-me`, and record the fixes in a **Review fixes** Ledger row with SHAs, files and validation evidence. Have the reviewer re-check changed behaviour and affected findings at the new head. A fix that would change a recorded decision or reopen a closed ticket is a pause.
4. **Second review: cold `code-review`.** Start two fresh sessions, one per axis (`· Standards`, `· Spec`), so neither depends on a sub-agent of its own. Give each only the branch, `origin/<default>` as the fixed point, and the spec plus any parent spec it implements (e.g. a capability spec):

   > Call the Skill tool with `code-review`; if the tool can't load it, read `~/.agents/skills/code-review/SKILL.md` and every file it points to, and follow them. Review branch <spec-branch> in worktree <worktree> against the fixed point `origin/<default>`; the spec is <ref> (parent spec: <ref>). Run only the **<axis>** axis: do the skill's steps 1–3, then carry out that axis's sub-agent brief yourself, in this session. Report its findings and what you accessed.

   Collect both with bounded waits, present them side by side as the skill's aggregate step does, then triage and fix them as in step 3.

   Each review records what it actually accessed: requirements, base and head, diff and path coverage, independent reproductions, and anything unavailable. Allow one bounded transport repair, then mark that portion unavailable. A partial verdict clears only what it covered.
5. **Reconcile and push.** Push, then match every commit in the PR range one to one against the Ledger and Review fixes rows. Investigate unexplained commits, and pause if ownership can't be established. Confirm the final reviewed head is the pushed head.
6. **Open the PR.** Call the Skill tool with `deploy-check` on the range and put its verdict in the PR body. While CI can't run, the seat brief's local gates stand in: run them on the exact head and record the commands, results and head SHA in the body. Then call the Skill tool with `draft-pr` and take its draft-and-open branch; this workflow instructs opening the PR. Reuse an existing PR for this branch on resume.
   - The body references each ticket with `Refs #<ticket>`. It uses `Closes #<spec>` only when nothing on the spec remains after merge; otherwise `Refs #<spec>`, listing the post-merge steps (deploy-dependent records, acceptance after deploy).
   - It carries both reviews' findings with their dispositions and coverage, and the decisions made under the seat's delegation, for Atila's veto.
   - Wait until GitHub lists the PR's checks and linked issues before reading them.
7. **Acceptance tickets.** Pause for each one on the pushed PR head, with the fixtures and recipes its criteria ask for. A later fix changes the head: rerun the affected checks, push, and ask again.
8. **Rollup and caveats.** Comment a short rollup on the spec: the PR link, failed or deferred work, and *proposed* spec-body edits (Out of Scope candidates included) for Atila. Then settle the repo's caveats ledger (create it if missing: `gh issue create --label caveats --title "Known caveats"`): append each environment quirk this run diagnosed with its symptom, repro command, expected signature and date, and prune entries whose quirk didn't reproduce when its gate ran.
9. **Hand back.** Set *Run* to `complete` with the PR URL and final head, leaving the notes issue open for the seat's retro lane. Report to the seat: the PR URL, head and gate evidence, both reviews' findings and coverage (naming any portion marked unavailable) and what you did with each, the pauses and their answers, and anything refused or deferred.

**Done when** the PR is open at the final reviewed and pushed head, the rollup is posted, *Run* reads `complete`, and the seat has your report. Landing, the retro and retiring the sessions follow the run; all three are the seat's.

## If the run is stopped

A stop comes from Atila, or from the seat relaying him. Abort is a first-class exit:

1. Cancel running children (`agent_run op=cancel`).
2. Compare the worktree against the Phase 1 baseline, exclusions and Ledger, counting the active child's uncommitted changes as this run's.
3. Offer a patch-backed revert of this run's changes, preserving pre-existing edits even in a shared file. The revert, and reopening any closed ticket it undoes, wait for Atila's direct yes.
4. Set *Run* to `interrupted` with the phase, active ticket, repair count and uncommitted work, and leave the notes issue open. Stopped before the notes issue exists: report that state to the seat directly.

## Pauses

The one list of pause triggers:

- A gate check still failing after two repair attempts (Phase 3 §3).
- A choice between behaviours that the spec, the code and the seat's brief leave open: acceptance criteria, seams, product or architecture.
- Any edit to the spec: a graph repair, a scope change.
- A worktree that doesn't match the seat's brief.
- A frontier holding only human tickets, or a stuck graph.
- A review fix that would change a recorded decision or reopen a closed ticket.
- Anything destructive or irreversible (force-push, history rewrite, data loss, deleting remote objects), a merge, or production access. These need Atila himself; the seat relays them.

A pause that times out leaves the run interrupted: silence is neither consent nor cancellation. Record the question, its options and evidence in the notes issue, set *Run* to `interrupted` with the open decisions and the next safe step, and keep the pushed work and the worktree as they are. Record each cleanup step only after its result returns.

Everything else (a flaky test, a missing file, an unclear module) you resolve yourself, or by steering the child that holds the context.

## Tracker adapter

Resolve the tracker once from `git remote get-url origin` (github.com → GitHub, otherwise your GitLab host). Check `--help` for exact flags: the operations are the contract, the commands are hints. Every comment opens with the seat brief's attribution prefix, `**<Name> (<model-id>)** — `.

| Operation | GitHub (`gh`) | GitLab (`glab`) |
| --- | --- | --- |
| Read spec / ticket | `gh issue view <n> --json title,body,state,labels` | `glab issue view <n>` |
| Enumerate tickets | Sub-issues of the spec, via `gh api` GraphQL (`issue(number:N){ subIssues(first:50){ nodes{ number title state } } }`) | Task-list items in the spec description referencing issues (`- [ ] #12`); parse the body |
| Blocking edges | Native blocked-by relationships via `gh api` (issue dependencies); fall back to a `Blocked by:` section in the ticket body | `Blocked by:` section in the ticket body (canonical: blocking links are Premium-only) |
| Ticket done? | `state == CLOSED` | `state == closed` |
| Create / edit notes issue | `gh issue create` / `gh issue edit <n> --body-file` | `glab issue create` / `glab issue update <n> --description` |
| Comment | `gh issue comment` | `glab issue note` |
| Open PR | `gh pr create --title … --body "<Closes\|Refs> #<spec> …"` (Phase 4 §6) | `glab mr create --title … --description "<Closes\|Refs> #<spec> …"` |

On either tracker, a `Blocked by:` body section is the fallback when native data is missing; specs written by `to-tickets` carry it by construction.
