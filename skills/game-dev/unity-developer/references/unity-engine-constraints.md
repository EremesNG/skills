# Unity engine constraints

Use this reference before implementing or reviewing any solution that depends on
Unity object lifetime, serialization, frame callbacks, asynchronous work, pools,
tests, or performance. Confirm APIs against the project's installed Unity and
package versions.

## Lifecycle ownership

Unity callback order is context-dependent. Do not use callback names as a
substitute for an ownership model.

| Callback | Appropriate responsibility | Frequent failure |
|---|---|---|
| `Awake` | establish internal invariants; construct owned plain C# state | depending on another object's `Awake` order |
| `OnEnable` | subscribe and start work scoped to the enabled interval | starting the same work twice after re-enable |
| `Start` | first-frame coordination when enabled objects have completed `Awake` | treating it as a project-wide readiness guarantee |
| `OnDisable` | unsubscribe, pause, or cancel enabled-scope work | assuming it means permanent destruction |
| `OnDestroy` | release resources owned for the component lifetime | relying on it as the only application-quit persistence hook |

Make initialization and teardown symmetric. If `OnEnable` subscribes, `OnDisable`
must unsubscribe. If a component creates a native resource, runtime clone, or
long-lived task, identify the callback or explicit method that releases it.

Avoid cross-object script execution order dependencies. Prefer an explicit
composition root and an initialization method when collaborators need ordered
startup. Use configured script execution order only at a narrow engine boundary
and document the invariant it protects.

## Destroyed Unity objects

Objects derived from `UnityEngine.Object` have special null semantics: a managed
wrapper may remain while the native object has been destroyed. Therefore:

- use Unity-aware validity checks for Unity object references;
- do not use null-conditional (`?.`) or null-coalescing assumptions as the sole
  destroyed-object check without confirming the relevant Unity behavior;
- never retain scene objects past scene unload unless their owner and lifetime are
  explicit;
- treat callbacks captured by tasks, delegates, or closures as possible lifetime
  extensions;
- revalidate a Unity object after an `await` because it may have been destroyed or
  disabled while execution was suspended.

Plain C# objects do not have these semantics. Isolate engine references at an
adapter boundary when rules do not require them.

## Domain reload and static reset

Editor Play Mode options can disable Domain Reload. Static fields and static event
handlers may then survive between play sessions. Code must not depend on a fresh
managed domain for correctness.

- Give every mutable static an explicit static reset policy.
- Use the version-appropriate Unity runtime initialization hook when a static must
  reset before play starts.
- Clear static events or, preferably, avoid global static event ownership.
- Test repeated enter/exit Play Mode and repeated session start without restarting
  the Editor.
- Treat singleton `Instance` fields and static caches as state with a named owner,
  not as harmless syntax.

Do not assume that disabling Domain Reload has the same effect across Unity
versions. Check version-matched documentation and project settings.

## Events and delegates

The publisher normally retains delegate references to subscribers. Align the
subscription with the shortest required lifetime:

```csharp
private void OnEnable()  => model.Changed += HandleChanged;
private void OnDisable() => model.Changed -= HandleChanged;
```

Always subscribe and unsubscribe symmetrically. Additional safeguards:

- make repeated subscription idempotent or prove it cannot occur;
- do not use anonymous lambdas when later removal requires the original delegate;
- define whether event ordering matters and whether a listener may mutate the
  collection during delivery;
- capture and surface listener failures deliberately rather than swallowing them;
- test disable/enable, scene reload, and pooled reuse;
- avoid strong global publishers retaining destroyed scene objects.

## Unity serialization

Unity serialization is an authoring and persistence mechanism with version- and
type-specific rules. It is not equivalent to arbitrary .NET serialization.

- Prefer supported fields with explicit `[SerializeField]` when Inspector
  authoring is required.
- Keep serialized data separate from runtime caches, subscriptions, tasks, and
  native resources.
- Use `ISerializationCallbackReceiver` only when a simpler serialized shape is
  insufficient; callbacks should transform data, not perform Unity scene work.
- Plan migration before renaming fields, moving types, or changing polymorphic
  representations.
- Validate prefab, scene, and asset round-trips in the target Unity version.

`SerializeReference` supports managed-reference graphs and polymorphism but adds
identity, editor tooling, migration, and missing-type risks. Use it only when the
authored graph truly needs shared references or polymorphic managed objects.
Prefer a tagged serializable value, separate assets, or explicit composition when
those are easier to inspect and migrate.

Do not serialize runtime delegates, cancellation sources, or arbitrary service
graphs. Reconstruct runtime behavior from stable authored data.

## ScriptableObject safety

`ScriptableObject` is a good home for shared authored definitions. A referenced
asset is shared, so mutating it at runtime can couple actors and can create
confusing Editor behavior.

- Treat definition assets as read-only at runtime.
- Create actor/session-owned plain C# runtime state from authored values.
- If a runtime `ScriptableObject` clone is required, name its owner and destroy the
  clone during teardown.
- Do not store transient listeners, scene objects, or save-game state in a shared
  asset without a deliberate reset and persistence contract.
- Test with the project's Domain Reload settings.

## Asynchronous work and threading

