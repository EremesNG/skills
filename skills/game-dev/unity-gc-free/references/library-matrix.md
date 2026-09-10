# Low-allocation library matrix

Dependencies are conditional tools, not badges of allocation freedom. Start
with direct/built-in mechanisms, locate a measured allocation boundary, and add
one library only when its complete contract is a better project fit.

## Decision dimensions

For every candidate record:

- **Fit**: the concrete repeated workload it simplifies.
- **Allocation boundary**: what it can remove and what remains.
- **Semantic contract**: ordering, timing, errors, cancellation, completion,
  mutation, overflow, and result ownership that must remain or intentionally change.
- **Compatibility**: installed Unity/editor, C# compiler, dependency graph, API
  surface, and migration cost.
- **Lifecycle**: initialization, capacity, pooling, subscription, cancellation,
  reset, disposal, scene/domain reload, and teardown.
- **Platform/AOT/threading**: IL2CPP/source generation, stripping, WebGL, Jobs,
  main-thread affinity, and continuation behavior.
- **Provenance/license**: exact tag/commit/package, manifest, upstream license,
  and project approval. Pin the exact artifact evaluated.
- **Avoid when** the direct solution is clearer, the source is not hot, semantics
  do not match, compatibility is unproved, or ownership cannot be enforced.
- **Revisit when** the workload, package lock, platform/backend, capacity,
  lifecycle, license, or profiler evidence changes.

## Summary matrix

| Candidate | Fit | Allocation boundary | Key semantic/lifecycle gate |
|---|---|---|---|
| Direct/built-in | One loop, reused list/array, Unity caller-buffer API, `ObjectPool<T>`, or Unity Awaitable | Avoids dependency and often removes iterator/result/object churn; capacity growth and final outputs remain | Best default when code stays clear; installed-version behavior and ownership still require measurement |
| ZLinq | Repeated LINQ-like pipelines where readability matters | Struct value-enumerables can remove iterator-chain allocations | Captured closure, materialization, interface conversion, ordering, pooled-result ownership |
| Unity Awaitable | Unity 2023.1+ engine operations and simple async flows | Engine-provided instances are pooled | Strict single-await, synchronous continuation, thread affinity, cancellation/error behavior |
| UniTask | Broader PlayerLoop timing, cancellation, composition, and supported async sources | Pooled promises and struct awaitables reduce many `Task` costs | PlayerLoop initialization/order, ECS reset, cancellation registration, WebGL threads, debugger/build differences |
| PrimeTween | Runtime tween/sequence workloads after semantic migration | Low-allocation core with configured capacity | Captured callbacks, non-reusable tweens, overwrite/parallel policy, cancellation, adapters, material reset |
| ZString | Repeated formatting or direct TextMeshPro writes | Pooled formatting buffers avoid intermediates | Builder must be disposed; producing a final string still allocates |
| MemoryPack | Source-generated binary serialization for a controlled schema | Buffer-writer paths avoid a fresh final output | Source generation, schema rules, IL2CPP/AOT build, buffer ownership, supported Unity version |
| MessagePack-CSharp | Versioned interoperable serialization with configured resolvers | Writer/reused buffer paths can avoid final byte-array materialization | Resolver/source-generation configuration, stripping/AOT, schema/security limits, Unity-version evidence conflict |
| R3 | Reactive pipelines whose event/error/completion model is accepted | Designed to reduce common reactive subscription/event costs | Subscription disposal, scheduler/time provider, thread and completion semantics |
| ObservableCollections | Observable list/dictionary/set plus view synchronization | Reduces some snapshot/event churn through synchronized views | View/subscription disposal, mutation/thread model, event semantics, retained references |
| `System.Buffers.ArrayPool<T>` | Variable-size temporary arrays with strict lexical ownership | Reuses backing arrays; a larger first rent and pool growth remain | Return exactly once, never use after return, clear sensitive/reference content, accept larger-than-requested arrays |

## Enumeration: direct loop or ZLinq

Use a direct loop when it is local and clearer. Use ZLinq when a measured,
repeated pipeline benefits from composability and the installed Unity/compiler
matches the evaluated package.

- ZLinq's value-enumerable chain can avoid ordinary LINQ iterator allocations;
  it cannot remove a captured closure, user-created objects, boxed interface
  conversions, ordering state, or terminal materialization.
- `ToArray`, `ToList`, grouping, sorting, and user selectors have their own
  boundaries. A pool-returning terminal such as `ToArrayPool` transfers
  ownership: dispose/return exactly once and do not copy a disposable struct in
  ways that cause double return or use-after-return.
- Preserve numeric/order/exception semantics and compare a direct loop in the
  target player. Do not introduce a dependency for cold setup code.
- Verify package name, tag/commit, Unity manifest minimum, compiler support, and
  MIT license from the exact artifact.

## Async: direct state, Unity Awaitable, or UniTask

Prefer an explicit update/state machine for tiny deterministic per-frame logic.
For engine async APIs on supported Unity versions, evaluate Awaitable before a
third-party dependency. Choose UniTask when its wider PlayerLoop timing,
composition, cancellation, or async-source integration is materially useful.

