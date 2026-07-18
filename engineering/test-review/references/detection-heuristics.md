# Detection Heuristics

Reference for `test-review`. `SKILL.md` carries the diagnostic questions; this carries the exhaustive signals behind them — the full smell catalogue (Pass 1), static flaky signals, and coverage heuristics (Pass 2).

## Quality smells (Pass 1)

### Tautological

- Expected value recomputed the way the code computes it, instead of a known-good literal from the spec.
- Asserts a mock's own configured return value.
- `expect(mock).toHaveBeenCalledWith(...)` as the _only_ assertion — proves a call happened, not that the outcome is right.
- Round-trips through the same serializer both ways and asserts they match.

### Implementation-coupled

- Mocks internal collaborators (as opposed to the process / network / clock / fs boundary).
- Tests a private or internal function directly.
- Asserts call count or call order.
- Verifies through a side door — queries the DB directly instead of the public read path.
- Test name describes HOW ("calls `save`"), not WHAT ("persists the order").

### Vacuous / low-signal ("smoke")

- `toBeDefined` / `toBeTruthy` / `not.toThrow` as the whole assertion.
- Snapshot-only over volatile output — re-baselined on every change, so it goes numb.
- Renders-without-crashing with no behavioural assertion.
- Asserts a literal it set two lines above.

### Flaky-prone (static signals)

- Uncontrolled time: `Date.now()`, `new Date()`, timers — without fake timers or an injected clock.
- Randomness without a seed.
- Real network / filesystem / DB instead of a boundary fake.
- `setTimeout` / sleep-based waiting instead of awaiting a condition.
- Order-dependence: shared mutable module state, no reset between tests, leaked globals.
- Unawaited promises / a missing `await` on an async assertion.
- Reliance on locale, timezone, or wall-clock.

### Disabled / silent

- `.skip`, `.only` (also narrows the run to a hidden green), `xit`, `xdescribe`.
- `test.todo` with no owner or ticket.
- Commented-out tests.

### Weak assertion

- Loose matcher where an exact expected exists (`toEqual(expect.anything())`).
- Brittle coupling to a full error-message string.
- `objectContaining` / superset that would still pass with the field under test missing.

## Coverage heuristics (Pass 2)

Read the code under test, not a checklist. For each unit in the target:

- **Branches / guards** — every `if`, `switch`, ternary, `&&` / `||` short-circuit, early return: is there a test that takes it?
- **Error paths** — every `throw`, rejected promise, `Result`-error, `catch`: asserted, or only the happy path?
- **Boundaries** — empty collection, null / undefined, zero, negative, max, off-by-one at each range edge.
- **Real use cases** — the happy path a user actually hits end-to-end, not just unit-level fragments.
- **Regression surface (diff mode)** — the behaviour the diff changed: would a test here have caught the old bug?

Write each untested one as `input → expected` grounded in that branch (G2). If it maps to no behaviour a caller observes — a log line, a defensive `?.` that can't fire — leave it uncovered (G1).

## Framework notes

- **Vitest / Jest** — `.only` leaks a hidden green in CI when lint doesn't catch it; flag it `fix`. Prefer `vi.useFakeTimers()` or an injected clock over real time. Reset modules / mocks between tests to kill order-dependence.
- **Testing Library (React)** — assert on accessible output (role / text), not component internals; `container.querySelector` into internals is implementation-coupled. Await `findBy*` rather than `setTimeout`.
- **Coverage tools** — read the number as a map to unread branches, never as a target (G1). A green line count riding on tautological tests is worse than an honest gap.
