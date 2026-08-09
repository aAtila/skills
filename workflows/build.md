---
id: 0D2B339E-379A-430D-AF06-183853B955F9
name: "Builder Mode"
icon: ""
description: ""
---

# Builder Mode

Task: $ARGUMENTS

Orientation → `context_builder` plan → implement directly. Trust the plan; consult `ask_oracle` only on a **gap**.

Two words carry this workflow:

- **The selection** — the files `context_builder` curated. The oracle sees the selection completely (full content) and sees only the selection.
- **A gap** — a concrete, nameable question the plan plus reading the selection cannot answer. A gap is something you can state in one sentence ("how do X and Y connect across these files?"). Vague unease is not a gap — read the selection first.

## Phase 1: Orientation

Get a lay of the land: `get_file_tree` (`mode:"auto"`), then targeted `file_search` / `get_code_structure` probes on key terms from the task. Skim paths and signatures; full file contents come after the builder selects them.

**Done when** you can restate the task in the codebase's own terms — specific modules, patterns, terminology. That reformulated prompt is this phase's output.

## Phase 2: Plan

```json
{
  "tool": "context_builder",
  "args": {
    "instructions": "<reformulated prompt>",
    "response_type": "plan"
  }
}
```

Returns the selection, an architectural plan grounded in actual code, and a `chat_id` for follow-ups. Trust the plan — the builder explores deeply and selects intelligently.

**Done when** you hold the plan and its `chat_id`.

## Phase 3: Implement

Implement the plan directly with `apply_edits`, `file_actions`, and `read_file`. Implementation is your job; the oracle reasons, you edit.

- **Token budget:** stay under ~160k; check `manage_selection(op:"get")` if you add files. Prefer slices for large additions.
- **Coverage:** if the selection is missing files you materially need, rerun `context_builder` with a better prompt — that is its job, and the single fix for coverage. Reach for `manage_selection` only for one small targeted addition, always leaving the builder's selection intact.

**Done when** every step of the plan is implemented — not when the first edit compiles.

## On a gap: `ask_oracle`

Continue the builder's chat — same context, no restart:

```json
{
  "tool": "ask_oracle",
  "args": {
    "chat_id": "<from context_builder>",
    "message": "<the gap, stated in one sentence, plus what you already read>",
    "mode": "plan",
    "new_chat": false
  }
}
```

The oracle deep-reasons over the selection: cross-file connections, edge cases, "what am I missing here" questions. A question about files outside the selection is a coverage problem, not a gap — go back to `context_builder`.
