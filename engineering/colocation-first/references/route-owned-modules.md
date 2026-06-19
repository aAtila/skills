# Route-owned modules

## Why this exists

Route colocation is one of the strongest tools we have for keeping product behavior understandable. When a route owns behavior, the easiest place to understand and change that behavior should be inside that route.

At the same time, colocating everything directly under a route can bloat the route tree. A route folder full of technical buckets such as `_components`, `_services`, `_hooks`, `_model`, and `_utils` makes the routing structure harder to scan and turns the route into a hybrid of several competing organization styles.

This concept keeps the benefits of colocation without letting route folders become junk drawers.

## Decision

Use **route-owned modules**: keep route-specific behavior under the route, but place it behind one private, domain-named folder.

For example, the search route should prefer this shape:

```txt
pretraga/[transactionType]/[[...otherSegments]]/
├── page.tsx
├── loading.tsx
├── error.tsx
└── _search/
    ├── search-page.tsx
    ├── search-page-data.ts
    ├── search-metadata.ts
    ├── search-results/
    ├── premium-ads/
    ├── map-search/
    ├── search-filters/
    └── saved-search/
```

The route folder stays clean, while the route-owned implementation remains close to the route that owns it.

## Why not move everything to `src/modules`?

Moving route behavior into root-level `src/modules` can make the route tree look cleaner, but that cleanliness is often misleading.

If the search route is in `app/` while its behavior lives in `src/modules/search`, the route is no longer understandable from the route folder. A maintainer has to jump away from the route to understand the route.

That weakens **locality**.

Root-level `src/modules` should be reserved for modules that are genuinely shared across multiple routes or product areas. It should not become the default place to put route-specific code just because the route folder feels large.

## Why not keep everything directly under the route?

Pure colocation can also go too far:

```txt
pretraga/[transactionType]/[[...otherSegments]]/
├── page.tsx
├── _components/
├── _services/
├── _hooks/
├── _model/
└── _utils/
```

This keeps files close to the route, but organizes them by technical kind instead of domain concept. Understanding one concept often requires bouncing across several folders.

Instead, organize by the concept that changes together.

```txt
_search/
├── premium-ads/
├── search-results/
├── map-search/
├── search-filters/
└── saved-search/
```

Do not move the same technical buckets one level deeper:

```txt
_search/
├── components/
├── services/
├── hooks/
└── utils/
```

That keeps the same shallow modules and only hides them under a new folder.

## Module vocabulary

Terms used throughout this doc — **module, interface, implementation, seam, adapter, leverage, locality**, plus applied terms like **module interface file**, **`internal/`**, **barrel**, and **promotion** — are defined once in [`glossary.md`](glossary.md). This doc uses them consistently.

A route-owned module should be deep enough to provide leverage and locality. Avoid creating folders or seams that only move complexity around.

A route-owned module is not a folder pattern. It is a behavior-hiding module. The folder shape is only useful when it gives callers a smaller interface and maintainers better locality.

## Module interface files

A module interface file is a file at a module seam that outside callers are allowed to import directly because it represents a stable domain capability.

Public does not mean globally public. It means public to the surrounding route/module.

A module interface file should:

1. Have a domain name.
2. Own useful behavior or invariants.
3. Let callers depend on it without learning its internals.
4. Have a small, intentional export surface.
5. Survive internal refactors without forcing caller changes.

Examples inside a search route:

```txt
_search/search-results/search-results.ts
_search/premium-ads/premium-search-ads.ts
_search/map-search/search-map-pins.ts
_search/search-filters/search-filter-form.tsx
_search/saved-search/saved-search.ts
```

Private implementation details can live under `internal/` when there are enough hidden files to justify the extra structure:

```txt
_search/premium-ads/internal/premium-ads-adapter.ts
_search/premium-ads/internal/map-premium-ad.ts
```

Do not create `internal/` by default. A single module interface file with private functions is often enough.

External callers should not import from `internal/`.

## No barrel files

Avoid `index.ts` and avoid `export *`.

Uncontrolled barrel files make it too easy to leak internals, create accidental cycles, and blur seams. They also make navigation worse: jumping to an import often lands on a re-export file before reaching the real implementation.

Prefer direct imports from module interface files:

```ts
import { getPremiumSearchAds } from './premium-ads/premium-search-ads';
import { getSearchResults } from './search-results/search-results';
```

If a module needs a central file, it should own real behavior. It should not exist merely to re-export other files.

## Folder or flat file?

A module can be a single file. Do not create a folder automatically.

Use a flat file when the concept is small:

```txt
_search/
├── search-results.ts
├── search-map-pins.ts
└── premium-search-ads.ts
```

Create a folder when the concept has enough implementation to benefit from locality:

```txt
_search/
└── premium-ads/
    ├── premium-search-ads.ts
    ├── premium-search-ads.test.ts
    ├── premium-ads-section.tsx
    ├── premium-ad-card.tsx
    └── internal/
        ├── premium-ads-adapter.ts
        └── map-premium-ad.ts
```

