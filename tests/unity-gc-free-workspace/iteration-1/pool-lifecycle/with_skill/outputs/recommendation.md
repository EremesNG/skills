# Lifecycle-safe projectile pooling migration

## Conclusion

Adopt a **scene-owned, fixed-capacity projectile pool backed by successfully completed Addressables instance acquisitions**, with an application-lifetime factory retaining ownership of every operation until it settles. Use `UnityEngine.Pool.ObjectPool<Projectile>` only as the synchronous lease manager for already-created instances; its `createFunc` must never start `InstantiateAsync` in gameplay. Make every lease carry a pool epoch and per-instance generation so a return, tween callback, homing continuation, impact callback, or Addressables completion can affect only the lease that created it.

Use `128` as a **provisional prewarm and hard pooled-instance count**, not as a proven production peak. It is twice the user-stated observed high-water mark of `64`, but the believed peak of `128` has not been demonstrated. A pool miss must never silently call `ObjectPool.Get()` and grow: during rollout it follows the separately measured legacy `InstantiateAsync` overflow lane to preserve shots, and any miss fails the warmed steady-state acceptance gate. Do not drop a shot or recycle the oldest projectile unless that gameplay change is separately specified and approved.

Replace the saturated `Collider[32]` with a scene-owned, non-reentrant damage-query workspace using prepared `64`, `128`, and `256` tiers. A result equal to a tier's length is treated as potentially truncated and retried. If the `256` tier is also full, use the allocating complete-query path as a correctness fallback, emit saturation telemetry, and account for it outside the normal zero-allocation window. Apply damage in an explicitly tested canonical order; never rely on physics-query return order.

This is a migration decision and acceptance protocol, not a claim that the workload is already GC-free. The normal path earns that label only after the functional gates and the identical warmed target-player allocation comparison below pass.

## Context and evidence classification

- **User-stated:** the project is a Unity 6 co-op game; projectile prefabs are created with Addressables `InstantiateAsync` and destroyed after impact; a Development Player capture shows recurring managed allocation during bursts.
- **User-stated:** peak concurrency is believed to be `128`, while only `64` concurrent projectiles were observed.
- **User-stated:** the current damage buffer is `Collider[32]` and sometimes returns `32`. That is evidence of saturation, not evidence that exactly 32 colliders existed.
- **User-stated:** each projectile owns event subscriptions, a PrimeTween trail fade, and a UniTask homing loop tied to scene lifetime; combat scenes are additive and can unload while Addressables work is pending; Editor Domain Reload is disabled.
- **Unknown:** the allocation call stacks, byte and allocation counts, relevant threads, burst duration, target platform/device, scripting backend, Unity 6 patch, Addressables/UniTask/PrimeTween versions, PrimeTween capacity, physics layer/query options, networking authority model, and current spawn/damage ordering semantics.
- **Inferred, pending a call-stack capture:** `InstantiateAsync`/destroy churn, tween or UniTask setup, event subscription mutation, pool growth, and full-buffer fallback are plausible allocation boundaries. None should be called the cause until the named profiler samples identify it.

The exact Unity/package manifests, installed API contracts, and PrimeTween artifact/license must be recorded before code changes. No new dependency is needed for this design.

## Allocation contract

Lock the following contract in the repository before implementing. Replace provisional counts only with a recorded, stricter representative workload.

