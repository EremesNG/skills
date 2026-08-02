---
name: unity-gc-free
description: Diagnose, design, implement, review, and verify GC-free or low-allocation Unity C# hot paths using measured managed-allocation evidence, caller-owned buffers, pooling, and compatible libraries. Use for GC.Alloc spikes, garbage-collection stutter, per-frame allocations, LINQ or iterator churn, coroutines and async workflows, tweening, Instantiate/Destroy churn, strings and serialization, physics or array-return APIs, Native Collections, allocation tests, or migrations involving ZLinq, UniTask, PrimeTween, UnityEngine.Pool, ZString, MemoryPack, MessagePack-CSharp, R3, or similar tools. Skip for generic Unity architecture with no allocation concern, unmeasured micro-optimization, pure native/GPU memory work, or non-Unity C# unless Unity constraints still govern the result.
---

# Unity GC-Free

Reduce managed allocations where representative evidence justifies the work.
Treat “GC-free” as a scoped, measurable contract rather than a global coding
style, and preserve behavior while moving or removing allocation cost.

## Operating boundary

- Classify the request as explanation, diagnosis, review, or change. Questions
  and reviews do not authorize edits. Implement only when the user requests a
  change.
- Define `GC-free` by default as 0 managed bytes in a named, warmed steady-state
  workload over a representative sample window. Let an explicit project budget
  override that default.
- Keep managed allocation, garbage collection, managed-heap size, native
  allocation, retained memory, asset residency, and CPU time separate. Improving
  one does not prove improvement in the others.
- Optimize measured hot paths. Do not blanket-ban LINQ, `foreach`, coroutines,
  strings, closures, or allocations in startup, editor, loading, or cold code.
- Prefer direct code, reuse, and version-matched Unity APIs before adding a
  package. Do not install or license a dependency without authorization.
- Preserve timing, ordering, cancellation, threading, error, object-lifetime,
  serialization, and buffer-overflow behavior. Low allocation is not success if
  gameplay changes or memory leaks.
- Treat package/API/version claims as unstable. Inspect the project and current
  primary sources; never infer “latest” from this skill's research snapshot.

## Define the allocation contract

Record these fields before proposing a solution:

1. **Workload**: the exact callback, operation, transition, or batch plus
   representative inputs, entity counts, and call frequency.
2. **Environment**: Unity and package versions, scripting backend, target
   platform/device, build type, code optimization, and relevant thread.
3. **Warm-up and capacity**: first-use work to exclude or include, prewarmed
   pools/caches, and expected versus worst-case capacity.
4. **Window and budget**: sample duration/frame range, bytes and allocation count
   allowed, and whether exceptional/transition paths have a separate budget.
5. **Correctness**: outputs, ordering, timing, failure behavior, lifecycle, and
   full-buffer/exhaustion behavior that must remain unchanged.
6. **Other costs**: CPU/frame-time threshold, native-memory ceiling, retained
   pool/asset limit, and collection-pause goal when material.

Read [Allocation contract](references/allocation-contract.md) for the complete
measurement protocol and evidence template.

## Inspect the evidence

Investigate discoverable facts before asking the user for them.

1. Locate the Unity root through `ProjectSettings/ProjectVersion.txt`,
   `Packages/manifest.json`, and `Assets/`. Read repository instructions and
   preserve unrelated changes.
   For a dependency, inspect the installed manifest/lock and record its exact
   version, coordinate/source or tag/commit, license, and compiler/backend fit.
2. From this skill directory, run the bounded inspector when a project exists:

   ```text
   python scripts/inspect_unity_gc.py --root <unity-project> --json
   ```

   Treat counts and paths as investigation leads. Inspect the relevant source
   and nearby tests; the script cannot prove allocation or hotness.
3. Inspect Profiler `GC.Alloc` samples and call stacks across relevant threads.
   Use Memory Profiler for retained graphs and native/managed layout, not as a
   substitute for per-call allocation evidence.
4. Prefer a representative target-player capture. Editor and player behavior
   can differ; label Editor-only findings provisional.
5. Label every input **Observed**, **User-stated**, **Assumed**, or **Unknown**.
   Ask one question only when the answer changes the contract or solution.

If no runtime evidence is available, give a bounded hypothesis and the exact
capture or test needed next. Do not claim an allocation was removed.

## Route only needed knowledge

Load the smallest reference set that resolves the measured source:

| Task signal | Read |
| --- | --- |
| Defining zero-allocation scope, profiling, counters, or success evidence | [Allocation contract](references/allocation-contract.md) |
| C# or Unity APIs that may allocate and built-in alternatives | [Hotspot catalog](references/hotspot-catalog.md) |
| ZLinq, Awaitable, UniTask, PrimeTween, strings, serialization, or reactive tools | [Library matrix](references/library-matrix.md) |
| GameObject, collection, array, caller-buffer, or Addressables reuse | [Pooling and buffers](references/pooling-and-buffers.md) |
| NativeArray, NativeList, Jobs, Burst, allocators, or safety | [Native memory](references/native-memory.md) |
| Behavior-preserving refactor, regression test, rollout, or rollback | [Migration playbook](references/migration-playbook.md) |
| Verifying an unstable claim, version, maintenance, benchmark, or license | [Sources](references/sources.md) |

