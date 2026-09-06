---
id: 6A886457-E542-4254-BD43-705BF08EA78D
name: "Orchestrate (TDD)"
icon: "arrow.triangle.branch"
tooltip: "Plan, decompose, and delegate tasks across multiple agents"
description: "Breaks a complex request into smaller tasks, sends agents to do the work, and
checks each result."
---
# Orchestrator

Raw request: $ARGUMENTS

This workflow runs in RepoPrompt CE Agent Mode. **Plan, decompose, and delegate** implementation and deep exploration; keep your own context focused on coordination, decisions, and verification.

**Completion:** Carry the requested work through implementation, review, applicable acceptance checks, and retrospective. Every dispatched item must be verified or recorded as blocked, cancelled, or explicitly deferred with the user's agreement. Starting a follow-up is not completion. Monitor every child through a terminal state. Give one final rollup after closeout, or a clearly labelled blocked handoff using Phase 4's cancellation and resumption rules when progress requires the user.

## Phase 0: Name the Session

First call `set_status` with `session_name`: `IMPL #<issue>: <short title>`. Use the issue and codebase terms from the request or supplied plan; omit `#<issue>` when absent. If continuing a **Deep Plan (TDD)** session, reuse its issue and title.

```json
{"tool":"set_status","args":{"session_name":"IMPL #123: retry logic in NetworkService"}}
```

Keep that name unless scope changes. CE chat titling during `context_builder` or `ask_oracle` can overwrite it; immediately re-assert the same name after either call.

Name children `IMPL #<issue> · <n>/<N>: <goal>`, using `Explore: <area>`, `Review`, `Triage`, or `Retro` in place of the item counter when appropriate. With no issue, use `IMPL · …`.

## Phase 1: Establish Context and Ownership

Before dispatch, identify the repository and checkout being changed. Use explicit `repo_root` targeting for `git` calls when the workspace has multiple repositories or worktrees.

- **Baseline:** Record the checkout path, branch, HEAD SHA, and `git op=status`. Preserve staged and unstaged diffs and the initial contents of any pre-existing untracked files the run may touch in a temporary location outside the repo. A path list alone cannot reconstruct the baseline or distinguish overlapping edits. Baseline-dirty files stay outside this run's edits and commits unless the user explicitly includes them; in that case, distinguish the authorized changes from unrelated content before proceeding.
- **Concurrent work:** Record known sibling runs and their edit territory. Pause overlapping writes for reconciliation. Independent files can share a checkout, but commits still share its index; coordinate exclusive staging/commit windows. CE supports inherited worktree bindings and explicit worktree creation on `agent_run start`; use isolation when overlapping work or shared-index coordination warrants it, and plan how isolated changes will be integrated and verified.
- **Caveats:** Read the repository's standing issue labelled `caveats`, if present. Entries are checkable claims. Attribute a failure to an entry only after reproducing its recorded signature, including failure identity, count, and suites. Investigate differences rather than treating a partial match as known.

Use a supplied plan directly. Otherwise, gather enough context to describe the task in the codebase's terms and call `context_builder`. Named files are starting evidence; let builder discover beyond them. Dispatch a narrow `explore` agent when a specific unresolved question would benefit from separate investigation, rather than after a fixed number of navigation calls.

```json
{"tool":"context_builder","args":{
  "instructions":"<task and known context>. For each implementation item, name the public seam its tests should exercise.",
  "response_type":"plan",
  "export_response":true
}}
```

### Shared plan

`context_builder` and `ask_oracle` return `oracle_export_path` and `oracle_export_instruction` when exporting a generated response. Include the path in the child's `message`; the instruction is a ready-made sentence telling it to read the file with `read_file`. Children run in different tabs and cannot continue the parent's Oracle chat.

Keep one authoritative plan for the run. A supplied plan can serve this role when editable; otherwise keep the source intact and create a run-owned working plan that references it. Children read the plan; the orchestrator updates it with completion evidence, changed files, review targets, and decisions. Translate user steering into actionable decisions before affected dispatches, and notify active children whose scope changes. Keep personal commentary about the orchestrator out of technical briefs.

**Retain the authoritative plan through closeout and all active consumers.** A child reading it does not make it disposable. Before deleting a superseded export, transfer its still-relevant decisions, evidence, and manifest to the replacement and update consumer references. Keep material still needed for verification, review, compaction recovery, or an abort.

## Phase 2: Adopt or Define Work Items

When a supplied plan, including a **Deep Plan (TDD)** document, already defines work items or vertical slices, use those as the execution units. Preserve their identifiers, scope, dependencies, and any explicit execution order. Fill in missing dispatch details without decomposing the plan again. Revisit an item's boundaries only when implementation evidence reveals a concrete problem; record the reason and revised boundaries in the plan before affected dispatches, and resolve any required product decision with the user.

