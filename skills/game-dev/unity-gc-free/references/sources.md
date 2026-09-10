# Sources and freshness policy

Accessed 2026-08-02. These links are starting points, not timeless compatibility
claims. Resolve the exact installed Unity editor, package artifact, scripting
backend, compiler, target platform, and license again before recommending a
dependency.

## Authority order

Use evidence in this order:

1. Observed target-player captures, project manifests/locks, source, tests, and
   accepted project constraints.
2. Version-matched Unity or package documentation.
3. The exact upstream release/tag manifest, changelog, source, tests, and license.
4. A project-authored benchmark, labeled as such and reproduced in the target
   workload. It is a hypothesis, not independent proof or a universal ranking.
5. Explicitly labeled inference.

Technical claims in this skill use primary sources. Do not upgrade a README
headline, an Editor capture, a synthetic benchmark, or remembered folklore into
proof of allocation behavior.

## Unity managed-memory and measurement sources

- Managed memory model:
  <https://docs.unity3d.com/Manual/performance-managed-memory-introduction.html>
- Garbage collection:
  <https://docs.unity3d.com/Manual/performance-garbage-collector.html>
- Incremental garbage collection:
  <https://docs.unity3d.com/Manual/performance-incremental-garbage-collection.html>
- Track garbage collection and `GC.Alloc`:
  <https://docs.unity3d.com/Manual/performance-track-garbage-collection.html>
- Reference types, strings, closures, boxing, and `params`:
  <https://docs.unity3d.com/Manual/performance-reference-types.html>
- Reusable objects and collections:
  <https://docs.unity3d.com/Manual/performance-reusable-code.html>
- Array-return and caller-buffer guidance:
  <https://docs.unity3d.com/Manual/performance-optimizing-arrays.html>
- `ProfilerRecorder`:
  <https://docs.unity3d.com/ScriptReference/Unity.Profiling.ProfilerRecorder.html>
- Unity 6 profiler counters:
  <https://docs.unity3d.com/6000.0/Documentation/Manual/profiler-counters-reference.html>
- Performance Testing package:
  <https://docs.unity3d.com/Packages/com.unity.test-framework.performance@latest>

## Unity built-in alternatives and memory domains

- `UnityEngine.Pool.ObjectPool<T>`:
  <https://docs.unity3d.com/6000.0/Documentation/ScriptReference/Pool.ObjectPool_1.html>
- Unmanaged memory and allocator lifetimes:
  <https://docs.unity3d.com/Manual/performance-unmanaged-memory.html>
- NativeContainer job safety:
  <https://docs.unity3d.com/6000.0/Documentation/Manual/job-system-native-container.html>
- Burst compilation boundary:
  <https://docs.unity3d.com/Manual/script-compilation-burst.html>
- Physics NonAlloc query guidance:
  <https://docs.unity3d.com/6000.0/Documentation/Manual/physics-optimization-raycasts-queries.html>
- `Collision.GetContacts` caller-buffer overloads:
  <https://docs.unity3d.com/ScriptReference/Collision.GetContacts.html>
- Pooled Unity `Awaitable` and its single-await rule:
  <https://docs.unity3d.com/ScriptReference/Awaitable.html>
- Awaitable continuation and threading semantics:
  <https://docs.unity3d.com/Manual/async-awaitable-introduction.html>
- Addressables 2.7 asset and bundle lifetime:
  <https://docs.unity3d.com/Packages/com.unity.addressables@2.7/manual/memory-assets.html>

## Upstream library evidence

- ZLinq repository, license, and Unity package manifest:
  <https://github.com/Cysharp/ZLinq>
  <https://github.com/Cysharp/ZLinq/blob/master/LICENSE>
  <https://raw.githubusercontent.com/Cysharp/ZLinq/master/src/ZLinq.Unity/Assets/ZLinq.Unity/package.json>
- UniTask README, releases, and license:
  <https://raw.githubusercontent.com/Cysharp/UniTask/master/README.md>
  <https://github.com/Cysharp/UniTask/releases>
  <https://github.com/Cysharp/UniTask/blob/master/LICENSE>
- PrimeTween README, changelog, package manifest, and license:
  <https://raw.githubusercontent.com/KyryloKuzyk/PrimeTween/main/README.md>
  <https://raw.githubusercontent.com/KyryloKuzyk/PrimeTween/main/changelog.md>
  <https://raw.githubusercontent.com/KyryloKuzyk/PrimeTween/main/Packages/com.kyrylokuzyk.primetween/package.json>
  <https://raw.githubusercontent.com/KyryloKuzyk/PrimeTween/main/LICENSE>
- ZString repository and license:
  <https://github.com/Cysharp/ZString>
  <https://github.com/Cysharp/ZString/blob/master/LICENSE>
- MemoryPack repository, Unity manifest, releases, and license:
  <https://github.com/Cysharp/MemoryPack>
  <https://raw.githubusercontent.com/Cysharp/MemoryPack/master/src/MemoryPack.Unity/Assets/MemoryPack.Unity/package.json>
  <https://github.com/Cysharp/MemoryPack/releases>
  <https://github.com/Cysharp/MemoryPack/blob/master/LICENSE>
- MessagePack-CSharp repository, Unity manifest, releases, and license:
  <https://github.com/MessagePack-CSharp/MessagePack-CSharp>
  <https://raw.githubusercontent.com/MessagePack-CSharp/MessagePack-CSharp/master/src/MessagePack.UnityClient/Assets/Scripts/MessagePack/package.json>
  <https://github.com/MessagePack-CSharp/MessagePack-CSharp/releases>
  <https://github.com/MessagePack-CSharp/MessagePack-CSharp/blob/master/LICENSE>
- R3 README, releases, and license:
  <https://raw.githubusercontent.com/Cysharp/R3/master/README.md>
  <https://github.com/Cysharp/R3/releases>
  <https://github.com/Cysharp/R3/blob/master/LICENSE>
- ObservableCollections repository, releases, and license:
  <https://github.com/Cysharp/ObservableCollections>
  <https://github.com/Cysharp/ObservableCollections/releases>
  <https://github.com/Cysharp/ObservableCollections/blob/master/LICENSE>
- .NET `ArrayPool<T>` ownership API:
  <https://learn.microsoft.com/dotnet/api/system.buffers.arraypool-1>
- Collections.Pooled package and repository maintenance evidence:
  <https://www.nuget.org/packages/Collections.Pooled>
  <https://github.com/jtmueller/Collections.Pooled>

## Known conflicts and qualifications

- PrimeTween is **not MIT**. Its license restricts source redistribution and
  repackaging; legal/project acceptance is required. Its README examples,
  changelog, manifest, and distribution channel can expose different version
  strings, so pin and inspect the artifact actually installed.
- MessagePack-CSharp has had a **version conflict** between conservative Unity
  or IL2CPP support described in its README and the minimum declared by its
  package manifest. Treat the installed release plus a target AOT build as the
  deciding evidence.
- Documentation URLs containing `current` or `latest` can move. Resolve them to
  the installed editor/package version whenever exact semantics matter.
- Collections.Pooled has old published-package evidence. Its maintenance status,
  framework fit, license, and target-player behavior require renewed evaluation;
  it is not a default recommendation.
- Upstream allocation numbers are author measurements. Repeat them as a
  project-authored benchmark for the real workload and label the result.

## Refresh when

Refresh this evidence when Unity, the scripting backend, compiler, target
platform, package lock, dependency version, license, or upstream maintenance
status changes; when a source URL no longer describes the installed artifact;
or when the workload/capacity/lifecycle contract changes. Re-run functional and
allocation measurements after every such change.