### Unity Awaitable

- Pooled instances have a strict **single-await** contract. Never await the same
  instance twice or expose it as a reusable multi-consumer promise.
- Continuations run synchronously when completion is triggered. Most Unity APIs
  complete on the main thread; explicit main/background-thread switching changes
  affinity and order.
- Lock start timing, same-frame completion, exception propagation, cancellation,
  owner destruction, and shutdown behavior before replacing a coroutine.

### UniTask

- UniTask uses struct awaitables and pooled promise sources, but user captures,
  combinators, cancellation registrations, async exceptions, and some debug
  async state-machine tracking still allocate.
- Its PlayerLoop injection and selected `PlayerLoopTiming` affect ordering.
  Systems that replace the loop, including some ECS initialization paths, may
  require reinjection in the version-specific documented order.
- Immediate cancellation can cost more than loop-polled cancellation. Bind
  cancellation to the real owner and dispose registrations.
- WebGL has no general worker-thread support; `RunOnThreadPool` and thread
  switching need platform guards. Test IL2CPP, stripping, and the target platform.
- Coroutine-to-UniTask adapters do not prove identical first-step, yield,
  cancellation, exception, or object-disable/destroy semantics.

## Tweening: direct animation or PrimeTween

First consider Animator, AnimationCurve plus an explicit update, or the existing
tween system if the measured source does not justify migration. PrimeTween is a
candidate for hot runtime tween/sequence creation after these gates:

- Configure/warm its tween and sequence capacity from observed peaks; capacity
  expansion is not steady-state free.
- A captured closure in `OnUpdate`, completion, or sequence callbacks can still
  allocate. Prefer stateful overloads when the exact API provides them.
- Tween handles are non-reusable after completion/cancellation. Do not cache a
  completed tween as though it were a replayable definition.
- Specify target/property **overwrite** versus concurrent-tween behavior instead
  of assuming DOTween equivalence. Lock order, loops, ease, delays, time scale,
  update phase, cancellation, completion callbacks, and sequence nesting.
- Coroutine and async wrappers can allocate even when the core tween path does
  not. Measure the API actually invoked.
- Reset `MaterialPropertyBlock`/renderer state and cancel owner-bound work on
  pool release, scene unload, or destruction.
- PrimeTween is **not MIT**. Inspect and approve its restrictive redistribution/
  repackaging license and exact package provenance before adoption.

## Text: direct update, TMP, or ZString

Avoid rebuilding unchanged UI. Cache stable labels, update on value change, and
prefer TMP numeric setters or supported direct writers. ZString can rent a
formatting buffer and write directly to compatible sinks.

- Dispose the scoped builder exactly once, including exceptional exits.
- `ToString` creates a final string. A pooled builder removes intermediates, not
  the required final string object.
- Validate localization, culture, rounding, rich-text escaping, fallback fonts,
  and thread rules. Never retain a span/view beyond its owner.

## Serialization: direct writer, MemoryPack, or MessagePack-CSharp

Serialization replaces an object graph with an output; it cannot make the final
output disappear. Prefer caller-owned/pooled buffers and streaming writer APIs
when the consumer accepts them.

### MemoryPack

- Uses source generation and version/schema rules that must match all readers.
- A convenience API returning `byte[]` allocates the final output; writing to a
  reusable `IBufferWriter<byte>` changes ownership and may avoid that array.
- Verify the exact Unity package minimum, compiler, IL2CPP/AOT generation,
  stripping, generic registrations, and supported types. Current upstream
  evidence is not a promise for older editor lines.

### MessagePack-CSharp

- Select and configure resolvers/source generation explicitly; reflection-like
  fallbacks, generated-code omissions, typeless features, and security settings
  alter behavior and AOT viability.
- A `Serialize` overload returning `byte[]` allocates the final output. Writer,
  stream, sequence, and pooled-buffer choices have different ownership.
- Upstream README and Unity manifest support minima have conflicted. Test the
  pinned release in a real IL2CPP build; do not infer compatibility from one file.

## Reactive state: direct events, R3, or ObservableCollections

Use a direct event with stable delegate ownership for simple one-to-one flows.
R3 is appropriate only when operators/composition justify its semantics.
ObservableCollections fits mutable data that genuinely needs synchronized views.

- For R3, lock error/completion semantics, scheduler/time-provider behavior,
  main-thread delivery, hot/cold lifetime, and subscription disposal. Captured
  observers and user operators remain allocation boundaries.
- For ObservableCollections, lock mutation order, reset/batch events, view
  filters, synchronization/thread model, retained-item behavior, and view
  disposal. Do not treat a synchronized view as an immutable snapshot.
- In both cases, bind ownership to scene/service/domain lifetime and test reload,
  disable, destroy, cancellation, and late notifications.

## Selection gate

Recommend a library only when the response names the measured source, direct
alternative, exact dependency provenance/license, preserved or intentionally
changed semantics, allocation boundary that remains, lifecycle owner, target
platform/backend proof, rollback path, and target-player verification. Otherwise
report it as a candidate and the missing evidence, not as “GC-free.”