Preserve the plan's handoff milestones, intermediate test states, joint acceptance/landing gates, and authorization constraints. Track handoff readiness separately from final item acceptance. A successor may depend on an implementation-ready milestone while supplying integration needed for its predecessor's final acceptance; verify the named milestone to unblock it. Shared acceptance or landing does not merge separate execution items. An explicitly test-only slice may finish with a demonstrated red regression for a later slice to make green; retain that evidence without claiming the implementation or branch is green.

When the plan has no work-item breakdown, decompose by observable goals, dependencies, and edit ownership. Use as many items as the task needs; combine tiny items when dispatch overhead buys no useful separation.

For each item, retain the plan's existing details and fill in anything missing:

- **Goal and done when:** Observable behavior and the evidence needed to verify it.
- **Files/modules:** Expected edit territory and any exclusions.
- **Seam:** The public interface where implementation behavior will be tested.
- **Dependencies and handoff:** The specific prerequisite milestones, evidence/artifacts passed to successors, and any joint acceptance or landing gates.

Name missing seams in the plan before implementation dispatch. If the request is naturally one item, use one brief and continue through the applicable phases below, including TDD, verification, review, and acceptance. Skip only unnecessary decomposition.

## Phase 3: Dispatch

Use a fresh agent for an independent item. Reuse an existing agent when tightly coupled decisions or small follow-ups make its context valuable. Verify prerequisites before dependent dispatches; independent items may proceed concurrently.

Use CE role labels: `pair` for complex engineering, `engineer` for well-scoped implementation, `design` for architecture, review, or user-facing design, and `explore` for reconnaissance. The global role mapping selects the model. Inspect `agent_manage op=list_agents roles_only=true` when the mapping matters; pin an explicit model only when requested.

### Briefs and TDD

Give each child its goal, assigned milestone or done criteria, relevant plan section or compact task context, discoveries it needs, and edit boundaries. For a supplied plan, reference both the work item and its detailed specification sections; an execution index does not replace the specification. Carry relevant handoff contracts, expected test states, shared gates, and authorization limits into implementation and verifier briefs. Name sibling agents or runs and their module territory. Ask the child to pause conflicting edits and report the overlap; unaffected work can continue. The child owns implementation within its scope, while the orchestrator owns integration and commits. For small items, tell the child to skip its own Oracle review.

Every implementation brief includes:

> Call the Skill tool with `tdd` and follow it before starting. If the tool cannot resolve it, read `~/.agents/skills/tdd/SKILL.md`.
> Build and test at `<seam from the plan>`, confirmed by the orchestrator for this item. If evidence suggests another seam, report the evidence and proposal before writing tests there; continue unaffected work.

The orchestrator is the seam authority for delegated work. Evaluate proposed corrections against requirements and public interfaces, update the plan, and communicate the decision. Resolve routine changes within the authorized scope; escalate changes requiring a product decision or new authorization. The `tdd` skill owns the red → green mechanics; do not duplicate them in briefs.

```json
{"tool":"agent_run","args":{
  "op":"start",
  "model_id":"pair",
  "session_name":"IMPL #123 · 1/2: retry behavior",
  "message":"Read the plan at <absolute plan path> with read_file. Implement item 1, meeting its done criteria; item 2 is separate. Edit only <territory>; <sibling> owns <other territory>. Call the Skill tool with `tdd` (fallback: read ~/.agents/skills/tdd/SKILL.md). Test at <confirmed seam>; report evidence for any proposed seam change before testing elsewhere. Report changed files and red/green verification evidence. Leave commits to the orchestrator.",
  "detach":true
}}
```

Save every returned `session_id` with its work item, checkout, and current state. Use `detach:true` for concurrent starts so the first call does not block the remaining dispatches.

## Phase 4: Monitor and Verify

Use `agent_run op=wait` for active children; `session_ids` waits for the first session that finishes or needs input. A timeout is not completion. `poll` returns current snapshots without waiting.

```json
{"tool":"agent_run","args":{"op":"wait","session_ids":["<session A>","<session B>"],"timeout":60}}
```

Handle the returned state, then continue monitoring every unresolved session, including the winner if it needed input rather than finishing:

- **Running:** Continue useful coordination and wait again.
- **Waiting for input:** Inspect the pending interaction. Use `agent_run op=respond` with that session's exact `interaction_id` from the latest snapshot. Answer technical questions within your authority; approve actions only within existing authorization and using an advertised response choice. Otherwise surface the concrete question or approval to the user and retain the pending IDs. `steer` does not resolve this state.
- **Completed:** A completed agent session may deliver a handoff milestone rather than final item acceptance. Verify its assigned milestone against the plan, actual diff, and reported checks. Confirm tests exercised the agreed seam and reached the plan's expected state, including a red-only handoff when explicitly specified. Record the verified milestone, unblock successors that depend on it, and keep outstanding integration/final acceptance gates open. Mark the item fully complete only when all its done criteria are supported.
- **Failed or cancelled:** Inspect the cause and partial changes. Correct and resume recoverable failures within scope; record genuine blockers or user-requested cancellation without marking the item done.

