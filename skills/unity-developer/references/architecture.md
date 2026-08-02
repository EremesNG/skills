# Unity architecture selection

Use this reference when a problem crosses component, scene, feature, or team
boundaries. Architecture is a set of explicit ownership and dependency choices,
not a requirement to install a framework.

## Default shape

Prefer the smallest shape that preserves the required change boundary:

1. Keep local behavior in one component when it has one owner and one lifetime.
2. Extract plain C# policy when rules need fast tests or reuse.
3. Introduce a feature-level composition root when several collaborators need
   coordinated initialization and teardown.
4. Add a project-wide framework only when measured scale, tooling, or team
   constraints justify its runtime, learning, and migration costs.

A healthy default dependency flow is:

```text
Unity input/view adapters -> application use cases -> domain policy
Unity persistence/audio/navigation adapters <------ ports/interfaces
```

The domain does not know about scenes, prefabs, `MonoBehaviour`, or a dependency
container. Unity-facing adapters translate engine callbacks and data into explicit
calls.

## Composition root

A composition root is the one place that creates a feature's object graph,
connects dependencies, starts it, and disposes it. Choose a scope deliberately:

- **Prefab root:** a self-contained actor or reusable feature.
- **Scene root:** scene-specific presentation and services.
- **Session root:** state that survives scene transitions for one play session.
- **Application root:** truly process-wide infrastructure such as platform
  telemetry; use sparingly.

Keep construction separate from behavior. Serialized Unity references may enter
at the root, but collaborators below it should receive explicit constructor or
method dependencies whenever practical.

```csharp
public sealed class CombatInstaller : MonoBehaviour
{
    [SerializeField] private CombatHud hud = default!;
    [SerializeField] private WeaponTuning tuning = default!;

    private CombatPresenter? presenter;

    private void Awake()
    {
        var rules = new DamageRules(tuning.BaseDamage);
        presenter = new CombatPresenter(rules, hud);
    }

    private void OnEnable() => presenter?.Start();
    private void OnDisable() => presenter?.Stop();
}
```

The example is a shape, not a mandate: adapt it to the project's Unity and C#
versions and nullability policy.

## Ownership and lifetime

Every mutable resource needs one owner responsible for initialization and
teardown. Consumers may borrow or observe it, but must not silently extend its
lifetime.

| Scope | Typical owner | Initialization | Teardown | Common failure |
|---|---|---|---|---|
| Component | same `MonoBehaviour` | `Awake` or explicit `Initialize` | `OnDestroy` | another component destroys borrowed state |
| Enabled interval | same behavior/presenter | `OnEnable` / `Start` | `OnDisable` / `Stop` | duplicate event subscriptions |
| Scene | scene composition root | scene load | scene unload | stale references across scenes |
| Session | session root | new/load game | return to menu | static state survives the session |
| Application | bootstrap root | application boot | application quit | accidental global service graph |

For each dependency, record:

- who creates it;
- who can mutate it;
- whether it survives disable, scene unload, or a new session;
- who cancels work and releases subscriptions;
- what happens when its Unity object has been destroyed.

## Dependency direction

Stable policy should not depend on volatile delivery mechanisms. Keep these seams
explicit:

- **Domain policy:** plain C# values, rules, state transitions, and deterministic
  calculations.
- **Application orchestration:** use cases that coordinate domain policy through
  narrow interfaces.
- **Unity adapters:** `MonoBehaviour`, `ScriptableObject`, input, physics,
  navigation, animation, audio, scenes, and persistence.
- **Composition:** the only layer allowed to know concrete implementations across
  the graph.

Do not introduce an interface for every class. Add one at a true change boundary,
for a substitutable external service, or where a test seam provides material
value. A concrete class is simpler when there is one implementation and no
independent reason for substitution.

## Messaging

Select messaging by topology and semantics, not by fashion:

| Mechanism | Use when | Avoid when | Required discipline |
|---|---|---|---|
| Direct call | caller knows one receiver and needs an immediate result | producers and consumers must evolve independently | make ownership and error flow explicit |
| C# event / Observer | one producer notifies a small known set | ordering, history, or cross-scene discovery is required | subscribe and unsubscribe in symmetric lifetime hooks |
| ScriptableObject event channel | designers need authored wiring across prefabs | events carry transient or sensitive runtime state without an owner | distinguish the asset from runtime listeners; document replay behavior |
| Feature mediator | collaborators would otherwise form a dense graph | it becomes a generic manager for unrelated domains | keep commands/events typed and feature-scoped |
| Message bus | many independently deployed modules genuinely require decoupling | a direct call would express the relationship | define delivery order, failure policy, ownership, observability, and allocation budget |

Avoid string topics and a universal event bus. Typed, local messages make usage
searchable and preserve compile-time contracts.

## UI architecture

Separate view rendering from game rules when UI behavior is non-trivial:

- The **view** owns Unity widgets and translates user gestures.
- The **presenter/view-model** is plain C# where possible and exposes explicit
  state or commands.
- The **model/application layer** owns game state and use cases.

