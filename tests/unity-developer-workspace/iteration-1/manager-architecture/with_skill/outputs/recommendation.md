# Incremental architecture recommendation

## Context and evidence

**User-stated:** this is a Unity 6 project with a 1,800-line
`DontDestroyOnLoad` `GameManager`. It owns input, audio, saving, combat, UI
navigation, and scene transitions. Other components reach it through
`GameObject.Find`; two shared `ScriptableObject` assets are mutable session
state; additive loading sometimes leaves stale UI listeners. Twelve developers
work in feature teams. There are a few PlayMode tests, almost no plain C# tests,
and assembly definitions are available. A DI container and ECS/DOTS require
evidence rather than being defaults.

**Observed:** no repository, source, scene, package manifest, Unity patch
version, test output, player build, or profiler capture was supplied. The
specific call graph and the listener failure mechanism therefore remain to be
confirmed in the project.

**Assumed for this plan:** one local play session is authoritative; audio may
persist across scene changes; authored assets should be read-only at runtime;
and the current behavior must remain releasable throughout the migration. If
the game has multiplayer authority, rollback/replay requirements, or multiple
concurrent sessions, those constraints must be added before fixing the final
domain boundaries.

## Decision

Use an incremental, feature-oriented architecture with explicit application,
session, scene, and feature lifetimes, wired by manual dependency injection in
composition roots. Keep `GameManager` as a compatibility shell while callers
are migrated one capability at a time; it must stop being an owner of new state.

This is a controlled strangler migration, not a rewrite. Do not introduce a DI
container, a global message bus, a Service Locator, or ECS/DOTS at this stage.

## Why it fits

The dominant force is mixed ownership and lifetime: process-wide audio,
per-session state, scene-local UI, and encounter-local combat currently share a
single persistent owner. `GameObject.Find` hides dependency failures, shared
mutable assets hide state ownership, and long-lived publishers can retain
scene-local UI. Those are dependency and lifecycle problems; neither a
container nor ECS solves them by itself.

Manual composition gives the team explicit dependencies and a reversible
migration seam without package adoption. Plain C# application/domain objects
make the rules fast to test. Narrow Unity adapters retain the engine concerns
that actually need `MonoBehaviour`, scenes, input, audio, and serialization.
Assembly definitions can then enforce the dependency direction already
established by the code.

The cost is more explicit startup/teardown code, temporary compatibility
adapters, and a period in which old and new modules coexist. That cost is
bounded by moving one authoritative capability at a time and deleting each
bridge as soon as its callers are migrated.

### Revisit triggers

- Consider a DI container only if several composition roots repeatedly build
  the same non-trivial scoped graph, manual wiring is causing measured release
  defects or material maintenance time, and a representative spike validates
  startup, AOT/stripping, debugging, onboarding, and removal on every target.
- Consider ECS/DOTS only if target-device profiling identifies a homogeneous
  simulation workload that misses a named CPU or memory budget and a thin
  prototype demonstrates a worthwhile gain at representative entity counts.
- Consider a feature-scoped message bus only if independently evolving
  producers and consumers cannot be expressed with direct calls or typed local
  events, and ordering, failure, disposal, and observability are specified.
- Split an assembly further only when it represents a real team/change boundary
  or materially reduces compilation coupling; assembly count is not a quality
  metric.

## Target architecture and lifetimes

```text
Persistent AppBootstrap / ApplicationRoot
  owns platform adapters and creates/disposes SessionScope
                    |
                    v
SessionScope (new game / loaded game -> return to menu)
  owns mutable SessionState and session use cases
       |                  |                    |
       v                  v                    v
SceneFlow port       Save port            feature use cases
Unity adapter        storage adapter      (combat, navigation)
       |
       v
SceneCompositionRoot (one per loaded presentation scene)
  owns scene references, views, presenters, and subscriptions
       |
       v
Views / input / audio emitters / scene objects
```

Dependencies point inward:

```text
Unity views and input adapters -> application use cases -> plain C# policy/state
Unity audio, save, and scene adapters <- narrow application ports
Composition roots are the only code that knows concrete implementations.
```

Do not replace one `GameManager` with six globally accessible managers. Each
mutable object has one owner and the narrowest lifetime that matches its data:

| Scope | Owns | Starts | Tears down | Must not own |
| --- | --- | --- | --- | --- |
| Application | bootstrap, platform logging, truly cross-session audio playback if continuity is required, session factory | application boot | application quit | combat state, scene views, current save state |
| Session | mutable `SessionState`, current profile/save model, session input context, session use cases | new/load game | return to menu or session replacement | scene objects or shared asset mutation |
| Scene | serialized scene references, UI views/presenters, scene-local audio emitters, listener registrations | scene readiness | disable/unload | persistent mutable game state |
| Encounter/actor | combat model, timers, transient effects and subscriptions | encounter/actor creation | encounter/actor end | application services by global lookup |

