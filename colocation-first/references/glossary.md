# Glossary — colocation-first

> The working vocabulary for placing and naming code in this codebase. Skim it before a
> structure discussion or a PR review so we all mean the same thing. Definitions are written
> for *how we use each term here*.

## Core concepts (the philosophy)

| Term | What it means here | Example |
|---|---|---|
| **Module** | A unit with a small public **interface** and a hidden **implementation**. May be a single file or a folder. | `premium-ads/` — or just `premium-search-ads.ts` |
| **Interface** | Everything a caller must know to use the module correctly — the exported functions/types **plus** invariants, error modes, ordering, config. Not just the signature. | `getPremiumSearchAds(filter)` and its placement-ordered guarantee |
| **Implementation** | The code the interface hides; callers should not need to read it. | the fetch + mapping inside `premium-ads/internal/` |
| **Depth** | How much behavior sits behind how small an interface. **Deep** = small interface, big behavior. **Shallow / pass-through** = interface almost as complex as the implementation (pure indirection). Prefer deep. | `getSearchResults(query)` hiding endpoints, params, and mapping |
| **Seam** | Where an interface lives — a place you can change behavior without editing callers. | the `search-results.ts` boundary |
| **Adapter** | A concrete implementation that satisfies an interface at a seam. | `internal/premium-search-api-adapter.server.ts` |
| **Leverage** | What callers gain from depth: a lot of capability for little they must learn. | a page calls `getSearchResults(filter)` and ignores all retrieval detail |
| **Locality** | What maintainers (and AI) gain from depth: change, bugs, and knowledge in one place. | everything about premium ads lives in `premium-ads/` |

## Tests we decide with

| Heuristic | How to use it |
|---|---|
| **Deletion test** | Imagine deleting the module/folder. Complexity **reappears scattered across callers** → it earned its keep (keep or deepen it). Complexity **just vanishes** → it was a pass-through (delete it). Use it for folder-vs-flat and "is this seam real?". |
| **One adapter = hypothetical seam · two = real seam** | Don't create an abstraction — or a `src/modules` extraction — until something genuinely varies, or a second caller actually exists. |

## Applied terms (how we name and place things)

| Term | What it means here | Example |
|---|---|---|
| **Colocation** | Keep code next to the feature/route that owns it — code that changes together lives together. | search behavior under `_search/` |
| **Route-owned module** | Route-specific behavior kept under the route, behind one private `_<domain>/` folder. | `pretraga/.../_search/` |
| **Module interface file** | A domain-named file outside callers may import directly because it is a stable capability. *Public* means public to the route/module, not the whole app. | `premium-ads/premium-search-ads.ts` |
| **`internal/`** | A module's private implementation; nothing outside the module imports from it. Add it only when enough hidden files justify the structure. | `premium-ads/internal/` |
| **Concept folder vs technical bucket** | Group by the concept that changes together (good), not by file type. Buckets like `_components/`, `_services/`, `_hooks/` — or those same buckets pushed one level deeper — are the anti-pattern. | `premium-ads/` (concept) vs `_components/` (bucket) |
| **Barrel** | An `index.ts` / `export *` re-export hub. We don't use them — import directly from the interface file. A central module file is allowed only if it owns real behavior. | avoid `premium-ads/index.ts` |
| **Promotion** | Moving a module from route-owned to `src/modules/<domain>/` once reuse is real (a second route depends on it). | filter-url parsing → `src/modules/search/` |
| **Role suffix** | A suffix after the domain concept that signals a file's role: `.types.ts`, `.actions.ts`, `.server.ts` (pair with `import 'server-only'`), `.client.ts`, `.test.ts`, `-adapter.server.ts`. Avoid vague ones (`.utils.ts`, `.helpers.ts`, `.service.ts`). | `premium-search-api-adapter.server.ts` |

---

**See also.** These terms applied in full, with the worked premium-ads example: [`route-owned-modules.md`](route-owned-modules.md). The audit-time counterpart skill: `improve-codebase-colocation` (placement audit); for depth audits, see `improve-codebase-architecture`.
