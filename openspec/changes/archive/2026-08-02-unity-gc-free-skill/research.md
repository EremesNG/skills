# Research: Unity GC-Free Skill

**Access date**: 2026-08-02<br>
**Evidence policy**: Primary sources only for technical claims: current Unity
documentation, official package documentation, upstream repositories/manifests,
upstream changelogs/releases/licenses, and Microsoft .NET API documentation.

## Questions

1. What measurable contract makes “GC-Free” technically honest in Unity?
2. Which managed-allocation sources and Unity APIs deserve durable guidance?
3. When are ZLinq, UniTask, PrimeTween, pooling, native containers, or other
   libraries better than direct code or built-in Unity facilities?
4. Which compatibility, lifecycle, AOT, threading, semantic, maintenance, and
   license constraints prevent mechanical substitutions?
5. What reusable package shape lets an agent diagnose, implement, and verify
   low-allocation work without loading a large catalog on every Unity task?

## Authority order

1. Observed target-player behavior, profiler captures, repository/package
   manifests, source/tests, and accepted project constraints.
2. Official documentation for the installed Unity and package versions.
3. Upstream project source, manifest, changelog, release, and license for the
   exact dependency version.
4. Project-authored benchmarks, clearly labeled as self-reported evidence.
5. Inference, explicitly labeled and never used as proof of allocation behavior.

Community posts, secondary blogs, videos, and remembered folklore were excluded
from the technical evidence set.

## Evidence reviewed

### Unity managed memory and measurement

- Managed memory introduction:
  <https://docs.unity3d.com/jp/current/Manual/performance-managed-memory-introduction.html>
- Garbage collector and incremental collection:
  <https://docs.unity3d.com/cn/current/Manual/performance-garbage-collector.html>
  and
  <https://docs.unity3d.com/kr/current/Manual/performance-incremental-garbage-collection.html>
- Allocation tracking and target-player caveats:
  <https://docs.unity3d.com/jp/current/Manual/performance-track-garbage-collection.html>
- Reference types, strings, closures, boxing, and `params`:
  <https://docs.unity3d.com/jp/current/Manual/performance-reference-types.html>
- Reusable objects and collections:
  <https://docs.unity3d.com/cn/current/Manual/performance-reusable-code.html>
- Arrays and non-allocating Unity API alternatives:
  <https://docs.unity3d.com/jp/current/Manual/performance-optimizing-arrays.html>
- Profiler recorder API and counters:
  <https://docs.unity3d.com/ja/current/ScriptReference/Unity.Profiling.ProfilerRecorder.html>
  and
  <https://docs.unity3d.com/kr/6000.0/Manual/profiler-counters-reference.html>
- Performance Testing package for Unity 6:
  <https://docs.unity3d.com/jp/current/Manual/com.unity.test-framework.performance.html>

### Unity reusable/native facilities and version-sensitive APIs

- `ObjectPool<T>`:
  <https://docs.unity3d.com/6000.0/Documentation/ScriptReference/Pool.ObjectPool_1.html>
- Unmanaged C# memory and allocator lifetimes:
  <https://docs.unity3d.com/ja/current/Manual/performance-unmanaged-memory.html>
- Native-container job safety:
  <https://docs.unity3d.com/cn/6000.0/Manual/job-system-native-container.html>
- Burst compilation boundary:
  <https://docs.unity3d.com/ja/current/Manual/script-compilation-burst.html>
- Physics NonAlloc query guidance:
  <https://docs.unity3d.com/ja/6000.0/Manual/physics-optimization-raycasts-queries.html>
- Current collision contact reuse:
  <https://docs.unity3d.com/ja/current/ScriptReference/Collision.GetContacts.html>
- Unity `Awaitable`:
  <https://docs.unity3d.com/ja/current/ScriptReference/Awaitable.html>
  and
  <https://docs.unity3d.com/ja/current/Manual/async-awaitable-introduction.html>
- Addressables 2.7 retained asset/bundle lifetime:
  <https://docs.unity3d.com/Packages/com.unity.addressables@2.7/manual/memory-assets.html>

### Upstream low-allocation libraries

- ZLinq README and Unity package manifest:
  <https://github.com/Cysharp/ZLinq> and
  <https://raw.githubusercontent.com/Cysharp/ZLinq/master/src/ZLinq.Unity/Assets/ZLinq.Unity/package.json>
- UniTask README and releases:
  <https://raw.githubusercontent.com/Cysharp/UniTask/master/README.md> and
  <https://github.com/Cysharp/UniTask/releases>
