# HTML Report Format

The colocation review is a single self-contained HTML file in the OS temp directory. Tailwind and Mermaid both come from CDNs. The workhorse diagram here is a **hand-built two-column file tree** — scattered on the left, colocated on the right. Mermaid handles the graph-shaped cases (who-imports-what, cross-route leaks); don't force it on file trees, monospace `<pre>` reads better.

## Scaffold

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <title>Colocation review — {{repo name}}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script type="module">
      import mermaid from "https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs";
      mermaid.initialize({ startOnLoad: true, theme: "neutral", securityLevel: "loose" });
    </script>
    <style>
      /* small custom layer: highlight moved files, fade the folders they leave */
      .scattered { color: #dc2626; }   /* a file living in the wrong place */
      .colocated { color: #059669; }   /* where it lands */
      .leak { stroke: #dc2626; }       /* a cross-route import */
      .tree { white-space: pre; }
    </style>
  </head>
  <body class="bg-stone-50 text-slate-900 font-sans">
    <main class="max-w-5xl mx-auto px-6 py-12 space-y-12">
      <header>...</header>
      <section id="candidates" class="space-y-10">...</section>
      <section id="top-recommendation">...</section>
    </main>
  </body>
</html>
```

## Header

Repo name, date, and a compact legend: red path = file living in the wrong place, green path = where it lands, dashed red arrow = cross-route import, solid box = a route-owned module folder. No introduction paragraph — straight into the candidates.

## Candidate card

The diagram carries the weight. Prose is sparse and uses the glossary terms without ceremony.

Each candidate is one `<article>`:

- **Title** — short, names the move (e.g. "Colocate saved-search under the search route").
- **Badge row** — recommendation strength (`Strong` = emerald, `Worth exploring` = amber, `Speculative` = slate), plus a signal tag (`scattered-feature`, `technical-bucket`, `premature-promotion`, `barrel`, `vague-suffix`, `cross-route-import`, `bloated-route`, `internal-misuse`).
- **Files** — monospaced list of what moves, `font-mono text-sm`.
- **Before / After diagram** — the centrepiece. Two columns, side by side. See patterns below.
- **Problem** — one sentence. What's scattered or misplaced.
- **Solution** — one sentence. Where it lands.
- **Wins** — bullets, ≤6 words each, in glossary terms. e.g. "locality: one folder to edit", "kills a barrel", "deletion test now holds".
- **Promotion callout** (if applicable) — one line in an amber box when the move is a promotion to `src/modules` (needs a second real caller).

No paragraphs of explanation. If the diagram needs a paragraph to be understood, redraw the diagram.

## Diagram patterns

Pick the pattern that fits the candidate. Mix them.

### Two-column file tree (the workhorse)

Left column: the current tree with the feature's files highlighted `.scattered` (red) across `src/services/`, `src/model/`, `src/hooks/`, `src/store/`. Right column: the same files pulled into one `_<domain>/` folder, highlighted `.colocated` (green). Render as monospace `<pre class="tree">` inside Tailwind cards so the indentation reads as a real tree.

```html
<div class="grid grid-cols-2 gap-4">
  <div class="rounded-lg border border-slate-200 bg-white p-4">
    <div class="text-xs uppercase tracking-wider text-slate-400 mb-2">before — scattered</div>
    <pre class="tree text-sm">src/
├── services/<span class="scattered">saved-search-api.ts</span>
├── model/<span class="scattered">saved-search.ts</span>
├── hooks/<span class="scattered">use-saved-search.ts</span>
└── store/<span class="scattered">saved-search-store.ts</span></pre>
  </div>
  <div class="rounded-lg border border-emerald-200 bg-white p-4">
    <div class="text-xs uppercase tracking-wider text-slate-400 mb-2">after — colocated</div>
    <pre class="tree text-sm">_search/
└── <span class="colocated">saved-search/</span>
    ├── saved-search.ts
    ├── saved-search.actions.ts
    └── internal/
        └── saved-search-api-adapter.server.ts</pre>
  </div>
</div>
```

### Mermaid import graph (for premature promotion and cross-route leaks)

Use a Mermaid `flowchart` when the point is "only one route imports this shared module" or "route A reaches into route B's `internal/`." Colour the offending edge red.

```html
<div class="rounded-lg border border-slate-200 bg-white p-4">
  <pre class="mermaid">
    flowchart LR
      R[pretraga route] -- imports --> M[src/modules/saved-search]
      classDef lonely stroke:#dc2626,stroke-width:2px;
      class M lonely
  </pre>
</div>
```

One arrow into a "shared" module is the tell: it was promoted too early. Two+ arrows from different routes means the promotion is real — don't flag it.

### Count strip (good for bloated route / barrel)

A thin horizontal strip of cells, one per file directly under a route (or per `export *` line in a barrel). Before: a long strip. After: one cell labelled with the `_<domain>/` folder (or the handful of direct imports that replace the barrel).

## Style guidance

- Lean editorial, not corporate-dashboard. Generous whitespace. `font-serif` for headings works well with stone/slate.
- Colour sparingly: emerald for "lands here", red for "wrong place" / leaks, amber for promotion warnings.
- Keep diagrams ~320px tall so before/after sits comfortably side by side without scrolling.
- `text-xs uppercase tracking-wider` for tree-section labels — they should read as schematic, not as UI.
- The only scripts are the Tailwind CDN and the Mermaid ESM import. The report is otherwise static — no app code, no interactivity beyond Mermaid's own rendering.

## Top recommendation section

One larger card. Candidate name, one sentence on why, anchor link to its card. That's it.

## Tone

Plain English, concise — the architectural nouns come straight from colocation-first's glossary.

**Use exactly:** colocation, route-owned module, module interface file, internal, barrel, promotion, concept folder, technical bucket, deletion test, locality, leverage, seam.

**Never substitute:** "feature folder" (say route-owned module) · "index file" when you mean barrel · "shared" used loosely (a thing is shared only when two+ routes import it).

**Phrasings that fit the style:**

- "saved-search is scattered across four technical buckets."
- "Colocate under `_search/` — one folder changes together."
- "Promoted too early: one route imports it."
- "Kill the barrel; import the interface file directly."

**Wins bullets** name the gain in glossary terms: *"locality: one folder to edit"*, *"deletion test now holds"*, *"removes a cross-route import"*, *"barrel gone, jump-to-file direct"*. Don't write *"cleaner"* or *"better organized"* — those aren't glossary terms and don't earn their place.

No hedging, no throat-clearing, no "it's worth noting that…". If a sentence could be a bullet, make it a bullet. If a bullet could be cut, cut it. If a term isn't in the colocation-first glossary, reach for one that is.