| Field | Contract |
| --- | --- |
| Workload | `ProjectileBurstSteadyState`: replay the captured co-op burst schedule and collider layout, plus a capacity boundary case with 128 simultaneous leases, for at least 100 complete rent-impact-return cycles. The marker begins immediately before shot-to-instance admission and ends after all corresponding returns and damage dispatch. Use the same deterministic seed, network topology, physics settings, and target state in both runs. |
| Environment | Exact Unity 6 patch, Addressables/UniTask/PrimeTween versions and provenance, scripting backend, target platform/device, player type, optimization/stripping, frame cap, quality/physics settings, and thread list. A Development Player supplies diagnostic call stacks; the representative Release Player confirms production behavior. |
| Warm-up | Complete all 128 Addressables instances, seed all 128 pool records, prepare damage arrays and sort/dedup scratch, configure PrimeTween capacity for the maximum concurrent trail work plus measured margin, initialize UniTask/PlayerLoop paths, cache delegates, and exercise generic/static first use before the sample. No Addressables operation or pool creation may remain pending when the normal window opens. |
| Capacity state | Exactly 128 pooled instance records; no runtime pool growth. Damage tiers are provisionally 64/128/256 and all are allocated before measurement. Record active/inactive counts, pool high-water, misses, each damage-tier saturation count, and top-tier fallback count. |
| Normal managed budget | Default: `0 B` and `0 managed allocation events` inside the named warmed marker across all relevant threads. Pool miss/legacy overflow, top-tier physics fallback, exceptions, first use, scene transitions, and teardown are separate named paths with separately reported budgets; they cannot be hidden inside the normal result. |
| Preserved behavior | Shot admission and activation phase, host/client authority, projectile count and identity, trajectory, collision and impact timing, damage values, duplicate-collider policy, target ordering, event order, tween appearance, cancellation/error behavior, and Addressables lifetime. Any intentional change must be stated in a behavior test before implementation. |
| Other budgets | Record CPU/frame time, pool/asset retained bytes, Addressables live-instance count, native physics memory, and collection-pause behavior separately. Set numeric retained/native/CPU limits from the baseline before rollout; zero managed allocation is not permission for unbounded retention. |

Also define two transition workloads:

1. `ProjectilePoolExhaustion`: request lease 129 while 128 remain active. The shot follows the legacy overflow lane, is never returned to the pool, and is released by its own Addressables origin. This path must be correct even though it may allocate.
2. `CombatSceneChurn`: repeatedly unload an additive combat scene with inactive leases, active leases, and controlled pending successes/failures. At the end of each cycle there are no scene callbacks, live projectile records, or unmatched Addressables ownership entries for that epoch.

## Selected design

### Two-level ownership

Use two owners with different lifetimes:

1. **Application-lifetime `AddressableProjectileFactory`.** It owns every in-flight Addressables operation from the moment it is started until success or failure is fully settled. It has no dependency on an additive scene object. A completion attempts to transfer a successful instance to the requesting scene owner only if that owner ID, session ID, pool epoch, and request are still accepting it. Otherwise the factory releases the successful instance immediately through the matching Addressables release route. Cancellation of a waiter never abandons the underlying operation.
2. **Combat-scene `ProjectilePoolOwner`.** It owns the fixed pool, all transferred active/inactive instance records, the scene cancellation token, damage-query workspace, telemetry, and the drain state. It stops admission before scene unload and releases every accepted instance before its final owner handle, if a separate load/acquire handle actually exists.

This separation prevents a late `InstantiateAsync` callback from dereferencing a destroyed scene object or leaking an instance simply because the scene's cancellation token fired.

### Owner and record state machines

The scene owner has a monotonic state:

```text
Constructing -> Warming -> Ready -> Draining -> Disposed
                          \-> Faulted -> Draining -> Disposed
```

Each successful instance has one record:

```text
PendingTransfer -> Inactive -> Leased -> Returning -> Inactive
                                \--------------------> Releasing -> Released
Inactive -------------------------------------------------------> Releasing
```

Only the Unity main thread mutates the pool or Unity objects. Network or worker-thread requests are marshalled into the existing main-thread command phase. State transitions are checked; invalid transitions create telemetry in production and fail tests in development.

The externally visible value is a lease, not a raw reusable component:

```text
ProjectileLease = { poolId, ownerEpoch, instanceId, leaseGeneration, component }
```

Every impact, event, tween completion, homing continuation, and return includes the immutable `ownerEpoch + instanceId + leaseGeneration`. `TryReturn` succeeds exactly once only while the matching record is `Leased`. A stale or duplicate callback is ignored and reported; it must never call `ObjectPool.Release` a second time or act on a later renter.

