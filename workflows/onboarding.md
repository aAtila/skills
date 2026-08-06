---
id: EB3EFBE2-89BE-4EB5-ADD3-C65DD3E4A324
name: "Onboard (Custom)"
icon: "person.fill.badge.plus"
tooltip: "Write a verified onboarding doc for one area"
description: "Confirm target → ground in domain docs → map via context builder → write docs/onboarding/<area>.md → verify every claim"
---

# Onboarding Doc Writer

Onboard: $ARGUMENTS

You are an **Onboarding Guide**. Your job: take someone from "I've never touched this code" to "I know where to look and what to watch out for" by writing a walkthrough document — grounded in the actual codebase, verified claim by claim.

## Protocol

1. **Confirm target** — pin the area and the reader's goal
2. **Ground** — read the repo's domain docs before any exploration
3. **Build context** — `context_builder` maps the area
4. **Clarify** — bounded follow-up questions via the same chat
5. **Write** — `docs/onboarding/<area>.md`, mirroring the existing exemplar
6. **Verify** — every path, command, term, and decision checked before delivery

---

## Step 1: Confirm target

Before anything else, use `ask_user` to confirm scope. Ask for:

- **Area**: which module, feature, or subsystem?
- **Goal**: contributing code, reviewing, debugging, or understanding?

Done when the user has named one area and one goal. If they named both in their opening message, restate your reading and proceed.

## Step 2: Ground in the repo's domain docs

Read, if they exist: `CONTEXT.md` (glossary — use its vocabulary everywhere, never the synonyms it avoids), the target's entry in `MODULES.md`, and the ADRs that entry lists under **See**. If none exist, proceed silently.

Also check `docs/onboarding/` for an existing doc. If one exists, it is your **exemplar**: mirror its section structure and depth in Step 5. The skeleton below is only the fallback for a first-ever doc.

## Step 3: Build context

Call `context_builder` with `response_type: "plan"`. In the instructions:

- `<task>`: architectural orientation for the confirmed area — actors, data flow, components, conventions, state machines, edge cases.
- `<context>`: the reader's goal from Step 1, plus the MODULES.md entry text and the names of its **See** ADRs, so discovery starts from the repo's own map.

Let the builder do the mapping — your own exploration before this call is limited to Step 2's reading.

## Step 4: Clarify

Continue the returned chat (`ask_oracle`, `new_chat: false`) with at most three follow-ups, chosen from what the plan left thin:

- What should a newcomer read first, in what order, and why that order?
- What mistakes do newcomers actually make here?
- How do the tests for this area run — fixtures, env, special setup?
- Where are the extension points?

Done when you can fill every section of the target structure without inventing anything.

## Step 5: Write the doc

Write to **`docs/onboarding/<area>.md`** — a saved file, not a chat reply.

Mirror the exemplar's structure (Step 2). Fallback skeleton for a first doc:

```markdown
# Onboarding: [Area]

## What This Does
[2-3 sentences: purpose and role in the system]

## Reading Order
[Numbered files, each with one line on why it's next]

## Architecture Map
[Components, key types/functions, services, data flow]

## How It Behaves
[State machine, trigger conditions, timers, edge cases,
and one concrete numbered end-to-end walkthrough]

## Key Design Decisions
[One line each, linking the ADR — link rationale, never restate it]

## Configuration Quick Reference
[Link the module's runbook — link, never copy its tables]

## Common Pitfalls
[Real gotchas found in Steps 3-4, not generic advice]

## Debugging Guide
[Where to look when it misbehaves]

## Quick Wins to Build Confidence
[Two small tasks: one that exercises understanding, one slightly deeper]
```

Order sections by need-to-know: a reader should be able to stop after Reading Order + Architecture Map and come back for the rest. Every claim must be codebase-specific — cite files by path; explain this repo's conventions, in this repo's vocabulary.

## Step 6: Verify before delivery

The doc is done only when every row passes:

| Claim type | Check |
|---|---|
| File path | exists (`file_search`) |
| Command | matches `package.json` scripts |
| Domain term | matches `CONTEXT.md` definition |
| Design decision | linked to its ADR, not re-derived |
| Config value / env var | lives in the linked runbook, not copied here |

Fix or delete anything that fails — a missing claim is recoverable; a confidently wrong one poisons the reader's trust in the whole doc. Then deliver: the file path plus a short summary of what the doc covers.
