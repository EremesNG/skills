# Roblox Caveats

Load only when a Roblox-specific caveat could change the design; mappings are not equivalences.
Roblox-specific skills win on API details, runtime restrictions, and deployment conventions.

## Design-Changing Caveats

- **Observer** — RBXScriptSignal and BindableEvent → retain connections for deliberate Disconnect; BindableEvent stays within one runtime, not across client/server boundaries.
- **Service scope** — ModuleScript require caching and GetService → results are cached per Luau environment, not globally across client and server; lookup is not injection. See [Singleton](../creational.md#singleton).
- **Shared data** — ModuleScript tables and Attributes → mutable tables alias within an environment; Attributes are per-instance metadata, and client-visible configuration is neither secret nor authoritative.
- **Composition** — CollectionService tags → classify Instances, but provide neither ECS storage/scheduling nor a complete component lifecycle.
- **State and AI** — Humanoid states → character-specific states are not a general gameplay FSM or AI graph; use explicit gameplay state logic where needed.
- **Object pooling** — Instance reuse → reset signal connections, physics, network ownership, and gameplay state; reuse does not supply cleanup guarantees.
- **Update ordering** — RunService Heartbeat, PreSimulation, PostSimulation, and PreRender → choose the simulation/render phase deliberately; render callbacks are client-only.
- **Deferred work** — task.defer, task.delay, and task.spawn → engine scheduling points are not exact deadlines or guarantees of domain-event ordering and durability.
- **Persistence** — Server-only DataStoreService → design for request budgets, failures, and concurrent updates with UpdateAsync; this is not an automatic session snapshot.
- **Networking** — RemoteEvent, RemoteFunction, and Instance replication → validate client payloads on the server; server-side gameplay decisions do not guarantee physics network ownership. See [Multiplayer Architecture](../game-programming.md#multiplayer-architecture).
- **Remote calls** — Server-to-client RemoteFunction → the client can fail to return; critical server progress must not depend on a timely response.
- **Concurrency** — Parallel Luau Actors → obey parallel-safe API restrictions and do not assume mutable ModuleScript state is shared across Actors.

## ECS

No built-in ECS identified in official docs (verified 2026-10); CollectionService tags alone are not ECS.
Matter and jecs are community libraries with unverified maintenance.

## Version Notes

Live Roblox Creator Hub docs verified 2026-10-25; Input Action System availability is rollout-sensitive.
Check current RunService timing and parallel API safety; do not assume older Stepped/RenderStepped examples have identical timing.