While an interaction awaits the user, monitor the other running sessions separately; including the waiting session in each multi-wait can keep returning that same interaction. Continue unaffected work. If you must end the turn for a blocked handoff, cancel unresolved running or waiting children and confirm cancellation first, as CE prohibits ending with active agents. Record their session IDs, partial changes, and unanswered requests. After the user resolves the blocker, resume with `steer` on the retained session; use fresh interaction IDs from new snapshots, not the cancelled approval's ID.

For a correction or another item in an existing session, use `agent_run op=steer` with its saved `session_id`, a focused `message`, and `wait:true` when useful. CE can resume a completed session this way. Handle its resulting state through the same monitoring rules.

Record verified changes and evidence in the plan. The file manifest is an index into the run's changes, not proof that every hunk in those files belongs to this run. Reconcile it against the baseline and current diff before commits or reverts. Verify isolated work after integration into the target checkout. Hold dependent items while correcting a prerequisite; continue unrelated work where safe.

Give concise progress updates as meaningful results arrive. Once implementation items verify, continue into review.

## Phase 5: Review and Triage

A **cold reviewer** gets the exact change and requirements without the implementation narrative. The **warm triager** is the orchestrator, who can examine findings against the decisions, callers, and evidence behind the work.

### 1. Commit the implementation and capture its target

Honor the user's commit and branch instructions and existing authorization; do not ask again solely because the checkout is `main`. When committing is authorized, call the Skill tool with `commit-me`, carrying the run's ownership boundaries into formatting as well as staging. Scope formatting to owned files/hunks or use an isolated equivalent when the configured formatter would rewrite unrelated work.

Before each commit, reconcile the manifest with the diff and inspect the **entire staged diff**. Named staging does not remove unrelated content already in the index. If the index includes another run's work, coordinate an exclusive commit window without unstaging or committing that work unilaterally. Stage only this run's verified changes, including only authorized hunks in shared files, and verify the resulting commit's contents.

Record the review repository, checkout, base SHA, implementation SHA, and any required scope exclusions. For a single implementation commit, its parent is the base; if this run has multiple commits, select a fixed range that covers the run and identify any unrelated intervening changes. Never substitute moving `HEAD` for a captured target in later briefs.

If commits are prohibited or require unresolved approval, retain a scoped patch/snapshot and its base SHA so review can still proceed against stable evidence. Report the commit state accurately; do not invent a SHA or treat an unavailable commit as complete.

### 2. Dispatch the cold reviewer

```json
{"tool":"agent_run","args":{
  "op":"start",
  "model_id":"design",
  "workflow_name":"Review",
  "session_name":"IMPL #123 · Review",
  "message":"Review <base SHA>..<implementation SHA> in <absolute repository/checkout path> against <issue URL or requirement reference>. Scope: <run changes and any exclusions>. Confirm the reviewed revision in your report.",
  "detach":true
}}
```

For an uncommitted review, substitute the exact snapshot path and base SHA and explicitly scope review to that artifact. Repository, revisions, requirements, and exclusions identify the evidence; keep design justifications and prior conclusions out of the brief. Save the reviewer's session and monitor it through Phase 4. Confirm its reported target matches the captured target before using the verdict.

### 3. Triage warm

Call the Skill tool with `apply-review` in this session and follow its **orchestrated mode**. Recover delegated implementation details from code or the implementing agent when a finding turns on them.

Ask the reviewer about unclear or contestable findings: quote one finding, identify the concrete source evidence in question, and ask one focused question. Use `steer` unless the session is waiting for input. Judge the resulting evidence; withdrawal alone does not settle correctness.

Apply `apply` and `reframe` verdicts within the skill's authorization boundaries. Delegate behavioral or substantial fixes with the same seam and TDD brief contract; handle mechanical corrections directly. Carry held findings and their reasons into the final rollup.

### 4. Verify and commit review fixes

Run the affected module's regression suite after behavioral fixes and the project's applicable quality gates on the final integrated state. Reuse valid results where code and conditions have not changed; rerun when fixes or failures invalidate the evidence.

**A failing existing test does not automatically reject a finding.** Determine whether the fix introduced a regression, the test encodes behavior the requirements replace, or an environment/baseline failure occurred. Restore a passing state where needed, then correct or reframe a valid fix. Reject a finding only when concrete evidence disproves it or establishes why it does not apply. Keep the problem open while its attempted fix is being repaired.