### Addressables reference-count protocol

- Hide the version-specific API behind a small adapter that records how each instance was acquired and how it must be released. Match the installed `InstantiateAsync` form, handle-tracking option, and corresponding `ReleaseInstance`/handle API exactly. Do not pair a successful instance acquisition with `Object.Destroy`, and do not release both an instance and its handle unless the installed API explicitly requires both ownerships.
- Register the operation with the application factory **before** attaching/awaiting completion. Addressables cancellation may cancel a wait without canceling the operation, so every operation remains in the factory registry until it settles.
- On successful warm-up completion, the factory transfers one ownership record to the live scene owner. Pool release after impact merely deactivates the object; it does **not** decrement the Addressables reference count. The Addressables instance reference remains held while the object is active or inactive.
- `actionOnDestroy` is the only normal pooled-instance path that invokes the adapter's exactly-once Addressables release. It must be idempotently guarded by the record state. `ObjectPool.Clear()` covers inactive objects only, so teardown must first quiesce/force-return active records and then clear the inactive pool.
- A legacy overflow instance has origin `OverflowTransient`. It is never inserted into or returned to the fixed pool. Its impact, cancellation, or stale completion routes to the adapter's exactly-once release.
- If warm-up is canceled or any required creation fails, stop transfer, settle all started operations, release every success, and fault the pool atomically. Do not expose a partially warmed pool as `Ready` unless a smaller capacity is an explicitly tested product policy.
- If there is a separate long-lived asset/load handle in the installed design, keep it until all dependent active, inactive, overflow, and late-completion instances are released; release that handle last. Do not add such a handle merely by assumption.
- Maintain the invariant per prefab key: `successful instance acquisitions - successful matching instance releases == live active + live inactive + successful instances still owned by the factory`. Pending operations are tracked separately. Both sides must be zero after final drain. Separate load/acquire handles need their own equation.

### Warming an asynchronous source into `ObjectPool<T>`

`ObjectPool<T>.createFunc` is synchronous and is not a safe place to call `InstantiateAsync`. Warm-up therefore proceeds as follows:

1. Start up to 128 factory requests with a bounded setup-time concurrency chosen for loading/CPU pressure. Keep every request record even if the scene begins draining.
2. Await/settle all requests outside gameplay. Successful, validated components are disabled, reset, parented under the pool root, and placed in a setup-only reservoir.
3. Construct `ObjectPool<Projectile>` with `defaultCapacity = 128`, `maxSize = 128`, collection checks enabled in development, and a `createFunc` that synchronously removes exactly one record from the reservoir. It must fail closed if unexpectedly called after priming; it never instantiates.
4. Call `Get` 128 times into a setup-only fixed scratch array before releasing any of them, then `Release` all 128. This causes the pool to account for all created records without repeatedly reusing the first inactive item. Discard the setup scratch before the measured window.
5. Enter `Ready` only when the reservoir is empty, the pool reports 128 inactive records, the owner registry reports 128 live pooled instances, and no warm-up operation is pending.

`ObjectPool.maxSize` must not be mistaken for a hard concurrent-creation limit. The wrapper enforces the hard total of 128 by checking `CountInactive > 0` before `Get`; an empty pool takes the explicit overflow route and never lets `Get` invoke `createFunc`.

### Capacity and exhaustion

- **Initial cap:** prewarm and retain 128. This is a provisional engineering bound based on the user-stated belief, not a percentile estimate.
- **Normal admission:** `TryRent` may call `Get` only if the owner is `Ready` and an inactive record exists. Activation remains on the Unity main thread.
- **Miss behavior during migration:** route the shot through the unchanged `InstantiateAsync` seam, tag it `OverflowTransient`, and preserve the old completion/activation timing. Emit request ID, active/high-water count, pending overflow count, and owner epoch. Do not charge ammo, replicate a shot, or emit gameplay callbacks twice when switching lanes.
- **Acceptance:** any pool miss in `ProjectileBurstSteadyState` fails the capacity gate even if the overflow shot behaves correctly. First investigate the representative high-water distribution; increase the fixed cap only within an approved retained-memory budget.
- **Not selected:** silent growth creates allocation/load spikes; reusing the oldest lease causes use-after-return; dropping a projectile changes gameplay; blocking the main thread on Addressables is unsafe. Those choices require a separate behavior contract.
- **Rollout alert:** initially surface every miss and every late completion. After soak data exists, set a rate alert from the accepted service-level target rather than inventing a permissive threshold.