### Capability boundaries

- **Input:** a Unity-facing input adapter translates engine callbacks into
  explicit application commands such as `Pause`, `Navigate`, or `Attack`. The
  combat model does not reference the input package. Active maps or contexts
  belong to the session/scene that enables them and are disabled symmetrically.
- **Audio:** an `IAudioOutput`-style port is justified because engine audio is an
  external effect. A persistent audio adapter may own mixer/music continuity;
  scene emitters remain scene-owned. Gameplay asks for typed audio intents and
  does not locate an audio manager.
- **Saving:** a session use case creates a versioned, plain-data snapshot and
  passes it to a storage adapter. Authored assets and live Unity objects are not
  the save contract. Async I/O owns cancellation and errors; only thread-safe
  plain data crosses a worker boundary.
- **Combat:** rules, state transitions, time/random inputs, and results live in
  plain C#. Unity components adapt animation, physics, VFX, and sound. This is
  the largest initial source of fast unit tests.
- **UI navigation:** keep Unity widgets in passive views and put non-trivial
  navigation behavior in a presenter/controller. The scene root injects a
  narrow use case. Presenters expose explicit `Start`/`Stop` or `Dispose`
  semantics; views never find gameplay services globally.
- **Scene transitions:** one coordinator serializes transition requests through
  a scene-loading port. Load the destination, obtain exactly one destination
  composition root within that newly loaded scene, initialize it with the
  current session context, wait for an explicit ready result, and only then
  retire the prior scene. On failure, surface a typed error and clean up the
  partially loaded destination rather than leaving two active owners.

A bounded query for the destination root at the scene-composition boundary is
acceptable if the installed Unity API supports it and the result is validated.
Repeated name-based searches from arbitrary components are not.

### ScriptableObject boundary

Convert the two mutable shared assets into authored definitions, for example
`SessionDefaults`, `CombatTuning`, or catalogs. Keep serialized fields private
and expose read-only values to consumers. At session start, create a new plain
C# `SessionState` initialized from those values. Only the `SessionScope` mutates
that state, and returning to the menu discards it. Saving maps the state to and
from a versioned DTO.

If migration requires legacy code to read the asset-shaped API, provide a
temporary adapter backed by `SessionState`; do not keep the asset and the new
model as two writable sources of truth. A runtime clone is a fallback only if a
Unity API needs a `ScriptableObject` instance; its owner and destruction point
must then be explicit.

### UI listener contract

The persistent publisher outlives scene UI, so the scene scope must own every
subscription. Use named handlers or a disposable registration that can be
removed reliably. A safe presenter contract is:

```text
Initialize(dependencies) once
Start() on the enabled interval; idempotent subscription
Stop() on disable/unload; symmetric unsubscription and cancellation
Dispose() for resources owned for the whole scene scope
```

Do not use anonymous lambdas where removal requires the original delegate. A
callback that resumes after an `await` must re-check its Unity view before use.
`OnDisable` is the normal listener cleanup boundary; `OnDestroy` is a final
safety boundary, not the only cleanup path.

### Assembly direction

Introduce assembly definitions only around extracted code, not across the whole
legacy tree in one change. A practical initial graph is:

```text
Game.Session.Domain        (plain C# state and save DTOs)
Game.Combat.Domain         (plain C# rules)
Game.Application           (use cases and narrow external ports)
Game.Infrastructure.Unity  (input, audio, save, scene adapters)
Game.Presentation.Unity    (views and presenters/adapters)
Game.Bootstrap.Unity       (composition only)
*.Tests                    (plain/EditMode and PlayMode test assemblies)
```

The exact split should follow existing namespaces and team ownership. Keep the
domain/application assemblies free of Unity presentation dependencies where the
installed Unity configuration permits. Avoid a broad `Common` assembly and
cycles between feature assemblies.

During the first slices, code in an assembly definition cannot depend on legacy
types in the predefined `Assembly-CSharp` assembly. Use that constraint to the
migration's advantage: keep a temporary legacy adapter/composition entry point
on the legacy side, have it depend on the new contracts, and never let new
domain code reference `GameManager`. Move the bootstrap into its final assembly
only after legacy dependencies have been inverted or removed.

## Incremental implementation plan

Each slice is independently releasable. Add one failing behavior test, make the
minimum coherent change, run the relevant test ladder, and merge before starting
the next ownership transfer. Do not run old and new implementations as
simultaneous writers. A rollback switch may select a route, but exactly one
model remains authoritative.

### 0. Characterize and make ownership visible

