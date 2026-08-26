---
id: 0D2B339E-379A-430D-AF06-183853B955F9
name: "Build It"
icon: "hammer"
tooltip: "Plan with the context builder, implement, review, and commit"
description: "Orients in the codebase, builds a plan with context_builder, implements it directly, then gets an oracle review and commits the work."
---

# Build It

Task: $ARGUMENTS

Orientation → `context_builder` plan → implement directly → review & commit. Trust the plan; consult `ask_oracle` only on a **gap**.

Two words carry this workflow:

- **The selection** — the files `context_builder` curated. The oracle sees the selection completely (full content) and sees only the selection.
- **A gap** — a concrete, nameable question the plan plus reading the selection cannot answer. A gap is something you can state in one sentence ("how do X and Y connect across these files?"). Vague unease is not a gap — read the selection first.

## Phase 0: Name the Session (REQUIRED — first action)

Before anything else, call `set_status` to name this session:

```
BUILD #<issue>: <short title>
```

- **`BUILD`** — always uppercase, always first, so builder sessions sort and scan together.
- **`#<issue>`** — the issue/ticket number when the request names one. **Omit the segment entirely if there is none** — don't invent one, don't write `#TBD`.
- **`<short title>`** — a few words in the codebase's own terms, not a restatement of the whole request.

```json
{"tool":"set_status","args":{"session_name":"BUILD #123: retry logic in NetworkService"}}
```

With no issue number: `BUILD: retry logic in NetworkService`.

Set this once, up front. Don't rename mid-run unless the scope genuinely changes. One exception: `context_builder` overwrites this name with its chat title — Phase 2 re-asserts the identical string. That's a restore, not a rename.

## Phase 1: Orientation

Get a lay of the land: `get_file_tree` (`mode:"auto"`), then targeted `file_search` / `get_code_structure` probes on key terms from the task. Skim paths and signatures; full file contents come after the builder selects them.

**Done when** you can restate the task in the codebase's own terms — specific modules, patterns, terminology. That reformulated prompt is this phase's output.

## Phase 2: Plan

```json
{
  "tool": "context_builder",
  "args": {
    "instructions": "<reformulated prompt>",
    "response_type": "plan",
    "export_response": true
  }
}
```

Returns the selection, an architectural plan grounded in actual code, a `chat_id` for follow-ups, and an `oracle_export_path` — the plan serialized to a file. That file is the plan of record: it survives compaction, and Phase 4's review checks the diff against it. Trust the plan — the builder explores deeply and selects intelligently.

**Re-assert the session name immediately after this call** — `context_builder` renames the session to its chat title. Pass the byte-identical string from Phase 0:

```json
{"tool":"set_status","args":{"session_name":"BUILD #123: retry logic in NetworkService"}}
```

**Done when** every step of the plan maps onto files in the selection. A step naming a file the selection lacks is a coverage problem — fix it now (see Coverage below), not mid-implementation.

## Phase 3: Implement

Implement the plan directly with `apply_edits`, `file_actions`, and `read_file`. Implementation is your job; the oracle reasons, you edit.

- **Token budget:** stay under ~160k; check `manage_selection(op:"get")` if you add files. Prefer slices for large additions.
- **Coverage:** one missing file → `manage_selection op=add`, leaving the builder's selection intact. More than one → rerun `context_builder` with a better prompt; that is its job. A rerun returns a new `chat_id` — it supersedes the old one everywhere below.

**Done when** every step of the plan is implemented — not when the first edit compiles.

## Phase 4: Review & Commit

Like asking your mentor to look over your work before it goes to main.

**Trivial task** (a few lines, single-step plan)? Commit with `commit-me` and wrap up — skip the rest of this phase.

1. **Commit the implementation** with the `commit-me` skill. Landing it first gives the reviewer an exact diff target, and review fixes get their own commit — a bad fix reverts cleanly without touching the implementation.
2. **Publish the diff**: `git op=diff compare="back:1" artifacts=true` (use `compare="main"` if the branch holds several commits) — after committing, the default `uncommitted` spec diffs nothing. The review artifacts land in the selection so the oracle sees exactly what changed.
   **Footprint check**: map every changed file in the diff to a plan step. Tests, docs, and mechanically required callers extend the plan freely; a changed production file no plan step explains is drift — name it in your summary and flag it to the reviewer, so the review judges it rather than blesses it.
3. **Ask the oracle to review**, continuing the builder's chat:

```json
{
  "tool": "ask_oracle",
  "args": {
    "chat_id": "<from context_builder>",
    "message": "Review the committed changes against the plan.",
    "mode": "review",
    "new_chat": false
  }
}
```

The oracle is a *warm* reviewer — it holds the selection and the plan, so it catches drift from the plan cheaply. It will also excuse mistakes it helped plan; accept that trade. If the work warrants a cold read, that's a different workflow.

4. **Apply findings you agree with**, verify, then **commit the fixes with `commit-me` as a second commit** referencing the review. Findings you reject: note why in your summary — don't silently drop them.

**Done when** the implementation and any review fixes are committed, and the final summary lists applied and rejected findings.

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