### Dirty reset and lease ordering

All reset operations are main-thread-only. Fields are split between setup-stable state, lease state, and scene state so the reset is reviewable.

On **rent**, in this order:

1. Validate owner state and record state, increment `leaseGeneration`, and bind the immutable lease stamp.
2. Assign shooter/network authority, team, damage parameters, target, collision mask, callbacks, and impact policy. Clear prior hit/dedup state and exception state.
3. Reset transform/parent, Rigidbody position/rotation/linear and angular velocity, sleeping/interpolation state as applicable, collider enabled/trigger state, collision-ignore pairs, layer, TrailRenderer points/width/color, particles/audio, animator, renderer/material-property state, timers, and lifetime counters.
4. Install only lease-specific references or callback fields; do not allocate a new captured delegate. Stable handler delegates are cached during setup.
5. Activate only after required state is valid because `SetActive(true)`/`OnEnable` can synchronously invoke code. Start the trail fade and homing work with the new lease stamp, preserving the characterized PlayerLoop phase and first-step timing.

On **impact/return**, in this order:

1. Atomically transition the matching record `Leased -> Returning` and invalidate the current generation before invoking user code. Disable further collider/impact admission.
2. Stop/cancel the current PrimeTween operation using the installed API, clear the non-reusable handle, and restore the trail/renderer/material state. A late completion callback checks the old lease stamp and becomes a no-op.
3. Cause the homing loop to exit through its generation guard, detach lease-specific subscriptions, and clear target, shooter, damage, owner, callbacks, delegates, collections, and retained object graphs.
4. Stop particles/audio/animation, restore physics and collision-ignore state, clear trails, reparent under the inactive root, and deactivate. Lock `OnDisable` ordering with tests.
5. Transition `Returning -> Inactive` and call `ObjectPool.Release` once. If the owner is already draining or the record is overflow-origin, transition to `Releasing` instead and invoke the matching Addressables release.

On an exception anywhere after rent, the same guarded return path owns cleanup. Never add a second `finally` that can release the same instance without the generation/state check.

### Events, UniTask, and PrimeTween

**Events**

- Subscribe stable projectile handlers to a scene-owned router once during warm-up and unsubscribe once during teardown. Handlers gate on record state/generation. This deliberately retains the pooled projectile while its owner is alive and avoids C# event invocation-list churn on every rent.
- Represent lease-specific callbacks as predeclared fields or router slots keyed by instance/generation, clear them on return, and cache non-capturing delegates. If an external publisher truly requires per-lease subscribe/unsubscribe, keep that path in the measured workload; if it allocates, replace it only after a behavior test proves an equivalent direct/router dispatch.
- Dispatch damage/gameplay events only after the shared damage workspace has been released, preventing nested callbacks from reusing it.

**UniTask homing**

- Create one scene-lifetime cancellation source outside the measured window. Do not create a linked `CancellationTokenSource` on every lease merely to stop pooled work.
- Pass `ownerEpoch + leaseGeneration` into the homing state machine. Check scene cancellation and the lease stamp immediately after every await and immediately before every Unity-object mutation. Returning the projectile invalidates the generation, so a suspended prior loop cannot steer a later lease.
- Avoid cancellation exceptions on the normal return path; return normally when the stamp is stale. Scene unload is a separately measured transition path. Dispose any version-specific registrations exactly once.
- Lock the first synchronous step, first suspension, `PlayerLoopTiming`, same-frame completion, time scale, main-thread affinity, exception observation, and cancellation/completion race. Verify UniTask PlayerLoop injection for the installed version and any system that replaces the PlayerLoop. Guard thread-pool APIs on platforms without general worker threads.
- If starting the per-lease UniTask still allocates in the named call stack after warm-up, replace only that loop with an explicit projectile update state machine. Do not assume a struct awaitable removes captures, registrations, adapters, or exception allocations.

