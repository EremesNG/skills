# Decision Framework

Use this reference when several solutions look plausible, the request starts
with a named pattern, or the cost of the architecture could exceed the value of
the feature. The objective is not to identify the most sophisticated option; it
is to make the smallest decision that remains safe under the observed forces.

## Problem classifier

Classify the problem by the behavior that must vary or remain stable. A prompt
can contain several signals, but select one dominant force before composing
solutions.

| Signal in the code or requirement | Dominant force | First options to examine |
| --- | --- | --- |
| Repeated construction/setup or runtime-selected types | Creation | Direct factory method, Factory, Builder, Prototype/Prefab, pool |
| A third-party or platform API leaks through gameplay code | Translation | Adapter, Facade, anti-corruption boundary |
| Many combinations create subclass explosion | Composition | Components, Strategy, Decorator, Composite, data-driven effects |
| One change fans out to independent reactions | Communication | Direct call, C# event, UnityEvent, scoped channel, mediator |
| Behavior changes by mode and transitions matter | State | Enum/switch, State, FSM, HFSM |
| One goal has interchangeable algorithms | Variation | Function/delegate, Strategy, policy asset |
| Requests need queue, replay, undo, or serialization | Action history | Command plus explicit state capture |
| Complex values are derived repeatedly from changing inputs | Recalculation | Direct calculation, Dirty Flag/cache, broker/modifier chain |
| UI contains domain rules or is hard to test | Presentation | Passive View plus Presenter/controller boundary |
| Shared services have hidden creation and lifetime | Dependency ownership | Inspector reference, composition root, manual DI, container only at scale |
| NPCs must choose actions under changing conditions | Decision-making | Rules, FSM/HFSM, behavior tree, utility, GOAP, learned policy |
| A measured hot path scales poorly with entity count | Data/scale | Pooling, batching, spatial partition, jobs/Burst, ECS after evidence |

If the symptom is merely a large class, do not choose a pattern from size alone.
Find the reason it changes: mixed ownership, mixed lifetimes, repeated variation,
or missing domain boundaries.

## Decision forces

Record only forces that can make one candidate win over another:

- **Behavior contract**: player-visible outcome, inputs, outputs, transitions,
  failures, invariants, and latency.
- **Change frequency**: which behavior is likely to vary, how often, and who
  changes it. Stable code does not need speculative extension points.
- **Cardinality and scale**: instances, events, agents, commands, states, assets,
  scenes, and concurrent operations at representative peaks.
- **Ownership and lifetime**: creator, authoritative owner, scene/session/app
  lifetime, initialization, teardown, and behavior during reload or cancellation.
- **Authoring**: whether programmers, designers, technical artists, or live-ops
  data own changes; required Inspector/graph/debug visibility.
- **Serialization and persistence**: asset data versus runtime state, save/replay,
  version migration, and reference stability.
- **Testability and observability**: public seam, deterministic inputs, logs,
  graph/state visibility, and failure diagnosis.
- **Determinism**: reproducible random/time inputs, ordering, simulation ticks,
  rollback, and cross-platform numeric expectations.
- **Network authority**: server/client ownership, prediction, validation,
  replication cost, and whether decisions or only results cross the network.
- **Frame budget**: target hardware, update frequency, main-thread milliseconds,
  allocation budget, memory ceiling, and measured baseline.
- **Adoption cost**: files, concepts, packages, editor tooling, build size,
  training, migration, and ongoing debugging burden.

Unknown forces are not automatically blockers. Label them, choose a reversible
default, and state which observation could reverse it.

## No-pattern gate

Prefer a direct mechanism when all material conditions remain true:

- one or two callers and a stable ownership path;
- one lifetime with obvious initialization and teardown;
- no queueing, undo, replay, family creation, or runtime substitution;
- no designer-authored polymorphism or cross-scene communication requirement;
- a small stable state/branch set;
- a public test can exercise the behavior without a new abstraction;
- no measured scale or performance pressure requires a specialized structure.

