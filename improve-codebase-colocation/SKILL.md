---
name: improve-codebase-colocation
description: Find placement and organization opportunities in a codebase, measured against the colocation-first conventions. Use when the user wants to improve code organization, colocate a feature scattered across technical folders (src/services, src/model, src/hooks, src/store), pull route-specific code back under its route, kill barrels, fix premature promotion to shared modules, rename vague *.utils.ts files, or make a codebase more colocated and AI-navigable. This is the audit counterpart to colocation-first (which places code as you write it).
---

# Improve Codebase Colocation

Surface placement friction and propose **colocation moves** — relocations that pull code which changes together into one place. The aim is locality: when a feature changes, you edit one folder, not five.

The audit counterpart to the `colocation-first` skill. Where `colocation-first` places code as you write it, this skill finds code that's already in the wrong place.

## The question every candidate answers

> When this feature changes, how many places must I understand and edit?

Surface a candidate when that number is greater than **one** because of *where the code lives* — not because of how deep its modules are. (Depth is the sibling skill `improve-codebase-architecture`'s job; don't re-litigate it here.)

## Glossary

Use these terms exactly. The canonical definitions — with the worked premium-ads example and every naming rule — live in colocation-first's references; treat them as the source of truth and don't drift:

- [`../colocation-first/references/route-owned-modules.md`](../colocation-first/references/route-owned-modules.md)
- [`../colocation-first/references/glossary.md`](../colocation-first/references/glossary.md)

The terms you'll lean on most:

- **Colocation** — code that changes together lives together.
- **Route-owned module** — route-specific behavior kept under the route, behind one private `_<domain>/` folder.
- **Concept folder vs technical bucket** — group by the concept that changes together (`premium-ads/`), never by file kind (`_components/`, `_services/`, `_hooks/`) — and not those buckets pushed one level deeper either.
- **Module interface file** — a domain-named file outside callers may import directly; public to the route/module, not the whole app.
- **`internal/`** — a module's private implementation; nothing outside imports it. Add it only when enough hidden files justify it.
- **Barrel** — an `index.ts` / `export *` re-export hub. We don't use them.
- **Promotion** — moving a module to `src/modules/<domain>/` once a *second* route actually depends on it.
- **Deletion test** — imagine deleting the feature. If it should mostly delete one folder, that folder earns its keep.

## Process

### 1. Explore

Map the route tree and the shared roots (`src/services`, `src/model`, `src/hooks`, `src/store`, `src/components`, `src/lib`, `src/modules`) first. An Explore sub-agent works well for walking the tree without flooding context.

Hunt these signals — most are greppable:

- **Scattered feature** — one concept split across `src/services/X`, `src/model/X`, `src/hooks/useX`, `src/store/X`. Changes-together not living-together. (Strongest signal in a root-by-kind layout.)
- **Technical buckets** — `_components/`, `_services/`, `_hooks/`, `_model/`, `_utils/` under a route — or those same buckets pushed one level deeper inside a `_<domain>/`.
- **Premature promotion** — a `src/modules`/`src/services` module imported by exactly one route → belongs under that route.
- **Barrels** — `index.ts` / `export *` hubs that blur seams and slow jump-to-file.
- **Vague role suffixes** — `*.utils.ts`, `*.helpers.ts`, `*.service.ts`, `*.domain.ts` — usually a sign the concept needs a sharper name.
- **Cross-route imports** — a route reaching into another route's private `_<domain>/` (a promotion signal, never a license to import internals).
- **Bloated route folder** — many files directly under a route instead of behind one `_<domain>/`.
- **`internal/` misuse** — created for a single file, or absent while raw API/response shapes leak into a module's public surface.

**Filter false positives with the deletion test and the promotion rule.** A `src/lib/*` adapter or a genuinely shared `src/components/ui/*` used by many routes is correctly shared — leave it. One caller = colocate; two+ routes = legitimately shared. Present reuse, not hypothetical.

### 2. Present candidates as an HTML report

Write a self-contained HTML file to the OS temp dir so nothing lands in the repo. Resolve the temp dir from `$TMPDIR`, falling back to `/tmp` (or `%TEMP%` on Windows), and write to `<tmpdir>/colocation-review-<timestamp>.html` so each run gets a fresh file. Open it (`open` on macOS, `xdg-open` on Linux, `start` on Windows) and tell the user the absolute path.

Tailwind + Mermaid via CDN. Each candidate gets a **before/after file-tree diagram** — scattered tree → one colocated `_<domain>/` tree. See [HTML-REPORT.md](HTML-REPORT.md) for the scaffold, diagram patterns, and styling.

Each candidate card carries: **Files**, **Problem** (one sentence), **Solution** (one sentence), **Wins** (bullets in glossary terms), a **signal tag** (`scattered-feature`, `technical-bucket`, `premature-promotion`, `barrel`, `vague-suffix`, `cross-route-import`, `bloated-route`, `internal-misuse`), and a **recommendation strength** badge (`Strong`, `Worth exploring`, `Speculative`). End with a **Top recommendation** section.

Do NOT start moving files yet. After the file is written, ask the user: "Which of these would you like to explore?"

### 3. Grilling loop

Once the user picks a candidate, walk the move with them:

- Is this **colocation** (one route owns it → under the route) or **promotion** (two+ routes → `src/modules/<domain>/`)?
- What's the folder named, domain-first? What becomes the **module interface file**? What's hidden in `internal/` — and is there enough to justify `internal/` at all?
- Which files move, which imports rewrite, which barrels die, which vague names get sharpened.
- Does the **deletion test** hold for the resulting folder?

Side effects happen inline as decisions crystallize — if the move surfaces a cross-route dependency, settle whether it's a promotion before touching files.

### 4. Execute the move

After grilling locks the shape, perform the relocation — it's mechanical and safe. See [RELOCATION.md](RELOCATION.md) for the order of operations, import rewriting, barrel removal, and verification. A move is a move: don't change behavior on the way.
