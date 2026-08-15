# to-epic — draft notes

**Status: DELIBERATION, not ratified.** Nothing here is Fact until Atila ratifies. Open questions to settle before this leaves `in-progress`:

1. **Scope of the skill.** `to-epic` is r3call-specific — the Epic tier is r3call-invented vocabulary; no other repo has it, and no Pocock skill covers the cross-repo tier. Should it live in the general skills library at all, or move into r3call (or a r3call-scoped skills dir)? Parked in `in-progress` for now.

2. **Coupling to r3call config.** Step 6 points at r3call's `docs/agents/issue-tracker.md` → "Wayfinding operations" for the sub-issue / dependency `gh api` calls, to keep a single source of truth. That is a cross-repo pointer: it only resolves when the skill runs inside a r3call clone. Acceptable while the skill is r3call-only; revisit if it ever generalizes.

3. **Invocation.** User-invoked (`disable-model-invocation: true`), matching `to-spec` / `to-tickets` — zero context load, you remember to type it. Correct unless another skill must reach it autonomously.

4. **Relationship to `wayfinder`.** The `wayfinder` **map** already uses the same GitHub machinery an Epic needs — a coordinating issue with native sub-issues and native dependency edges. `to-epic` is the *planned-decomposition* cousin of wayfinder's *fog-of-war* map. If the overlap grows, decide whether Epic and map should share a substrate rather than duplicate the wiring.

5. **Wiring into `/setup-matt-pocock-skills`.** Deferred until the first real Epic proves the repeatable shape — draft now, ratify on first use, rather than guess the skill's shape from a hypothetical.