**PrimeTween trail fade**

- Record the exact installed PrimeTween version/provenance/license and configure tween/sequence capacity before sampling. Size it from maximum concurrent fades and any other shared PrimeTween users, not projectile count alone.
- Treat every tween handle as single-use. Cancel/stop the current handle on return and teardown, clear it, and create a new operation for the new lease. Never replay or retain a completed handle.
- Use an installed stateful callback overload where available or a cached non-capturing callback plus lease stamp. Preserve ease, duration, delay, scaled/unscaled time, update phase, overwrite/concurrent-target behavior, completion order, and visual reset.

## Damage-query buffer protocol

The `DamageQueryWorkspace` belongs to the combat-scene owner, is used on the Unity main thread, and is non-reentrant. The provisional arrays and candidate scratch are allocated during warm-up. Collider density, not projectile concurrency, ultimately determines their sizes.

1. Query the prepared `Collider[64]` with the exact layer mask, trigger interaction, center, and radius.
2. If `count < 64`, process only `[0, count)` and do not inspect stale slots. If `count == 64`, record tier saturation and retry the same query into `Collider[128]`.
3. Repeat at 128 and 256. Equality with capacity always means **possibly truncated**, including the case where the true answer happens to equal capacity.
4. If the 256 tier is full, record a top-tier saturation and use the installed allocating complete overlap API for that impact. This fallback preserves correctness but is not inside the normal zero-allocation budget. Never process the incomplete 256 as if it were complete.
5. Resolve colliders into the existing damage semantics. If damage is once per gameplay entity, deduplicate by a stable authoritative entity/network ID using pre-sized scratch. If each collider currently receives damage, preserve that instead. This choice requires a characterization test.
6. Sort candidates by the explicitly chosen stable gameplay key, with a documented tie-breaker, using prepared scratch and a cached comparer/direct in-place sort. Do not use raw physics return order or `GetInstanceID()` for cross-peer authority. The host/authority applies damage and replicates results in this canonical order.
7. Clear the logical collider ranges and all candidate reference slots before returning the workspace so pooled arrays do not retain destroyed scene objects or large graphs.
8. Release the workspace before invoking user callbacks or damage events. A development guard fails on nested acquisition; production code must batch/serialize impacts through the existing main-thread combat phase rather than allocate a second hidden workspace.

Tests must permute physics return order and prove the same canonical outcome. If current observable behavior intentionally depends on query order, record that conflict and do not change it under an allocation-only migration.

## Scene, application, and Domain-Reload-disabled teardown

All lifecycle exits converge on one idempotent `DrainAsync(reason, epoch)` protocol:

1. Transition `Ready/Warming -> Draining`, increment/invalidate the owner epoch, reject new rents, and remove the owner from shot routing before unloading gameplay objects.
2. Cancel the scene-lifetime token and stable event routing. Invalidating the epoch happens first so callbacks already queued for the main thread cannot mutate a new lease.
3. Mark outstanding factory requests non-transferable. Do not forget or prematurely release their handles. The application factory will settle them; every late success is immediately released without activation, subscription, tween, homing, parenting under the dead scene, or callback into it.
4. Quiesce active pooled leases through the guarded return path. Cancel tweens, invalidate homing work, unsubscribe/clear references, and disable physics before scene objects disappear. Release active overflow instances through their own origin.
5. Clear the inactive `ObjectPool`, causing exactly one Addressables instance release per record. Verify active + inactive + transferred-but-not-in-pool records reach zero. Release any separate long-lived asset handle last.
6. Clear damage buffers/router slots, dispose scene cancellation and version-specific registrations, detach the owner from the factory, and enter `Disposed`. A repeated drain is a no-op with telemetry, not a second release.