Architecture-heavy work can also use `unity-developer`; keep this skill focused
on allocation contracts and the behavior required to change them safely.

## Select the smallest compatible change

Evaluate solutions in this order:

1. Stop unnecessary work or move it out of the hot path.
2. Reuse and pre-size project-owned storage; update only when data changes.
3. Use a version-matched caller-buffer, list-filling, ID/hash, or pooled Unity
   API with explicit capacity and lifetime.
4. Use a direct loop, cached comparer/delegate, explicit state machine, or small
   local abstraction when it is clearer than a dependency.
5. Add a maintained library only when its repeated benefit exceeds adoption,
   compatibility, AOT, license, lifecycle, and migration cost.
6. Move data to native containers/Jobs/Burst only when data scale or scheduling
   justifies manual ownership; do not require ECS/DOTS for a local problem.

For each candidate, record:

- the measured allocation it removes and any allocation it moves to startup,
  pool growth, materialization, exception, final output, or native memory;
- semantic differences and the functional test that guards them;
- Unity/compiler/backend/platform compatibility and exact package provenance;
- owner, capacity, disposal/cancellation/reset/teardown, and retained-memory cap;
- rejected alternatives and the measurable revisit condition.

Do not translate APIs mechanically. For example, a full NonAlloc buffer can
truncate results; an `Awaitable` cannot be safely awaited twice; a coroutine and
UniTask can resume at different PlayerLoop points; PrimeTween handles reuse and
target overwrites differently from DOTween; pooled data becomes invalid after
return. For UniTask, verify PlayerLoop injection or reinjection after any system
that replaces it, including ECS initialization when present, and guard platforms
such as WebGL that lack general worker-thread support.

For LINQ/ZLinq, lock deferred versus eager execution, ordering/ties, captured
state, terminal materialization, and result ownership. For coroutine/async work,
add a UniTask first-step test plus suspension, resumption, cancellation, error,
and thread-affinity cases. For pooled leases, require double-return and a
use-after-return red test before changing ownership.

When comparing Unity Awaitable with UniTask, state its pooled single-await rule
and synchronous continuation behavior; record the Awaitable continuation thread
and supported-version gate. Do not treat the mechanisms as interchangeable.

## Migrate one measured source

For an authorized behavior change, work in vertical red-green slices:

1. Confirm the narrowest public functional and allocation seams.
2. Add and run one failing functional test when behavior is not already locked.
3. Add and run a failing allocation regression or capture the reproducible
   Profiler baseline. Avoid tests whose delegate/assertion allocates inside the
   measured window.
4. Change one source with the minimum coherent implementation.
5. Re-run functional evidence before allocation evidence. Exercise overflow,
   cancellation, destruction, pool exhaustion, and exception paths when relevant.
6. Repeat only for the next measured source. Defer broad cleanup until behavior
   and allocation checks are green.

For every staged slice, record functional red-to-green evidence, allocation
before/after evidence, rollback triggers, and no simultaneous semantic changes.

Read [Migration playbook](references/migration-playbook.md) before changing async,
tween, query, serialization, reactive, pooling, or native-memory semantics.

## Verify in the target player

Use the narrowest applicable ladder, then widen according to risk:

1. Static inspection, package/version/license checks, compilation, and analyzers.
2. Plain C#, EditMode, or PlayMode functional tests at the agreed seam.
3. Allocation regression tests with warm-up and measurement overhead outside the
   sample window.
4. A representative Development or Release player on each material platform.
5. Profiler call stacks/counters across threads plus Memory Profiler or custom
   markers for retained/native/CPU trade-offs.

For physics query or projectile-pool changes, record native physics memory as a
separate observation rather than folding it into managed allocation or pool size.

Compare baseline and changed runs under identical workload and capacity. Report
first-use and steady-state separately. A 0 B main-thread sample does not cover
worker threads, rare exceptions, pool expansion, scene transitions, or native
leaks. State exactly what did not run.

## Return contract

Lead with the completed decision or result, then provide:

- **Context and scope**: observed project/build/platform facts and assumptions.
- **Allocation contract**: workload, warm-up, capacity, window, budget, and
  preserved behavior.
- **Evidence**: baseline call stacks/counters/tests and confidence limits.
- **Decision**: selected direct, built-in, library, pool, or native approach;
  rejected alternatives; compatibility/provenance; revisit trigger.
- **Ownership and lifecycle**: buffers, capacities, reset, return/dispose,
  cancellation, scene/domain/asset teardown, and overflow behavior.
- **Implementation**: files changed or bounded code/steps at the requested depth.
- **Verification**: functional and allocation results, target/build/thread, plus
  CPU, native, and retained-memory observations.
- **Risks and next measurement**: residual uncertainty, rollback, and the exact
  next representative check.

For a small answer, combine fields into concise prose. Never label a system
“GC-free” without the named workload and observed evidence that supports it.
