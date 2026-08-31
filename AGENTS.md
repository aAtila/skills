# Skills repo conventions

- When one skill invokes another, write the instruction as: "Call the Skill tool with `skill-name`." This phrasing triggers cross-skill invocation reliably; prose like "use skill-name here" often doesn't.
- Before writing or editing anything an agent/LLM will consume — a skill, prompt, workflow doc, AGENTS.md/CLAUDE.md — call the Skill tool with `writing-for-agents` (if available) and follow it.
- Prefer thin wrappers over copied bodies: a skill that extends another should invoke it (see `engineering/rot-hunt-to-issue`), keeping the shared logic a one-place edit.