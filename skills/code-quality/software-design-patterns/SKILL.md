---
name: software-design-patterns
description: Choose, apply and review patterns or architecture in any codebase. Use for pattern or architecture choices, tangled code, game systems (state machines, NPC AI, events, pooling, ECS, netcode), application or distributed architecture, and PR reviews for over-engineering or misapplied patterns, even when no pattern is named. Engine-agnostic with platform maps for Unreal, Unity, Godot, Roblox, TypeScript, Python, Java and .NET.
license: MIT
metadata:
  author: EremesNG
  version: "1.0.0"
  repository: https://github.com/EremesNG/skills
---

# Software Design Patterns

Choose the smallest design change that resolves a demonstrated force; patterns are means, not goals.
Add value through a real candidate contrast, explicit lifecycle contracts, platform traps and proportional scope.
Prefer a plain function or native mechanism when it meets the constraints.

## Boundaries

Defer APIs and lifecycle details to engine/framework skills such as `unity-developer` and `project-zomboid-modding`.
Use `simplify` for behavior-preserving cleanup and `grill-me` to interrogate open decisions.
Stay in scope and preserve sound conventions; offer larger redesigns as options, not unasked work.

## Workflow

1. Ground the choice in affected code, tests, engine/stack version, scale and constraints; distinguish evidence from assumptions.
2. Name the present force and point to evidence: variation, ownership, coupling, measured cost or failure. No force means no pattern.
3. Try the simplest thing first: function, enum/switch, data table, direct call or native feature. State the observable trigger that would justify upgrading.
4. Make one meaningful contrast with the closest credible alternative; explain why it loses here in state, ordering, ownership, indirection or migration cost. Do not survey patterns.
5. Apply incrementally, testing changed seams and preserving behavior; avoid combining patterns before the first earns its cost.
6. Verify failure and lifecycle paths; profile performance claims before/after and check determinism and desync behavior for netcode. Separate completed checks from proposed checks and unverified risks.

## Lifecycle and Interruption Checklist

- Name the owner and scope of each piece of state; make transfer and teardown explicit.
- Give each state machine one transition commit point per tick and explicit priority among competing requests.
- Queue transition requests from callbacks/signals; never transition recursively from them.
- Release acquired effects on exit, cancellation and interruption, including failed entry paths.
- Invalidate stale async completions with a generation counter/token; revalidate resumed or queued work before applying it.
- Tie subscriptions, timers, pooled objects and despawn cleanup to the owner's lifetime.
- Keep shared definitions/assets read-only; keep mutable runtime state per instance.
- Test interruption, re-entry of the same state and repeated lifetimes, including pool reuse and scene reload.

## Remote and Async Work

- Set a per-attempt timeout and an overall deadline; assign exactly one retry owner, not stacked retry layers.
- Treat a timeout as an ambiguous outcome, not proof of failure; require a receiver-enforced idempotency key for retried effects.
- Handle partial success explicitly; test duplicate delivery, late completion and interrupted recovery.
- Add durable handoff (outbox/queue) only if a stated requirement demands surviving process failure; say so conditionally, not by default.

## Proportionality Rules

- Justify every abstraction with current variation, a test seam, an external-system boundary or measured performance; one implementation can still justify a seam.
- Do not equate fewer classes with safety: preserve structures that protect invariants and ownership.
- When flags and branches accumulate in an abstraction, re-inline before re-abstracting.
- Give global access (singleton, locator, autoload, subsystem) explicit scope and teardown; lookup is not injection.
- Do not add a pattern to fix a pattern; avoid both speculative generality and dogma such as "FSM always", "no interfaces" or "never distribute".
- Consult [principles](references/principles.md) for SOLID over-application and the DI versus Service Locator debate.

## Reviewing Designs

Flag unnecessary indirection and missing structure; tie each finding to a present force and consequence.
Prioritize correctness defects caused by indirection: lifecycle leaks, unawaited async, ordering and lapsed listeners; trace registration through teardown.
Make removals concrete: name what to inline, its direct replacement and the protecting test.
Say when no actionable findings remain; do not invent a redesign.

## Symptom to Pattern

Start with the middle column; treat candidates as hypotheses, not prescriptions.

