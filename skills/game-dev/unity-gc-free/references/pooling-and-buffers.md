# Pooling and buffers

Pooling trades creation/allocation for retained capacity and manual lifecycle.
It is correct only when ownership, reset, saturation, and teardown are explicit.
Measure managed allocation, native memory, retained memory, and CPU separately.

## Common ownership record

Define this before implementing any pool or reused buffer:

- **Owner**: service/component/scene/domain that creates and tears down storage.
- **Lease**: who may `Get`/rent, when it becomes usable, and whether transfer is
  allowed.
- **Return**: the single point that can `Release`/return; exactly once.
- **Capacity**: expected steady-state, observed peak, warm-up count, retained
  memory estimate, and memory cap.
- **Exhaustion**: grow, fail, defer, drop, reuse oldest, or fall back; never leave
  it implicit.
- **Reset**: state cleared on get versus release, including references and Unity
  native state.
- **Destroy**: behavior for rejected/overflow objects and owner teardown.
- **Telemetry**: created, active/rented, inactive, peak, misses/growth,
  full-buffer events, overflow destroys/drops, and outstanding leases.
- **Validation**: double return, use after return, foreign-object return, leak,
  release-after-owner-death, and exceptional-exit tests.

Warm-up must exercise the same initialization path and capacities as the named
workload. A pool that grows during the sample has not demonstrated a warmed
steady-state contract.

## Object pooling with UnityEngine.Pool

`UnityEngine.Pool.ObjectPool<T>` and `LinkedPool<T>` provide create, action-on-get,
action-on-release, action-on-destroy, collection-check, default-capacity, and
max-size policies. They are **not thread-safe**; keep access on the authorized
thread or provide a separate proven synchronization design.

For a GameObject/component pool:

1. **Create** the object and cache stable component references. Do not call it
   from a steady-state sample unless growth is the declared exhaustion policy.
2. On **get**, assign the new owner/context, transform, active state, visual
   state, and fresh cancellation lifetime. Avoid inheriting a prior lease.
3. On **release**, stop particles/audio/tweens, cancel async work, detach or
   unsubscribe all subscriptions/events, clear callbacks and retained references,
   reset physics/animator/material-property state, and deactivate/reparent as
   the contract requires.
4. On **destroy**, perform the actual Unity destruction/release appropriate to
   the origin. `maxSize` overflow can invoke this path; it is not allocation-free.
5. On scene unload/domain reload/application shutdown, stop new leases, settle
   outstanding ones, clear the pool, and make late returns deterministic.

Collection checks can catch some double releases in development, but do not
replace ownership tests. A handle/generation or active-set guard may be useful
when stale callbacks can return a newly leased instance.

## Collection reuse

Retain a `List<T>`, `Dictionary<TKey,TValue>`, `HashSet<T>`, queue, or stack only
under one clear owner. Set initial capacity from evidence, call `Clear` at the
defined boundary, and remember that clear normally retains backing capacity.

- Reusing a collection avoids construction but capacity growth still allocates.
- Clear retained references when the collection or pooled element can keep large
  graphs alive. For a list, `Clear` removes logical elements; custom buffers may
  need explicit slot clearing.
- Do not expose a reusable mutable list as a stable result. Prefer a caller-owned
  destination, process-in-place callback, scoped lease, or copy whose allocation
  is explicitly accepted.
- Bound caches and pools. Shrink/evict only outside the measured path and only
  when retained-memory policy justifies the later regrowth cost.
- Avoid sharing ordinary Unity collections across threads without an explicit
  synchronization and mutation contract.

## ArrayPool leases

`System.Buffers.ArrayPool<T>.Shared.Rent(minimumLength)` can return an array
larger than requested. Treat the logical length separately from `array.Length`.

The lease protocol is strict:

1. Rent once and record the logical slice.
2. Keep the array inside the owner scope; do not store it in delayed callbacks,
   tasks, native jobs, or consumers that outlive the lease.
3. In `finally`, clear sensitive values and **clear retained references** when
   required, then return exactly once.
4. Never read/write after return, return to a different pool, or return the same
   array twice. Double return and use after return are correctness defects even
   when no test fails immediately.

The shared pool can allocate or choose a different size on first/large rents and
does not promise a project-specific memory cap. For strict bounds, use a private
pool or fixed buffers with explicit exhaustion behavior. Do not retain a span or
view after its array lease ends.

## Caller-owned buffers and NonAlloc APIs

Caller-owned buffers are often simpler than a general pool. Applicable examples
include physics NonAlloc queries, `Collision.GetContacts`, mesh APIs accepting a
list/native container, and methods that fill a supplied array/list.

Every migration needs a **full-buffer policy**:

- Detect saturation using the API's documented count convention.
- Define whether **truncation** is acceptable and visible to callers.
- Preserve documented result **ordering**, or explicitly sort with prepared
  scratch space. A full physics buffer may not contain the nearest hits.
- Choose a tested **fallback**: grow outside the hot window, retry with another
  prepared tier, stream/process chunks when supported, degrade/drop with
  telemetry, or fail fast. Silent truncation is not a policy.
- Record saturation telemetry and size from representative peaks plus margin.
- Preserve the API's mutation and stale-slot semantics; process only the returned
  logical count and clear old references if they retain objects.

## Addressables and pooled Unity objects

Pooling an Addressables asset or instance adds reference-count ownership. Match
the acquisition API with the corresponding release API from the installed
Addressables version; do not mix an `InstantiateAsync` instance lease with a raw
asset-handle release by assumption.

- One designated owner holds each long-lived load handle while the pool can
  create or serve dependent instances. Mirror every successful load/acquire with
  exactly one release when that ownership ends.
- A pooled instance must not outlive the asset/bundle handle it depends on.
- Reference count zero permits release; it does not guarantee an immediate flat
  memory graph because bundles and dependencies have their own lifetime.
- On scene unload, stop acquisition, cancel/settle in-flight operations, release
  or destroy active and inactive instances by origin, then release handles in a
  safe order. Test late completions and cancellation races.
- Across domain reload choices, static pools must either be reconstructed or
  intentionally persist with valid handles; never assume Editor reload behavior
  matches a player.

## Release/reset checklist

Before returning any pooled gameplay/UI object, consider:

- event and reactive **subscriptions** removed;
- async **cancellation** requested and callbacks unable to affect a later lease;
- timers, coroutines, tweens, animations, particles, audio, physics velocities,
  collision ignores, navigation, and input bindings reset;
- parent, transform, layer/tag, visibility, material property block, text, locale,
  model/view binding, collections, delegates, and object references reset;
- native containers/jobs completed or transferred under a separate contract;
- Addressables reference count and origin preserved;
- pool still alive and accepts the return.

## Acceptance gate

Test normal get/release, peak warm-up, empty-pool exhaustion, max-capacity
overflow, reset after dirty use, exception/cancellation return, double return,
use after return, owner teardown, scene unload, domain reload configuration,
Addressables late completion, full-buffer truncation/order/fallback, and memory
cap telemetry. Then remeasure the target player with the pool already warmed.