Most Unity API calls must occur on the Unity main thread. A background operation
may calculate over thread-safe plain data, but it must marshal results back through
a documented boundary before touching Unity objects.

Every asynchronous operation needs:

- an owner and lifetime;
- a `CancellationToken` or equivalent cancellation path;
- cancellation during the matching teardown operation;
- exception observation and reporting;
- a post-`await` validity check for any Unity object;
- a concurrency policy preventing stale or out-of-order results;
- a main-thread handoff mechanism validated for the chosen async library and Unity
  version.

Avoid `async void` except for unavoidable event/callback adapters that contain and
report exceptions. Return `Task`/the project-standard awaitable from testable
methods. Do not call Unity APIs from `Task.Run`, jobs, or worker threads unless the
specific API is documented thread-safe.

For component-scoped work, a safe shape is to create a cancellation source at
startup, pass its token down, cancel it at teardown, and dispose it. Also guard
against an older completion overwriting a newer request.

## Frame callbacks and scheduling

Do not move work into a manager merely because many objects use `Update`.
Classify the work first:

- event-driven work should run only when its input changes;
- fixed-step simulation belongs in an explicit fixed-timestep path;
- visual interpolation may use frame time but should not own authoritative state;
- expensive periodic work can be budgeted, staggered, or scheduled;
- large homogeneous numeric workloads may justify jobs/Burst/ECS after profiling.

An Update Manager trades engine callbacks for registration, ordering, lifetime,
and dispatch complexity. It does not automatically improve cache locality or
performance. Measure both versions at representative scale.

## Object pooling and pool reset

Pooling is a lifetime optimization, not a universal creation pattern. Use it when
profiles show recurring creation/destruction cost or allocation pressure at
representative frequency.

A pooled object needs an explicit state contract:

1. `Create` constructs one valid inactive instance.
2. `OnGet` establishes all state required for a new lease.
3. `OnRelease` performs a complete pool reset: subscriptions, timers, particles,
   physics state, animation triggers, navigation paths, ownership references,
   cancellation, and gameplay state.
4. `OnDestroy` releases the object when the pool discards it.

Test reuse across multiple leases. Avoid double release, use-after-release, and
returning an object to a destroyed pool. Bound pool size and define overflow
behavior. A pool can increase retained memory and stale-state risk; remove it when
evidence no longer supports it.

## Determinism, replay, and networking

When deterministic behavior matters, define it precisely: same decisions, same
simulation state, same rendered result, or merely repeatable tests.

- Use an explicit random source and seed; do not scatter calls to global random
  state.
- Separate authoritative simulation time from rendering time.
- Define ordering for commands, events, and simultaneous state transitions.
- Avoid depending on unordered collection traversal for authoritative results.
- Quantize or otherwise constrain numeric behavior only to the degree required by
  the networking/replay design.
- Record external inputs and relevant version/schema information for replay.
- Do not assume Unity physics is bitwise deterministic across platforms.

For multiplayer, name the authority for each state transition and AI decision.
Clients may predict or present, but must not silently become authoritative.

## Test seams

Use the narrowest test environment that can falsify the behavior:

- **Plain C# seam:** pure rules, state transitions, decision scoring, command
  history, serialization DTOs, and adapters behind interfaces.
- **EditMode:** Unity object/editor integration that does not require frame or scene
  progression.
- **PlayMode:** lifecycle, coroutines/async integration, scenes, physics,
  navigation, animation, pools, and frame-dependent behavior.
- **Target build:** platform APIs, stripping/AOT, input, graphics, memory, jobs, and
  real performance.

Keep the plain C# seam large enough that most rule failures are fast and
diagnosable. Use PlayMode tests for actual engine contracts instead of mocking
Unity lifecycle. Add regression tests for disable/enable, destroy, scene reload,
Domain Reload configuration, cancellation, and pooled reuse.

## Profiling contract

Measure before optimizing. Establish a reproducible baseline and a performance
budget for the relevant device class, scene, content scale, build configuration,
and workload.

Use Editor profiling for exploration, then validate with a development or release-
representative build on the target device. Capture at least:

- Unity and package versions;
- target hardware/OS and thermal state when material;
- build settings and scripting backend;
- scene/content scale and reproduction steps;
- frame-time distribution rather than only an average;
- CPU, GPU, memory/allocation, and loading evidence relevant to the claim;
- before/after captures using the same procedure.

Do not claim a performance improvement from code shape, fewer callbacks, pooling,
jobs, Burst, or ECS alone. Do not claim target-device performance from Editor-only
measurements. If the requested environment cannot be profiled, report the expected
mechanism as a hypothesis and provide the exact measurement plan.

## Final engine-safety check

Before handoff, confirm:

- ownership, initialization, and teardown are explicit;
- destroyed Unity objects cannot be used after disable, destroy, unload, or await;
- static reset behavior works with the project's Domain Reload setting;
- every event and task has cleanup and cancellation;
- serialized data has a migration and runtime-state boundary;
- pooled instances pass a second-lease test;
- authoritative ordering, time, randomness, and network ownership are defined;
- fast rules use a plain C# seam and engine contracts use EditMode/PlayMode tests;
- every performance conclusion is backed by a representative build on a target
  device, or is labeled unverified.
