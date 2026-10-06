# Skills repo conventions

- For model-invoked dependencies, write: "Call the Skill tool with `skill-name`." User-invoked skills (`disable-model-invocation: true`) cannot be called this way: ask the user to run them, or read their `SKILL.md` directly when a workflow needs their reference instructions.
- Before writing or editing anything an agent/LLM will consume — a skill, prompt, workflow doc, AGENTS.md/CLAUDE.md — call the Skill tool with `writing-for-agents` (if available) and follow it.
- Prefer thin wrappers over copied bodies: a skill that extends another should invoke it (see `engineering/rot-hunt-to-issue`), keeping the shared logic a one-place edit.