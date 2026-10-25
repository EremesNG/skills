# Unreal Engine Caveats

Load only when an Unreal-specific caveat could change the design; mappings are not equivalences.
Unreal-specific skills win on API details, lifecycle rules, and project conventions.

## Design-Changing Caveats

- **Observer** — Delegates and Blueprint event dispatchers → binding does not establish ownership; align subscription cleanup with the receiver's lifetime.
- **Service scope** — Engine, GameInstance, World, and LocalPlayer Subsystems → scope-bound services, not process-wide singletons; GameInstance-scoped services must clear world-lifetime references across world transitions. Lookup is service location, not injection.
- **Prototype** — Blueprint classes and class default objects (CDOs) → a CDO is a class template, not a live gameplay instance to clone; Data Assets describe configuration rather than actor copies.
- **Shared data** — Data Assets, Primary Data Assets, DataTable rows, and instanced static meshes → sharing configuration or rendering does not make mutable per-instance state safe to share; store it separately.
- **State and AI** — StateTree, Behavior Trees with Blackboard, Gameplay Ability System, and animation state machines → hierarchical state selection, AI decisions, ability/tag logic, and animation transitions are different responsibilities.
- **Object pooling** — Actor reuse → hiding is not release; reset lifecycle state, collision, ticking, and replication before reuse. See [Object Pool](../game-programming.md#object-pool).
- **Update ordering** — Tick groups, prerequisites, and TimerManager → express ordering through engine hooks rather than introducing a competing gameplay loop.
- **Concurrency** — Tasks system and dependencies → scheduling dependencies do not make UObject access thread-safe; isolate worker-safe computation and marshal game-thread-only changes back to the game thread.
- **Memento** — USaveGame and save-slot APIs → selected state needs an explicit schema; these do not provide an automatic world snapshot or complete undo history.
- **Networking** — Replication, RPCs, ownership, authority, and Actor relevancy → these are distinct decisions; replication neither validates client requests nor selects a prediction strategy. See [Multiplayer Architecture](../game-programming.md#multiplayer-architecture).

## ECS

MassEntity is ECS, not ActorComponent composition; account for Actor/entity bridging costs.
Core is production-ready since 5.2 and part of engine runtime since 5.5; companion plugins' maturity varies.

## Version Notes

Official docs verified 2026-10-25; live Unreal Engine docs rendered as 5.8.
StateTree, Enhanced Input, Tasks, modules, and Mass-related features require target-version checks.
