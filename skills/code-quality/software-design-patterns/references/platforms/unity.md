# Unity Caveats

Load only when a Unity-specific caveat could change the design; mappings are not equivalences.
Unity-specific skills win on API details, package setup, and lifecycle rules.

## Design-Changing Caveats

- **Observer** — C# events and UnityEvent → Inspector-persistent listeners and runtime subscriptions have different lifecycles; choose whether cleanup follows enablement, destruction, or a longer scope. See [Observer](../behavioral.md#observer).
- **Service scope** — Static state, shared ScriptableObjects, and DontDestroyOnLoad managers → none enforces uniqueness or useful scope; explicitly handle duplicate managers, scene transitions, play-session resets, and teardown.
- **Dependency injection** — Serialized references and plain C# constructor injection → the engine constructs MonoBehaviours; do not construct them like ordinary domain objects.
- **Prototype** — Prefabs and variants → asset overrides are not saved runtime instance state, and instantiation is not a general deep-copy contract.
- **Shared data** — ScriptableObject assets → runtime mutation affects every user and may persist in the Editor; keep per-instance/session state separate. Assets are not deployed-build save storage.
- **State and AI** — Animator, Visual Scripting state graphs, and Unity Behavior trees → animation, gameplay state, and AI decisions differ; Unity Behavior is a separately versioned package, not an assumed core feature.
- **Object pooling** — UnityEngine.Pool.ObjectPool<T> → not thread-safe; callbacks and callers own state reset and associated-resource cleanup. See [Object Pool](../game-programming.md#object-pool).
- **Update ordering** — FixedUpdate → can run zero or multiple times per rendered frame; do not assume a one-to-one relationship with Update.
- **Deferred work** — Coroutines and Awaitable → coroutines run on the main thread; Awaitable permits explicit thread switching, but suspension or async syntax alone does not establish background execution.
- **Persistence** — JsonUtility and Unity serialization → field/type restrictions include no JsonUtility Dictionary support; identity, schema migrations, and storage remain separate decisions.
- **Networking** — Netcode for GameObjects and Netcode for Entities → separate packages for different object models; package choice does not settle authority, request validation, or prediction.
- **Concurrency** — C# Job System and Burst → jobs and continuations must honor supported data/thread rules; Burst cannot call arbitrary UnityEngine APIs.

## ECS

Entities is the DOTS ECS package, separate from GameObject/MonoBehaviour composition.
Docs use the 1.4.x package line (verified 2026-10), not a guarantee that every Unity 6 editor bundles it.

## Version Notes

Official Unity 6000.x docs verified 2026-10-25 (mostly 6000.0; threading reference 6000.6).
Check Input System, Unity Behavior, Entities, Netcode, Awaitable, and worker-API versions against the target project.