MVP is a strong fit for imperative Unity UI and explicit presenter tests. MVVM is
worth considering only when the selected UI technology and binding solution make
observable state cheaper than hand-written synchronization. For a small static
panel, a single view component is usually sufficient.

Do not let a view locate gameplay services globally. Inject a narrow use case or
bind the presenter in the relevant composition root. Dispose bindings and event
subscriptions when the view's scope ends.

## ScriptableObject data

Use `ScriptableObject` primarily for shared authored data: tuning, catalogs,
definitions, and designer-authored strategies. Treat the asset as a project
artifact, not automatically as a runtime state store.

Keep the distinction explicit:

| Data kind | Recommended home | Reason |
|---|---|---|
| Authored data | immutable/read-only `ScriptableObject` definition | shared Inspector authoring and stable asset identity |
| Per-actor runtime state | plain C# instance owned by actor/session | isolation, deterministic reset, and testability |
| Mutable session state | session-owned model, optionally initialized from an asset | prevents play-session changes leaking through a shared asset |
| Save data | versioned serializable DTO | persistence contract is separate from authoring format |

If a runtime clone of a `ScriptableObject` is justified, name its owner and
destroy it at teardown. Never assume an asset resets when entering Play Mode,
especially when Domain Reload settings vary.

## Scene boundaries

Treat scenes as deployment and lifetime boundaries, not as the primary service
locator.

- Put persistent boot/session services in an explicit bootstrap scope.
- Put scene presentation and scene-only state in a scene composition root.
- Prefer serialized references inside a scene/prefab over runtime name lookup.
- For additive scenes, define which scene owns shared services and how dependents
  signal readiness.
- Pass durable identifiers or immutable handoff data across transitions rather
  than retaining arbitrary scene object references.
- Test repeated load/unload and return-to-menu flows, not only first boot.

## Assembly definitions

Assembly definitions should encode dependency direction and reduce compilation
surface:

- keep domain/application assemblies free of Unity presentation dependencies when
  practical;
- place Editor-only code in Editor assemblies;
- place EditMode and PlayMode tests in test assemblies with only required
  references;
- avoid cyclic assembly references and catch them as an architecture defect;
- do not split assemblies so finely that navigation and configuration costs exceed
  build benefits.

Use assembly boundaries to enforce an already-understood design. They cannot make
an incoherent dependency graph coherent by themselves.

## Dependency injection

Dependency injection is the act of supplying dependencies; it does not require a
container.

Start with serialized references, constructors for plain C# objects, factories,
and explicit composition. A DI container passes the adoption gate only when the
project has enough graph complexity, dynamic scopes, or repeated installers that
its validated benefits exceed:

- reflection or generated-code constraints;
- startup and allocation cost;
- scene/prefab integration complexity;
- debugging indirection;
- team learning cost;
- platform and ahead-of-time compilation compatibility;
- migration and removal cost.

Do not adopt a container merely to avoid writing constructors. If selected, keep
container calls inside composition roots; application and domain code should not
resolve dependencies from the container. A Service Locator hides dependencies and
is appropriate only at a deliberately constrained legacy or engine boundary with
explicit failure and reset behavior.

## ECS/DOTS

ECS/DOTS can be valuable for large numbers of similarly processed entities,
data-oriented parallel workloads, or a project already committed to its authoring
and debugging model. It is not a general synonym for clean architecture.

Apply this adoption gate before committing:

1. A representative target-device profile identifies a data/layout or scale
   bottleneck that object-oriented code cannot meet economically.
2. A thin prototype demonstrates a material gain at representative scale.
3. The team accepts entity authoring, baking, jobs, Burst constraints, debugging,
   and interoperability costs.
4. Package and Unity versions are supported for all target platforms.
5. Save/load, networking, presentation bridges, and test strategy have explicit
   owners.

Do not adopt ECS/DOTS for a small number of heterogeneous objects, as a premature
optimization, or only because a subsystem contains an `Update` loop. A hybrid is
often appropriate: data-oriented simulation behind a narrow adapter with ordinary
GameObjects for presentation.

## Framework adoption gate

For any architecture framework, record evidence for all of these:

- the recurring problem and its current cost;
- a smaller alternative and why it is insufficient;
- supported Unity, C#, platform, and build-pipeline versions;
- measured runtime/build/editor impact;
- authoring, onboarding, debugging, and upgrade workflow;
- ownership of initialization, teardown, errors, and migrations;
- an exit or containment strategy;
- a representative spike or characterization test.

Do not adopt a framework when its primary benefit is aesthetic consistency, when
the problem occurs only once, or when the team cannot validate the framework on
the actual target. Revisit after measured scale or collaboration forces change.

## Architecture verification

Before calling the architecture complete, verify:

- every mutable scope has one owner and symmetric initialization/teardown;
- dependencies point toward stable policy and no accidental cycles exist;
- important rules run in fast plain C# tests;
- scenes can load, unload, and reload without duplicate services or listeners;
- authored data cannot silently become shared runtime state;
- messaging order, failure, and disposal semantics are observable;
- selected frameworks have passed the adoption gate on target constraints;
- profiler claims come from a representative target build, not architectural
  intuition.
