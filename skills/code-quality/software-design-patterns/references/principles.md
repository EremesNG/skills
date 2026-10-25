# Design Principles
Use these as checks on demonstrated forces, not a scorecard for classes or interfaces.

## SOLID
Apply only the principle that addresses an observed contract or change problem; SOLID does not require a hierarchy or an interface per dependency.

### Single Responsibility
Keep a cohesive invariant together; splitting it into one-method objects can scatter its enforcement. A responsibility is a reason for change, not an action count.

### Open Closed
Close around a proven axis of variation, not guessed extensions. Edit a policy when its meaning changes; an extension point cannot prevent that change.

### Liskov Substitution
Test shared contracts against every implementation, including failures, ownership and permitted state changes. Matching signatures cannot excuse stronger preconditions or weaker guarantees.

### Interface Segregation
Split by actual client capabilities, not one interface per method. A narrow interface does not enforce authorization; the implementation must still do so.

### Dependency Inversion
Use a function/module boundary if it protects policy without interface ceremony. One implementation can justify an external boundary or test seam; mirroring a stable helper's methods usually cannot.

## Composition over Inheritance
Keep a shallow, genuinely substitutable hierarchy when stable; delegation can scatter invariants and add hot-path work. Do not replace inheritance with a collaborator graph merely for compliance.

## Dependency Injection and Composition Root
Prefer manual construction before a container; keep resolution at composition roots and state lifetime, disposal and ownership. A large constructor may expose an oversized responsibility.
Fowler treats injection and service location as alternatives, emphasizing configuration separate from use; Seemann rejects location because it hides dependencies and shifts failures to runtime.
Prefer explicit injection; constrain any necessary locator to an integration boundary rather than passing a container through policy code.

## Coupling and Cohesion
Check temporal order, schemas and coordinated releases, not just imports. A bus can hide dependencies without removing them; keep ordering-sensitive invariants cohesive.

## Law of Demeter
Do not count dots: fluent APIs and immutable pipelines differ from navigating mutable internals. Add an owning operation/query, not blind forwarding methods that preserve the same conceptual dependency.

## DRY and the Wrong Abstraction
Unify shared knowledge, not similar syntax. Follow Metz when flags and branches accumulate: re-inline the abstraction, let callers diverge, then extract only the commonality supported by real changes.
Treat AHA or the rule of three as prompts to learn, not permission to leave duplicated invariants inconsistent.

## YAGNI and KISS
Follow Fowler: defer speculative capabilities, not maintainability, tests or clear structure. Keep known correctness, security and recovery requirements; fewer lines can increase debugging and operating cost.

## Tell Dont Ask
Do not ban queries, getters or functional transformations; rendering/reporting need them. Move duplicated invariant enforcement to its owner without dragging UI/infrastructure policy there.
Define the actual atomicity boundary: moving a method cannot make a distributed read-then-write safe.

## Separation of Concerns
Do not mistake folders, forwarding layers or separate deployables for boundaries. Give cross-cutting transactions, authorization and observability explicit end-to-end ownership.

## When Patterns Hurt
Challenge single-product factories, one-hop buses, god objects and fragile inheritance with a present-force test, not an automatic ban. Keep proven safety/test boundaries even with one implementation.
Remove machinery before adding another pattern; a function can retain Strategy's seam. Profile hot paths because flexibility may discard assumptions that enabled optimization.
