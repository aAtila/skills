# Using Codex Orchestrate

Use this skill when a substantial task has independent parts that can progress in parallel. The coordinator divides the work, keeps track of dependencies, and verifies the combined result.

```text
$codex-orchestrate <task>
```

Your model preferences are built in, so you do not need to repeat them. See [Choose the role](../orchestrate/SKILL.md#choose-the-role) for the model defaults and assignment criteria. The coordinator keeps its current model and reasoning effort. Keep the companion `orchestrate` skill installed; it supplies the coordination policy shared with `rp-orchestrate`.

## When to use it

| Task | Useful division of work |
| --- | --- |
| Investigate an unfamiliar feature or bug | Scouts trace separate code paths, tests, and dependencies. |
| Implement an agreed plan | Workers take independent items as their prerequisites become ready. |
| Apply a settled change across many callers | Mechanical workers update separate groups of files to the agreed pattern. |
| Build a feature across distinct modules | Workers own separate files after shared interfaces are settled. |
| Review several independent concerns | Read-only agents investigate separate questions and return evidence. |

Handle a small edit, a single tightly coupled problem, or a strictly sequential task directly. Each agent needs context and coordination; more agents do not automatically make a task faster or cheaper.

## Give it a useful brief

Name the outcome, scope, settled decisions, and what counts as done. Include the plan or relevant files if you already know them. Let the coordinator choose the number of agents and assign ownership.

```text
$codex-orchestrate <outcome>.
Scope: <files, modules, or plan>.
Already decided: <behavior or approach>.
Done when: <observable result and relevant checks>.
```

Resolve ambiguous behavior before assigning mechanical work. “Update these callers to this agreed contract” is a bounded assignment. “Decide what our new API should be” still needs design judgment.

## Examples

Replace the example paths and feature names with those from your project.

### Investigate before editing

```text
$codex-orchestrate Investigate why the settings page sometimes
loses changes after saving. Keep this read-only. Investigate the
save path and existing test coverage in parallel where useful.
Return the evidence-backed cause, remaining uncertainty, and
recommended fix.
```

Use this when you want a diagnosis to discuss before authorizing a fix.

### Execute an existing plan

```text
$codex-orchestrate Implement docs/plans/settings-save.md.
Preserve its item IDs, dependencies, and explicit execution order.
Complete the relevant checks and verify the integrated behavior.
```

The existing plan supplies the context. You do not need to rewrite it as individual agent assignments.

### Apply a mechanical change

```text
$codex-orchestrate Update callers under src/features to the new
saveSettings({ values, revision }) signature. The implementation
and expected behavior are already established in
src/settings/save-settings.ts and its tests. Preserve caller
behavior, update affected fixtures, and run the relevant checks.
Report callers that need a design decision before changing them.
```

This gives mechanical workers a concrete contract and a boundary for unexpected cases. Group related edits into useful assignments instead of asking for one agent per file.

### Review independent concerns

```text
$codex-orchestrate Review this branch against main for save-path
regressions and gaps in test coverage. Keep the review read-only.
Split independent questions where useful, reconcile the findings,
and return actionable issues with file and line references.
```

Use orchestration to divide the investigation. Include any project-specific review criteria that matter to your decision.

## Continue the same task

You can follow up naturally after a result:

```text
Apply the agreed fix. Keep the public API unchanged and add a
regression check for the reproduced failure.
```

The coordinator can reuse agents whose context remains useful. When the scope changes, state the change directly; you do not need to manage agent IDs yourself.

For a task with related design decisions, you can request a persistent advisor:

```text
$codex-orchestrate Implement docs/plans/settings-save.md.
Use an Astra advisor for the open concurrency question, and reuse
that advisor for related decisions as implementation evidence arrives.
```

An advisor starts when there is a concrete question to answer and may stay available for follow-ups within the task. New agents using a different model receive a fresh, focused brief. Reusing the advisor continues its own conversation; it does not fork the coordinator again.

For agent instructions and completion rules, see [SKILL.md](SKILL.md). Codex-specific dispatch details live in [the tool reference](references/codex-tools.md).
