# Book-Inspired Skill Briefs — Roadmap for Writer Agents

Ten skill briefs derived from a gap analysis of the existing aAtila + mattpocock skill libraries
(2026-06-12). Each brief is self-contained: a writer agent should read **this file**, the
**house-style section below**, and the named sibling skills, then write ONE skill per session.

Status:
- [ ] 1. `legacy-seams` (Feathers) — highest priority
- [ ] 2. `hotspot-analysis` (Tornhill) — most novel / most scriptable
- [ ] 3. `model-types-first` (Wlaschin)
- [ ] 4. `refactor-catalog` (Fowler)
- [ ] 5. `production-readiness` (Nygard)
- [ ] 6. `functional-core` (Normand) — lowest priority; may become a tdd reference file instead
- [ ] 7. `safe-migration` — dependency upgrades / API migrations / data migrations
- [ ] 8. `post-ship-retro` — close the loop: learnings back into CONTEXT.md / ADRs
- [ ] 9. `harvest-language` (Evans, DDD) — bootstrap CONTEXT.md + retroactive ADRs from an existing codebase
- [ ] 10. `language-drift` — keep the language layer aligned with code; detect naming inconsistencies
- [x] 11. `test-review` — read-only auditor of an existing test suite (quality smells + coverage gaps as `tdd` inputs); built 2026-07-18, beyond the original ten

---

## The pipeline map (canonical — reference this from new skills)

The flow these skills serve, as actually practiced day to day:

```
ALIGN      grill-with-docs → (prototype, to brainstorm approaches) → (handoff, for context management)
PLAN       to-prd (new/complex feature) ─or─ skip PRD for small tasks → to-issues (vertical slices)
PREPARE    legacy-seams (if blast radius untested) → tidy-first (warm-up on existing code)
BUILD      tdd, issue by issue (red → green → refactor)
VERIFY     review (see routing rule) → qa-plan (realistic UX flows — additive to unit tests, not a replacement)
SHIP       commit-me → draft-pr
MAINTAIN   improve-codebase-architecture / improve-codebase-colocation, fed by hotspot-analysis
           language-drift (periodic glossary↔code alignment sweep)
```

**The language layer** (the docs the ALIGN phase reads): `harvest-language` bootstraps
CONTEXT.md + retroactive ADRs on a brownfield repo (run once); `grill-with-docs` and
`post-ship-retro` maintain it per-change; `language-drift` is the periodic safety net for
changes that bypassed both (teammates who don't use the skills).

**The bug path** (distinct from the feature path — don't skip discipline because it's "just a fix"):
`reproduce → diagnose → failing regression test (tdd red) → fix → green → commit-me`.

**Review routing rule** (which review when):
- `aa-simplify` — always, on every non-trivial change (removal-biased pass).
- `aa-second-opinion` — risky or unfamiliar territory.
- `production-readiness` — any change crossing a process/network boundary (fetches, queues, cron, third-party scripts).
- `react-doctor` / `semantic-html` — React/markup changes respectively.

**Spike valve**: if a `to-issues` slice looks too big or too uncertain, route it through `prototype`
as a timeboxed throwaway spike first — risk reduction is a first-class outcome, like sprouting in
`legacy-seams`.

---

## House style (applies to every skill below)

Match `aAtila/skills/tidy-first/SKILL.md` — it is the canonical example. Concretely:

1. **One core discipline, stated as gates.** tidy-first is "the two gates (this is the whole
   skill)". Every new skill needs its equivalent: 1-3 hard gates / stop-rules that define when
   the skill refuses to act. A skill that always says yes is a vibe, not a skill.
2. **Frontmatter description** = trigger phrasings (including casual ones) + pipeline position
   + explicit `NOT ...` boundaries naming the sibling skills it must not be confused with.
3. **Pipeline placement section.** The libraries share an implicit pipeline:
   `pick issue → context_builder → tidy-first → tdd (red→green→refactor)` plus review-time
   skills (`aa-simplify`, `aa-second-opinion`, `qa-plan`) and sweep skills
   (`improve-codebase-architecture`, `improve-codebase-colocation`). State exactly where the
   new skill slots in and which skills it hands off to / receives from.
4. **A defined primary output** and an explicit **stop point** where the user decides
   (tidy-first stops after presenting the shortlist; it does not auto-edit).
5. **Worked examples**: one good case, one rejected case (fails a gate), one wrong-skill case
   (routed to a sibling).
6. **Boundaries section + closing checklist.**
7. **Progressive disclosure**: SKILL.md ≤ ~100 lines of body; depth goes in `references/`
   (see `colocation-first/references/` and `mattpocock tdd/*.md` for precedent).
8. **Naming**: methodology skills are unprefixed (`tidy-first`, `colocation-first`, `qa-plan`);
   `aa-` prefix is for personal workflow/review skills. All six below are methodology → unprefixed.
