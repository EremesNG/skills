# Lifecycle-safe projectile pooling migration (Unity 6)

## Conclusion

Adopt a scene-owned `ProjectilePool`/`ProjectileLease` protocol: Addressables loads are acquired once per prefab key, pooled instances are activated only while leased, and every lease has an explicit generation/token. A lease is returned through one idempotent `Release` path after impact, cancellation, scene unload, or pool shutdown. Reset all mutable projectile state before requeueing, cancel and dispose all owned async/tween/event work first, and reject callbacks whose generation or pool lifetime token is no longer current. Size for the proven peak (128, not the 64 observed), use a 32-entry `OverlapSphereNonAlloc` buffer with deterministic truncation telemetry plus a configured fallback, and make teardown drain leases before releasing Addressables handles. This removes burst instantiate/destroy churn while making late callbacks and additive-scene/domain-lifetime edges safe.

## Evidence

- `InstantiateAsync` and destruction during bursts are a recurring managed-allocation source; pooling amortizes component/GameObject setup and avoids per-impact churn.
- Observing 64 concurrent projectiles is not a safe capacity contract when the believed peak is 128. Warm 128 (or a documented lower warm count with a hard cap of 128) and test 129th acquisition explicitly.
- A 32-collider non-alloc query can return a full buffer, which means the result is truncated. Never treat a full result as complete: emit a counter/sample, define stable target ordering (distance, then collider instance ID), and either run a bounded fallback query or apply an explicit gameplay policy.
- Projectile-owned subscriptions, PrimeTween trail fades, and UniTask homing loops are retained work unless they are canceled/killed and detached before reset. A per-lease `CancellationTokenSource` linked to pool/scene shutdown prevents work from surviving a return.
- Additive scene unload can race Addressables completion. Completion must verify the pool lifetime token and scene ownership before instantiating/activating; otherwise release the acquired handle and destroy/discard the result.
- Domain Reload disabled means static pools, event handlers, CTS objects, tween handles, and counters survive play-mode transitions. Provide an explicit editor/runtime reset hook and avoid static ownership of scene instances.

## Test-first migration

1. **Characterize current behavior and define seams.** Introduce interfaces for Addressables acquisition/release, projectile factory, clock/tween control, physics query, and event bus. Add allocation assertions around acquire, impact, and return (allowing one-time warm-up allocations).
2. **Write failing pool contract tests.** Cover warm-up count, maximum capacity 128, exhaustion policy (queue, reject, or controlled expansion), duplicate release idempotence, lease generation mismatch, and no activation of an object after shutdown. Make the chosen exhaustion policy visible in metrics and gameplay tests.
3. **Write failing reset/ownership tests.** Set every mutable field dirty (velocity, damage, owner/team, target, trail alpha, timers, hit set, event subscriptions), return, reacquire, and assert pristine defaults. Assert that `Release` cancels the homing CTS, kills/completes the trail fade, unsubscribes events, clears references, and leaves no callbacks able to mutate the next lease.
4. **Write failing cancellation/race tests.** Complete an Addressables operation after scene unload; cancel during homing and impact; invoke a queued tween/event callback after release; call shutdown twice. All paths must be harmless, release handles exactly once, and never activate or damage a stale lease.
5. **Write failing Addressables reference tests.** Keep one operation/handle per prefab key (or a precisely counted handle per instance), retain the prefab handle while pool owns instances, release only after all instances are destroyed and pending operations are settled, and assert balanced reference counts on normal return, exhaustion, load failure, cancellation, and teardown.
6. **Write failing physics/damage tests.** Use the reused 32-element `OverlapSphereNonAlloc` array. Verify deterministic ordering, duplicate filtering, team/owner filtering, and full-buffer behavior. Preferred policy: when `count == buffer.Length`, run one configured fallback (larger reusable buffer or bounded `OverlapSphere` allocation) and record `DamageBufferOverflow`; if fallback is unavailable, process the deterministic first 32 and expose the truncation to gameplay telemetry. Test that one target is damaged at most once per impact.
7. **Implement the smallest green slice.** Add `ProjectilePool` with `WarmAsync`, `TryAcquire`, `Release`, `ShutdownAsync`; `ProjectileLease` generation; `Projectile.ResetForPool`; and `DamageQuery` with reusable buffers/fallback. Keep Addressables and scene ownership in the pool, not in projectile callbacks.
8. **Integrate lifecycle boundaries.** The combat scene owns the pool and passes a linked scene/pool cancellation token to every lease. On unload: stop new acquisitions, cancel pool token, release all active leases, await/settle pending Addressables operations, destroy pooled instances, then release prefab handles. Register a runtime/editor play-mode reset path for Domain Reload disabled.
9. **Migrate call sites behind a feature flag.** Run pooled and legacy paths side by side in Development Player captures; compare hit results, active counts, overflow counts, Addressables refcounts, and managed/native memory. Roll back to legacy instantiation by disabling the flag if correctness or memory gates fail.
10. **Target-player verification.** On representative target hardware/player build, run sustained bursts at 128 concurrent projectiles, repeated scene load/unload, cancellation at each lifecycle phase, and full-buffer encounters. Require stable post-warm allocations, no stale damage/tween/event callbacks, balanced Addressables refs, and bounded retained/native memory after quiescence.

