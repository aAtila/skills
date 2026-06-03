# Relocation

How to perform a colocation move safely once grilling has locked the target shape. Assumes the vocabulary in colocation-first's [glossary](../colocation-first/references/glossary.md) — **route-owned module**, **module interface file**, **internal/**, **barrel**, **promotion**.

A move is a move. **Don't change behavior on the way** — relocating and refactoring are separate steps. If the implementation needs work, do it before or after, never tangled into the move, so the diff stays reviewable and reversible.

## Order of operations

1. **Lock the shape.** From the grilling: the folder name (domain-first), which file is the **module interface file**, what's public vs hidden, and whether this is colocation or promotion. Don't start moving until this is settled.
2. **Move the files.** One file at a time with `file_actions move`, so each step is verifiable. Rename vague files as you move them (`saved-search.utils.ts` → `build-saved-search-query.ts`) — the move is the moment to sharpen the name.
3. **Rewrite imports.** For each moved file, find every importer (`file_search` for the old path) and repoint it at the new path. Direct imports only.
4. **Kill barrels in the path.** If the old location had an `index.ts` re-exporting the moved file, repoint each importer at the real interface file, then delete the barrel. Never leave a re-export shim behind for backward compatibility (CLAUDE.md requires explicit approval for any backward-compat layer).
5. **Verify.** See the checklist below.

## Colocation vs promotion

- **One route owns it** → move under that route, into `_<domain>/<concept>/`. The route can now change its internals freely.
- **Two+ routes depend on it** → this is a **promotion**: move to `src/modules/<domain>/` with a stable module interface file. Promote only on a *second real caller*, never hypothetical reuse.
- **A cross-route import you found** is a promotion signal — resolve it by promoting to a shared module both routes import, or by extracting a smaller shared module. Never resolve it by importing another route's `internal/`.

## Public surface vs internal/

- The **module interface file** sits at the folder root with a domain name; outside callers import only this.
- Push raw API/response shapes, adapters, and mapping into `internal/`. Nothing outside the module imports from `internal/`.
- **Don't create `internal/` for a single file** — a flat folder with one interface file and a couple of private functions is often enough. Add `internal/` only when there are enough hidden files to justify the structure.

## Verification checklist

- No imports of the old paths remain (`file_search` the old paths — expect zero hits).
- No file imports another route's `internal/`.
- Every killed barrel is gone, and its importers point at real interface files.
- Typecheck / build passes (`npm run build`, or the project's typecheck script).
- The **deletion test** holds: deleting the feature now mostly deletes one folder.
- The diff is a pure move + import rewrite — no behavior changes rode along.

## What not to do

- Don't leave backward-compat re-exports at the old location.
- Don't promote to `src/modules` just to tidy a route tree — a noisy route is fixed by a `_<domain>/` subfolder, not by exile.
- Don't fold behavior changes into the move.
- Don't add `index.ts` barrels at the new location.