Examples of valid professional answers include a serialized component reference,
a direct method call, a named C# event, a short enum/switch, a delegate, a list or
dictionary, or one focused component. Do not wrap a stable method in an
interface, command, event bus, and service locator merely to appear extensible.

Fail the no-pattern gate only for a named force. "The project might grow" is not
enough; identify the expected change and its cost.

## Option ladder

Compare adjacent levels before jumping upward:

1. **Direct mechanism**: language feature, component reference, built-in Unity
   API, or small data structure.
2. **Local pattern**: one interface or object family around a single variation
   seam, owned by one subsystem.
3. **Subsystem architecture**: explicit composition root, lifecycle, data flow,
   assembly boundary, and test harness for repeated interactions.
4. **Project framework**: DI container, graph authoring tool, ECS/DOTS, global
   messaging, or third-party platform adopted across teams.

Choose the lowest level that satisfies the contract. A higher level must name a
recurring cost it removes, the team that owns it, the debugging model, and an
exit/migration strategy.

## Compare credible candidates

For each candidate, answer with evidence rather than a generic pros/cons list:

| Dimension | Question |
| --- | --- |
| Contract fit | Which acceptance scenario becomes simpler or safer? |
| Coupling | Which concrete dependency becomes explicit, stable, or replaceable? |
| Lifetime | Who creates, resets, disposes, unregisters, or cancels it? |
| Authoring/debug | Can the responsible role configure and inspect it? |
| Runtime cost | What work/allocation happens per event, frame, agent, or load? |
| Failure mode | How does missing configuration, stale state, or partial failure surface? |
| Test seam | Which behavior can be tested without an entire scene or service? |
| Migration | Can it be introduced and rolled back incrementally? |

Reject candidates that solve a different problem. For example, Object Pooling
addresses reuse cost, not arbitrary Instantiate bugs; an event bus addresses
communication topology, not ownership; ECS addresses data-oriented scale, not a
large manager by itself.

## Compose without multiplying responsibility

A composition is justified when each element owns a different force, such as:

- Factory selects a prefab type; Object Pool owns reuse and reset.
- State owns mode transitions; Strategy varies one algorithm inside a state.
- Behavior tree owns control flow; Blackboard owns shared decision memory;
  NavMesh owns pathfinding.
- MVP isolates presentation; Observer publishes model changes.
- ScriptableObject stores authored configuration; a runtime service owns mutable
  session state.

Avoid overlapping global mechanisms. A static event bus, service locator,
Singleton, and ScriptableObject event channel together can make dependency and
lifetime flow impossible to trace.

## Compact decision record

Use this structure for any nontrivial recommendation:

```text
Problem: <observable contract and dominant force>
Evidence: <project facts, measurements, user constraints, labeled unknowns>
Selected option: <one bounded solution>
Why: <which forces it satisfies and at what cost>
Rejected alternatives: <credible option -> concrete reason it loses here>
Boundaries: <owner, dependencies, data flow, lifetime, initialization, teardown>
Consequences: <added complexity, failure modes, migration and rollback>
Verification: <tests, builds, target profiling, acceptance threshold>
Revisit when: <measurable trigger that invalidates this choice>
```

Keep the record close to the implementation or handoff. Do not manufacture an
ADR file unless the repository uses ADRs or the decision is durable enough to
need one.

## Revisit triggers

Prefer measurable triggers over calendar promises:

- callers, variants, states, or supported platforms exceed the current simple
  structure's explicit limit;
- scene/session lifetimes diverge and current ownership cannot express them;
- a designer needs authoring or debugging that code-only configuration blocks;
- network authority, replay, save migration, or deterministic simulation becomes
  a real requirement;
- target-device profiling crosses a named frame, allocation, memory, or loading
  budget;
- tests require repeated scene/service setup because the public seam is wrong;
- a package or Unity upgrade invalidates the API or serialization assumption.

Until a trigger occurs, do not prepay framework cost.
