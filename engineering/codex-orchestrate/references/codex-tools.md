# Codex tool mechanics

Use this reference when dispatching through Codex's `collaboration` tools. These details describe the contract observed on 2026-09-07; inspect the current tools before using them. Other harnesses need their own supported calls.

## Spawn and context

Call `collaboration.spawn_agent` with a descriptive `task_name` and a self-contained `message`. Apply the role's model and effort from the [shared policy](../../orchestrate/SKILL.md#choose-the-role) using this context policy:

| Child settings relative to parent | Fork behavior |
| --- | --- |
| Different model | Set `fork_turns: "none"` and explicitly set `model` and `reasoning_effort`. Do not use partial or full history forks. |
| Same model, different effort | Default to `fork_turns: "none"` with explicit settings. Use a supported positive integer string only when those recent turns materially help. |
| Same model and effort | Default to fresh context. A partial or full history fork is appropriate when earlier reasoning is useful; for `fork_turns: "all"`, omit both model and effort overrides. |

Omitting `fork_turns` defaults to `"all"`; always choose it explicitly. Full-history forks inherit the parent's model and effort and reject overrides in this contract. Although the tool accepts model overrides with partial forks, this skill deliberately keeps different-model spawns fresh.

For Sol low scouts and Luna max mechanical workers, use fresh context unless a same-model assignment warrants the exception above. Include the workspace, applicable project instructions, task constraints, ownership, and leaf boundary in the message. Fresh conversation context does not remove inherited sandbox restrictions or grant new permissions.

An Astra advisor follows the same spawn rules: starting one from a Sol or Luna parent requires `fork_turns: "none"`. Retain its returned ID for related questions within the current task. Send new evidence with `send_message` while it is running, or use `followup_task` to start its next turn when idle. Reusing it preserves its own context without another spawn or fork; supply relevant coordinator decisions it has not seen. Persistence does not schedule future work or reserve an exemption from the live capacity limit.

Read the live concurrency limit rather than encoding the guide's example of four agents. Account for existing children and any nested delegation according to the tool's counting rules. Do not change global configuration to make room for this skill.

The tools in this environment are called directly in the commentary channel; `collaboration` is not available inside `functions.exec`.

## Messages, follow-ups, and completion

- `send_message` delivers context to a running agent but does not trigger an idle agent's next turn. Use canonical task names for messages between separate branches of the agent tree.
- `followup_task` sends another assignment to an existing child and triggers a turn if it is idle. Use it when continuing related work with that child's existing settings and context.
- `wait_agent` waits for a mailbox update; it does not mean every child has finished and does not itself return the message contents. Process the delivered messages and retain the outstanding IDs. Use a bounded wait compatible with the session's communication requirements.
- `list_agents` resolves uncertainty about active agents or available capacity. Avoid repeated unchanged status checks.
- `interrupt_agent` stops the child's current turn but leaves the agent available. Confirm its state before transferring write ownership. A later `followup_task` can resume it.

For subtasks of the current request, use these child-agent tools. Codex app `create_thread` creates a separate user-owned task and is appropriate only when the user explicitly asks for a new task.
