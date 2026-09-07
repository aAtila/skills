# RepoPrompt CE tool mechanics

Checked against the installed CE tool, model, and workflow catalogs on 2026-09-08. Inspect the active contract before dispatch; available tools depend on the caller and bound context.

## Connect and target the checkout

Prefer the exposed RepoPrompt CE MCP tools. From an external harness without them, use the installed CE CLI. On this Mac it is `/Applications/RepoPrompt CE.app/Contents/MacOS/repoprompt-mcp`; confirm the executable and server before use. A generic `rp-cli` or debug executable may target a different app instance.

Use `bind_context op=list`, then bind the requested repository with `working_dirs` or a returned `context_id`. For CLI calls, retain that context with `--context-id`. Inspect `workspace_context` and `git op=status` to verify repository, branch, checkout, and existing changes. Use explicit `repo_root` for git operations when multiple roots are present. Do not select whichever workspace happens to be frontmost. If the requested workspace is missing, use the advertised workspace-binding flow and its approval requirements.

The CLI supports `--tools-schema` for the bound catalog and `-c <tool> -j @<arguments.json>` for structured calls. Keep requests with multiline briefs in JSON files outside the repository. Agent Mode may expose different tool names from external MCP; use its advertised tools rather than assuming identical catalogs. A similarly named Rhei tool is not a substitute for the CE contract.

If the app, permission, or spawn policy blocks access, report the specific limitation and continue unaffected work. Do not launch a built-in workflow automatically: it brings its own instructions. The live contract permits MCP-started Orchestrate runs to delegate, but prohibits recursive child spawning. A leaf session must return the needed assignment to its coordinator rather than escaping through another tool surface.

## Resolve models

Call `agent_manage` with `op: "list_agents"` and inspect both `task_labels` and `agents[].models[]`. Match the [shared model and effort preferences](../../orchestrate/SKILL.md#choose-the-role) to an available provider's advertised compound `model_id`. Pass that exact value to `agent_run start`; do not construct IDs from a naming convention.

Verified examples include `codexExec:gpt-5.6-sol-low`, `codexExec:gpt-5.6-luna-max`, and `codexExec:gpt-6-astra-high`. These identify Codex CLI execution managed by RepoPrompt. Role aliases such as `explore` and `engineer` can have user overrides, so they are not evidence of a particular model or effort. A missing preferred target needs a disclosed, supported fallback, not a global settings change.

`agent_run start` has no separate Codex `reasoning_effort` or `fork_turns` parameter. The compound target carries the effort. Use the returned session snapshot to verify the resolved settings when available.

## Context and worktrees

Use `file_search`, `get_code_structure`, and `read_file` for focused discovery. Curate source with `manage_selection`. When a plan or broader context is needed, `context_builder` accepts `instructions`, `response_type: "plan"`, and `export_response: true`. A supplied plan does not need regeneration.

Include `oracle_export_path` and the returned read instruction in the child's `message`. Keep one authoritative plan and retain its exports while children or reviewers need them. Children run in separate tabs; a parent's Oracle `chat_id` is not transferable context. For Oracle consultations, external MCP exposes `oracle_send` and native Agent Mode may expose `ask_oracle`; inspect the current schema. Oracle chat IDs and agent session IDs are different identifiers.

`agent_run start` creates a new session/tab. Supply a focused brief and relevant source or plan references; do not attach a transcript handoff when changing models. Reuse existing sessions through `steer` instead of creating repeated handoff copies.

`inherit_worktree` controls checkout bindings, not conversation history. From Agent Mode, children inherit the parent's worktree bindings by default. Leave that intact when they should work in the same checkout; use explicit worktree arguments only when isolation is useful, with a plan for integration and verification. Give shared files one writer and coordinate the shared git index.

## Start and continue

Use `agent_run` with `op: "start"`, the discovered `model_id`, a descriptive `session_name`, the full assignment in `message`, and `detach: true` for concurrent work. Save the returned `session_id`; `start` does not accept an existing session ID. Do not attach a workflow to a leaf assignment unless the user chose that workflow and it is compatible with the child's permissions.

Use `op: "steer"` with the same `session_id` and a focused `message` for related follow-ups. This can steer a running child or reactivate a completed session. Use it for the persistent Astra advisor, supplying new evidence it has not seen. Optional `wait: true` and `timeout_seconds` bound a follow-up wait. Persistence keeps a session available within the task; it does not schedule future work.

## Monitor and close out

- `op: "wait"` accepts one `session_id` or an array `session_ids`. An array returns when the first session finishes or needs input. Track the others. Use bounded waits, for example `timeout: 60`, and treat timeouts as pending work.
- `op: "poll"` returns snapshots immediately. Use it to resolve state uncertainty, not as a busy loop.
- For `waiting_for_input`, use `op: "respond"` with the exact `session_id` and latest `interaction_id`. Approval choices belong in the top-level scalar `response` field and must match an advertised option. Answer within existing authorization; surface requests for new approval to the user. `steer` does not resolve this state.
- Exclude a session waiting on the user from repeated multi-waits so it does not hide progress by returning the same interaction. Continue tracking it separately.
- Verify a completed child's actual changes and evidence before accepting its outcome. Inspect failed or cancelled sessions for partial work before retrying or transferring ownership.
- To end a blocked handoff, `op: "cancel"` applies only to running or waiting sessions. Confirm they stopped and retain IDs, unanswered requests, and partial changes. After the blocker is resolved, continue with `steer`; use new interaction IDs from new snapshots rather than reusing the cancelled approval.

`agent_manage get_log` retrieves session evidence. Keep completed advisor sessions for further consultation. `cleanup_sessions` deletes session history; it is not required for normal completion and should not erase evidence still needed for review or follow-up.