9. Use the `write-a-skill` skill's conventions when authoring. Credit the source book in the
   body (one quote max), the way tidy-first credits Beck.
10. **One skill per writer session.** Do not let a writer agent draft two.

---

## 1. `legacy-seams` — Working Effectively with Legacy Code (Michael Feathers)

**Essence (one line):** Make untested code *safe* to change before `tidy-first` makes it *easy*
to change: pin current behavior with characterization tests at a seam, then allow edits.

**Pipeline position:** The step that fires when tidy-first's "No tests on the blast radius?"
branch triggers. `pick issue → context_builder → legacy-seams (only if blast radius untested)
→ tidy-first → tdd`. The skill's tagline should extend Beck: *"Make the change safe, then make
the change easy, then make the easy change."*

**Core concepts the skill must encode:**
- **Legacy code = code without tests** (Feathers' definition). Not "old code".
- **Seam**: a place where you can alter behavior without editing the code in that place.
  The skill identifies seams in the blast radius (function params, module imports, constructor
  args, injection points).
- **Characterization tests**: tests that pin what the code *does*, not what it *should* do.
  Mechanics to spell out: write the assertion with a deliberately wrong expected value → run →
  copy the actual value into the expectation. If pinned behavior looks like a bug: **file an
  issue, keep the pin on actual behavior, never fix during pinning.**
- **Minimal dependency-breaking moves** (pick ~5, not all 24 from the book; put mechanics in
  `references/dependency-breaking.md`): Parameterize Function/Constructor, Extract & Override
  (or its TS equivalent: extract the dependency to an injectable param), Wrap Function,
  Subclass/Adapter at the boundary, Introduce Seam at module import (DI over module mocking).
- **Sprout method/class**: when getting the old code under test costs more than the change is
  worth, write the NEW logic TDD-style in a fresh, tested unit and call it from one place in
  the legacy code. The skill must present sprouting as a legitimate outcome, not a failure.

**Gates:**
1. **Coverage gate (the stop-rule):** no behavioral edit to legacy code until a
   characterization test pins the specific behavior the change will disturb. Mechanical,
   tool-verified moves (IDE rename) are exempt — consistent with tidy-first's existing wording.
2. **Scope gate (inherited from tidy-first):** characterize ONLY the blast radius of the
   one-sentence change. Pinning a whole module is a sweep — refuse.

**Primary output + stop point:** A *seam map* (where to inject/observe), the characterization
tests written and green, and a go/no-go recommendation: "characterized — proceed to tidy-first"
vs "too expensive to pin — sprout instead". Stop and let the user choose before any edit to
legacy code itself.

**Anti-patterns to warn against in the body:** refactoring while characterizing (two acts, two
commits — reuse tidy-first's discipline); chasing coverage % instead of pinning the disturbed
behavior; mocking everything (prefer real collaborators; seam only the awkward dependency:
network, clock, fs, randomness); fixing bugs discovered mid-pin.

**Boundaries:** `tidy-first` (assumes green tests exist — this skill creates that precondition);
`tdd` (new behavior, test-first — sprouted code is written under `tdd`); `diagnose` (you know
something is broken; here nothing is broken yet, you're making change safe); `improve-codebase-
architecture` (sweep; this is bound to one imminent change).

**Worked example to include:** an 800-line untested function needing a one-term change — show
seam choice, 2-3 characterization tests on just the disturbed path, and the sprout alternative.

---

## 2. `hotspot-analysis` — Your Code as a Crime Scene / Software Design X-Rays (Adam Tornhill)

**Essence:** Mine git history for *empirical* refactoring signals — hotspots (churn ×
complexity) and change coupling (files that change together but live apart) — and route the
findings to the existing `improve-*` skills. Adds **data** to a library that is currently all
judgment.

**Pipeline position:** A standalone, **read-only** survey skill, like `improve` /
`improve-codebase-*`. Its findings are *evidence feeds*: hotspot → candidate for
`improve-codebase-architecture`; cross-directory change coupling → candidate for
`improve-codebase-colocation`; a hotspot the user is about to touch → input to `tidy-first`.
It edits nothing.

**Form:** This is the most scriptable skill — most of the work is `git log` mining. Bundle:
- `scripts/hotspots.sh` — `git log --numstat` over a time window → churn per file; complexity
  proxy = **indentation-based (whitespace) complexity** (Tornhill's own language-agnostic
  metric — no parser needed) or LOC as fallback; output = churn × complexity ranking.
- `scripts/change-coupling.sh` — co-commit pairs with support (≥ N shared commits) and
  confidence (% of A's commits that include B) thresholds.
- Follow the `mac-disk-hygiene` precedent: scripts measure (read-only), SKILL.md interprets.
- Optional: an HTML report following the existing `HTML-REPORT.md` pattern in the `improve-*`
  skills.

**Critical parameters the skill must get right (this is where naive versions fail):**
- **Time window**: default to the last 6–12 months; history before a big refactor/rename lies.
  Make the window an explicit first question.
- `--follow`/rename detection on; **exclude** lockfiles, generated code, vendored dirs,
  snapshots; treat test⇄source coupling as *expected* (filter it from coupling findings).
- Normalize for file age (a 5-year-old file accumulates churn innocently).

**Gates:**
1. **Evidence gate:** a finding needs minimum support (e.g. ≥ 5 commits in window for a
   hotspot, ≥ 5 co-commits and ≥ 50% confidence for coupling) — below that, stay silent.
2. **"Data proposes, code disposes":** never recommend action from numbers alone. For each
   top finding, READ the file and confirm the complexity is real (config files and i18n
   churn legitimately). The output must show *both* the metric and the code-level confirmation.

**Primary output + stop point:** A ranked findings report: finding → evidence (numbers) →
code-level confirmation → routed recommendation (`improve-codebase-architecture` item,
`improve-codebase-colocation` item, or "watch, no action"). Stops there — like the `improve`
skill, strictly read-only on source.

**Out of scope (state explicitly):** per-author knowledge maps / bus-factor analysis (team
dynamics and privacy — keep it out); whole-history-since-init analysis; treating churn as
guilt by itself.

**Boundaries:** `improve-codebase-architecture` / `improve-codebase-colocation` (judgment
sweeps — this skill supplies their evidence); `aa-commit-clarity` (commit hygiene going
forward; this reads history backward); `diagnose` (a specific bug, not statistical signals).

---

## 3. `model-types-first` — Domain Modeling Made Functional (Scott Wlaschin)

**Essence:** Before implementing a feature with non-trivial domain state, design the domain
*types* (TypeScript) so that illegal states are unrepresentable — then implementation becomes
filling in total functions between honest types.

**Pipeline position:** After spec/alignment (`aa-design-spec` / `grill-with-docs` /
`grill-me`), before `tidy-first`/`tdd`. It extends the DDD thread (ubiquitous language,
CONTEXT.md) *into the type system*. Trigger condition: the feature has domain state with
rules — statuses, transitions, mutually exclusive fields — not for plumbing/UI-only changes.

**Core moves to encode (TypeScript-flavored — this matters for the audience):**
- **Discriminated unions over flag soup**: replace `{status: string, paidAt?: Date,
  cancelReason?: string}` with `Pending | Paid {paidAt} | Cancelled {reason}`.
- **Smell list to hunt for** (give it as a checklist): optional fields that are "required
  sometimes"; booleans that travel in packs; two `string` ids in one signature; status +
  nullable-data pairs; primitive obsession on validated values (email, money).
- **Branded/newtype ids and validated values** — but see the YAGNI gate below.
- **Parse, don't validate**: validate once at the boundary (zod/valibot `parse` → return the
  *narrowed domain type*), trust types everywhere inside. No re-validation in the core.
- **Errors as values** for *expected* failure paths (Result/union return), exceptions only for
  bugs.
- **Workflows as type signatures first**: write `placeOrder: (cmd: UnvalidatedOrder) =>
  Result<OrderPlaced, PlaceOrderError>` style signatures before any body.
- Harvest names from CONTEXT.md / ubiquitous language; if a needed term is missing there,
  flag it back to `grill-with-docs` territory.

**The interactive part (this is what makes it a skill, not a lecture):** after drafting the
state enumeration, **grill the user** in the `grill-me` style with illegal-state questions:
"Can an order be both cancelled and paid?", "Is `shippedAt` ever set while status is draft?"
Each answer either eliminates a state or becomes a documented invariant.

**Gates:**
1. **Types-only gate:** the skill produces type declarations and function *signatures* only —
   zero implementation logic. If you're writing a function body, you've left the skill.
2. **YAGNI/brand gate** (aligns with `aa-simplify`): brand a primitive only when confusion is
   *plausible in an actual signature* (two ids side by side); union only states that are
   *genuinely* exclusive per the user's answers. Do not produce a cathedral of newtypes.

**Primary output + stop point:** a compilable types file (proposed, not yet placed —
placement per `colocation-first`), the list of illegal states eliminated (before/after), and
open invariant questions. Stop; hand to `tdd` (whose `interface-design.md` it complements at
the domain level rather than function level).

**Boundaries:** `grill-with-docs` (language & decisions; this is type mechanics);
`tdd/interface-design` (single-function interfaces; this is the domain model across the
feature); `aa-design-spec` (the what/why; this is the shape).

---

## 4. `refactor-catalog` — Refactoring (Martin Fowler)

**Essence:** Execute ONE medium-sized, *named*, behavior-preserving refactoring in safe
mechanical steps. The deliberate middle of the spectrum: bigger than a tidy-first tidying,
smaller than an `improve-codebase-architecture` redesign. (Beck himself positions Tidy First
as the small end of Fowler's continuum — say so in the body.)

**Entry points (encode all three):**
1. A tidy-first candidate failed its scope gate as "too large" but is genuinely needed for the
   change → routed here instead of being smuggled in.
2. The refactor step of `tdd`'s red-green-refactor found a real smell post-green.
3. The user names a smell directly ("this conditional is out of hand").

**Core content:**
- `references/catalog.md` with **12–15 high-leverage refactorings**, each with Fowler's
  *mechanics* (the tiny steps, run tests between each). Suggested set: Extract Function,
  Inline Function, Extract Class, Move Function, Rename (mechanical), Introduce Parameter
  Object, Replace Primitive with Object, Decompose Conditional, Replace Conditional with
  Polymorphism, Replace Nested Conditional with Guard Clauses (note the overlap: at small
  scale this is a tidy-first tidying), Replace Temp with Query, Encapsulate Collection,
  Separate Query from Modifier, Split Phase. Do NOT reproduce the book — terse mechanics,
  TS-flavored examples.
- A smell → refactoring routing table in SKILL.md (Long Function → Extract Function/Split
  Phase; Shotgun Surgery → Move Function — and note shotgun surgery is what
  `hotspot-analysis` change-coupling detects empirically).

**Gates:**
1. **Test gate:** suite green AND the refactored surface is covered. If not covered →
   **route to `legacy-seams` first** (this hand-off is the keystone of the suite; make it loud).
2. **One named refactoring per commit.** Mid-refactor behavior fixes are forbidden — if a bug
   surfaces, finish or revert the refactoring, then fix in a separate commit (`diagnose`).
3. **Wrong-abstraction guard** (Sandi Metz — cite "The Wrong Abstraction"): a refactoring that
   *introduces* an abstraction needs ≥ 2–3 concrete existing call sites as evidence.
   Duplication is cheaper than the wrong abstraction; prefer *inlining* a bad abstraction back
   to duplication before re-abstracting along better lines.

**Primary output + stop point:** name the smell, name the chosen refactoring, list the
mechanical steps, state the test checkpoint after each — then stop for user approval before
executing. After execution: own commit, suite green, hand back to whichever skill called it.

**Boundaries:** `tidy-first` (smaller, pre-change, gated on an imminent behavioral change —
this skill can run standalone on an agreed smell); `improve-codebase-architecture` (finds and
prioritizes opportunities; this executes one); `aa-simplify` (removal-biased review; this is
transformation); `legacy-seams` (precondition supplier).

---

## 5. `production-readiness` — Release It! (Michael Nygard)

**Essence:** Review a change that crosses a process/network boundary for survival under
*partial failure* before it ships. `qa-plan` asks "does it do what we intended?"; this asks
"what happens when everything around it misbehaves?"

**Pipeline position:** Review-time, alongside `qa-plan` / `aa-second-opinion` /
`aa-simplify`. Read-only; output is findings, not edits. Trigger: before PR/deploy of anything
with outbound calls, queues, caches, cron, or third-party scripts.

**Core review frame — interrogate every *integration point* (Nygard: integration points are
the #1 killer):** for each outbound call / boundary crossing, ask in order:
1. **Timeout?** (No call without one. What is it, and is it shorter than the caller's own?)
2. **Slow vs down**: what happens when the dependency is *slow* (the worse case — threads/
   requests pile up) — not just when it errors?
3. **Retry policy**: bounded? backoff + jitter? Is the operation **idempotent** if retried?
4. **Retry storms / self-inflicted DoS**: cache stampede, thundering herd on recovery.
5. **Bulkheads**: is one slow dependency able to exhaust a shared pool/queue/event loop?
6. **Unbounded result sets**: queries/responses with no LIMIT/pagination.
7. **Graceful degradation**: is there a designed fallback (stale cache, hidden widget,
   default), or does the page/feature take the whole experience down with it?
8. **Observability**: when it fails at 3am, can you tell WHICH integration point failed
   (log/metric per boundary, not a generic 500)?

**Scale-to-context rule (critical — this is how the skill avoids enterprise cosplay):** first
detect what kind of system this is and apply the relevant subset. For a frontend/Next.js
codebase: fetch timeouts + AbortController, loading/error/empty states, fallback UI, SWR/cache
behavior on error, third-party script failure (analytics/ads/GTM blocking render), image/CDN
failure. For a service: pools, queues, circuit breakers. Do not recommend circuit breakers
for in-process calls in a monolith.

**Gates:**
1. **Concrete-trigger gate:** every finding must name a concrete, plausible trigger scenario
   ("when the geo API takes 30s...") — no speculative resilience engineering. This keeps it
   aligned with `aa-simplify` instead of at war with it.
2. **Severity by blast radius**, not by smell: rank findings by "stops the world / degrades a
   feature / cosmetic", and lead with the worst.

**Primary output + stop point:** a findings table — integration point → unhandled failure mode
→ concrete trigger → consequence → *smallest* fix — then stop for discussion (mirror
`aa-simplify`'s "findings for discussion, not direct edits" stance).

**Boundaries:** `qa-plan` (intent verification); `diagnose` (after the incident; this is
before); `aa-second-opinion` (general review; this is the failure-mode lens only);
`semantic-html`/`react-doctor` (correctness of the happy path).

---

## 6. `functional-core` — Grokking Simplicity (Eric Normand) — LOWEST PRIORITY

**Essence:** Classify code into **actions** (side effects, time/order-dependent),
**calculations** (pure: data in → data out), and **data** — then refactor toward a functional
core / imperative shell, motivated by a concrete testing pain.

**Honest direction for the writer agent — decide form first:** the smallest correct version of
this may NOT be a standalone skill. Evaluate two options and pick one:
- **Option A (preferred):** a new reference file in mattpocock's `tdd` skill
  (`tdd/functional-core.md`), wired into its "hard to test" path — because the trigger is
  almost always "this test needs heavy mocking", which is `tdd`/`mocking.md` territory.
- **Option B:** standalone skill, only if it also serves `tidy-first` as a candidate-generator
  lens ("extract calculation from action" is a legitimate tidying) and `refactor-catalog`
  (Split Phase / Separate Query from Modifier are the same move by other names).

**Core moves (whichever form):** spot the buried calculation inside an action; extract it as
data-in/data-out; push the action to the edge; never let extraction *copy* the side effect
deeper. Test the calculation with plain assertions (no mocks); the thin shell may need only
1-2 integration tests.

**Gate:** motivated by a *named, concrete* testing pain or comprehension pain — not aesthetics.
("I can't test the discount logic without mocking stripe" — good. "This file isn't functional
enough" — refuse.)

**Boundaries:** `tdd/mocking.md` (the symptom usually shows up there); `refactor-catalog`
(overlapping named moves); `aa-simplify` (this adds structure; aa-simplify removes it — note
the tension and the tiebreak: if removal solves the testing pain, remove).

---

## 7. `safe-migration` — dependency upgrades, API migrations, data migrations

**Essence (one line):** Execute wide-blast-radius, no-new-behavior changes (framework bumps,
library swaps, API/codemod migrations, schema changes) as a sequence of small, individually
revertible, mechanically-verified steps — never as one big-bang diff.

**Why it exists:** This shape of work fits neither `tdd` (no new behavior to test-drive) nor
`tidy-first` (not bound to one imminent change) nor `refactor-catalog` (not a named code-level
refactoring). It's a real chunk of weekly engineering work with no skill today.

**Pipeline position:** Standalone track, parallel to the feature pipeline. Receives from:
the user directly ("upgrade Next to 16", "replace moment with date-fns"), or `improve` /
`hotspot-analysis` findings. Hands off to `commit-me` per step and `draft-pr` at the end.
If the migration surface is untested → `legacy-seams` first (same keystone hand-off as
`refactor-catalog`).

**Core moves to encode:**
- **Inventory first**: enumerate every call site / usage before touching one (`file_search`,
  deprecation output, type errors after a trial bump on a branch). The inventory IS the plan.
- **Expand → migrate → contract** (the universal pattern): introduce the new thing alongside
  the old, move call sites over incrementally (in batches that each compile + pass tests),
  then delete the old path. Applies to APIs, config, and data schemas alike.
- **One mechanical transform per commit** — a reviewer should be able to verify a commit by
  understanding its *rule* ("every `moment(x).format(F)` → `format(x, F)`"), not by reading
  every line. Prefer codemods/scripts for >20 call sites; commit the codemod too.
- **Data migrations**: never destructive in the same deploy that changes code; old code must
  tolerate new schema and vice versa for one deploy cycle.
- **Changelog/breaking-changes reading is step zero** — dispatch an explore agent to digest
  upstream release notes rather than discovering breakage empirically.

**Gates:**
1. **No-new-behavior gate (the stop-rule):** if a desired behavior change sneaks into scope
   ("while we're at it..."), refuse — file it as an issue for the feature pipeline. A migration
   PR must be boring by construction.
2. **Revertibility gate:** every commit must leave the suite green and the app deployable.
   If a step can't be made green-to-green, the batch is too big — split it.

**Primary output + stop point:** the inventory + step plan (expand/migrate/contract phases,
batch boundaries, codemod rule per batch) — stop for user approval before executing.

**Worked examples:** good case — library swap via expand/migrate/contract in 4 commits;
rejected case — "upgrade React AND restructure the hooks while at it" (fails gate 1, split);
wrong-skill case — "this module is poorly designed, rewrite it" → `improve-codebase-architecture`.

**Boundaries:** `tdd` (new behavior); `tidy-first` (one imminent change, small); 
`refactor-catalog` (named code-level transformation within a codebase, not a dependency
boundary); `legacy-seams` (precondition supplier when the surface is untested).

---

## 8. `post-ship-retro` — close the loop after shipping

**Essence (one line):** After a feature ships (PR merged), harvest what was learned into the
places future sessions actually read — CONTEXT.md, ADRs, qa-plan flows, and the issue tracker —
so `grill-with-docs` keeps grilling against reality instead of stale docs.

**Why it exists:** The pipeline currently ends at `draft-pr`. Without a closing step,
domain language drifts, decisions made mid-implementation never become ADRs, and the docs that
power the ALIGN phase decay. This skill is the flywheel that keeps the whole system honest.

**Pipeline position:** Terminal step, after merge (or at natural milestones). Receives from
the whole pipeline; feeds forward into `grill-with-docs` (docs), `to-issues`/`triage` (deferred
work), and `qa-plan` (flow updates).

**Core moves to encode:**
- **Diff the plan against reality**: compare the PRD/issues/spec with what actually got built.
  Every divergence is either (a) a doc update, (b) an ADR ("we decided X mid-flight because Y"),
  or (c) a new issue — never silent.
- **Harvest mid-flight decisions into ADRs**: scan the branch's commits and the conversation for
  "we chose A over B" moments that never got documented. One short ADR each, not a novel.
- **Update ubiquitous language**: new domain terms coined during implementation go into
  CONTEXT.md; terms that turned out wrong get corrected.
- **Sweep the TODO/deferred list**: tidy-first drops, refactor-catalog rejects, review findings
  marked "later" — confirm each is filed or consciously dropped (same explicit-decision rule as
  tidy-first's gates).
- **qa-plan delta**: did the shipped UX invalidate or extend existing qa flows? Update them.

**Gates:**
1. **Evidence gate:** every doc/ADR change must trace to a concrete divergence or decision from
   THIS shipped change — no speculative doc rewrites, no "while we're here" doc sweeps.
2. **Brevity gate:** the whole retro output should be small (a few doc edits, 0-2 ADRs, a
   handful of issues). If it sprawls, the unit of shipping was too big — note that and move on.

**Primary output + stop point:** a proposed delta list — doc edits, ADR stubs, issues to file,
qa-plan updates — each with its triggering evidence. Stop for user approval before writing.

**Worked examples:** good case — mid-flight switch from polling to SSE becomes a 10-line ADR +
CONTEXT.md term; rejected case — "let's also reorganize all the ADR files" (fails evidence
gate); wrong-skill case — "the feature is buggy in prod" → `diagnose`, not a retro item.

**Boundaries:** `grill-with-docs` (consumes the docs this skill maintains; that one updates docs
*before* building, this one *after* shipping); `draft-pr` (describes the change outward;
this records learnings inward); `to-issues` (this routes deferred work to it); `diagnose`
(production misbehavior is a bug, not a learning).

---

## 9. `harvest-language` — bootstrap the language layer on an existing codebase (Evans, DDD)

**Essence (one line):** Mine an existing, undocumented codebase for its de-facto ubiquitous
language — including the inconsistencies real multi-author codebases accumulate — and, through
a grill session, produce a populated `CONTEXT.md` (and optionally retroactive ADRs).

**Why it exists:** `grill-with-docs` assumes a CONTEXT.md exists or builds it lazily, term by
term, only as new plans touch terms — on a mature repo that takes months. The deprecated
`ubiquitous-language` skill extracts only from *conversation*, never from code. Nothing today
goes codebase → glossary. This is the brownfield bootstrap, run once per repo/context.

**Pipeline position:** Pre-ALIGN, one-time. Run before the first `grill-with-docs` session on
a brownfield project. Output feeds `grill-with-docs`, `improve-codebase-architecture` (which
already reads CONTEXT.md), `model-types-first` (harvests names from CONTEXT.md), and
`language-drift` (which needs a baseline to diff against).

**Mining sources, in order of signal strength (encode this ordering):**
1. **DB schema / domain types** — table, entity, and union names are the team's real nouns.
2. **API routes + exported function names** — the domain verbs (cancel vs void vs revoke).
3. **UI copy and error messages** — the language users see; where it disagrees with the code's
   language, that disagreement is a first-class *flagged ambiguity*, not noise.
4. **Git history / PR titles / issue tracker** — how humans talk about the system.

**Ambiguity hunting (the heart of the skill — this is the "usual stuff of a real codebase"):**
- **Synonym clusters**: same concept, different names across modules (`client` / `customer` /
  `account`). Detect by co-occurrence in similar signatures/shapes, shared FK targets, and
  mapping code (`toCustomer(client)` is a confession).
- **Homonyms**: one word, two concepts (`account` = auth identity in one module, billing
  entity in another).
- **Casing/inflection drift** (`order_item` vs `orderItem` vs `LineItem`) — only when it
  crosses concept boundaries; pure style is a linter's job, not this skill's.
- **Confusable-but-distinct concepts**: distinct concepts whose names *read* as synonyms
  (`type` / `structure` / `category` as three classification axes; `Place` vs `PlaceTag`;
  `Bookmark` vs `SavedSearch`). Not a synonym cluster — the fix is an explicit boundary
  definition per term, not a canonical pick.
- **Duplicate definitions**: the same type/concept defined twice with divergent shapes
  (e.g. an `AdvertiserType` const object in one module and a numeric union in another).
  Cheap heuristic: same exported type name in two modules. A confession of drift in itself.
- **Opaque abbreviations** as domain terms (`ng` for *novogradnja*): glossary entry must
  settle the canonical spelling and whether the abbreviation is allowed in code.
- **Cross-language synonym pairs** in bilingual codebases (`oglas`/`Ad`, route slugs in one
  language, models in another): treat as a synonym cluster, but the canonical pick may be
  per-layer (e.g. Serbian in URLs, English in code) — record the layer rule in CONTEXT.md.
- **False-positive guard — projections/DTOs**: multiple shapes of one concept for different
  surfaces (`Ad` / `AdDetailsAd` / `PremiumListAd`) are NOT a synonym cluster. Record them
  in the glossary as named views of one concept so the naming signals sameness.
- The agent detects clusters; only the user picks the canonical term. End with a
  grill-with-docs-style session: one ambiguity at a time, recommendation attached, then write
  the resolved term to CONTEXT.md **inline** (inherit grill-with-docs' no-batching rule).

**Format rules:** reuse the deprecated `ubiquitous-language` skill's glossary craft (opinionated
canonical terms, "aliases to avoid" column, one-sentence definitions, relationships, example
dialogue, flagged-ambiguities section) but write to **CONTEXT.md per CONTEXT-FORMAT.md** —
never resurrect UBIQUITOUS_LANGUAGE.md. Detect multi-context repos (clear module boundaries
with conflicting languages → propose CONTEXT-MAP.md + per-context CONTEXT.md rather than
forcing one global glossary; a homonym across contexts may be *correct* DDD, not a bug).

**Retroactive ADRs:** while mining, surface "surprising decisions already in the code" (odd
tech choices, schema oddities, why-is-this-here architecture) via git archaeology; offer ADRs
using grill-with-docs' three-gate rule (hard to reverse + surprising + real trade-off). Cap at
a handful — this is a side dish, not the meal.

**Gates:**
1. **Glossary-only gate:** output is CONTEXT.md + optional ADR stubs. The skill NEVER renames
   code. Each resolved ambiguity where code disagrees with the canonical term becomes a
   *candidate rename issue* routed to `to-issues`/`refactor-catalog` — user decides.
2. **Evidence gate:** every glossary entry and flagged ambiguity must cite where it was found
   (file/table/route). No terms invented from vibes or from the agent's domain priors.
3. **User-decides gate:** never auto-pick a canonical term when a synonym cluster exists —
   recommend, then ask.

**Primary output + stop point:** a draft term inventory + flagged ambiguity list → grill
session (one at a time) → CONTEXT.md written inline as terms resolve, candidate-rename issue
list, optional ADR stubs. Stops after docs; no code edits.

**Worked examples:** good case — repo where `client`/`customer` coexist: cluster surfaced,
user picks Customer, CONTEXT.md entry with aliases-to-avoid, rename filed as issue; rejected
case — "also rename everything in the code now" (fails gate 1 → issues); wrong-skill case —
stress-testing a *new feature's* terminology → `grill-with-docs`.

**Boundaries:** `grill-with-docs` (per-change, forward-looking; this is whole-repo, backward-
looking, one-time); deprecated `ubiquitous-language` (conversation-only source, dead format);
`language-drift` (ongoing maintenance after this bootstraps the baseline);
`improve-codebase-architecture` (consumes the language; doesn't produce it).

---

## 10. `language-drift` — keep the language layer aligned with the code

**Essence (one line):** Periodically diff CONTEXT.md (+ ADRs) against the current codebase and
recent git history, report drift and new inconsistencies, and propose doc updates and candidate
rename issues — the safety net for changes that bypassed the docs-aware workflow.

**Why it exists (standalone, not a re-run mode of #9):** not everyone on a team uses
`grill-with-docs`/`post-ship-retro` — some teammates bypass or reject the whole concept. The
language layer must stay trustworthy anyway, or `grill-with-docs` starts grilling against
fiction and the layer dies. This skill assumes nothing about how the drift got in.

**Pipeline position:** MAINTAIN phase, periodic (weekly/monthly or pre-release) or on demand
("is the glossary still accurate?"). Requires a baseline CONTEXT.md — if none exists, route to
`harvest-language` first (make this routing loud). Complements `post-ship-retro` (per-change,
by the docs-aware author) by sweeping *everything else* (cross-change, any author).

**Checks to encode (mostly mechanical/greppable — keep it cheap):**
1. **New unknown terms**: prominent identifiers (exported types, tables, routes) introduced
   since the last sweep (git log since date/tag) that aren't in CONTEXT.md → propose entries.
2. **Dead terms**: glossary entries whose term no longer appears in code → propose removal or
   archive.
3. **Alias regressions**: "aliases to avoid" reappearing in *new* code (blame the line — old
   occurrences are the rename backlog, not new drift). Includes cross-language aliases where
   CONTEXT.md records a per-layer language rule (e.g. new code using *oglas* where `Listing`
   is canonical in code, or vice versa for URL slugs).
4. **New synonym/homonym clusters**: same hunting heuristics as `harvest-language` (including
   duplicate definitions and confusable-but-distinct concepts), scoped to code added since
   the last sweep.
5. **Definition contradictions**: code whose behavior contradicts a glossary definition or an
   ADR's decision (spot-check the top findings by reading the code — inherit hotspot-analysis'
   "data proposes, code disposes" rule).

**Gates:**
1. **Report-first gate:** output is a drift report + proposed CONTEXT.md edits — never silent
   doc rewrites, never code edits. User approves each proposed edit (terms are team decisions).
2. **Recency gate:** only flag drift introduced since the last sweep/baseline; re-litigating
   the whole repo every run is `harvest-language`'s job, done once.
3. **Signal gate:** suppress one-off occurrences (a single stray `client` in a test fixture is
   noise); flag patterns (a new module consistently using a banned alias is drift).

**Primary output + stop point:** a short drift report — finding → evidence (file/commit) →
proposed action (CONTEXT.md edit / ADR stub / candidate rename issue / ignore) — then stop for
approval. Track the sweep point (date or commit) so the next run is incremental.

**Worked examples:** good case — teammate added a `vendors` module using "supplier" everywhere
while CONTEXT.md says Vendor: flagged with commits cited, user picks one, docs + rename issue;
rejected case — flagging a 2-year-old alias as new drift (fails recency gate — that's the
backlog); wrong-skill case — no CONTEXT.md exists → `harvest-language`.

**Boundaries:** `harvest-language` (one-time bootstrap; this is incremental maintenance);
`post-ship-retro` (author-driven, per-change; this is sweep-driven, author-agnostic);
`grill-with-docs` (uses the docs during planning; this audits them between plans);
`hotspot-analysis` (statistical churn signals; this is semantic/vocabulary signals — kindred
read-only sweep skills, keep their report styles consistent).

---

## Dispatch notes (for the orchestrator)

- One writer agent per skill, fresh session each, `pair` role for 1–5 and 7–10, `engineer` for 6.
- Brief each agent to read: this file (its own section + house style), `tidy-first/SKILL.md`,
  and the sibling skills named in its Boundaries paragraph. Use the `write-a-skill` skill.
  Writers for 9 and 10 must also read `grill-with-docs/CONTEXT-FORMAT.md`, `ADR-FORMAT.md`,
  and the deprecated `ubiquitous-language/SKILL.md` (for its glossary craft, not its format).
- Recommended order: 9 → 1 → 2 → 4 → 3 → 10 → 5 → 7 → 8 → 6. (9 first — several briefs assume
  a populated CONTEXT.md, and it has no dependencies of its own; 4 after 2 so the catalog can
  reference hotspot-analysis's shotgun-surgery detection; 4's test-gate hand-off needs 1 to
  exist; 10 after 9 (needs the baseline concept) and ideally after 2 (shares report style and
  the "data proposes, code disposes" rule); 7 after 1 for the legacy-seams hand-off; 8 last
  among the priority set since it references qa-plan, to-issues, and the gates language
  established by the others.)
- Decide per skill whether it lives in `aAtila/skills/` (default) or belongs upstream in
  mattpocock's repo — default to aAtila, the user can upstream later.
- After each skill lands: verify gates/boundaries/checklist/worked-examples are present,
  description has trigger phrasings + NOTs, then check the box at the top of this file.
