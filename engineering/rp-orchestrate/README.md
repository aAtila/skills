# Using RepoPrompt Orchestrate

Use this skill for substantial work that can be divided into independent investigations or edits. RepoPrompt manages context and child sessions; your configured execution provider runs the models. The coordinator stays in the app where you invoke the skill.

In a top-level RepoPrompt Agent Mode session, ask:

```text
Use rp-orchestrate to implement this plan.
```

From Codex with access to RepoPrompt CE's MCP tools or CLI:

```text
$rp-orchestrate Implement docs/plans/settings-save.md in
/absolute/path/to/project using RepoPrompt CE workers.
```

Replace the paths with your actual plan and checkout. The session must have permission to start child agents; a skill cannot grant that permission to a restricted child session.

## What it adds

- Your [model preferences](../orchestrate/SKILL.md#choose-the-role), including Sol low scouts, Luna max mechanical workers, and an optional persistent Astra advisor.
- Exact model selection from RepoPrompt's catalog, even when its role aliases point elsewhere.
- Fresh worker sessions, clear ownership, and verification of the combined result.
- Follow-up handling for completed sessions, pending questions, and blocked runs.

Keep the companion `orchestrate` skill installed. It supplies the coordination policy shared with `codex-orchestrate`; use the adapter matching where you want workers managed.

This is a lightweight skill. Choosing it does not automatically run the fuller Orchestrate (TDD) workflow. Small edits or strictly sequential work usually need no orchestration.

## Examples

### Investigate without editing

```text
Use rp-orchestrate to investigate why settings sometimes revert
after saving. Keep this read-only. Split the save path and test
coverage investigation where useful, and return an evidence-backed
cause, remaining uncertainty, and recommended fix.
```

### Execute an agreed plan

```text
Use rp-orchestrate to implement docs/plans/settings-save.md.
Preserve the plan's item IDs and dependencies. Verify the combined
behavior and complete the relevant checks.
```

### Apply a settled transformation

```text
Use rp-orchestrate to update callers under src/features to the
saveSettings({ values, revision }) contract established in
src/settings/save-settings.ts. Preserve caller behavior and update
affected fixtures. Report callers that need a design decision
before changing them.
```

### Keep an advisor through related decisions

```text
Use rp-orchestrate for this implementation. Ask an Astra advisor
to assess the open concurrency question while workers handle
independent items. Reuse that advisor as new evidence arrives.
```

Follow up naturally with an agreed correction. The coordinator retains session IDs and sends related work to the existing sessions. It checks actual changes and integration results before reporting completion.

The [skill](SKILL.md) defines the RepoPrompt workflow; the [tool reference](references/repoprompt-tools.md) covers connection, model resolution, and session controls.
