---
name: codex-orchestrate
description: Coordinate independent work with Codex subagents. Use for requests to orchestrate a task, run a team, or delegate parallel work in Codex, with personal model defaults for scouts and workers.
---

# Codex Orchestrate

Stay available to the user while delegating substantive, bounded assignments to subagents. Delegate when an assignment can progress alongside useful work by you or another agent; handle small or tightly coupled work directly.

Preserve any supplied plan's work-item identifiers, dependencies, and explicit execution order. Fill missing dispatch details without decomposing an already agreed plan again. A review request stays read-only; a chosen implementation workflow keeps its own completion requirements.

## Choose the role

Keep the coordinator on its current model and reasoning effort. Use these personal defaults for children unless the user specifies otherwise:

| Role | Model | Reasoning | Suitable assignment |
| --- | --- | --- | --- |
| Scout | `gpt-5.6-sol` | `low` | A narrow, read-only question: locate ownership, trace a path, find tests, or check an API fact. |
| Mechanical worker | `gpt-5.6-luna` | `max` | Bounded execution with the approach already decided: consistent call-site edits, fixture updates, or a specified transformation. |
| Worker | `gpt-5.6-sol` | `medium` | Scoped implementation that still needs local judgment. |
| Smart worker | `gpt-5.6-sol` | `high` | Difficult implementation, conflicting evidence, or ambiguity requiring deeper reasoning. |
| Advisor (optional) | `gpt-6-astra` | `high` | A bounded, read-only design or review question; retain useful decision context for related follow-ups. |

Luna's high effort does not make an ambiguous assignment mechanical. Resolve the behavior first. If a worker discovers an undecided contract or needs wider ownership, have it return the evidence and decision needed; clarify the brief or use a suitable role.

## Dispatch with enough context

Before dispatching, read [Codex tool mechanics](references/codex-tools.md). Check supported model settings and live capacity; disclose any necessary fallback. If subagent tools are unavailable, continue directly and say so.

Give each agent an outcome, workspace and relevant files, read-only scope or exclusive write ownership, dependencies, essential user constraints, applicable project instructions, and concrete completion criteria. Request a compact result with file evidence, checks actually run, and blockers.

When a child's model differs from its parent's, start it with fresh context; do not fork conversation history. For the same model, default to fresh context and fork only when prior reasoning materially helps. Fresh-context briefs must carry the decisions the child cannot see. See the tool reference for exact fork settings and inheritance constraints.

Reuse agents when their existing context helps closely related work. An Astra advisor may remain available throughout the current task: send related questions and new evidence to the same advisor instead of spawning a replacement. Persistence means continuing that child's own conversation, not repeatedly forking the coordinator. Create an advisor only for a concrete advisory question that can run alongside useful work; it is not a mandatory team member.

Make children leaves by default: **Complete this assignment directly. Do not spawn other agents; the parent's delegation instructions apply only to the parent.** Allow nested delegation only for a concrete subtask with an explicit scope and capacity budget.

## Coordinate the work

Dispatch independent assignments concurrently; verify prerequisites before dependent work. Track agent IDs, ownership, and outstanding results. Give each writable file one owner at a time, including shared tests and manifests; confirm a writer has stopped before transferring ownership.

Let agents send useful discoveries directly to named teammates, copying scope or dependency changes back to you. Resolve conflicting decisions and ownership centrally.

While children run, advance a distinct part of the task without duplicating their investigation. Keep the user informed of meaningful findings; wait when no useful independent work remains.

Keep permissions within the user's existing authorization. Route requests for new approval to the user and continue unaffected work; another agent cannot grant it.

## Finish the whole request

Inspect actual changes and evidence, integrate the results, and verify the combined behavior against the user's request. Continue corrections until complete or concretely blocked. Account for every assignment before ending and stop unnecessary running work. Report what was delivered, what was verified, and what remains untested or blocked.

## Basis

Adapted from Eric Provencher's [orchestrate skill](https://github.com/provencher/codex-skills/blob/main/orchestrate/SKILL.md) and the user's saved companion guide, with personal model preferences. Mechanics checked against the live Codex contract and [official subagent documentation](https://learn.chatgpt.com/docs/agent-configuration/subagents) on 2026-09-07.