- PrimeTween README, changelog, and license:
  <https://raw.githubusercontent.com/KyryloKuzyk/PrimeTween/main/README.md>,
  <https://raw.githubusercontent.com/KyryloKuzyk/PrimeTween/main/changelog.md>, and
  <https://raw.githubusercontent.com/KyryloKuzyk/PrimeTween/main/LICENSE>
- ZString:
  <https://github.com/Cysharp/ZString>
- MemoryPack README and Unity manifest:
  <https://github.com/Cysharp/MemoryPack> and
  <https://raw.githubusercontent.com/Cysharp/MemoryPack/master/src/MemoryPack.Unity/Assets/MemoryPack.Unity/package.json>
- MessagePack-CSharp README and Unity manifest:
  <https://github.com/MessagePack-CSharp/MessagePack-CSharp> and
  <https://raw.githubusercontent.com/MessagePack-CSharp/MessagePack-CSharp/master/src/MessagePack.UnityClient/Assets/Scripts/MessagePack/package.json>
- R3 and ObservableCollections:
  <https://raw.githubusercontent.com/Cysharp/R3/master/README.md> and
  <https://github.com/Cysharp/ObservableCollections>
- Microsoft `ArrayPool<T>`:
  <https://learn.microsoft.com/en-us/dotnet/api/system.buffers.arraypool-1>

## Findings

### F1 - “GC-Free” must name the boundary

Unity records allocations on the managed heap as `GC.Alloc`. Managed-heap size,
native allocations, retained pools, asset/bundle residency, CPU time, and the GC
collection process are related but different quantities. A useful default target
is therefore:

> After declared warm-up and capacity preparation, the named steady-state
> workload allocates 0 managed bytes over a representative frame/sample window
> in the target player, across all relevant threads.

This does not claim zero startup work, zero memory, zero native allocation, zero
CPU cost, or zero retained state. Incremental GC spreads collection work; it does
not erase allocation cost or total GC work. Disabling GC can grow memory to OOM
and is not a general solution.

**Decision**: Make the allocation contract and cost taxonomy the first skill
step. Never accept “GC-free” as an unscoped adjective.

### F2 - Target-player evidence is authoritative

Unity documents that Editor behavior can differ from a player; for example,
`GetComponent` reports allocations in the Editor that do not occur in a built
player. `GC.Alloc` must be checked on all relevant threads, while managed-heap
growth is not the sum of per-frame samples. Profiler call stacks can identify
allocation sites without Deep Profiling, and `ProfilerRecorder` can support
repeatable counters when its metric is available for the installed version.

**Decision**: Require baseline, warm-up, fixed capacity, a representative
Development/Release player on target hardware, functional validation, an
allocation window, and separate native/retained/CPU reporting. Editor evidence
is diagnostic only.

### F3 - Direct reuse and built-in APIs come before dependencies

Current Unity guidance supports reusing lists/arrays, pre-sizing capacity,
passing caller-owned buffers, `Mesh.GetVertices(List<T>)`, `Input.GetTouch`,
NonAlloc physics queries, `Collision.GetContacts`, `ObjectPool<T>`, native
containers, and pooled `Awaitable` instances. It also documents strings,
closures, method references, boxing, `params`, array-return APIs, and collection
growth as allocation sources.

Old blanket rules are unsafe. Concrete array/List `foreach` can be allocation
free, and Unity 6 exposes allocation-free enumerators for some APIs; interface
conversion, iterator state, boxing, backend, and API implementation determine the
result. Likewise, LINQ, strings, coroutines, and allocations outside a measured
hot path are not automatically defects.

**Decision**: Route through the smallest mechanism: remove unnecessary work,
reuse existing storage, use a built-in caller-buffer API, then consider a
dependency when repeated complexity or readability justifies it.

### F4 - Caller-buffer APIs trade allocation for capacity semantics

NonAlloc physics methods stop when the supplied buffer is full. Results may be
truncated and, for version-pinned Raycast documentation, ordering is undefined;
the full buffer is not guaranteed to contain the nearest hits. A reused `List`
still allocates when it expands. Returning `ArrayPool` storage too early, twice,
or without clearing sensitive references can corrupt behavior or retain data.

**Decision**: Every caller-buffer migration must define maximum/capacity,
full-buffer detection, truncation/order policy, fallback or telemetry, ownership,
and tests for overflow/use-after-return.

### F5 - The headline substitutions are conditional

- **LINQ -> ZLinq**: Struct value-enumerables remove iterator-chain allocations
  on supported sources, but closures, materialization, interface conversions,
  pooled results, struct copies, long chains, numeric ordering, and Unity/compiler
  support still matter. A loop may remain simpler.
