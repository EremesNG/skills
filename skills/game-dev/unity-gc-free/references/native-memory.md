# Native memory, Jobs, and Burst

`NativeArray<T>`, `NativeList<T>`, and other `NativeContainer` types place their
storage outside the managed heap. This can remove a managed allocation and make
data job/Burst-compatible, but it creates a native allocation with allocator,
ownership, synchronization, and disposal costs. Report the domains separately.

## Choose native storage for the real problem

Good reasons include sharing blittable data with Jobs/Burst, avoiding a proven
managed hot-path allocation where a reusable native owner fits, or using a Unity
API that consumes/returns native views. Bad reasons include chasing “zero GC” in
cold setup, hiding an unbounded allocation elsewhere, or forcing an architectural
rewrite without CPU/memory evidence.

Prefer **local adoption**: a component/service may own a native buffer and use a
job without converting the project to Entities. Using Unity Collections, Jobs,
or Burst **does not require ECS** or DOTS-wide adoption.

For every container record element type, logical/capacity bounds, allocator,
creator/owner, aliases/views, readers/writers, scheduled dependencies, disposal
point, exceptional/shutdown path, and retained-native-memory budget.

## Allocator contract

- `Allocator.Temp` is for very short-lived work and must be disposed in the
  **same frame**; it is generally main-thread scoped by current Unity guidance.
- `Allocator.TempJob` may cross frames/jobs but must be disposed within **four frames**.
  Treat the warning as an ownership defect, not harmless noise.
- `Allocator.Persistent` supports longer lifetime and is comparatively costly;
  keep it under a bounded owner and dispose it explicitly.
- Installed Collections versions may expose allocator handles or rewindable
  allocators with additional rules. Use their version-matched contract rather
  than assuming the three labels cover every case.

Allocator choice is not a performance proof. Allocation/free still has CPU cost,
native fragmentation/retention is possible, and a missing dispose is a native
memory leak even when `GC.Alloc` remains zero.

## Creation, reuse, and disposal

Create or grow outside the steady-state sample when the workload contract says
capacity is prepared. Reuse by clearing logical length only when old values and
aliases cannot escape. A `NativeList<T>` can reallocate when capacity expands;
pre-size from observed peaks and record overflow behavior.

- Check `IsCreated` before disposal where multiple lifecycle paths can converge,
  but do not use it as a substitute for a single owner.
- Call `Dispose()` exactly once after all consumers are finished, ideally in a
  deterministic lifecycle/`finally` path for synchronous ownership.
- When jobs still use the container, schedule `Dispose(jobDependency)` if
  supported or `Complete()` the last job dependency before synchronous dispose.
- Disable/scene-unload/domain-reload/application-quit paths must converge on the
  same rule. Static native owners need explicit Editor reload handling.
- A copied container struct often refers to the same storage. Disposing one copy
  invalidates the others; copying is not ownership duplication.

## Aliases and views

Slices, reinterpretations, parallel writers, unsafe pointers, and arrays/views
returned by APIs can be an **alias** over another owner's memory. Record the
root allocation and invalidate every alias when its owner resizes, rewinds, or
disposes. Never retain a view beyond the documented lifetime of mesh data,
physics data, a temporary allocator, or a pool lease.

Treat `AsArray`, `GetSubArray`, `NativeSlice`, and unsafe pointers as borrowed
views unless version-matched documentation explicitly transfers ownership. Do
not dispose a borrowed alias as if it created the storage.

## Safety system and job dependency

Unity's AtomicSafetyHandle-based **safety system** detects many conflicting
reads/writes and lifetime errors in supported builds. Respect its exceptions:

- Pass every producer/consumer `JobHandle` through the declared job dependency
  chain. Combine dependencies when independent predecessors feed one consumer.
- A main-thread read/write must wait for the relevant handle to `Complete`.
- Use `[ReadOnly]`, parallel-writer APIs, and access restrictions only when the
  algorithm satisfies them; attributes do not synchronize incorrect access.
- Disabling safety restrictions or using unsafe containers moves proof to the
  project and can turn a clear exception into data corruption or a crash.
- Safety checks may differ between Editor/development/release. Verify functional
  correctness and native lifetime in the target configuration, not just GC.

## Burst boundary

Burst can compile compatible Jobs/static code over unmanaged data. It does not
make arbitrary managed code allocation-free and cannot freely use managed object
references, ordinary strings, virtual/reflection-heavy APIs, exceptions, or
unsupported runtime features.

Use blittable/unmanaged structs and supported containers. For bounded text or
diagnostics inside compatible code, evaluate `FixedString` types (for example
`FixedString64Bytes`) and fixed-capacity collections from the installed Unity
Collections version. A FixedString truncation/capacity rule is still required;
conversion to a managed final string allocates.

Compare Burst enabled/disabled behavior, compilation/fallback, floating-point
mode, platform support, job scheduling overhead, synchronization, and CPU cost.
For tiny workloads, direct main-thread reuse can be faster and simpler.

## Verification checklist

1. Functional tests cover bounds, overflow, aliases, scheduling order, exception/
   cancellation behavior, owner disable/destroy, scene unload, and shutdown.
2. Development checks report no safety violations, Temp/TempJob lifetime warning,
   undisposed allocation, use-after-dispose, or race.
3. The target-player allocation window distinguishes managed allocation from
   native allocation and proves the named `GC.Alloc` budget across relevant threads.
4. Native memory/retained capacity and allocation/free CPU cost remain inside
   separate budgets; profiler evidence shows no leak across repeated lifecycles.
5. The target backend/platform build (including IL2CPP/AOT when applicable)
   compiles and runs with the intended Burst/job path rather than an unreported
   fallback.