1. Inventory every public `GameManager` entry point and every
   `GameObject.Find`/global access with its caller, required result, and intended
   lifetime. Group them by capability rather than by method count.
2. Capture the current additive-load reproduction and add a PlayMode
   characterization test: repeatedly load, activate, disable, unload, and reload
   the relevant UI scene; one user action must produce one navigation result,
   and an unloaded view must receive none.
3. Add coarse diagnostics at composition/transition boundaries: session ID,
   scene-scope ID, subscribe/unsubscribe counts, transition ID, and failures.
   Avoid per-frame logging.
4. Record current PlayMode results and a representative player smoke test before
   changing ownership. These are gates, not proof that current design is good.

**Exit:** the stale-listener failure is reproducible or explicitly marked
intermittent with enough diagnostics to distinguish duplicate subscription,
missed unsubscription, duplicate roots, and a late async callback.

### 1. Establish roots without moving behavior

1. Add a small persistent `ApplicationRoot` next to the current manager. Its
   only initial responsibility is to build and dispose a `SessionScope` and to
   reject/destroy a duplicate bootstrap deterministically.
2. Add one `SceneCompositionRoot` to the affected additive UI scene with
   serialized local view references. Validate missing or duplicate roots with an
   actionable initialization error.
3. Keep `GameManager` behavior intact behind a `LegacyGameRuntimeAdapter` used
   only by composition. Redirect one low-risk caller from `GameObject.Find` to a
   serialized or explicitly injected narrow dependency.
4. Repeat caller by caller. Use serialized references for stable scene/prefab
   relationships, factory return values for dynamically created actors, and
   session-context injection for cross-scene services.

**Rollback:** redirect that caller to the legacy adapter. No state has moved yet.

### 2. Fix scene/UI lifetime as the first behavior slice

1. Move the affected UI navigation binding into a plain presenter owned by the
   scene root.
2. Pair `Start`/`Stop` with `OnEnable`/`OnDisable`; make repeated `Start` safe and
   cancel any scene-owned async operation on `Stop`.
3. Put transition serialization/readiness in a narrow coordinator while the
   actual Unity scene calls remain in an adapter. Coalesce or reject duplicate
   requests according to the existing player-visible contract; do not allow two
   transitions to mutate active-scene ownership concurrently.
4. Run the repeated additive-load PlayMode scenario with Domain Reload both in
   the project's normal setting and in the configuration most likely to reveal
   surviving static handlers. Clear or eliminate mutable static events.

**Exit:** repeated load/unload produces exactly one UI reaction per action, no
unloaded view reacts, and a transition failure leaves one known active scene
scope.

### 3. Move session state out of shared assets

1. Add tests proving that two newly created sessions have independent state,
   new-session reset is deterministic, and authored default values remain
   unchanged after mutations.
2. Introduce `SessionState` and create it in `SessionScope` from the read-only
   definition assets.
3. Move one state field and all its writers in a vertical slice. Route legacy
   reads/writes through a temporary adapter to the same `SessionState`.
4. Repeat until neither asset is mutated. Then make the legacy mutating API
   unavailable and add a validation check for accidental runtime writes where
   practical.
5. Map state to a versioned save DTO; preserve a fixture for the current save
   schema before changing serialized field names or formats.

**Rollback:** restore the adapter route, not a second mutable asset copy.

### 4. Extract input and audio adapters

1. Define application commands at the behavior seam, not an interface mirroring
   every engine callback.
2. Move one input action end-to-end: Unity input callback -> use case -> observable
   result. Test the use case in plain C# and the binding lifecycle in PlayMode.
3. Move one audio intent end-to-end through a narrow output port. Keep mixer,
   clip, and source details in the Unity adapter.
4. Continue by feature, deleting the equivalent `GameManager` methods when the
   last caller has migrated.

### 5. Extract combat and UI behavior by feature

1. Start with one combat rule that currently changes often. Specify inputs,
   deterministic time/random sources if relevant, result, and failure behavior
   in a plain C# test.
2. Move the rule and encounter state into `Game.Combat.Domain`; leave physics,
   animation, VFX, and scene references in Unity adapters.
3. Bind the combat view through a scene/prefab composition root. Use direct calls
   for one known receiver and typed, feature-scoped events only for genuine
   one-to-many notifications.
4. Repeat per combat capability. Do not create an `ICombatEverything` service or
   a universal event bus.

### 6. Extract saving and complete scene flow

1. Test save DTO round-trip, schema failure, cancellation, and storage failure in
   plain C#. Keep Unity object reads out of background work.
2. Test the transition policy with a fake scene-loading port: success, destination
   readiness failure, duplicate request, cancellation, and session shutdown.