## Ownership protocol

- **Pool:** sole owner of prefab `AsyncOperationHandle`, pooled instances, active/free collections, reusable physics buffers, and pool lifetime CTS. It may activate/deactivate but never lets a stale lease re-enter.
- **Lease/projectile:** owns only per-lease data and disposable work (linked CTS, tween handle, event subscription tokens). `Release` uses an atomic state transition and generation check, then performs cancel → kill tween → unsubscribe → clear references/state → deactivate → return to pool.
- **Addressables:** acquire prefab/asset once per key before warm-up; instantiate through the factory with the pool token. If completion arrives after cancellation/unload, release the operation/instance immediately and do not add it to the pool. Release handles after all dependent instances and operations are gone.
- **Damage query:** pool-owned reusable arrays; no projectile stores collider-array references. Define stable sort/filter semantics before applying damage and log overflow/truncation.
- **Scene/domain:** no static reference to scene objects. `OnDestroy`/scene-unload invokes idempotent shutdown; an editor play-mode callback clears static registries and verifies zero active leases, CTS, subscriptions, tween handles, and Addressables refs.

## Verification gates and rollback

- Unit/integration: all contract, race, refcount, reset, and overflow tests green; repeated shutdown and duplicate release remain no-ops.
- Development Player: after warm-up, acquire/impact/release produces no recurring managed allocations attributable to projectile lifecycle; retained managed and native memory returns to baseline after quiescence; no Addressables handle leak.
- Gameplay: deterministic damage ordering and target-player parity against the legacy path for representative multi-target and overflow scenes.
- Rollback: feature flag switches new acquisitions to the legacy path, drains and shuts down the pool safely, and preserves telemetry. Keep the legacy factory until at least one release cycle of target-player evidence passes.

## Verification

This recommendation is design/test guidance only; no repository commands, profiling sessions, or target-player runs were performed here.

## Risks

- A fallback `OverlapSphere` allocation can reintroduce spikes; prefer a second preallocated buffer sized from telemetry and retain the allocation fallback only as a guarded emergency path.
- Warm-up of 128 instances can increase startup time and native memory. Make warm count configurable (for example 64) while keeping a tested hard cap of 128, and measure before shipping.
- Incorrect reset ordering can leak subscriptions or let a callback touch a reused lease; enforce idempotent release and generation assertions in Development builds.
- Addressables API/factory behavior differs between versions; encapsulate handle ownership and add refcount tests around the project’s exact API.

## Open questions

- Should exhaustion reject/fire a gameplay event, temporarily expand up to 128, or queue? The answer affects hit semantics and back-pressure.
- What is the acceptable overflow gameplay policy when more than 32 valid colliders are in range, and what larger reusable buffer fits the target memory budget?
- Which object/tween abstractions expose deterministic kill/await semantics in the project’s PrimeTween and UniTask versions?
- What target devices and post-quiescence memory/allocation thresholds constitute release gates?

## Next action

Approve the exhaustion and overflow policies, then add the failing pool/reset/race/refcount/physics tests behind the seam interfaces. Implement the pool as the sole lifecycle owner, run the tests, and only then enable the feature flag for target-player capture.
