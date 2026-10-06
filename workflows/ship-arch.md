---
id: 5DB85E60-8C74-477B-8D5B-07328F9A100C
name: "Ship Arch"
icon: "building.columns"
tooltip: "Triage and implement an architecture-review audit issue"
description: "Consumes an architecture-review audit issue: oracle triages and orders the
candidates, each survivor is planned, TDD-implemented, cold-reviewed, and committed in
sequence with a revalidation gate between candidates, then the branch ships as one PR."
---
# Ship Arch

Raw request: $ARGUMENTS

You are an orchestrator consuming one **audit issue** — an `architecture-review`-labeled tracker issue produced by the `improve-codebase-architecture-to-issue` skill: a checklist at the top, a top-recommendation callout, and one `## C<n>` section per deepening candidate. This run triages its candidates, implements the worthwhile ones in sequence, and closes the issue. The issue is the run's only memory: every phase transition lands on it as a comment or checklist edit, so a resumed run reconstructs everything from the tracker alone.

**Oracle is the judge; you are the clerk and dispatcher.** Whether a candidate is addressed at all, in what order, and whether the next one is still worth it after the last one landed — those calls are oracle's. You record its verdicts on the issue and act on them.

## Phase 0: Name the session (REQUIRED — first action)

Call `set_status` with `ARCH #<issue>: <short title>` (issue number from `$ARGUMENTS` when present; resolve it in Phase 1 otherwise and set the name then). Children use `ARCH #<issue> · <n>/<N>: <candidate name>`. Any call that titles a chat — `context_builder` or `ask_oracle` — renames this session to that title: re-assert the byte-identical name straight after each one.

## Phase 1: Intake

1. **Resolve the audit issue.** `$ARGUMENTS` names it; otherwise list open `architecture-review` issues (`gh issue list --label architecture-review --state open` / `glab` equivalent). Exactly one → take it. Zero or several without an explicit number → ask the user, don't guess. Read the full issue body and all comments.
2. **Resume check.** Run comments already on the issue (triage verdict, per-candidate ledger comments) mean an interrupted run: reconstruct state from them, verify every recorded commit SHA is reachable on the run's branch, adopt that branch, and continue from the next unresolved candidate. A recorded SHA missing from the branch is a pause: tracker and branch disagree, the user decides.
3. **Baseline.** `git op=status` — a dirty tree is a pause. Read the repo's **caveats ledger** (standing tracker issue labeled `caveats`, one per repo) if it exists; its entries are checkable claims, not standing facts — attributing a later failure to one requires an exact signature match, and a partial match is a diff to investigate. The recorded gates list is what **green** means for every check in this run.
4. **Branch.** Create `arch/<issue>-<slug>` off the remote default branch and check it out (unless the resume check adopted one).

**Done when** the audit issue is loaded, the baseline recorded, and the run branch checked out.

## Phase 2: Oracle triage

1. Build context: `context_builder` over the union of files named by all candidate sections (`response_type` omitted — context only). Re-assert the session name.
2. Ask oracle (`ask_oracle mode=review`, continuing the builder chat) to judge the candidate set:
   - **Validate** each candidate: still real against the actual code, worth the change?
   - **Order** the survivors by dependency and supersession — a candidate that makes another easier (or moot) goes first (or kills it).
   - **Cap** the run: pick the top 1–3 that form a coherent arc for one PR; the rest stay pending for a future run.
   Oracle selecting **nothing** is a valid verdict: comment it on the issue and end the run — no branch push, no PR.
3. Record the verdict on the issue:
   - Append an `## Oracle triage` section to the body: the ordered selection with one-line justifications.
   - Checklist edits: rejected candidates become `~~C<n>: <name>~~ — rejected: <one-line reason>`; deferred ones stay pending with `— deferred to a future run`.
   - Post the full triage as a comment (the chronological ledger starts here).
4. **ADR offers.** A rejection whose reason is durable (would be needed by a future audit to avoid re-proposing the same candidate) gets an ADR in the project repo's `docs/adr/`; ephemeral reasons ("superseded by C2", "not now") get only the comment.

**Done when** the issue carries the triage section, the checklist reflects every verdict, and the selection (possibly empty) is commented.

## Phase 3: Candidate loop

Work the selection strictly in oracle's order. For each candidate:

### a. Revalidation gate (skipped for the first candidate)

The previous candidate changed the codebase the remaining ones were judged against. Ask oracle to re-judge the next candidate — and the remaining order — before spending anything on it. Oracle has full authority: **proceed**, **reorder** the remainder, **drop** this candidate, or **stop the run** ("what's left is no longer worth it"). Record the call as an issue comment; a drop also strikes the checklist item (`~~…~~ — dropped: <reason>`), a stop sends the run to Phase 4 with whatever has landed.

### b. Just-in-time plan

`ask_oracle mode=plan, export_response: true` for this one candidate, against the codebase as it now stands. The plan must name the **seam** — the public boundary the candidate's tests are written against — and a concrete **done-when**. Re-assert the session name after the call.

### c. Dispatch a fresh TDD implementer

