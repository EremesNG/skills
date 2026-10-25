# Application Architecture
Choose application, UI, and subsystem boundaries from demonstrated change, ownership, and testing needs—not diagrams or deployment fashion.

## Layered Architecture

- **Choose when:** Presentation, policy, and persistence change independently, or policy tests repeatedly require infrastructure.
- **Simpler first:** Direct cohesive functions with isolated external calls; add a layer when it owns a distinct decision, not forwarding methods.
- **Contract:** Declare allowed dependency directions. Logical layers are not physical tiers; network hops require separate justification.
- **Traps:** Horizontal slicing scatters features; UI/database-owned rules and cycles undo separation. Test rules without rendering or storage, and check forbidden dependencies.

## Hexagonal Architecture

- **Choose when:** The same use case needs multiple delivery mechanisms, or vendor semantics repeatedly invade policy tests.
- **Simpler first:** Pass an external dependency explicitly; introduce ports when multiple adapters or recurring translation justify them.
- **Contract:** Application-owned ports express application needs; adapters translate external types, errors, and semantics without moving policy outward.
- **Traps:** Mirroring a vendor API preserves coupling; abstracting every helper adds indirection. Contract-test adapters against real boundary behavior, not only permissive fakes.

## Onion and Clean Architecture

- **Choose when:** Long-lived domain policy must survive UI/storage changes and needs independently testable orchestration.
- **Simpler first:** One explicit infrastructure seam; add boundaries when actual policy dependencies need protection, not to complete concentric rings.
- **Contract:** Source dependencies point inward. Runtime calls may travel outward through inward-owned interfaces; wire implementations at the [composition root](principles.md#dependency-injection-and-composition-root).
- **Traps:** Diagrams do not mandate folders or identical named layers. Check inward code for framework imports; remove mappings that protect no boundary.

## Modular Monolith

- **Choose when:** Capabilities need separate ownership but independent deployment has no demonstrated benefit.
- **Simpler first:** Ordinary cohesive modules; formalize APIs when cross-module changes or ownership conflicts recur. Extract services only for concrete deployment/isolation needs.
- **Contract:** Assign table ownership, permitted module dependencies, and cross-module transaction coordination inside one deployable; shared storage is not public storage.
- **Traps:** Deep imports and shared-table writes erase boundaries. Enforce dependency rules and test that non-owning modules cannot bypass an owner's invariants.

## Plugin Architecture

- **Choose when:** Independent authors need optional extensions without changing host internals.
- **Simpler first:** A function table or explicit construction; expose a plugin contract once independent extension development requires stability.
- **Contract:** Version interfaces and capabilities; define startup, shutdown, compatibility negotiation, and resource ownership before accepting extensions.
- **Traps:** Test incompatible versions, failed initialization, and cleanup. In-process plugins are not a security sandbox; untrusted code needs real isolation. Configuration-time implementation linkage alone does not supply a full extension lifecycle.

## MVC

- **Choose when:** Multiple views share state or the platform already gives model, view, and controller useful, established roles.
- **Simpler first:** Local state and callbacks; separate roles when input coordination or shared-state presentation becomes hard to test.
- **Contract:** Agree on the local meaning: desktop and web MVC coordinate views differently. Controllers invoke use cases; models need not be database rows.
- **Traps:** Fat controllers hide domain policy and persistence. Test rules without controllers or rendering; naming a type Model does not establish cohesion.

## MVP

- **Choose when:** Interaction rules need tests without constructing a visual hierarchy and binding offers little help.
- **Simpler first:** Direct callbacks; introduce a presenter when meaningful coordination, not every visual property, needs isolation.
- **Contract:** Passive View centralizes presentation logic for isolation but adds synchronization code; Supervising Controller leaves simple binding in the view, narrowing presenter-test coverage. Tie subscriptions to screen lifetime.
- **Traps:** Presenters must not own domain rules. Test reopen/dispose cycles and view synchronization; presenter-only tests cannot verify behavior deliberately left in the view.

## MVVM

- **Choose when:** A binding-capable UI needs synchronized presentation state, validation, and actions across several controls.
- **Simpler first:** Callbacks or [MVP](#mvp); adopt binding when manual synchronization repeatedly causes defects, not for every simulation value.
- **Contract:** Define notification ordering, binding direction, view-model lifetime, and subscription cleanup; keep domain policy and persistence outside presentation state.
- **Traps:** Silent binding failures and notification fan-out obscure causality. Trace property-to-view updates, test reopening/disposal and stale async results, and profile recomputation before binding high-frequency state.

## Unidirectional Data Flow

- **Choose when:** Shared presentation mutations have unclear ownership and action-history inspection would resolve recurring bugs.
- **Simpler first:** Local state with explicit updates; centralize only when cross-view coordination becomes demonstrably difficult.
- **Contract:** Pure reducers compute state; separate effect handlers perform external work and dispatch results. Define how request identity/order rejects stale completions.
- **Traps:** A global store can over-coordinate real-time simulation. Test out-of-order completions and deterministic transitions; an action log is not a durable [event-sourced record](distributed-systems.md#event-sourcing).

## Event Bus

- **Choose when:** Several independent, optional in-process reactions follow a completed occurrence.
- **Simpler first:** Direct calls for one known receiver or required workflow; upgrade only when independent subscribers actually need decoupling.
- **Contract:** Specify synchronous/deferred dispatch, ordering, reentrancy, error propagation, and subscription ownership/lifetime.
- **Traps:** Hidden subscriber chains obscure required work; test handler failure, recursive publication, and disposed subscribers. A bus provides no durable-delivery guarantee.
- **Not:** [Event Queue](game-programming.md#event-queue) emphasizes deferred timing; broker [pub-sub](distributed-systems.md#publisher-subscriber) adds cross-process transport and delivery contracts.

## Request Mediator

- **Choose when:** Many entry points need consistent handler discovery and meaningful authorization, validation, or tracing pipelines.
- **Simpler first:** Direct application-service calls; add dispatch when repeated cross-cutting processing warrants an explicit boundary.
- **Contract:** One handler per request, defined result/error propagation, pipeline ordering, and transaction ownership; test which stages run inside the transaction.
- **Traps:** Discovery hides control flow and overhead; test missing/duplicate handlers. Request routing is a specialization, not the full GoF [Mediator](behavioral.md#mediator), publish-to-many notification, or durable messaging.

## Repository and Unit of Work

- **Choose when:** Domain-oriented retrieval protects real storage semantics and related changes require one supported transaction.
- **Simpler first:** Use the ORM's collection/transaction facilities; add repositories only when they protect domain concepts rather than duplicate generic CRUD.
- **Contract:** One owner opens, commits, and rolls back the unit of work; repositories do not commit independently. Guarantees stop at the actual storage boundary, not remote services.
- **Traps:** Lazy loading and query types leak persistence. Test a failure between related writes and access after the unit-of-work lifetime.

## Specification

- **Choose when:** Reused eligibility rules genuinely need AND/OR/NOT composition across selection or validation.
- **Simpler first:** A named predicate; introduce composition after repeated combinations appear, not for imagined flexibility.
- **Contract:** Specify evaluation context and whether predicates run in memory, storage, or both; failure explanations and context retrieval are separate concerns.
- **Traps:** Database and in-memory evaluators differ on nulls, comparison, and supported operations. Run equivalent cases through both. An expanding expression language adds validation, tooling, and versioning obligations.

## Domain Model and Transaction Script

- **Choose when:** Recurring invariants across workflows favor domain objects; straightforward, local workflows favor transaction scripts.
- **Simpler first:** A short procedure; extract proven domain behavior when scripts begin duplicating complex rules or state transitions.
- **Contract:** Give each invariant one authority, even when capabilities use different styles; define the operation's commit boundary separately from object organization.
- **Traps:** Anemic objects add ceremony while services mutate everything. Test the same invariant through every entry point; do not load domain objects with rendering, transport, or persistence responsibilities.

## Data-Driven Design

- **Choose when:** Content authors repeatedly change variants expressible through a small, understood behavior vocabulary.
- **Simpler first:** Constants and functions; introduce schemas when repeated content changes justify validation and authoring tools.
- **Contract:** Version, validate, migrate, and roll back data; define flat/additive/multiplicative modifier ordering and every cached-result invalidation input.
- **Traps:** Arbitrary executable capabilities create an accidental language. Test malformed/old data, modifier order, and stale caches; data changes still need release responsibility.
- **Not:** [Data-oriented design](ecs-data-oriented.md#when-ecs-pays-off) concerns layout/processing; domain-driven design concerns domain modeling. Neither means configuring behavior through data.
