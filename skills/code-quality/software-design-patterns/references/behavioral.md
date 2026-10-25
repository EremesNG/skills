# Behavioral Patterns

Read when request routing, undo, notification, lifecycle, traversal, or algorithm variation needs an explicit ordering and failure contract.

## Chain of Responsibility
- **Choose when:** Runtime context selects an eligible receiver, or higher-priority handlers can consume requests before others see them.
- **Simpler first:** Use a direct call or closed switch; upgrade for independently changing receiver/order rules. Use a pipeline when every step must run.
- **Contract:** Distinguish consumed, rejected, and unhandled outcomes; make handler order and terminal behavior inspectable.
- **Traps:** Cycles or ambiguous rejection cause duplicate handling or silent drops; test terminal unhandled cases and priority changes.
- **Not:** [Decorator](structural.md#decorator) layers optional behavior rather than primarily searching for a receiver.

## Command
- **Choose when:** Requests need ordered scheduling, history, undo, or replay independently of input/AI triggers.
- **Simpler first:** Use a call or lambda; upgrade when requests need retained data, not merely input bindings.
- **Contract:** Capture prior state at execution; keep per-entry undo data independent. Record successful effects and define partial-failure handling.
- **Traps:** Inverse actions cannot undo external effects. Test failed execution and reused requests; replay needs reproducible initial state, randomness, timing, and execution.
- **Not:** [Strategy](behavioral.md#strategy) chooses algorithms; Command retains what was requested. [Memento](behavioral.md#memento) can supply undo snapshots.

## Interpreter
- **Choose when:** A small, stable grammar expresses combinations that typed configuration cannot; tree-walking cost is acceptable.
- **Simpler first:** Use functions/configuration; upgrade for data-authored expressions. Embed an existing scripting language for richer semantics; measured hot paths may need compilation.
- **Contract:** Specify precedence, types, missing values, and errors; bound depth, work, and accessible operations for untrusted input.
- **Traps:** Parsing success does not validate evaluation; custom syntax is no sandbox. Test malformed, over-deep, and invalid-context expressions.
- **Not:** [Bytecode](game-programming.md#bytecode) changes execution representation rather than repeatedly evaluating expression objects.

## Iterator
- **Choose when:** Clients need independent cursors, traversal orders, or lazy results without owning storage bookkeeping.
- **Simpler first:** Use native iteration/generators or an indexed loop; upgrade only for missing traversal semantics, not another hierarchy.
- **Contract:** Choose mutation behavior: forbid, invalidate, snapshot, or deliberately support it. Specify cursor lifetime, cancellation, and resource cleanup.
- **Traps:** Lazy traversal retains resources and may observe later state; test early termination and mutation. Yielding does not itself time-slice or parallelize work.
- **Not:** [Visitor](behavioral.md#visitor) separates type-specific operations from elements; Iterator controls traversal independently.

## Mediator
- **Choose when:** Tangled peers repeatedly coordinate one bounded collaboration whose rules need a single testable owner.
- **Simpler first:** Keep a direct call or orchestration function; upgrade when recurring peer interactions scatter coordination rules.
- **Contract:** Name interactions, retain participants' local responsibilities, and specify state-change ownership and reentrancy behavior.
- **Traps:** Coordinator updates can trigger notification loops; test feedback paths. Split by collaboration before unrelated rules create a god object.
- **Not:** [Request Mediator](application-architecture.md#request-mediator) dispatches requests to handlers; [Event Bus](application-architecture.md#event-bus) broadcasts. Neither by itself owns peer coordination rules.

## Memento
- **Choose when:** Coherent restoration needs an originator-owned snapshot opaque to caretakers, within capture/memory budgets.
- **Simpler first:** Store a previous value in a command or copy safe values; upgrade when restoring linked invariants needs an encapsulated snapshot.
- **Contract:** Eliminate mutable aliases; restore related state consistently and define notifications and already-emitted-effect policy.
- **Traps:** Test branching after undo and cap retained history. Persistent snapshots need versioning, identity, reference resolution, and validation; serialization alone is insufficient.
- **Not:** [Prototype](creational.md#prototype) copies objects; Memento defines restoration. Neither rewinds external side effects automatically.

## Observer
- **Choose when:** Independent local reactions vary by subscription and synchronous notification cost is acceptable.
- **Simpler first:** Call required collaborators directly; upgrade for optional subscribers with explicit subscription owners.
- **Contract:** Specify listener order, list mutation, exceptions, and reentrancy; unsubscribe at disable/destruction or equivalent scope end.
- **Traps:** Slow callbacks stall emitters; reentrant mutation can deadlock under locks. Strongly retained lapsed listeners survive GC; test scope-end cleanup, slow callbacks, and reentrant changes.
- **Not:** [Event Queue](game-programming.md#event-queue) defers delivery; cross-process [Publisher-Subscriber](distributed-systems.md#publisher-subscriber) needs messaging delivery semantics, not ordinary synchronous callbacks.

## State
- **Choose when:** State changes alter several operations and entry/exit actions must establish and release lifecycle conditions.
- **Simpler first:** Use an enum/switch; upgrade when branching and cleanup repeat. Separate independent machines rather than multiplying state combinations.
- **Contract:** Specify transition requester and commit boundary; centralize exit/change/enter and define same-tick update order.
- **Traps:** Actor-specific timers cannot live in shared state instances. Test interruptions, recursive transition requests, and cleanup, not just successful entry.
- **Not:** [Strategy](behavioral.md#strategy) replaces an algorithm, usually caller-selected, without owning a lifecycle or transition graph.

## Strategy
- **Choose when:** Several real algorithms share one role while selection varies independently of the consuming workflow.
- **Simpler first:** Use a function/lambda or parameter data; add objects only when algorithm dependencies/state need explicit ownership, not for difficulty multipliers.
- **Contract:** Align inputs, failures, side effects, and cost expectations; do not accidentally share mutable execution state across actors or requests.
- **Traps:** Downcasts and whole-context access indicate incompatible responsibilities; test each algorithm against the same contract, including failures.
- **Not:** [Command](behavioral.md#command) packages a request; Strategy supplies how it executes.

## Template Method
- **Choose when:** Existing subclasses share an invariant workflow while a few narrow steps differ.
- **Simpler first:** Pass callbacks to a function; upgrade when inheritance already fits and the base must own ordering. Compose independent steps instead.
- **Contract:** Define invariants hooks may change; never invoke overridable steps before subclass initialization.
- **Traps:** Base-order changes affect every subclass; test representative overrides together. Skipped/reordered steps or proliferating optional hooks signal a false shared skeleton.
- **Not:** [Subclass Sandbox](game-programming.md#subclass-sandbox) gives subclass-authored behavior a constrained toolkit rather than fixing its overall sequence.

## Visitor
- **Choose when:** Element kinds stay stable while new cross-cutting, type-specific operations are frequent.
- **Simpler first:** Use an exhaustive pattern match or switch; upgrade only when explicit dispatch makes operations clearer.
- **Contract:** Assign traversal to exactly one owner; expose meaningful queries rather than opening private representation for visitors.
- **Traps:** New element kinds change the visitor contract and implementations; default no-op visits hide omissions. Test every element kind and exactly-once traversal; interaction matrices can grow rapidly.
- **Not:** [Iterator](behavioral.md#iterator) traverses; Visitor selects type-specific operations, not necessarily traversal order.