- **Coroutines -> Unity Awaitable/UniTask**: Unity 2023.1+ offers pooled
  `Awaitable` with a strict single-await rule and synchronous continuation
  semantics. UniTask supplies a wider PlayerLoop/cancellation/composition model
  and promise pooling, but PlayerLoop injection, ECS reset, cancellation cost,
  WebGL thread limits, debug async state machines, and IEnumerator timing differ.
- **DOTween -> PrimeTween**: PrimeTween provides low-allocation tween/sequence
  APIs and measured capacity configuration, but captured callbacks still
  allocate; async/coroutine wrappers allocate; tweens are non-reusable; target
  overwrite, cancellation, material overrides, and migration-adapter behavior
  differ. Its license is not MIT and restricts source redistribution/repackaging.
- **Instantiate/Destroy -> pooling**: Pooling moves creation cost to warm-up and
  retains objects. Empty pools still create; full pools may destroy; reset,
  capacity, scene/addressable ownership, subscriptions, async cancellation, and
  teardown decide correctness.

**Decision**: Encode a compatibility-and-semantics matrix, not a replacement
dictionary.

### F6 - Text, serialization, and reactive tools have output boundaries

StringBuilder avoids intermediate strings but `ToString` allocates the final
string. ZString rents buffers and can write directly to TMP, but builders need
proper disposal and final string creation still allocates. MemoryPack and
MessagePack use source-generation/AOT paths and pooled buffers, but final
materialization, compatibility, schema behavior, and Unity version vary. R3 and
ObservableCollections reduce some subscription/event allocations but change
error, completion, view, disposal, and thread behavior.

MemoryPack currently documents Unity 2022.3.12f1. MessagePack's manifest and
README disagree about the conservative Unity/IL2CPP minimum. Such conflicts make
the installed release artifact and compiler/backend the deciding evidence.

**Decision**: Keep these tools in an advanced reference; recommend them only for
a measured source and an accepted semantic/AOT/lifecycle contract.

### F7 - Native memory avoids GC but creates manual ownership

NativeArray/NativeList and other Unity Collections allocate unmanaged memory.
They support Jobs/Burst, but still incur allocation/free CPU cost and require
allocator, disposal, alias, job-dependency, and safety ownership. `Temp` cannot
cross the documented boundary, `TempJob` must be disposed within four frames,
and `Persistent` is slower and unbounded by time. Disabling safety can turn a
lifetime error into a crash. Burst does not require wholesale ECS adoption.

**Decision**: Treat native containers as a separate memory domain and require
explicit disposal evidence. Prefer local adoption when it solves a measured
data/scheduling problem.

### F8 - Freshness and license are part of correctness

As of the access date, upstream releases indicate active ZLinq, UniTask, R3,
MemoryPack, and MessagePack maintenance. PrimeTween uses a changelog/package
channel rather than GitHub Releases, and its README/changelog package versions
can differ; its package provenance must be pinned. Project-authored benchmarks
are valuable hypotheses, not independent rankings. `Collections.Pooled` has a
2019 NuGet release and is not a responsible default without renewed evaluation.

**Decision**: Store source starting points and conflicts, not timeless “latest”
versions. At invocation time, verify exact package, license, Unity/compiler,
backend, platform, and upstream advisory state.

### F9 - A bounded inspector improves evidence without pretending to parse C#

A read-only script can reliably find Unity metadata, relevant declared packages,
and path-level text signals such as System.Linq, iterator/coroutine constructs,
DOTween, Instantiate/Destroy, allocating query APIs, array-return properties,
temporary collections, lambdas, logging/string formatting, and native
containers. It cannot prove runtime allocation, hotness, closure capture, or
semantic intent.

**Decision**: Bundle a dependency-free Python inspector that emits only counts
and bounded relative paths, excludes generated/secret-like paths, and labels
results as leads. The agent must inspect the source and measure before diagnosis.

## Resulting package shape

```text
skills/unity-gc-free/
├── SKILL.md
├── agents/openai.yaml
├── evals/evals.json
├── references/
│   ├── allocation-contract.md
│   ├── hotspot-catalog.md
│   ├── library-matrix.md
│   ├── pooling-and-buffers.md
│   ├── native-memory.md
│   ├── migration-playbook.md
│   └── sources.md
└── scripts/inspect_unity_gc.py
```

## Unresolved research

None blocks authoring. Exact package versions, license acceptance, supported
compiler/backend, target platform, real hot-path capacity, and profiler results
remain invocation-time evidence rather than global skill defaults.
