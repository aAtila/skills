# Skill Brief — `blindspot` (article-inspired)

Sibling to the ten briefs in `book-inspired-skills.md`. Source is not a book but Thariq Shihab's
"unknowns" article (the known/unknown 2×2, the "blindspot pass", "unknown unknowns"). Same
house style — a writer agent should read **the house-style section of `book-inspired-skills.md`**,
this brief, and the named sibling skills, then write ONE skill.

Status: [ ] not started

---

## Why this one is worth building (and the nine article techniques that aren't)

The "unknowns" article is a catalogue of *prompts*. Almost all of them already have a home in
the library — its "interview me" **is** `grilling`; its "brainstorm/prototype" **is**
`prototype`; its "implementation plan" **is** `to-prd`/`aa-design-spec`; its "references" and
"pitches" are one-line prompts with no gate, so they aren't skills at all. Turning each into a
skill would bloat the library with vibes.

**One idea in the article is genuinely orthogonal to everything the library already does: the
blindspot pass.** Every grill skill walks a decision tree that *already exists* — it resolves
decisions you know you face. Nothing in the library reveals the **existence** of decisions,
concepts, and landmines you don't know you face. That is the unknown-unknowns quadrant, and it
is a distinct act with a distinct output. This brief is only for that.

**The conceptual spine (encode it, it's the borrowable core):** the known/unknown 2×2, mapped
onto the existing pipeline so the skill knows what it is *not*:

| | you're aware of it | you're not aware of it |
|---|---|---|
| **you know it** | Known known → *the prompt* | Unknown known → **`prototype`** (you know it when you see it) |
| **you don't know it** | Known unknown → **`grilling`** (resolves it) | Unknown unknown → **`blindspot`** (reveals it) |

`blindspot` owns exactly one cell. If a candidate finding fits any other cell, it belongs to
that other skill.

---

## Essence (one line)

Before starting work in **unfamiliar** territory, surface the unknown-unknowns — the decisions,
domain vocabulary, and landmines you don't yet know exist — grounded in *this* codebase and
high-trust primary sources, and teach the user just enough to prompt well. It reveals the
decision tree; `grilling` then walks it.

## Pipeline position

A **pre-ALIGN on-ramp**, gated on unfamiliarity. It sits one step before `grill-with-docs`:

```
blindspot (unfamiliar territory only) → grill-with-docs → to-prd/implement → …
```

Its output *is* the opening agenda for the grill session: each surfaced unknown becomes either a
grilling question, a `prototype` to run, a doc/reference to read, or a bounded `research` task.
`blindspot` is also an *investigation orchestrator* — it should dispatch `research` and Explore
agents as its arms rather than reasoning from parametric priors (see the grounding gate). On
familiar ground it does not run at all — it routes straight to `grilling`.

## Core moves the skill must encode

- **Establish the user's starting point first.** The article is emphatic: *"give Claude context
  about your starting point… disclose your experience with the problem and codebase."* The skill's
  first act is to ask (or infer from the conversation) what the user already knows about this
  domain and this area of the code. This both feeds the unfamiliarity gate and calibrates depth —
  a blindspot pass for a novice and for a near-expert are different documents.
- **Investigate on two axes, in parallel:**
  1. **Codebase axis** — walk the area the task touches with Explore agents: what patterns,
     abstractions, historical decisions (ADRs, git archaeology), and conventions exist here that
     the user would blunder past? Where are the load-bearing assumptions?
  2. **Domain axis** — for the subject matter itself (auth, color grading, rate limiting, video
     encoding), pull high-trust primary sources via `research`/explore agents: what does "good"
     look like, what are the standard failure modes, what vocabulary does the user lack?
- **Surface, rank, and route — don't resolve.** Produce unknowns, not answers. Rank by *"would
  this change the approach?"* (the article's own prioritization: *"prioritize questions where my
  answer would change the architecture"*). Lead with approach-changing unknowns; bury the minor
  ones or cut them.
- **Teach just enough to prompt.** Each blindspot includes the *minimum* vocabulary/context the
  user needs to make a decision or write a better prompt — not a lecture. The test: after reading,
  can the user now ask a sharp question they couldn't have asked before?

## The interactive part (this is what makes it a skill, not a lecture)

After presenting the map, have the user triage each blindspot one line at a time:
**"knew that" / "news to me" / "need to go learn this"**. This does three jobs: (a) it *validates
the unfamiliarity gate* — if everything comes back "knew that", the skill misfired and should have
routed to `grilling`; (b) the "news to me" items become the `grill-with-docs` agenda; (c) the
"need to learn" items route to `research` or `teach`. Inherit `grilling`'s no-batching rule: one
at a time.

## Gates (three hard stop-rules — this is what keeps it from being a vibe)

1. **Unfamiliarity gate (the stop-rule).** A blindspot pass only fires when the territory is
   genuinely unfamiliar to *this* user. If they already know the domain and the code area, there
   are no unknown-unknowns to surface and the skill degenerates into a patronizing lecture —
   **refuse and route to `grilling`/`grill-with-docs`.** The skill must confirm unfamiliarity
   before investigating, and abort mid-pass if the triage step reveals the user knew it all.
2. **Surface-don't-solve gate.** Output is unknowns *made visible*, never decisions *made*. The
   moment the skill is answering the questions it raised, prototyping, or editing code, it has
   left the skill — that's `grilling`/`prototype`/`implement`. It reveals the tree; it does not
   walk it.
3. **Grounding gate (evidence, not priors).** Every blindspot must trace to a concrete source —
   a file/module/ADR/schema in *this* repo, or a cited high-trust primary source. A generic
   best-practice checklist ("have you considered error handling, logging, tests?") fails this
   gate and must be cut. If it isn't grounded in this codebase or a real source, it isn't a
   blindspot — it's boilerplate.

## Primary output + stop point

A ranked **blindspot map** — a self-contained HTML artifact (follow the `teach` /
`improve-codebase-architecture` HTML precedent; the article leans on HTML for exactly this).
Each blindspot card:

- **What you didn't know to ask** — the unknown, stated as the question the user couldn't have posed.
- **Why it matters** — the blast radius on the decision/approach (drives the ranking).
- **Grounding** — the file, ADR, or cited source it came from (satisfies gate 3).
- **Where it routes** — a `grilling` question, a `prototype`, a doc to read, a `research` task, or
  a reference to point Claude at.

The map ends with the *minimum vocabulary* section (enough to prompt) and the triage step. Then it
**stops** and hands the now-visible decision tree to `grill-with-docs`. It decides nothing and
builds nothing.

## Out of scope (state explicitly)

- **Multi-session mastery of a concept** — that's `teach` (builds a durable course). `blindspot`
  is one-shot, task-scoped reconnaissance thrown away after the task.
- **Answering a single bounded factual question** — that's `research`. `blindspot` is the
  meta-step that tells you *which* questions you didn't know to research; it may *dispatch*
  `research`, but it isn't `research`.
- **Resolving the surfaced decisions** — `grilling`. **Building anything** — `prototype`/`implement`.
- **A codebase-health survey** — `improve-codebase-architecture` surveys the *code's* deepening
  opportunities; `blindspot` surveys *the user's* knowledge gaps relative to one task.

## Anti-patterns to warn against in the body

- **Generic checklist masquerading as insight** — fails the grounding gate; the single most likely
  failure mode. Every item must be grounded in this repo or a real source.
- **Lecturing the whole domain** — only blindspots that bear on *this* task; respect task scope.
- **Answering its own questions** — that's `grilling` leaking in; the skill raises, it doesn't resolve.
- **Running on familiar ground** — patronizing; fails the unfamiliarity gate.
- **Analysis paralysis / 40 unknowns** — rank hard, cap the list, lead with approach-changers,
  cut the rest. A map you can't act on is noise.

## Boundaries

- **`grilling` / `grill-me` / `grill-with-docs`** — they walk a *known* decision tree, resolving
  decisions one at a time. `blindspot` *reveals* the tree when you can't see it. `blindspot` asks
  *"what should I even be asking?"*; grilling asks the questions. `blindspot` is the on-ramp;
  `grill-with-docs` is the immediate next step and consumes its output as the agenda.
- **`prototype`** — resolves an *unknown known* ("I'll know the right state model when I see it
  run"). `blindspot` resolves *unknown unknowns* ("I didn't know this decision existed"). Different
  quadrant of the 2×2; a surfaced unknown may *route to* a prototype.
- **`research`** — answers ONE bounded question against primary sources. `blindspot` is the
  meta-step upstream that identifies which topics you didn't know you needed to research; it uses
  `research`/Explore agents as its investigation arm.
- **`teach`** — deliberate multi-session learning of a concept for its own sake, with a stateful
  workspace and a course. `blindspot` is one-shot, task-bound, and disposable; "need to go learn
  this" items are where it *hands off* to `teach`.
- **`improve-codebase-architecture`** — read-only survey of the *code's* shallowness/friction.
  `blindspot` is a read-only survey of *your* knowledge gaps for a task. improve finds candidates
  in the code; blindspot finds gaps in the person.

## Worked examples (include all three)

- **Passes all gates (good case).** User: *"I'm adding a second auth provider but I've never
  touched the auth modules here."* Unfamiliarity confirmed. The pass surfaces: an existing
  `SessionProvider` seam the user didn't know constrained the design (grounded in a file), an ADR
  that already rejected a prior provider for reason X (git archaeology), and the OAuth-vs-OIDC
  distinction the user lacked vocabulary for (cited primary source). Ranked, routed to grilling
  questions, minimum vocab taught. Stops. **Run it.**
- **Fails the unfamiliarity gate (rejected case).** User is the person who wrote the auth module
  and knows the domain cold. There are no unknown-unknowns to surface. **Refuse — route straight
  to `grill-with-docs`.** (If the skill only discovers this at the triage step — everything comes
  back "knew that" — it aborts and routes then.)
- **Wrong-skill case.** User already knows *what* decisions they face and just wants them resolved
  → `grilling`. User wants one primary-source question answered ("does Whisper timestamp at word
  level?") → `research`, not a whole blindspot pass. User wants to master color grading over
  weeks → `teach`.

## Naming, credit, placement

- **Name:** `blindspot` — methodology skill, unprefixed (per house rule #8), consistent with
  `tidy-first` / `colocation-first`.
- **Credit:** one line in the body to Thariq Shihab's "unknowns" article, the way `tidy-first`
  credits Beck. Reproduce the 2×2 as the conceptual spine; one quote max.
- **Placement:** default `aAtila/skills/` (house rule). But it is a strong upstream candidate for
  mattpocock's repo — it's a pure on-ramp that plugs directly into his idea→ship flow. Flag the
  upstream question for the user; don't decide it unilaterally.

## Dispatch notes (for the orchestrator)

- One writer agent, fresh session, `pair` role. Brief it to read: the house-style section of
  `book-inspired-skills.md`, this brief, `tidy-first/SKILL.md` (canonical gate style), and the
  sibling skills named in Boundaries — especially `grilling/SKILL.md`, `prototype/SKILL.md`,
  `research/SKILL.md`, and `teach/SKILL.md`. Use the `write-a-skill` / `writing-great-skills`
  conventions.
- **Two design forks to resolve before writing** (decide, then write — don't ship both):
  1. **Standalone skill vs a `grilling` mode.** This brief argues standalone (distinct act,
     distinct output, distinct gate). If the writer finds the gates collapse into grilling's, fall
     back to a `grilling` reference file (`grilling/BLINDSPOT.md`) instead — mirror how brief #6
     (`functional-core`) may become a `tdd` reference rather than a skill. Standalone is the
     default; only demote it with a stated reason.
  2. **Router integration.** The known/unknown 2×2 is a routing lens for `ask-matt`. Recommend a
     one-paragraph addition to `ask-matt` placing `blindspot` as the unfamiliar-territory pre-step
     before `grill-with-docs`, and naming the four quadrants → four skills. That edit is higher
     leverage than the skill itself and should ship with it.
- After it lands: verify the three gates, the sharp boundary paragraphs (each names its sibling
  and the *distinguishing act*), the worked examples (good / rejected-by-gate / wrong-skill), and
  a description with casual trigger phrasings ("I know nothing about X", "blindspot pass", "what
  don't I know here", "help me find my unknown unknowns") plus explicit `NOT grilling / NOT
  research / NOT teach` boundaries. Then check the box at the top of this file.
