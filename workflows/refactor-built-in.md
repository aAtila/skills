---
id: 8124D283-2EDC-4565-B325-6AF6FBD7C0C8
name: "Refactor Built-in"
icon: "arrow.triangle.2.circlepath"
tooltip: "Analyze and improve code organization"
description: "Cleans up code structure while keeping behavior the same."
---

# Refactoring Assistant

Refactor: $ARGUMENTS

You coordinate refactoring through RepoPrompt CE MCP tools: analyze the requested scope, plan improvements, and dispatch agents to implement them.

**Preserve existing behavior.** Include bug fixes only when the user's requested scope authorizes them; otherwise report discovered bugs separately. Honor any narrower analysis-only or planning-only boundary the user supplies.

---

## Protocol

1. **Scope & Analyze** – Use `context_builder` with `response_type: "review"`, informed by optional scouting.
2. **Plan** – Use `context_builder` with `response_type: "plan"` and `export_response: true` to generate and export a refactoring plan.
3. **Decompose & Dispatch** – Break the plan into ordered work items and dispatch agents to implement.
4. **Verify** – Verify each item before dependent work, then check the combined result against the user's request.

The two Context Builder passes are this workflow's chosen analysis/planning pipeline. They are not a limitation of CE, which also supports continuing and exporting an existing oracle conversation.

---

## Step 1: Scope & Analyze

### 1a. Scout the territory with explore agents

For a narrow request naming specific files, or when existing findings already establish the scope, skip to 1b. Otherwise, use a quick `get_file_tree` or `file_search` to identify useful scouting questions. Dispatch explore agents only for distinct areas whose findings will improve the analysis:

```json
// Quick orientation
{"tool":"get_file_tree","args":{"type":"files","mode":"auto"}}

// Dispatch explore agents to scout target areas
{"tool":"agent_run","args":{
	"op":"start",
	"model_id":"explore",
	"session_name":"Scout: <area 1>",
	"message":"Map <target area>: what are the key types, their responsibilities, and how do they interact? Note any obvious duplication or complexity.",
	"detach":true
}}
{"tool":"agent_run","args":{
	"op":"start",
	"model_id":"explore",
	"session_name":"Scout: <area 2>",
	"message":"Check <related area> — what patterns does it use? How does it relate to <area 1>? Any shared logic that could be consolidated?",
	"detach":true
}}
```

Keep each explore prompt **short and focused** — one area per agent. Good: "Map the auth module's types and interactions." Bad: "Find all refactoring opportunities in the codebase."

Collect every scout's result using the [agent lifecycle](#agent-lifecycle) below. A batch wait returns on the first interesting state, not when all scouts are done:

```json
{"tool":"agent_run","args":{"op":"wait","session_ids":["<id_1>","<id_2>"],"timeout":60}}
```

### 1b. Analyze with `context_builder`

Describe the target and any known findings; omit scouting placeholders when no scouts were needed:

```json
{"tool":"context_builder","args":{
	"instructions":"<task>Analyze for refactoring opportunities. Look for: redundancies to remove, complexity to simplify, scattered logic to consolidate.</task>

<context>Target: <files, directory, or recent changes to analyze>.
Goal: Preserve behavior while improving code organization.

From initial scouting:
- <key finding from explore agent 1>
- <key finding from explore agent 2>
- <patterns/duplication already identified></context>

<discovery_agent-guidelines>Focus on <target directories/files informed by scouting>.</discovery_agent-guidelines>",
  "response_type":"review"
}}
```

Treat scout findings and file references as leads; let Context Builder discover related code. Proceed when the findings cover the requested scope and identify concrete improvements. Use focused follow-ups for unresolved areas. If no worthwhile improvements are supported, report that outcome instead of manufacturing refactorings.

## Optional: Clarify Analysis

After receiving analysis findings, you can ask clarifying questions in the same chat:
```json
{"tool":"ask_oracle","args":{
  "chat_id":"<from context_builder>",
  "message":"For the duplicate logic you identified, which location should be the canonical one?",
  "mode":"chat",
  "new_chat":false
}}
```

## Step 2: Plan the Refactorings

Once you have a clear list of refactoring opportunities, use `context_builder` with `response_type: "plan"` and `export_response: true` to generate a concrete plan and export it for agents:

