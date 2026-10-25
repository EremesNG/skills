# Godot Caveats

Load only when a Godot-specific caveat could change the design; mappings are not equivalences.
Godot-specific skills win on API details, scene lifecycle, and version-specific usage.

## Design-Changing Caveats

- **Observer** — Signals and CONNECT_DEFERRED → connection lifetime and receiver ownership still matter; deferred delivery changes timing, not ownership or domain meaning.
- **Service scope** — Autoload nodes/scripts → not strictly enforced singletons; reserve cross-scene lifetime deliberately rather than letting global access determine ownership.
- **Prototype** — PackedScene.instantiate() and Node.duplicate() → duplicating a node does not deep-copy every referenced Resource; inspect duplication rules before assuming independent state. See [Prototype](../creational.md#prototype).
- **Shared data** — Cached Resources and resource_local_to_scene → mutable shared Resources affect all users; enabling scene-local copies later does not retrofit already-instantiated copies.
- **Composition** — Reusable scenes and exported references → coupling a scene to external get_node paths undermines reuse; inject scene-local dependencies or communicate through its boundary.
- **State and AI** — AnimationTree and AnimationNodeStateMachine → animation state transitions are not a general gameplay AI architecture; keep gameplay state logic separate.
- **Object pooling** — Node reuse → hiding does not deactivate processing, physics, or collisions; reset those and gameplay state explicitly. See [Object Pool](../game-programming.md#object-pool).
- **Update ordering** — _process and _physics_process → physics uses a fixed tick; keep rendering-rate assumptions out of physics logic rather than adding a competing loop.
- **Deferred work** — call_deferred and deferred signal connections → neither worker-thread execution nor a domain-event queue with persistence and backpressure.
- **Networking** — MultiplayerAPI, RPCs, MultiplayerSpawner, and MultiplayerSynchronizer → assigning authority does not validate remote requests; define server checks and replication boundaries separately.
- **Concurrency** — WorkerThreadPool and Thread → the active scene tree is not thread-safe; isolate worker data and apply scene changes through supported main-thread mechanisms.

## ECS

No built-in ECS identified in official docs (verified 2026-10); nodes/scenes are composition, not ECS.

## Version Notes

Official Godot stable 4.x docs verified 2026-10-25; the stable alias moves, and 3.x examples are not interchangeable.
Check Resource duplication/local-to-scene semantics and thread-safe operations against the project's exact version.
