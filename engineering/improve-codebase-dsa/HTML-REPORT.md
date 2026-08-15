# HTML Report Format

The DSA review is a single self-contained HTML file in the OS temp directory. Tailwind and Mermaid both come from CDNs. The workhorse here is a **state matrix** — a hand-built truth table of the current boolean/nullable combinations, invalid rows struck out, collapsing into a union of the few valid states. Mermaid handles the graph-shaped case (state machines with transitions); don't force it on truth tables, an HTML `<table>` reads better.

## Scaffold

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <title>DSA review — {{repo name}}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script type="module">
      import mermaid from "https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs";
      mermaid.initialize({ startOnLoad: true, theme: "neutral", securityLevel: "loose" });
    </script>
    <style>
      /* small custom layer: strike invalid combinations, mark the valid states */
      .invalid { color: #dc2626; text-decoration: line-through; }  /* a state the domain forbids */
      .valid { color: #059669; }                                   /* a state that should exist */
      .tag { stroke-dasharray: 4 4; }                              /* a discriminant / union tag */
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

Repo name, date, and a compact legend: red struck row = a state the domain forbids, green row = a valid state, dashed box = a union tag / discriminant. No introduction paragraph — straight into the candidates.

## Candidate card

The diagram carries the weight. Prose is sparse and uses the vocabulary without ceremony.

Each candidate is one `<article>`:

- **Title** — names the re-representation (e.g. "Collapse the upload flags into an `UploadState` union").
- **Badge row** — strength (`Strong` = emerald, `Worth exploring` = amber, `Speculative` = slate), plus a signal tag (`boolean-soup`, `optional-soup`, `shape-guessing`, `branch-duplication`, `scan-in-loop`, `stale-state`).
- **Files** — monospaced `file:line` list, `font-mono text-sm`.
- **Invalid states today** — the crux. The forbidden combinations the current representation permits, named plainly.
- **Before / After diagram** — the centrepiece. See patterns below.
- **Problem** — one sentence. What the loose representation permits.
- **Solution** — one sentence. The proposed representation.
- **Wins** — bullets, ≤6 words each, in vocabulary terms. e.g. "3 invalid states gone", "one tag, no re-guessing", "O(1) lookup replaces scan".
- **Migration & risk** — one line: smallest credible scope, plus the regression risk of the re-representation (a behavior-preserving change, so name what shifts at the boundary — serialization, persisted shapes, API contracts).

No paragraphs of explanation. If the diagram needs a paragraph to be understood, redraw the diagram.

## Diagram patterns

Pick the pattern that fits the candidate. Mix them.

### State matrix (the workhorse — for `boolean-soup` / `stale-state`)

Left: an HTML `<table>` of every combination of the current booleans/nullables, with the domain-forbidden rows `.invalid` (struck red). Right: the discriminated union those valid rows collapse into, each variant `.valid` (green) with only its own fields.

```html
<div class="grid grid-cols-2 gap-4">
  <div class="rounded-lg border border-slate-200 bg-white p-4">
    <div class="text-xs uppercase tracking-wider text-slate-400 mb-2">before — 2³ combinations, 3 valid</div>
    <table class="text-sm font-mono">
      <thead><tr class="text-slate-400"><th class="pr-3">isLoading</th><th class="pr-3">error</th><th class="pr-3">data</th></tr></thead>
      <tbody>
        <tr class="valid"><td>true</td><td>–</td><td>–</td></tr>
        <tr class="valid"><td>false</td><td>set</td><td>–</td></tr>
        <tr class="valid"><td>false</td><td>–</td><td>set</td></tr>
        <tr class="invalid"><td>true</td><td>set</td><td>–</td></tr>
        <tr class="invalid"><td>true</td><td>–</td><td>set</td></tr>
        <tr class="invalid"><td>false</td><td>set</td><td>set</td></tr>
      </tbody>
    </table>
  </div>
  <div class="rounded-lg border border-emerald-200 bg-white p-4">
    <div class="text-xs uppercase tracking-wider text-slate-400 mb-2">after — 3 states, nothing else representable</div>
    <pre class="text-sm valid">type RequestState =
  | { status: "loading" }
  | { status: "error"; error: Error }
  | { status: "ready"; data: Data }</pre>
  </div>
</div>
```

The struck rows are the whole argument: each one is a state the code must currently guard against and the union deletes.

### State machine (Mermaid `stateDiagram-v2` — for `stale-state` / lifecycle)

Use when the point is "these transitions are the only legal moves, but the flags allow any jump." Colour illegal transitions out of the picture by simply not drawing them — the diagram shows only what the union permits.

```html
<div class="rounded-lg border border-slate-200 bg-white p-4">
  <pre class="mermaid">
    stateDiagram-v2
      [*] --> Idle
      Idle --> Uploading
      Uploading --> Ready
      Uploading --> Failed
      Failed --> Uploading
  </pre>
</div>
```

### Union split (for `optional-soup` / `shape-guessing`)

Two stacks side by side. Before: one type with a long list of optional fields, each annotated with the state it silently belongs to. After: N variants, each carrying only its own fields, tagged by a discriminant. Render as monospace `<pre>` so the field lists line up.

### Dispatch map (for `branch-duplication`)

Before: the duplicated `switch`/`if`-ladder shown once, with a note of how many call sites repeat it. After: a keyed map/registry and the single lookup that replaces every copy. A thin count strip — one cell per duplicated site — makes the leverage visible.

### Collection swap (for `scan-in-loop`)

Before: a `find()`-in-a-loop with its complexity labelled (`O(n·m)`). After: the index built once and the `O(1)` lookup. Keep it to two short code blocks with the complexity called out above each.

## Style guidance

- Lean editorial, not corporate-dashboard. Generous whitespace. `font-serif` for headings works well with stone/slate.
- Colour sparingly: emerald for valid/after, red for invalid states, amber for migration warnings.
- Keep diagrams ~320px tall so before/after sits comfortably side by side without scrolling.
- `text-xs uppercase tracking-wider` for table and diagram labels — they should read as schematic, not as UI.
- The only scripts are the Tailwind CDN and the Mermaid ESM import. The report is otherwise static — no app code, no interactivity beyond Mermaid's own rendering.

## Top recommendation section

One larger card. Candidate name, one sentence on why, anchor link to its card. That's it.

## Tone

Plain English, concise — the nouns come straight from the skill's vocabulary.

**Use exactly:** representation, invalid state, make invalid states unrepresentable, state machine, discriminated union, dispatch map, the right collection, the illegal-state test.

**Never substitute:** "flag" (say boolean, and mean the invalid state it permits) · "enum of strings" when you mean discriminated union · "refactor" for a re-representation · "cleaner" / "nicer" for a named win.

**Phrasings that fit the style:**

- "Three of eight combinations are invalid states the code guards against."
- "Collapse into a `RequestState` union — the wrong combinations stop being representable."
- "One discriminant replaces the shape-guessing at nine call sites."
- "Index built once; the `O(n·m)` scan becomes an `O(1)` lookup."

**Wins bullets** name the gain in vocabulary terms: *"3 invalid states gone"*, *"one tag, no re-guessing"*, *"scan becomes O(1) lookup"*, *"illegal transitions unrepresentable"*. Don't write *"cleaner"* or *"more robust"* — those aren't vocabulary terms and don't earn their place.

No hedging, no throat-clearing, no "it's worth noting that…". If a sentence could be a bullet, make it a bullet. If a bullet could be cut, cut it. If a term isn't in the skill's vocabulary, reach for one that is.
