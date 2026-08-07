# Invoking `/doc-sync`

Operator notes — how to call this skill well. The agent doesn't need this file; you and your teammates do.

**The habit that matters most:** name the baseline in the invocation. It pre-answers Step 2 (confirm baseline) and scopes the whole run.

## After a feature branch — the routine invocation

```
/doc-sync uncommitted + this branch vs main
```

Run at branch-end, before writing the PR. Most runs report "verified clean" quickly because the module-map lookup scopes tightly.

## Naming a specific change and baseline

```
/doc-sync the bulk ZIP download work — everything since 76d9091
```

Changed paths → MODULES.md **Lives in** lookup → the owning module's whole doc set (entry, runbook, walkthrough, glossary terms, ADRs read-only).

## After a vocabulary or concept rename

```
/doc-sync we renamed Consumer cursor semantics in the last 3 commits — check CONTEXT.md, MODULES.md and anything downstream
```

Exercises the kind-boundary scope: root-level docs (CONTEXT.md, MODULES.md, README) are in bounds, not just `docs/`.

## As a scheduled sweep

Standing baseline per doc: diff since each walkthrough's `Verified:` stamp over the module's code homes. Empty diff → bump the stamp and move on; non-empty → verify and file `ready-for-agent` issues. Same skill, no new machinery — the stamp is the receipt.
