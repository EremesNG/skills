---
name: simplify
description: Simplify and refine recently changed code without changing behavior. Use after implementing or fixing code, before final verification, or whenever the user asks to clean up, reduce complexity, improve readability, remove duplication, or make a diff easier to maintain. Apply it even when the user does not explicitly say "simplify" if a completed implementation needs a focused behavior-preserving cleanup pass.
---

# Simplify

Make the current change easier to understand and maintain while preserving its
observable behavior. Treat simplification as a focused review of the recent diff,
not permission to redesign the surrounding system.

## Establish the boundary

1. Read repository instructions and the task's accepted requirements.
2. Inspect the current diff and identify files changed for this task. If the
   workspace already contained unrelated changes, distinguish them before
   editing.
3. Read enough neighboring code and tests to understand local conventions and
   public seams.
4. Write down the behavior that must remain stable: public API, outputs, error
   contracts, side effects, ordering, concurrency, performance constraints, and
   visible UI.

If the target diff cannot be distinguished from unrelated user work, report the
ambiguity instead of editing broadly.

## Find high-value simplifications

Prioritize changes that reduce cognitive load:

- remove duplication introduced by the current change;
- flatten needless nesting with clear guard clauses;
- replace indirect or speculative abstractions with direct code;
- name concepts by domain meaning rather than mechanics;
- make data flow, ownership, and error propagation explicit;
- delete comments that merely restate code and preserve comments that explain
  non-obvious constraints or intent;
- consolidate repeated conditions without hiding important differences;
- remove dead branches, redundant conversions, and unused compatibility paths;
- align the change with nearby repository patterns when those patterns remain
  clear and safe.

Do not optimize for fewer lines. A small helper, explicit branch, or intermediate
name is worthwhile when it makes intent or invariants easier to see.

## Preserve behavior

Do not change:

- accepted requirements or externally observable semantics;
- public names, schemas, protocols, persistence formats, or error contracts;
- timing, ordering, idempotency, or concurrency behavior unless explicitly in
  scope;
- security, authorization, validation, or recovery guarantees;
- dependencies, build configuration, or unrelated files merely to make the diff
  look uniform;
- test meaning just to accommodate a refactor.

Never discard pre-existing workspace changes. Avoid broad formatting runs unless
the formatter can be limited to files owned by the task.

## Apply in small steps

1. Choose one coherent simplification.
2. Make the smallest edit that expresses it.
3. Run the nearest relevant check or inspect the existing behavioral evidence.
4. Continue only while each change makes the code materially clearer.

Stop when further cleanup would require a new design decision, expand the task,
or trade clarity for cleverness. Leave worthwhile out-of-scope improvements as
brief follow-up notes rather than silently implementing them.

## Verify

Run the focused tests, type checks, lint checks, or build steps appropriate to the
changed behavior. Compare the final diff with the original task and confirm:

- no unrelated files were changed;
- public behavior and failure behavior remain intact;
- tests still verify the same user-facing contract;
- complexity actually decreased rather than moving elsewhere;
- comments and names match the resulting code.

If verification cannot run, state exactly what was inspected and what remains
uncertain.

## Return contract

Return a concise report with:

- **Simplifications**: the meaningful cleanup performed;
- **Behavior preserved**: the contracts and evidence checked;
- **Verification**: commands or manual checks and results;
- **Deferred**: cleanup intentionally left out of scope, or `none`.

