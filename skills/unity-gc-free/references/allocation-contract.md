# Allocation Contract

Define a claim that another developer can reproduce. “This code allocates less”
is not a contract until the workload, warm state, player environment, observed
counter, budget, and preserved behavior are explicit.

## Scope the workload

Name one observable operation, not an entire project. Examples include one enemy
sensor tick with 500 agents, one inventory refresh after a value change, or 600
steady-state projectile updates after pool warm-up.

Capture:

- entry point and end boundary;
- inputs, entity/item counts, frequency, and deterministic seed when relevant;
- target Unity/package versions, scripting backend, platform/device, build type,
  code optimization, frame rate, and quality settings;
- main-thread and worker/job work included in the operation;
- first-use, scene transition, loading, exceptional, and steady-state paths;
- pool/list/tween/cache capacity before the measured window;
- required output, ordering, timing, overflow, cancellation, and failure behavior.

### Default steady-state contract

Use this default only when the user has not supplied a different budget:

> After declared warm-up and capacity preparation, the named representative
> workload produces 0 managed bytes over the measurement window in the target
> player across all relevant threads, while its functional behavior remains
> unchanged.

The contract does not promise zero startup work, zero native memory, zero retained
memory, zero CPU time, or zero garbage-collection work. State those budgets
separately when they matter.

## Separate the cost domains

| Domain | What it means | Useful evidence | Common false conclusion |
| --- | --- | --- | --- |
| Managed allocation | New data on the managed heap | `GC.Alloc` bytes, allocation count, call stacks, thread | A stable heap size means no allocation. |
| Garbage collection | Work that finds/reclaims unreachable managed objects | GC markers, collection duration/count, frame spikes | Incremental GC removes allocation cost. |
| Managed heap | Used/reserved capacity and fragmentation of the GC-controlled heap | Memory module and snapshots | Sum of `GC.Alloc` equals heap growth. |
| Native allocation | Unity/native-container/plugin memory outside managed GC | Native counters, Memory Profiler, allocator records | Moving data to NativeArray makes memory free. |
| Retained memory | Objects/buffers/assets kept alive by references, pools, caches, or bundles | Snapshot diff, reference graph, pool high-water mark, Addressables events | No per-frame GC means no leak or memory cost. |
| CPU time | Execution, allocation, copying, scheduling, and collection cost | Profiler markers, frame time, target-device timings | Fewer bytes is automatically faster. |

An optimization can improve one row and regress another. Report every material
trade-off instead of collapsing them into “memory.”

## Measurement protocol

### 1. Lock functional behavior

Run or add the narrowest functional test before measuring. Define ordering,
timing, cancellation, exception, full-buffer, pool-exhaustion, reset, and teardown
semantics that the optimization must preserve.

### 2. Record an identical baseline

Use the same scene/data, seed, device, player build, backend, frame settings,
package versions, pool capacities, and sample window for baseline and changed
runs. Save profiler markers or test output that identifies the workload.

### 3. Split first-use from steady state

Measure first-use and transition work deliberately if it affects experience.
Then warm up JIT/AOT-visible code paths, asset handles, generic/static
initialization, async promise pools, tween storage, object pools, reusable lists,
and caches before the steady-state window. Record the exact warm-up count and
capacity state; do not hide pool growth by accident.

### 4. Observe the correct player

- Use a **Development player** on the target platform for call stacks and
  diagnostic capture when possible.
- Repeat the acceptance window in a **Release player** or equivalent production
  configuration when compiler optimization, async state machines, stripping, or
  instrumentation can change the result.
- Treat an **Editor-only** result as **provisional**. Unity documents Editor and
  player allocation differences; Editor instrumentation can add work.
- Record Mono versus IL2CPP and every material platform. Web, mobile, console,
  and desktop runtimes can differ.

### 5. Capture managed allocations