One fresh `pair` agent, session `ARCH #<issue> · <n>/<N>: <candidate name>`. The brief is pointers plus the operational envelope — plan export path, audit issue ref, scope boundary ("this candidate only; the rest of the issue is handled separately") — and carries the two TDD lines verbatim:

> Call the Skill tool with `tdd` and follow it before you start (fallback if the Skill tool lacks it: read `~/.agents/skills/tdd/SKILL.md`).
> Build at this seam: `<seam from the plan>`. It's already confirmed — treat it as settled. If it looks wrong, stop and tell me rather than choosing another one.

Verify the result against the plan's done-when before anything else, then commit the implementation — call the Skill tool with `commit-me`, staging exactly this candidate's files, message ending `Refs #<issue>`.

### d. Cold pass: review and grade in one

Dispatch one cold reviewer (`design` role, `workflow_name: "Review"`), brief kept to one sentence plus the grading mandate — the diff and the repo are its entire input; naming your decisions warms it up and defeats the cold read:

> Review the recently committed changes for candidate C<n> of issue #<issue>. Besides the code review, grade the implementation against that candidate's stated problem, solution, and done-when — does it achieve the goal?

Triage the findings **warm, in this session** — read `~/.agents/skills/apply-review/SKILL.md` (or its Claude skills counterpart) and follow its orchestrated mode. Interrogate the reviewer by steering its session for anything contestable, one finding per steer. Verify applied fixes against the affected module's full test suite (a cold fix is the change most likely to break a contract the reviewer never saw), then commit them as their own commit via `commit-me`, `Refs #<issue>` — separate from the implementation commit so a bad fix reverts alone.

### e. Settle the candidate

- **Pass** (review clean or all fixes landed, done-when met): tick the checklist item — `- [x] C<n>: <name> — landed <sha(s)>` — and comment the SHAs and verdict table on the issue.
- **Fail twice** (two cold passes and the implementation still doesn't meet the goal): revert this candidate's commits, mark the checklist item `— blocked: <reason>`, comment the findings, and move on. A blocked candidate never holds the run hostage; the next audit re-surfaces it if it's still real.

Dismiss the implementer session once recorded (`agent_manage op=cleanup_sessions`); keep the reviewer until its triage is done. Delete consumed plan exports. Then loop to (a) for the next candidate.

**Done when** every selected candidate is landed, dropped, or blocked — each with its ledger comment on the issue.

## Phase 4: Ship and close

Runs only if at least one candidate landed; otherwise skip to the rollup comment and retro.

1. **PR.** Push the branch; call the Skill tool with `draft-pr` and tell it explicitly to open the PR. Body references the audit issue with `Refs #<issue>` — never `Closes`; the verifier closes it deliberately.
2. **Cold verifier.** Dispatch a fresh `engineer` agent: "Read `~/.agents/skills/triage/SKILL.md` (or its Claude skills counterpart) and follow it. Audit issue #<issue> — the selected candidates are implemented and the PR is open at <url>. Verify each landed candidate against its section's goal and the checklist state; close the issue with a rollup comment if everything checks out, report any gap instead of closing." Unmet gaps come back to you: follow-up dispatch or user escalation, your call by size.
3. **Rollup to the user**: per-candidate outcomes (landed/rejected/dropped/blocked with reasons), the PR link, held review findings.
4. **Caveats ledger.** Append any environment quirk this run diagnosed that the ledger doesn't list (create the issue if the repo lacks one: `gh issue create --label caveats --title "Known caveats"`); each entry states symptom, repro command, expected signature, and date. Prune entries whose quirk didn't reproduce when its gate ran this run.
5. **Retrospective — always, and cold.** Export your transcript (`agent_manage op=extract_handoff`, `output_path` in a temp location outside the repo). Dispatch a fresh agent whose brief is pointers only — this workflow file and the export:

   > Read the Ship Arch workflow at `<workflow path>` and the run transcript at `<export path>`. Audit this run against the workflow's own contract: oracle's authority respected (triage, revalidation gates, order), the issue's checklist and comments kept current at every transition, briefs pointer-only, cold reviews kept cold, blocked candidates reverted cleanly. Report traps (where the wording steered behaviour wrong or nearly did, with turn references), clean areas, and proposed workflow edits.

   Post the findings as a retro issue **in the skills repo** (resolve `owner/repo` from the skills clone's remote, pass `--repo` explicitly): title `Retro: Ship Arch — <project repo> — <date>`, labels `retro` and `ship-arch`, body opening `Workflow: ship-arch | Repo: <owner>/<project-repo> | Issue: #<issue> | Session: <id> | Date: <date>`. Leave it open — the Workflow Therapist closes it. Skills repo unreachable → hand the retro text to the user. Then delete the transcript export.

**Done when** the PR is open, the audit issue is closed (or its gaps surfaced), the rollup is posted, and the retro issue is open in the skills repo.

## If the user stops the run

1. Cancel running children (`agent_run op=cancel`).
2. Diff against the baseline; separate this run's commits and in-flight edits from baseline-dirty files.
3. Offer a patch-backed revert of this run's uncommitted changes; landed commits stay on the branch.
4. Post the interruption state as a comment on the audit issue (leave it open) — Phase 1's resume check picks the run back up from there.