A timeout may stop waiting for scene presentation, but it must not discard operation ownership. The application factory/reaper remains alive until each Addressables operation settles and releases stale successes.

With Domain Reload disabled:

- Prefer instance owners over static pools. A bootstrap `DontDestroyOnLoad` factory may exist, but any static facade/session ID is reset at `RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.SubsystemRegistration)` and never preserves a prior play session's pool, cancellation source, delegate, handle, or epoch.
- Route `OnDisable`, `OnDestroy`, additive scene unload, application quit, and Editor play-mode exit into the same idempotent drain. Editor-only hooks belong behind `#if UNITY_EDITOR` and must be unregistered as well as registered.
- Increment an application session generation so a callback captured in a prior no-domain-reload session cannot transfer into the next one.
- Exercise two consecutive Enter Play Mode sessions with Domain Reload disabled and a pending completion during exit. The second session must start with zero registered owners and no usable stale handles.

## Test-first migration sequence

Introduce narrow seams such as `IProjectileInstanceFactory`, `IProjectileSpawner`, `IDamageOverlapQuery`, and the lease-state validator so deterministic tests can control completions and saturation. Tests describe behavior; production remains on the legacy spawner until each vertical slice is green.

### 1. Characterize the existing behavior

Before pooling, lock shot request/activation PlayerLoop phase, host/client ordering, same-frame versus delayed spawn, impact ordering, duplicate-collider damage, event order, PrimeTween visual result, homing first step, exceptions, and cancellation on additive unload. Pooling may make an async spawn immediately available; it must not silently change authoritative timing.

Add a failing allocation regression or preserve the reproducible Development Player marker/call-stack baseline that exceeds the declared budget. Test setup, delegates, recorder creation, assertions, and formatting stay outside the sample window.

### 2. Pool lease and reset reds

Add tests that initially fail for the missing protocol:

- warm-up is not `Ready` until exactly 128 successful transfers exist; partial failure releases all successes;
- 128 simultaneous rents succeed, rent 129 takes the overflow lane, and returning one enables the next pooled rent without creation;
- `ObjectPool.Get` never calls an async/growing creation path after priming;
- normal return, impact return, exception return, active-on-unload return, and max-size destroy each release/retain the correct origin exactly once;
- dirty reuse resets target/shooter/damage/callbacks, transform, Rigidbody, collider, collision ignores, trail, particles/audio, renderer/material state, timer, and hit state;
- double return, foreign-pool return, and a stale lease fail safely without changing pool counts;
- a callback, tween completion, impact, or homing continuation from generation N cannot mutate or return generation N+1;
- stable subscriptions receive only current-lease events and are removed at pool teardown.

### 3. Addressables race reds

Use a controllable fake operation source and assert exact acquisition/release counts for:

- success, failure, and cancellation before completion;
- unload immediately before and immediately after successful completion;
- waiter cancellation while the underlying operation later succeeds;
- simultaneous completion and owner drain;
- warm-up failure after some successes;
- overflow success followed by impact, overflow canceled while pending, and overflow late success after unload;
- repeated drain/application quit; and
- an optional separate asset handle released only after its dependent instances.

In all stale-success cases, the instance is never activated and is released once. In all failure cases, the installed handle cleanup route is followed once.

### 4. Damage workspace reds

At the pure query seam and in a PlayMode physics scene, cover `0`, below-capacity, exact-capacity, and over-capacity results at 64, 128, and 256. Assert:

- exact full retries rather than silently truncates;
- top-tier full selects the complete allocating fallback and records it;
- only the returned logical count is processed; stale slots do not damage;
- multiple colliders follow the characterized duplicate-target rule;
- permuted physics order yields the same canonical damage order and totals;
- callbacks run only after workspace release; and
- nested use is detected while normal same-frame impacts are serialized.

### 5. Async/tween lifecycle reds