3. Add PlayMode tests for the real Unity adapter: boot -> game -> additive UI ->
   unload -> return to menu -> new game.
4. Validate a representative target player because async behavior, stripping,
   platform storage, and scene loading are not proven by EditMode tests.

### 7. Retire the shell

Remove `GameManager` only when its public-call inventory is empty, it owns no
mutable state or subscriptions, no production `GameObject.Find` reaches it, and
the application/session/scene teardown tests pass. Delete compatibility adapters
in the same capability's final migration change so they do not become permanent
architecture.

For twelve developers, assign one writer/owner per capability and publish the
dependency graph plus current migration table. Keep composition changes small
and reviewed by the owners of both scopes. Do not let a shared bootstrap file
become the new merge-conflict hub; delegate feature wiring to feature installers
that expose explicit `Start`/`Stop` contracts, while the root remains the sole
scope owner.

## Verification gates

No tests, Unity compilation, build, migration, or profiling were run for this
recommendation. The following evidence is required before calling the refactor
complete:

### Plain C# tests

- separate sessions never share mutable state and reset from definitions;
- authored defaults remain unchanged;
- combat rules cover success, invalid input, transition, time/random, and error
  cases relevant to their contracts;
- UI presenters can start, stop, and start again without duplicate behavior;
- save DTO round-trip and version/failure behavior are explicit;
- scene-transition policy handles success, duplicate requests, failure,
  cancellation, and stale completions.

### EditMode/static checks

- all new assembly definitions compile without cycles;
- domain/application assemblies do not reference Unity presentation assemblies;
- serialized composition references and definition assets validate;
- every remaining global lookup is listed as an intentional migration item;
- every mutable static has an explicit reset policy, preferably by removal.

### PlayMode tests

- exactly one application root and one session owner exist after duplicate boot
  and repeated scene changes;
- the affected additive scene can load/unload repeatedly (use a fixed count such
  as ten in CI) with one UI result per user action and no stale listener reaction;
- disable/enable and return-to-menu/new-game flows clean subscriptions, input
  bindings, coroutines/tasks, and scene references;
- a destroyed/disabled view is never used by a delayed callback;
- the shared definition assets retain their authored values across sessions;
- the real scene adapter handles readiness failure and cancellation without
  leaving duplicate active scopes.

### Player/build checks

- run the existing smoke path and the repeated transition flow in a
  representative build on each material target;
- exercise the actual storage path and scripting backend;
- compare behavior and error telemetry to the characterization baseline;
- profile only if a performance claim is made, using the same content and target
  procedure before and after.

Removing `GameObject.Find`, splitting updates, or adding assemblies may improve
maintainability, but no frame-time or memory improvement should be claimed from
code shape alone.

## Rejected alternatives

- **Rewrite the manager in one pass:** too large a behavioral and merge-conflict
  blast radius, with insufficient fast tests and poor rollback granularity.
- **Six replacement singletons/managers:** changes file size but preserves hidden
  access, global lifetime, and teardown ambiguity.
- **Service Locator or global event bus:** makes the current lookup/listener
  problem less visible and creates another global retention path.
- **DI container now:** dependency injection is useful, but explicit constructors,
  serialized references, factories, and composition roots meet the present need
  without package, AOT, debugging, and training cost.
- **ECS/DOTS now:** the evidence describes ownership and coupling defects, not a
  measured homogeneous-data performance bottleneck.
- **Keep mutable `ScriptableObject` session state:** shared asset identity does
  not express independent session ownership or deterministic reset.
- **Assembly-definitions-first reorganization:** it risks a broad compile break
  before the desired dependency direction is known.

## Risks and next checks

- The intermittent listener bug may also involve duplicate scene roots, late
  async completion, or a static publisher. Characterize it before assuming
  unsubscription is the only cause.
- Moving state can temporarily create dual writers. Maintain a field-level
  ownership table and move all writers of one field together.
- Assembly definitions can expose hidden legacy dependencies. Start with new
  extracted folders and preserve GUID-backed Unity assets and `.meta` files.
- Save changes need schema compatibility and rollback fixtures before release.
- Scene transitions need an explicit rule for duplicate requests, activation,
  failure, and cancellation based on current game behavior.
- Domain Reload settings can hide or expose surviving static handlers; verify the
  actual project configuration and repeated Play sessions.
- Confirm the exact Unity 6 patch, packages, target platforms, input/UI stack,
  scripting backend, save compatibility requirements, and any multiplayer or
  replay constraints before selecting exact APIs.

The next concrete action is Slice 0 plus the single UI-lifetime vertical slice:
capture the failing additive-load scenario, introduce the application/scene
composition roots beside the legacy manager, migrate only the affected UI
binding, and require the repeated-load PlayMode gate before extracting any other
capability.