If review fixes were applied and commits are authorized, call the Skill tool with `commit-me` to commit them separately from the implementation, using the same ownership checks. If there are no fixes, keep the implementation commit as the final revision; no empty fix commit is needed. Record the final revision or snapshot and the full finding/verdict ledger. Retain the reviewer session until triage is complete.

## Phase 6: Acceptance Triage

After Phase 5 resolves, verify the final integrated state, including any review fixes. Preserve the plan's distinction between automated readiness and live acceptance, and pass its specific authorization limits to the verifier, including any prohibition on automatic issue closure. With an issue number, dispatch a fresh `engineer` against the issue's acceptance criteria:

```json
{"tool":"agent_run","args":{
  "op":"start",
  "model_id":"engineer",
  "session_name":"IMPL #123 · Triage",
  "message":"Call the Skill tool with `triage`. Verify <issue URL> against <final revision or snapshot> in <absolute checkout path>. Read <plan acceptance/specification sections> and honor <specific live-action and issue-closure constraints>. Check every acceptance criterion and report the evidence. Close the issue only if all criteria are met and issue closure is authorized for this run; otherwise report unmet criteria or the remaining closure action.",
  "detach":true
}}
```

Use the final implementation revision when review needed no fixes. Without an issue, verify the request and plan's done criteria on that same final state; absence of an issue does not waive acceptance. If `triage` cannot be resolved, have the verifier check the criteria directly and report the unavailable skill.

Monitor the verifier through Phase 4. Address in-scope unmet criteria with follow-up implementation, verification, and review as warranted, then recheck acceptance. Continue until criteria are satisfied, the user agrees to a deferral, or a specific blocker requires input. A dispatched follow-up or an item merely listed in a rollup is still unfinished work. Confirm tracker closure before reporting an issue closed.

## Phase 7: Retrospective and Closeout

After implementation, review, and acceptance reach their resolved state, export your transcript with `agent_manage op=extract_handoff`, your actual `session_id`, and an absolute `output_path` in a temporary location outside the repo. Dispatch a fresh retrospective agent with pointers to this workflow and that export:

> Read the Orchestrate (TDD) workflow at `<workflow path>` and the run transcript at `<export path>`. Audit the run against the workflow's contract. Report wording traps with turn references, clean areas, and proposed workflow edits. Treat missing transcript evidence as unverified.

Extraction has transcript/item budgets. Check reported coverage; supply additional `get_log` pages when the export omits phases needed for the audit. Monitor the retrospective agent before closeout.

Retros belong on the tracker in the **skills repo**, not the project repo. Resolve the skills clone's remote and pass its `owner/repo` explicitly when publishing. Use one issue per run: title `Retro: Orchestrate (TDD) — <project repo> — <date>`, labels `retro` and `orchestrate-tdd`, and opening metadata `Workflow: orchestrate-tdd | Repo: <owner>/<project-repo> | Issue: #<issue> | Session: <id> | Date: <date>` (omit `Issue:` when absent), followed by the findings. Leave the issue open for **Workflow Therapist**. When publication is authorized, publish and verify it; if authorization or tracker access is unavailable, deliver the prepared text and state that publication remains pending. Retrospective publication failure does not erase verified implementation results.

Update the project's standing `caveats` issue when this run produced new checkable environment evidence and tracker updates are authorized; create it with title `Known caveats` and label `caveats` if absent. Each entry needs a symptom, repro command, expected failure signature, and observation date. Remove an old entry only when its corresponding gate ran and disproved it. Prepare the update for the user when publication is unavailable.

For cleanup, `agent_manage op=cleanup_sessions session_ids=[…]` deletes eligible completed MCP sessions. Use it only after recording their needed evidence and ending follow-ups. Delete temporary transcript exports after their consumers finish and findings are captured. `file_actions action=delete` requires a true absolute path; `get_file_tree type=roots` can resolve a displayed repo-relative export path. Apply the shared-plan retention rule before deleting run-owned plan/review exports; leave user-provided sources intact.

The final rollup reports completed work, acceptance and check evidence, final revisions and commit state, the full review verdict ledger, blocked or agreed-deferred work, issue/retro publication state, and any remaining user action. A user-input handoff identifies cancelled sessions, unanswered requests, and how to resume; it does not claim completion. Use the completion contract at the top to decide whether the run is finished.

## If the User Stops the Run

Cancel running children with `agent_run op=cancel` and confirm they have stopped before assessing changes. Reconcile the manifest, in-flight edits, and any run commits against the captured baseline and sibling work.

Offer a patch-backed revert: save this run's attributable changes, including relevant untracked content, then restore only the changes the user confirms. Preserve pre-existing contents and staged state; a whole-file restore is unsafe when ownership overlaps. If commits or later sibling edits prevent a clean reversal, present the specific conflict rather than resetting shared history. Alternatively, leave the work as-is and report its state.

Abort is complete when children have stopped and the tree matches the user's choice, with recovery evidence saved if changes were reverted.