Cover UniTask cancellation before first step, during suspension, after normal completion, simultaneous impact/unload, and exception observation. Assert the PlayerLoop phase and main-thread affinity. Cover PrimeTween completion, cancellation on impact, cancellation on unload, overwrite/concurrent-target behavior, and dirty visual reset. A stale callback from the previous lease must be harmless.

### 6. Scene/domain and retention reds

Load/unload an additive combat scene with active, inactive, overflow, and pending records. Repeat the cycle, including two Editor play sessions with Domain Reload disabled. Assert owner/factory registries, subscriptions, operations, instance ownership equations, and scene references converge to zero for each dead epoch.

### 7. Allocation red/green

First show the unchanged representative workload exceeds the named normal budget at a recorded call stack. Then compare the pooled slice under the identical workload after all capacity preparation. Functional tests run before allocation checks. A microbenchmark or Editor-only result is supporting evidence, not the target-player acceptance result.

## Representative verification ladder and report

Record each item as `PASS`, `FAIL`, or `PENDING`, with an artifact/reference and exact version/configuration. Until populated, status is `PENDING`.

1. **Static and compatibility:** exact installed APIs, Addressables acquire/release pairing, UniTask PlayerLoop configuration, PrimeTween capacity/version/license, main-thread pool access, build compilation, analyzers, IL2CPP/AOT/stripping where applicable.
2. **Functional:** plain/EditMode state-machine and deterministic race tests, then PlayMode pool, physics, additive-scene, no-domain-reload, and real Addressables integration tests.
3. **Allocation:** create recorders/markers outside the window; warm all 128 records and all buffer/tween/async paths; run repeated identical samples; inspect `GC.Alloc` bytes, event count, and call stacks on all relevant threads. Report first use, normal path, pool miss, top-tier buffer fallback, exception, and teardown separately.
4. **Development target player:** replay the captured networked burst and capacity boundary on the representative device/backend. The normal marker must be 0 B/0 events, with zero pool misses and zero top-tier fallbacks; otherwise the scoped claim fails.
5. **Release target player:** repeat the acceptance workload to catch optimization, stripping, async-state-machine, and backend differences. Repeat on every materially supported platform; do not generalize from one platform.
6. **CPU/native/retained:** compare frame-time markers, physics time, sort/retry cost, native physics memory, pool high-water, native GameObject/component retention, Addressables asset/bundle residency, and managed retained graphs.

Take Memory Profiler snapshots at the same milestones in baseline and changed builds: before scene load, pool ready/inactive, peak 128 active, after all return, after additive unload, and after repeated load/unload cycles. A pool intentionally retains 128 GameObjects, components, TrailRenderer/native buffers, and dependent assets while ready; that retained cost must fit the project cap. After drain, no projectile or dead-scene reference should remain reachable from the factory, router, tween, UniTask state, static facade, or Addressables ownership records. Record physics native memory separately from managed `Collider[]` capacity.

## Rollout and rollback

- Put legacy and pooled implementations behind `IProjectileSpawner`; select one when the combat-scene owner is created. Do not flip an active scene mid-request or allow both implementations to own one shot ID.
- Land in reversible vertical slices: ownership/fakes/tests, fixed pool, dirty reset, async/tween guards, damage workspace, then target-player instrumentation. Avoid unrelated refactors.
- During canary rollout retain the overflow lane and emit created/active/inactive/high-water/miss counts, outstanding/late operations, success/release balance, duplicate/stale returns, damage-tier saturation/fallback, drain duration, and retained/native memory.
- Roll back on a shot/damage/timing/order mismatch, unsupported target build, stale callback, double/missing Addressables release, pool miss above the accepted service target, top-tier saturation above its accepted target, managed-budget failure, CPU regression, retained/native cap breach, scene reference leak, unobserved async exception, or dependency/provenance problem.
- Rollback means stop new pooled admission, fully drain and release the current pool through the protocol, then create subsequent scenes with the legacy spawner. Never abandon pooled Addressables ownership or merely destroy pooled GameObjects. Remove the legacy lane only after representative soak data and explicit project approval.