- Inspect CPU Profiler `GC.Alloc` samples and enable allocation call stacks for
  the bounded diagnostic capture. Prefer call stacks over Deep Profiling when
  Deep Profiling would distort the workload.
- Inspect all relevant threads. A 0 B main-thread sample does not cover worker or
  background allocations.
- Use both byte total and allocation count when available. One large allocation
  and many tiny allocations have different risk profiles.
- Use stable custom markers around the operation so unrelated frame work is not
  attributed to the target.
- Verify available counter names on the installed Unity version before using
  `ProfilerRecorder`. A recorder owns unmanaged resources: create it outside the
  measured window and dispose it after capture.

Do not use managed-heap size, `GC.CollectionCount`, or
`GC.GetAllocatedBytesForCurrentThread` alone as proof. They answer different or
narrower questions and can miss other threads or backend behavior.

### 6. Make allocation tests honest

Use the installed Unity Test Framework or Performance Testing package only when
its API is supported by the project version. Keep test setup, delegates,
assertions, result formatting, and recorder creation outside the measured body.
Warm the code and capacity before sampling. Make the test fail against the
observed baseline before implementing the change.

Allocation tests complement, not replace, a representative player capture. A
PlayMode test can establish lifecycle behavior; an EditMode/plain C# test can
establish deterministic logic; a target player establishes the performance
claim.

### 7. Repeat and compare

Run enough identical samples to expose intermittent first-use, exception path,
pool expansion, and scheduling noise. Report raw or summarized baseline and
changed values plus run count. Do not infer variance, causality, or platform-wide
behavior from one sample.

### 8. Check displaced costs

After the managed budget passes, inspect:

- pool/list/buffer high-water mark and retained references;
- native allocations, allocator lifetime, and disposal;
- Addressables asset/bundle residency and mirrored releases;
- CPU/frame-time change and copy/sort/scheduling cost;
- rare transition, cancellation, exception path, and teardown behavior.

## Budget template

Copy and complete this block near the decision or test:

```text
Workload: <entry point, representative input/count, call frequency>
Environment: <Unity/packages, backend, platform/device, build/optimization>
Warm-up: <first-use calls/frames and initialization included or excluded>
Capacity state: <pool/list/buffer/tween/cache sizes and overflow policy>
Measurement window: <marker, frames/iterations, relevant threads, repetitions>
Managed allocation budget: <bytes and allocation count; steady/transition paths>
Preserved behavior: <output/order/timing/error/cancel/lifecycle/full-buffer rules>
Other budgets: <CPU, native memory, retained memory, GC pause if material>
Baseline evidence: <capture/test and observed result>
Changed evidence: <capture/test and observed result>
Confidence limits: <what did not run or remains version/platform dependent>
```

## Evidence classification

Label each statement:

- **Observed**: produced by the named project, build, test, capture, or manifest.
- **User-stated**: supplied as a constraint but not independently reproduced.
- **Documented**: supported by a primary source for the matching version.
- **Inferred**: a reasoned hypothesis awaiting measurement.
- **Unknown**: material evidence is unavailable.

When observed project evidence conflicts with a generic benchmark or memory,
prefer the project. When documentation versions conflict, match the installed
artifact and record the discrepancy.

## Success gate

Mark the slice successful only when all applicable conditions hold:

1. Functional evidence passes, including lifecycle and boundary cases.
2. The warmed target-player window meets the managed allocation budget across
   all relevant threads.
3. First-use, transition, pool growth, cancellation, and exception path results
   are either within their own budgets or explicitly reported.
4. Native allocation, retained memory, Addressables ownership, and CPU cost show
   no unacceptable regression.
5. Build, backend, device, versions, capacities, sample window, and limitations
   are recorded so the result is reproducible.

Reject or qualify the claim when only Editor evidence exists, only heap size was
observed, the profiler was unavailable, the buffer silently truncated, the pool
grew during measurement, another thread was omitted, or functional behavior was
not verified. Report the exact next check rather than converting uncertainty into
“GC-free.”
