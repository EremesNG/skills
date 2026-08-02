# Recommendation: make health notifications instance-scoped and lifecycle-owned

## Context and evidence

- **User-stated:** Unity 2022.3 LTS; four-player co-op; `Health` is a
  `MonoBehaviour` that currently updates HUD, audio, and save statistics; a
  static `HealthChanged` event delivers duplicate callbacks after a
  gameplay -> menu -> gameplay cycle; Domain Reload is disabled; the team has
  four programmers, EditMode and PlayMode tests, wants no third-party
  framework, and has no profiler capture for this feature.
- **Inferred, not yet observed in code:** either scene listeners subscribe more
  than once, fail to unsubscribe, or a longer-lived publisher retains old scene
  listeners. Disabling Domain Reload makes a mutable static event able to retain
  handlers between Editor play sessions as well. These are investigation
  hypotheses, not a diagnosis proven from source.
- **Unknown:** the networking package and authority model, which objects survive
  the menu transition, the exact subscription sites, whether health statistics
  are per match or persistent, and whether audio is local-player-only. Those
  details affect wiring, but not the recommendation to remove process-global
  ownership from a per-player health signal.

Before changing code, search every `HealthChanged +=`, `HealthChanged -=`, and
assignment/reset of the static event, and record the lifetime of each publisher
and subscriber. That establishes the regression cause and prevents leaving a
second notification path active during migration.

## Decision

Replace the static event with a typed **instance event on each authoritative
`Health` instance**, remove HUD/audio/statistics calls from `Health`, and wire
three feature-scoped adapters to the correct player at the player or gameplay
composition root; every binding must have idempotent, symmetric start/stop
behavior.

This is a local Observer boundary plus explicit composition, not a project-wide
event system. It is the smallest design that decouples the responsibilities and
gives the notification the same lifetime as the player whose health changed.

## Why it fits

The dominant problem is mismatched ownership: a process-global publisher is
being used for per-player, scene/session-scoped state. An instance event makes
the source explicit, avoids cross-player filtering through global state, and
allows the gameplay graph to disappear on scene unload. Explicit bindings make
subscribe/unsubscribe behavior searchable and testable. No package, container,
service locator, or general message bus is needed.

The event should describe a committed state transition with an immutable plain
C# payload, for example:

```csharp
public readonly struct HealthChange
{
    public HealthChange(PlayerId playerId, int previous, int current,
        int maximum, DamageCause cause)
    {
        PlayerId = playerId;
        Previous = previous;
        Current = current;
        Maximum = maximum;
        Cause = cause;
    }

    public PlayerId PlayerId { get; }
    public int Previous { get; }
    public int Current { get; }
    public int Maximum { get; }
    public DamageCause Cause { get; }
}
```

Adapt the syntax and identifiers to the project's C# version and existing ID
types. Do not put scene-object references in the payload. `Health` commits and
clamps its new value first, then emits exactly one event for a real transition;
it does not know about UI, audio, persistence, or the menu scene.

```csharp
public sealed class Health : MonoBehaviour
{
    public event Action<HealthChange> Changed = delegate { };

    // ApplyDamage/Heal owns the invariant, commits state, then raises Changed once.
}
```

The empty-delegate initializer is optional if it conflicts with project style;
it does not replace lifetime cleanup. Avoid anonymous subscriptions that cannot
later be removed.

## Architecture and lifetimes

| Boundary | Owner and scope | Responsibility | Teardown |
| --- | --- | --- | --- |
| `Health` | One spawned player/actor | Own current/max health and publish an instance `Changed` signal after a transition | Actor despawn or gameplay-scene teardown |
| `HealthHudPresenter` | Local HUD/view scope | Render only the player(s) assigned to that HUD | Unbind in `OnDisable`/`Stop` |
| `HealthAudioResponder` | Player presentation scope | Translate an assigned health change into local audio behavior | Unbind in `OnDisable`/`Stop`; stop owned audio work if required |
| `HealthStatisticsRecorder` | Match/session scope | Aggregate authoritative statistics in memory; ask the existing persistence boundary to flush at its defined checkpoint | Unregister actor sources on despawn; reset or flush when the session ends |
| Player/gameplay composition root | Player prefab or gameplay scene | Supply concrete `Health` references and start bindings after actors/services are ready | Stop bindings before destroying scene objects |

Use the project's existing composition style. With serialized references, a
small adapter can follow this lifecycle shape:

```csharp
public sealed class HealthHudPresenter : MonoBehaviour
{
    [SerializeField] private Health source = default!;
    [SerializeField] private HealthHud view = default!;
    private bool subscribed;

    private void OnEnable()
    {
        if (subscribed)
            return;

        source.Changed += HandleChanged;
        subscribed = true;
        view.Render(source.Current, source.Maximum);
    }

    private void OnDisable()
    {
        if (!subscribed)
            return;

        if (source) // Unity-aware validity check
            source.Changed -= HandleChanged;

        subscribed = false;
    }

    private void HandleChanged(HealthChange change) =>
        view.Render(change.Current, change.Maximum);
}
```

If objects are spawned dynamically, put the same idempotent logic in explicit
`Bind(Health)`/`Unbind()` methods and have the composition root call them. Reject
or safely replace a second bind; never silently stack it. Keep the source
reference explicit rather than finding it by name or resolving it globally.

For the four-player topology:

- each player's presentation binds to that player's `Health` instance;
- the local HUD binds only to the locally relevant player(s), according to the
  existing split-screen/client design;
- the statistics recorder registers each authoritative player source once and
  unregisters it on despawn;
- only the network authority records authoritative health statistics. Clients
  may render replicated state, but a replicated presentation callback must not
  write the same statistic again. Confirm the exact authority API in the
  installed networking package before implementation.