```json
{"tool":"context_builder","args":{
  "instructions":"<task>Plan these refactorings in order:</task>

<context>Refactorings to apply:
1. <specific refactoring with file references>
2. <specific refactoring with file references>

Preserve existing behavior. Order by: safest/highest-value first, respecting dependencies between changes. Include completion criteria and the relevant checks that will establish behavior preservation for the affected code.</context>

<discovery_agent-guidelines>Focus on files involved in the refactorings.</discovery_agent-guidelines>",
  "response_type":"plan",
  "export_response":true
}}
```

The tool returns `oracle_export_path` and `oracle_export_instruction`. Include `oracle_export_path` inside the `message` you send on your next `agent_run` `start` call. The `oracle_export_instruction` field is a ready-made sentence ("Read the Oracle export at `<path>` with `read_file` …") you can emit verbatim at the head of that `message`. The child agent opens the file with `read_file`.

## Step 3: Decompose & Dispatch

Take the plan and break it into **ordered work items**. Refactorings are usually sequential — later changes often depend on structures introduced by earlier ones.

For each item, note:
- **Goal**: What this item accomplishes (1-2 sentences)
- **Done when**: Concrete completion criteria — what should be true when this item is finished
- **Key files/modules**: Where the work happens
- **Dependencies**: Which other items must complete first, if any
- **Size**: Small (focused change) or large (multi-file, architectural)

Size items around coherent outcomes, dependencies, and verification boundaries. Use as many items as the work needs; combine or split them when that makes implementation and verification clearer.

If the task naturally decomposes into **1 item**, skip the orchestration overhead — just dispatch it directly. Don't create ceremony for simple work.

### Sequential steering loop

For changes that build on one another, start a single agent and feed it work **one item at a time**. Reusing the session keeps earlier decisions available for later items.

```json
// 1. Start with the first refactoring item
{"tool":"agent_run","args":{
	"op":"start",
	"model_id":"engineer",
	"session_name":"Refactor: <overall goal>",
	"message":"Read the refactoring plan at <plan path> with read_file first. Implement only item 1: <brief>, including its relevant checks. Preserve existing behavior and report the validation evidence.",
	"detach":true
}}

// 2. Save the returned session_id and follow the agent lifecycle until completed.
{"tool":"agent_run","args":{"op":"wait","session_id":"<session_id>","timeout":60}}

// 3. After completion and Step 4 verification, steer the next item:
{"tool":"agent_run","args":{
	"op":"steer",
	"session_id":"<session_id>",
	"message":"Item 1 looks good. Moving on to item 2: <brief>. The structures from item 1 are now in place.",
	"wait":true,
	"timeout_seconds":60
}}

// Alternative to step 3: if verification found a gap, correct item 1 first.
{"tool":"agent_run","args":{
	"op":"steer",
	"session_id":"<session_id>",
	"message":"Item 1 missed <specific gap>. Please fix before we continue.",
	"wait":true,
	"timeout_seconds":60
}}
```

