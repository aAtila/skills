---
name: colocation-first
description: How to place, name, and organize files and modules in this codebase. Use whenever you create a new file, add a feature or sub-feature to a route, split a growing file, name a file or folder, or decide whether code should stay colocated under a route or move into a shared module. Apply this BEFORE writing new code or settling on a folder structure — even when the user never says "architecture" or "where should this go". This is the generative counterpart to the improve-codebase-colocation audit skill (which audits existing code for placement); reach for colocation-first whenever you are actively writing or placing code.
---

# Colocation First

This is the **operational layer** for placing, naming, and organizing code. It tells you when to apply the rules and the calls you must get right in the moment.

> **Canonical reference: [`references/route-owned-modules.md`](references/route-owned-modules.md)** is the single source of truth — full naming conventions, types-file rules, the worked premium-ads example, and the reasoning behind every rule. When a detail isn't spelled out here, read the doc. Term definitions (module, interface, seam, adapter, module interface file, barrel, promotion, …) live in [`references/glossary.md`](references/glossary.md).

## The belief everything serves

**Code that changes together lives together.** Colocation is the highest-leverage structural decision we make. The question is never "is this clean?" but:

> When this feature changes, how many places must I understand and edit?

Optimize for that number being **one**.

## Where does this code go?

1. **Owned by one route?** → Keep it under the route, behind **one** private, domain-named folder (the search route → `_search/`). This is the common case.
2. **Used by two or more routes today?** → Promote to `src/modules/<domain>/`. Present reuse, not hypothetical. A cross-route need is a **promotion signal** — never reach into another route's private folder to satisfy it.
3. **Technical adapter / plumbing** (transport, third-party wrapper, no domain meaning)? → `src/lib/<thing>/` if shared, else the owning module's `internal/`.

Don't optimize for a small route tree. Pushing behavior into `src/modules` just to tidy `app/` destroys locality — now understanding the route means hopping away from it. A noisy route folder is fixed by a private `_<domain>/` subfolder, not by exile.

## Organize by concept, not technical kind

Group files by the concept that changes together (`premium-ads/`, `search-results/`, `map-search/`), not by `_components/`, `_services/`, `_hooks/`, `_model/`. And don't just push those technical buckets one level deeper (`_search/components/`, `_search/services/`) — that's the same shallow split hidden under a new folder.

## Module interface files (the public surface)

A **module interface file** is a domain-named file outside callers may import directly because it represents a stable capability. "Public" means public to the surrounding route/module, not to the whole app. It should: have a domain name, own behavior or invariants, let callers depend on it without learning its internals, export a small intentional surface, and survive internal refactors without forcing caller changes.

Privacy is positional: files at a module's root are public; files in `internal/` are private; nothing imports another module's `internal/`. **Don't create `internal/` by default** — a single interface file with private functions is often enough; reach for `internal/` only when there are enough hidden files to justify the structure.

## No barrel files

No `index.ts`. No `export *`. Import directly from the interface file — it keeps jump-to-file fast, keeps seams honest, and avoids dragging client code into a server graph through a careless re-export. A central module file (e.g. `search.ts`) is allowed **only if it owns real behavior** (orchestration, invariants, composition) — never as a re-export hub.

## Name for the domain first

Pattern: `<domain-concept>[-specific-behavior][.<role>].ts`. Role suffixes are used only when they carry real meaning: `.types.ts` (shared module contract types), `.actions.ts` (Server Actions), `.server.ts` (server-only, pair with `import 'server-only';`), `.client.ts`, `.test.ts`, `-adapter.server.ts` / `-adapter.client.ts`. Avoid vague suffixes — `.utils.ts`, `.helpers.ts`, `.service.ts`, `.domain.ts` — which hide unclear ownership; name the behavior instead (`select-premium-search-ads.ts`, `map-premium-search-ad.ts`). Full naming and types-file rules live in the doc.

## Folder or flat file?

A module can be a single file. Create a folder only when the concept has enough implementation to earn locality. Use the **deletion test**: if removing the feature should mostly delete one folder, the folder is earning its keep. Don't extract upfront — start flat, promote when the complexity is real.

## A route-owned module is a behavior-hiding module, not a folder pattern

The folder shape earns its place only when it gives callers a smaller interface and maintainers better locality. If a folder or seam only moves complexity around, drop it.

## Checklist before you place or name a file

- Does it live next to what owns it? Route-owned → under the route in `_<domain>/`.
- Grouped by concept — not `components/`/`services/`/`hooks/`, and not those buckets pushed one level down?
- Does the name say what it owns, domain-first, with a meaningful role suffix only if it helps?
- Implementation detail → in `internal/` (and only when enough files justify it)?
- About to write `index.ts` or `export *`? Don't.
- Extracting to `src/modules` for one caller? Don't — wait for the second route.
- New folder for a sub-feature? Does the deletion test actually justify it?
- Need the full detail (naming tables, types files, premium-ads shape, rationale)? Read [`references/route-owned-modules.md`](references/route-owned-modules.md).
