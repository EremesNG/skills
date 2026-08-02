# Recommended refactor

Use an **instance-scoped `Health.Changed` event plus three small adapters**, and remove the static `HealthChanged` event. This is the smallest change that fixes the lifetime bug and separates responsibilities without introducing a framework.

The duplicate callbacks are consistent with a static delegate retaining subscribers across scene or Play Mode lifetimes. With Domain Reload disabled, Unity does not reset static fields automatically when entering Play Mode, so a missed unsubscribe—or an unsubscribe that does not match an anonymous lambda—can accumulate listeners.

## Ownership and lifetime

| Component | Owns | Lifetime |
|---|---|---|
| `Health` on each player | Current/max health and valid state transitions | That player object |
| HUD presenter | Rendering the local player's current health | Gameplay UI/scene |
| Health audio responder | Turning a health transition into local audio feedback | Player or gameplay scene |
| Statistics adapter | Translating authoritative health transitions into calls to the existing statistics/save boundary | Session service or gameplay scene, depending on the existing save design |
| Gameplay composition code | Binding a spawned player to its presenters/adapters | Gameplay scene or spawn lifetime |

`Health` should not know about the HUD, `AudioSource`, save files, or global services. It should publish a value describing a completed state change. Consumers should not be able to mutate health through the event.

For the co-op authority boundary, only the existing authoritative gameplay path should change health. The event should be raised once from the method that commits the authoritative or replicated value. UI and audio may react on clients; persistent statistics should be recorded only on the authority that already owns save progression, otherwise the same networked change can be counted on several peers.

## Minimal shape

```csharp
public readonly struct HealthChange
{
    public HealthChange(int previous, int current)
    {
        Previous = previous;
        Current = current;
    }

    public int Previous { get; }
    public int Current { get; }
    public int Delta => Current - Previous;
}

public sealed class Health : MonoBehaviour
{
    [SerializeField] private int maxHealth = 100;
    private int currentHealth;

    public int Current => currentHealth;
    public event Action<HealthChange> Changed;

    public bool SetCurrent(int requestedValue)
    {
        int next = Mathf.Clamp(requestedValue, 0, maxHealth);
        if (next == currentHealth)
            return false;

        int previous = currentHealth;
        currentHealth = next;
        Changed?.Invoke(new HealthChange(previous, next));
        return true;
    }
}
```

Damage, healing, initialization, and network replication should converge on one state-commit method so a transition cannot publish twice. If initialization should not produce gameplay feedback, make that explicit rather than relying on listener timing.

Each Unity listener subscribes and unsubscribes symmetrically:

```csharp
public sealed class HealthHudPresenter : MonoBehaviour
{
    [SerializeField] private Health health;
    [SerializeField] private HealthView view;

    private void OnEnable()
    {
        health.Changed -= OnHealthChanged; // idempotent guard
        health.Changed += OnHealthChanged;
        view.SetHealth(health.Current);
    }

    private void OnDisable()
    {
        if (health != null)
            health.Changed -= OnHealthChanged;
    }

    private void OnHealthChanged(HealthChange change)
        => view.SetHealth(change.Current);
}
```

Use named methods, not inline lambdas, unless the delegate instance is stored so it can be removed. The defensive `-=` before `+=` prevents accidental double attachment, but it is not a substitute for the `OnDisable` cleanup.

For dynamically spawned players, do not search the scene from each adapter. Let the existing spawn/gameplay composition point call an explicit `Bind(Health)` method. `Bind` should first unbind the previous player; `OnDisable`, player despawn, and scene teardown should also unbind. A persistent statistics adapter must never retain the old scene's `Health` after returning to the menu.

## Scene reload behavior

On gameplay load, the composition point binds the local player's `Health` to its HUD and audio responders and binds authoritative players to the statistics adapter. On unload or despawn, those bindings are removed before scene objects disappear. The next gameplay scene receives new `Health` instances and fresh bindings.

Because the recommended event belongs to the player instance, Domain Reload no longer controls this event's lifetime. Remove the old static delegate entirely. If another unrelated static event must remain, give it an explicit reset method marked with `RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.SubsystemRegistration)` and still require subscribers to unsubscribe; do not use that as the primary fix here.

## Tests to add first

Start with a regression test that reproduces the current enable/load/disable/reload sequence, then make the refactor pass it.

EditMode tests for `Health`:

- A real value transition publishes exactly one event with the correct previous/current values.
- A clamped request that leaves the value unchanged publishes no event.
- Damage, healing, and replicated updates all use the same commit path.
- Health state changes correctly even with no listeners.
- If death is represented separately, crossing zero emits that transition exactly once.

EditMode tests for non-Unity adapter logic, where practical:

- A presenter maps a change to one view update.
- The statistics adapter records only authoritative changes and includes the correct player identity.
- Fakes for the view, audio, and statistics boundaries prove that `Health` has no dependency on their implementations.

PlayMode tests:

- Enable, disable, and re-enable each listener; one health change produces one callback.
- Load gameplay, return to the menu, load gameplay again, and assert that the new player produces one HUD/audio/statistics reaction while the destroyed player produces none.
- Despawn and respawn a player and verify that a persistent adapter unbinds the old instance before binding the new one.
- If the project supports host/client integration tests, verify that one replicated health transition is not counted once per peer.

Also perform the editor reproduction manually with Domain Reload disabled by entering and exiting Play Mode twice. A normal PlayMode test can cover object and scene lifetimes, but it does not by itself prove behavior across separate Editor Play Mode sessions. These are proposed checks; no tests or profiling have been run here.

## Implementation boundaries

Keep the change narrow:

1. Add `HealthChange` and the instance event to `Health`; funnel mutations through one method.
2. Extract HUD, audio, and statistics calls into listeners using the project's existing interfaces/components.
3. Bind those listeners from the existing spawn or scene-composition location.
4. Delete the static event and all of its subscriptions.
5. Add the regression and unit tests before broad cleanup.

No profiler capture is needed to justify this correctness refactor, and no performance improvement should be claimed. The event frequency is likely small, but profile on target hardware if health later becomes a high-volume signal or the adapters begin doing expensive work.

## Rejected alternatives

- **A global event bus or ScriptableObject event channel:** still introduces global-style lifetime and routing concerns for a relationship that can be expressed with an explicit player reference.
- **A singleton/service locator:** hides ownership and makes scene teardown harder to reason about; it does not solve subscription hygiene.
- **A dependency-injection or reactive framework:** disproportionate for four programmers, explicitly unwanted, and unnecessary for this refactor.
- **Keeping the static event and only clearing it on scene load:** masks missed ownership rules, may disconnect legitimate persistent listeners, and remains fragile with Domain Reload disabled.
- **Polling health from HUD/audio/statistics:** avoids subscriptions but adds unnecessary update work and obscures exact transitions.
- **A full MVP/MVVM rewrite:** broader than the failing behavior requires. A small presenter is sufficient.

## Revisit the design when

Reconsider a broader messaging or architecture layer only if evidence shows one of these conditions:

- Many unrelated systems across multiple loaded scenes must consume the same health-domain events.
- Replay, rollback, deterministic simulation, or save reconstruction requires health changes to become durable commands/domain events.
- Network prediction and reconciliation need explicit predicted, confirmed, and corrected transitions.
- Dynamic binding code is repeated across many entity types and a shared composition mechanism would remove demonstrated duplication.
- Profiling on target hardware shows event processing or listener work is material.
- Ownership can no longer be stated as one publisher instance with clearly bounded subscribers.

Until then, instance events, explicit binding, symmetric cleanup, and focused tests provide the smallest professional solution.