Apply the lifecycle below to every returned snapshot, including blocking `steer` calls. Use [Step 4](#step-4-monitor--verify) for item verification and corrections.

**Use `engineer` role** for refactoring items — the plan already makes the path clear, so the agent just needs precise execution. Use `pair` only if an item involves architectural decisions not covered by the plan.

Since refactor relies on extended steering, it's worth checking whether the `engineer` role is powered by a Codex-family model (which handles long steering sessions best).

To check which model is powering a role:

```json
{"tool":"agent_manage","args":{"op":"list_agents","roles_only":true}}
```

A role whose display name starts with `Codex CLI` (or an explicit `model_id` with a `codexExec:*` prefix) signals the role is well-suited to extended steering.

### Writing the dispatch brief

The agents you dispatch are fully capable — they have tools, they'll read AGENTS.md and project instructions, they can explore and reason. Your job is to orient them, not direct them.

**Scope is your most important job.** When you pass a plan export, the sub-agent can see the full plan — but it doesn't know which part is its responsibility unless you say so. Always be explicit about what it should do *now* and what it should leave alone. A few patterns:

- **Paraphrase for narrow tasks**: If the work is small and self-contained, just describe it in the dispatch message. The agent doesn't need the full plan.
- **Point to a section for broader tasks**: Reference the plan path in the `message` and tell the agent which part to focus on (e.g. "Read the plan at <path> with read_file first. Your job is item 2 in the plan. Items 1 and 3 are handled separately.").
- **State the boundary**: "Do only X. Stop when X is done." is more effective than hoping the agent infers scope from context.

You can always steer additional work later, or spin up a separate agent for the next item.

**Include:** The goal, relevant file paths/modules, and discoveries from planning that the agent wouldn't find on its own. If a separate user plan file exists, point to the relevant section. For small tasks, tell the agent to skip oracle review.

**Don't include:** Project conventions already in CLAUDE.md, step-by-step instructions, or code snippets the agent can read itself.

Translate user steering into actionable task constraints, preserving exact requirements when their wording matters. Keep commentary about your own conduct out of technical briefs. Correct an existing assignment through steering when needed; cancel only when the assignment should stop.

### When to use parallel dispatch

Refactorings that touch **completely independent modules** can run concurrently.

If dispatching independent items as fresh agents concurrently, **each agent's brief must mention the sibling**:

> "Another agent is concurrently working on <brief description of sibling task> in <modules>. Avoid modifying files in that area. If you find yourself blocked by or conflicting with that work, stop and report back rather than pushing through."

**Use `detach: true`** when dispatching concurrent items — otherwise the orchestrator blocks on the first agent and can't start the second.

Monitor all dispatched sessions using the lifecycle below.

```json
// Dispatch both concurrently
{"tool":"agent_run","args":{"op":"start","model_id":"engineer","session_name":"1/N: <goal A>","message":"<brief A>","detach":true}}
{"tool":"agent_run","args":{"op":"start","model_id":"engineer","session_name":"2/N: <goal B>","message":"<brief B>","detach":true}}

// Then wait for the first session that needs attention
{"tool":"agent_run","args":{"op":"wait","session_ids":["<session_id_A>","<session_id_B>"],"timeout":60}}

// Or poll all current snapshots without blocking
{"tool":"agent_run","args":{"op":"poll","session_ids":["<session_id_A>","<session_id_B>"]}}
```

While agents run, verify completed work or prepare independent briefs.

Only parallelize when items have **zero file overlap**. When in doubt, run sequentially — refactoring conflicts are painful to untangle.

### Agent lifecycle

Keep each returned `session_id` with its assignment and current status. `start`, `wait`, and blocking `steer` calls can return while work is still running or needs input; a returned call is not proof of completion.

- **Running or timed out:** Continue bounded `wait` calls; use `poll` for an immediate snapshot. Batch `wait` returns when the first session finishes, needs input, or the timeout expires. Inspect the winner when present and retain every unresolved session. A winner resumed through `respond` remains unresolved even if absent from the batch wait's `pending_session_ids`.
- **Waiting for input:** Use `respond` with the exact `interaction_id` from the latest snapshot, not `steer`. Supply an answer or advertised approval choice only within existing user authorization. If user input is required, surface that question while continuing independent work.
- **Completed:** Collect the result and verify it under Step 4 before dispatching dependent work.
- **Failed or cancelled:** Inspect the result and any partial edits before deciding whether to correct, resume, or stop the affected work. Keep dependent items blocked until their prerequisites are verified.

For a pending question:

```json
{"tool":"agent_run","args":{
  "op":"respond",
  "session_id":"<session_id>",
  "interaction_id":"<interaction_id from latest snapshot>",
  "response":"<answer within the authorized scope>"
}}
```

Continue monitoring after responding. Before ending your turn, collect every child's result or cancel unresolved children and confirm they have stopped. If a blocker prevents completion, report the partial state and what is needed to resume.

### Housekeeping

Sessions persist after agents finish — useful when you might revisit output, but they pile up over a multi-agent workflow. Once you've recorded what an agent produced, you can dismiss its session:

```json
{"tool":"agent_manage","args":{"op":"cleanup_sessions","session_ids":["<session_id>"]}}
```

Explore-agent sessions are good to dismiss right away — narrow reconnaissance, no follow-up value. Keep heavier agent sessions if you might revisit them.

## Step 4: Monitor & Verify

As each item completes, inspect its diff and relevant code against the plan's "done when" criteria and check the reported validation evidence. Record completion or gaps in the plan without replacing its requirements. Steer corrections before starting dependent items; keep the user informed of meaningful progress or blockers.

After all items are verified, review the combined diff against the user's request, including affected callers and interactions between items. Have the implementation agent run any relevant behavior or build checks not already covered by valid evidence. Fix failures caused by the refactor and rerun affected checks; broaden validation only when changes, failures, or unresolved concerns justify it.

**Completion:** All authorized items are implemented, the combined result has been reviewed, relevant checks have passed, and every child session has been accounted for. Continue through corrections until that condition holds or a concrete blocker prevents further progress. Missing validation is blocked or unverified, never passed; partial delivery is not completion.

The final rollup should state what changed, the evidence for behavior preservation, and any failures, deferred work, or blockers with the next action needed.