Define event delivery as synchronous and state-after-commit. A listener should
not mutate `Health` recursively. Persistence must not perform blocking disk I/O
inside the event; aggregate through the existing save boundary and surface its
failures through that subsystem. If listener ordering is behaviorally important,
do not rely on multicast-event order—make the ordering explicit in one
feature-scoped coordinator and test it.

### Scene reload and Domain Reload behavior

On leaving gameplay, the scene/player owner calls `Stop` or disables subscribers
before their sources are destroyed. The statistics session owner unregisters all
actor sources, then deliberately flushes/resets according to the match contract.
Loading gameplay again creates a fresh player graph and one binding per
source/consumer pair. No scene object is retained by a static delegate.

Do not keep the static event and merely clear it in `OnDestroy`; destruction
order and persistent publishers make that unreliable. After this refactor, the
health notification itself has no mutable static state and therefore does not
depend on Domain Reload for correctness. Audit any remaining mutable statics in
the feature. If an unavoidable static cache exists, give it an explicit reset
using the Unity-2022.3-appropriate runtime initialization hook and test that
policy, but treat that as a separate owned mechanism—not the event fix.

## Bounded implementation plan

Implement in vertical slices and keep the old path only long enough to migrate
one reaction at a time:

1. Characterize the duplicate with a PlayMode test that performs the current
   gameplay -> menu -> gameplay sequence. Confirm that it fails for the expected
   extra callback before editing production code.
2. Introduce `HealthChange` and the instance `Health.Changed` contract. Add an
   EditMode/plain-C# test for one notification per committed transition, correct
   old/new/player data, clamping, and no notification for a no-op.
3. Move HUD response to a bound presenter. Add lifecycle tests, then remove the
   direct HUD call and any HUD static subscription.
4. Repeat independently for audio, then for the authoritative statistics
   recorder. Remove the old static event only when search confirms no remaining
   publisher or subscriber.
5. Add the scene-reload regression and a four-player isolation case. Keep each
   slice releasable so rollback is simply restoring the previous reaction path,
   not reverting a framework migration.

The concrete file names should follow the repository's assemblies and naming
conventions. Keep health rules in their existing class for this fix unless those
rules are already difficult to test; extracting a plain C# `HealthModel` is a
separate refactor justified by rule complexity or reuse, not required to solve
the duplicate listener bug.

## Verification

Run these checks in the affected test assemblies:

- **EditMode/plain C#:** damage/heal emits exactly once after state commit;
  payload values and player identity are correct; a no-op emits zero times;
  `Start`/`Bind` called twice still yields one callback; `Stop`/`Unbind` called
  twice is harmless; after stop, changes yield no reaction.
- **PlayMode:** enable -> disable -> enable yields one callback; destroy/despawn
  leaves no callback; gameplay -> menu -> gameplay produces exactly one HUD,
  one intended audio, and one authoritative statistics reaction per health
  transition; four simultaneous players do not cross-update HUDs; repeat the
  flow with the project's Domain Reload-disabled Editor setting.
- **Networking integration:** on the installed stack, apply one authoritative
  damage transition and verify the server/host records it once while each client
  performs only its intended presentation reaction. This is needed before
  claiming the co-op path correct.
- **Static inspection:** repository search finds no remaining static
  `HealthChanged`, no anonymous unremovable handlers, and no direct dependencies
  from `Health` to HUD, audio, or persistence.

No project files or Unity Editor were supplied for this recommendation, so none
of these tests, compilation checks, scene flows, builds, or networking checks
were run. There is also no profiler evidence. This refactor makes a correctness
and ownership claim, not a performance claim, so profiling is not a gate for the
bug fix. If runtime cost later becomes a concern, capture a reproducible target-
build baseline before introducing pooling, an update manager, ECS, or another
optimization.

## Rejected alternatives

- **Keep the static event and add more `-=` calls or a static reset hook:** useful
  as an emergency containment step, but it preserves the wrong process-wide
  lifetime and cross-player topology. A reset can hide Editor carry-over without
  fixing scene/session ownership.
- **ScriptableObject event channel or global message bus:** both still require
  exact listener lifecycle, ordering, and ownership rules. There is no stated
  designer-authored cross-prefab messaging need that pays for the extra
  indirection.
- **Singleton or Service Locator:** hides the player/session dependency and makes
  scene teardown and tests harder.
- **DI container or third-party architecture framework:** explicitly unwanted
  and unnecessary for one local object graph. Manual/serialized composition is
  sufficient.
- **Have `Health` directly call HUD, audio, and save services:** removes delegate
  retention but keeps the mixed responsibilities and makes local/remote-player
  behavior difficult to isolate.
- **ECS/DOTS or a broad reactive framework:** this is a lifetime/coupling defect,
  not a measured entity-scale or performance problem.

## Risks, next checks, and revisit trigger

The main residual risk is migrating only one notification path and temporarily
delivering both direct and event-driven reactions. Use repository search plus the
scene regression to prevent that. Other risks are ambiguous network authority,
subscriber exceptions interrupting multicast delivery, and session statistics
being reset or flushed at the wrong transition; resolve those contracts in the
relevant adapters, not in `Health`.

Revisit this design when one of these measurable conditions appears: many
unrelated systems must consume health changes across independently loaded
modules; event ordering/history/replay becomes an explicit requirement; dynamic
player scopes make manual composition repeatedly error-prone; UI presentation
logic becomes complex enough to warrant a fuller MVP boundary; or target-build
profiling shows this notification path violates a named budget. Until then, one
typed instance event with explicit bindings is the professional stopping point.