| Symptom | Try first | Candidates |
| --- | --- | --- |
| State soup | Enum + transitions | [State](references/behavioral.md#state), [HSM](references/game-ai.md#hierarchical-state-machine) |
| Data-only types / authored behavior | Validated tables | [Type Object](references/game-programming.md#type-object), [Data-Driven](references/application-architecture.md#data-driven-design), [Bytecode](references/game-programming.md#bytecode) |
| Algorithm variants | Function parameter | [Strategy](references/behavioral.md#strategy), [Template Method](references/behavioral.md#template-method) |
| Scattered / staged creation | Constructor function | [Factory Method](references/creational.md#factory-method), [Abstract Factory](references/creational.md#abstract-factory), [Builder](references/creational.md#builder) |
| Undo / replay / queued actions | Action records | [Command](references/behavioral.md#command), [Memento](references/behavioral.md#memento) |
| Listeners / deferred processing | Signals / bounded queue | [Observer](references/behavioral.md#observer), [Event Bus](references/application-architecture.md#event-bus), [Event Queue](references/game-programming.md#event-queue) |
| Coupled peers / object trees | Ownership / traversal | [Mediator](references/behavioral.md#mediator), [Component](references/game-programming.md#component), [Composite](references/structural.md#composite) |
| Vendor leaks / legacy replacement | Thin boundary wrapper | [Adapter](references/structural.md#adapter), [Anti-Corruption Layer](references/distributed-systems.md#anti-corruption-layer), [Strangler Fig](references/distributed-systems.md#strangler-fig) |
| Stackable modifiers | Function composition | [Decorator](references/structural.md#decorator) |
| Hidden global dependencies | Explicit parameters/scope | [DI](references/principles.md#dependency-injection-and-composition-root), [Service Locator](references/game-programming.md#service-locator) |
| Measured loop / allocation / query cost | Profile; batch or scan first | [Data Locality](references/game-programming.md#data-locality), [Object Pool](references/game-programming.md#object-pool), [ECS](references/ecs-data-oriented.md#when-ecs-pays-off), [Spatial Partition](references/game-programming.md#spatial-partition) |
| Simulation jitter | Native fixed tick | [Game Loop](references/game-programming.md#game-loop), [Double Buffer](references/game-programming.md#double-buffer) |
| Complex NPC rules | Small FSM first | [HSM](references/game-ai.md#hierarchical-state-machine), [Behavior Tree](references/game-ai.md#behavior-tree), [Utility AI](references/game-ai.md#utility-ai) |
| Network feel / cheating | Authority + latency budget | [Server](references/game-programming.md#authoritative-server), [Prediction](references/game-programming.md#client-side-prediction-and-reconciliation), [Rollback](references/game-programming.md#rollback-netcode) |
| UI tangled with view | Pure state updates | [MVC](references/application-architecture.md#mvc), [MVVM](references/application-architecture.md#mvvm), [Unidirectional Flow](references/application-architecture.md#unidirectional-data-flow) |
| Domain tangled with I/O | Pure core + explicit I/O | [Layers](references/application-architecture.md#layered-architecture), [Hexagonal](references/application-architecture.md#hexagonal-architecture), [Modular Monolith](references/application-architecture.md#modular-monolith) |
| Read/write divergence / partial transactions | Queries / local transaction | [CQRS](references/distributed-systems.md#cqrs), [Saga](references/distributed-systems.md#saga), [Outbox](references/distributed-systems.md#transactional-outbox), [Idempotent Consumer](references/distributed-systems.md#idempotent-consumer) |
| Flaky remote dependency | Deadline; safe retries | [Timeout](references/distributed-systems.md#timeout), [Retry](references/distributed-systems.md#retry-with-backoff), [Circuit Breaker](references/distributed-systems.md#circuit-breaker) |

## References

Read none when the answer is clear; otherwise search headings and open only the section behind the candidate being weighed, not whole files.
Open a platform map only if its caveat could change the design; use the stack actually being changed and verify relevant versions.
Never open sources during normal work; use that index only for attribution or reuse questions.
- [Principles](references/principles.md): abstraction cost; [Creational](references/creational.md): construction; [Structural](references/structural.md): wrappers/trees.
- [Behavioral](references/behavioral.md): collaboration/state; [Game programming](references/game-programming.md): loops/reuse/netcode; [Game AI](references/game-ai.md): decision architecture.
- [ECS/DOD](references/ecs-data-oriented.md): measured layout/scheduling; [Application](references/application-architecture.md): module/UI boundaries; [Distributed](references/distributed-systems.md): remote failure.
- [Unreal](references/platforms/unreal.md): engine ownership; [Unity](references/platforms/unity.md): components/assets; [Godot](references/platforms/godot.md): nodes/resources.
- [Roblox](references/platforms/roblox.md): client/server lifetimes; [General stacks](references/platforms/general-stacks.md): language idioms; [Sources](references/sources.md): attribution only.

## Output

Match length to the question; do not force a multipart template onto a small answer.
Default to a decision and why (including the one contrast), the key contract, a minimal sketch, a few tests at changed seams and a revisit trigger.
Expand into migration plans or full code only when asked or clearly needed.
For reviews, give severity-ordered findings with location, consequence and a simpler alternative.
Reply in the user's language and preserve project naming conventions.

## Sources

Use independently written summaries, not copied prose or figures; see [sources](references/sources.md).