## Rejected alternatives and revisit triggers

- **Continue Instantiate/Destroy for every projectile:** retained only as rollback/rare overflow because the user-stated capture associates bursts with recurring allocation. Revisit if call stacks show projectile creation is not material or pooling's retained/native/CPU cost is worse.
- **Allow `ObjectPool` to grow on demand:** rejected because async Addressables creation cannot safely live in synchronous `createFunc`, and growth contaminates steady-state capacity. Revisit only with a different explicit asynchronous pool contract and transition budget.
- **Drop/recycle the oldest on exhaustion:** rejected because it changes co-op gameplay and creates stale callbacks/use-after-return. Revisit only with an approved authoritative degradation rule.
- **Keep one `Collider[32]` and accept its count:** rejected because a full return is potentially truncated and query order is not a nearest-hit guarantee.
- **Call the allocating overlap API on every impact:** rejected for the normal path; retained only as the complete top-tier correctness fallback.
- **Move damage queries to native containers/Jobs/ECS:** rejected for this local measured source because it adds native ownership/scheduling complexity and does not by itself solve Addressables or physics-query semantics. Revisit only if scale/CPU evidence justifies Jobs/Burst and a version-matched API supports the needed data flow.

## Risks

- Immediate pool availability can change an originally asynchronous projectile's activation phase and network ordering; characterization is mandatory.
- The true projectile peak may exceed 128, and collider density is unrelated to projectile concurrency. Both capacities remain provisional until representative telemetry exists.
- Some Addressables operations cannot be canceled after start; cancellation must not be confused with release or operation abandonment.
- Repeated C# event subscription changes, UniTask cancellation registrations/adapters, captured callbacks, PrimeTween growth, and exception paths can allocate even when Instantiate/Destroy is gone.
- Physics NonAlloc results are not a complete ordered set when full. Tier retries add CPU; the complete fallback allocates; canonical sorting can expose a behavior change.
- Pooling retains managed wrappers, native GameObjects/components/trails, assets, bundles, and references. Incorrect reset can also leak gameplay state without a memory leak.
- Domain-Reload-disabled Editor behavior can hide stale statics and handles that a player never preserves, while Editor profiling can add allocations absent in a player.
- Exact Unity 6, Addressables, UniTask, and PrimeTween APIs and build behavior are version-sensitive. The installed artifacts, target backend, and platform decide compatibility.

## Open questions to resolve before locking tests

1. What exact call stacks, byte/event counts, threads, marker duration, target device/platform, backend, and Unity/package versions produced the Development Player burst sample?
2. Are projectiles authoritative gameplay objects or client visuals, and what activation PlayerLoop/network order does the current async path expose?
3. On capacity exhaustion, must a shot preserve current async behavior through a transient instance, may it wait, or may a visual be omitted while authoritative damage continues? This recommendation uses the legacy transient lane until product semantics say otherwise.
4. Can a projectile legitimately outlive its additive combat scene? If yes, the pool owner must be promoted to the combat-session lifetime rather than force-returning it at scene unload.
5. Does damage apply once per entity or once per collider, and what stable network/entity key defines canonical order and ties?
6. What numeric CPU, retained-memory, native-memory, overflow, saturation, and teardown-time limits are acceptable on the representative device?
7. Which Addressables handle-tracking mode and release API are installed, and is there a separate asset/load handle in addition to per-instance ownership?

## Next action

Capture and preserve the exact `GC.Alloc` call stacks and allocation counts for the named burst on the representative Development Player, then fill the environment and behavior unknowns above from the installed manifests and characterization tests. Start the first red slice with the lease/addressable ownership fakes and the `128 + 1` exhaustion case; keep the legacy spawner selected until exact-release, stale-generation, full-buffer, additive-unload, and no-domain-reload tests pass. Only then compare the identical warmed target-player workload and decide whether 128 pooled instances and the 64/128/256 damage tiers satisfy both allocation and retained/native-memory budgets.