Use the deletion test: if removing the feature should mostly delete one folder, the folder is probably earning its keep.

## Naming conventions

Use file names to communicate both the domain concept and, when useful, the file's role.

Prefer this shape:

```txt
<domain-concept>[-specific-behavior][.<role>].ts
```

Examples:

```txt
premium-search-ads.ts
premium-search.types.ts
premium-search-ad-selection.ts
premium-search-ad-selection.test.ts
premium-search-api-adapter.server.ts
premium-search-query-options.client.ts
saved-search.actions.ts
```

The domain concept comes first. The role suffix is useful only when it clarifies how the file participates in the module.

### Useful role suffixes

Use these when they carry real meaning:

- `.types.ts` — shared module contract types.
- `.actions.ts` — Next.js Server Actions.
- `.server.ts` — server-only code. Prefer pairing this with `import 'server-only';`.
- `.client.ts` — browser-only code.
- `.test.ts` — tests.
- `-adapter.server.ts` / `-adapter.client.ts` — a concrete adapter behind a seam.

### Types files

A `*.types.ts` file is allowed when it improves locality by collecting shared module contract types in one place.

Good:

```txt
premium-ads/
├── premium-search.types.ts
├── premium-search-ads.ts
├── premium-search-ad-selection.ts
└── premium-ads-section.tsx
```

`premium-search.types.ts` should contain types that define the module interface or shared vocabulary:

```ts
export type PremiumSearchAd = ...;
export type PremiumSearchPlacement = ...;
export type PremiumSearchAdsResult = ...;
```

Do not move every local type into the shared types file. Types used by only one file should usually stay in that file:

```tsx
type PremiumAdCardProps = {
  ad: PremiumSearchAd;
};
```

Keep private adapter types behind `internal/`:

```txt
premium-ads/internal/premium-search-api.types.ts
```

This keeps raw response/request shapes from leaking into the public module interface.

### Avoid vague role suffixes

Avoid files like:

```txt
premium-search.utils.ts
premium-search.domain.ts
premium-search.helpers.ts
premium-search.service.ts
```

These names usually hide unclear ownership. Prefer naming the behavior directly:

```txt
select-premium-search-ads.ts
map-premium-search-ad.ts
build-premium-search-request.ts
```

A file named `*.utils.ts` is usually a sign that the module's concepts need sharper names.

## Premium ads example

Premium ads are a good example of a route-owned submodule.

If premium ads in search only means one retrieval function, keep it flat:

```txt
_search/premium-search-ads.ts
```

If premium ads has retrieval rules, selection rules, placement rules, display behavior, tracking, experiments, fallback behavior, mapping, and tests, give it a folder:

```txt
_search/premium-ads/
├── premium-search.types.ts
├── premium-search-ads.ts
├── premium-search-ads.test.ts
├── premium-search-ad-selection.ts
├── premium-ads-section.tsx
├── premium-ad-card.tsx
└── internal/
    ├── premium-search-api.types.ts
    ├── premium-search-api-adapter.server.ts
    └── map-premium-search-ad.ts
```

Keep it under the search route while it is specifically about premium ads inside search results. Promote it to `src/modules` only when it becomes a shared concept used by multiple routes or product areas.

## Promotion rule

Start route-owned.

Promote to `src/modules` only when reuse is real:

- multiple routes depend on the same behavior
- the module has a stable interface independent of one route
- moving it improves locality instead of weakening it
- callers gain leverage from a shared seam

Do not promote because of hypothetical reuse or because a route folder feels large.

## Cross-route imports

Code outside a route-owned module should not import its internal implementation.

If another route needs the behavior, treat that as a promotion signal. Either promote the module to a shared location with a stable interface, or extract a smaller shared module that both routes can depend on.

Do not solve cross-route reuse by importing from another route's private folder. That weakens locality for both routes: the caller depends on implementation details, and the owning route can no longer change its internals freely.

## Recommended structure pattern

Use this shape for substantial route behavior:

```txt
route/
├── page.tsx
├── loading.tsx
├── error.tsx
└── _route-domain/
    ├── route-page.tsx
    ├── route-page-data.ts
    ├── concept-a/
    │   ├── concept-a.ts
    │   ├── concept-a.test.ts
    │   └── internal/
    ├── concept-b/
    │   ├── concept-b.tsx
    │   └── internal/
    └── shared-within-route/
```

For the search route, use `_search` as the route-owned module root.

## Summary

The goal is not to make the route tree artificially small. The goal is to make each route understandable from its own folder while keeping the route tree navigable.

Use route-owned modules for route-specific behavior. Use root-level modules for genuinely shared behavior. Organize by domain concept, not technical kind. Avoid barrels. Prefer module interface files with direct imports. Create folders only when they improve locality.
