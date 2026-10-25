# ECS and Data-Oriented Design
Evaluate ECS organization and data-layout changes against measured workloads, including integration costs; neither requires the other.

## When ECS Pays Off
- **Choose when:** Repeated bulk processing is measurably traversal/memory/dispatch-bound; component-set queries match real batches.
- **Simpler first:** Use engine components/nodes and batched arrays; move only a hot subset when an ECS prototype beats them.
- **Cost:** Include conversion, object/ECS synchronization, structural churn, scheduling, tooling, and debugging; external physics/rendering bottlenecks may not improve.
- **Contract:** Set baseline/target, authoritative-state ownership, and bridge boundaries before migration; compare equivalent outputs, tail latency, throughput, and memory.
- **Traps:** Ideal stationary benchmarks hide integration costs. Test real distributions and churn. ECS is not synonymous with [data-oriented design](#data-oriented-design-techniques).

## Core Concepts
- **Choose when:** Identities, data components, and query-driven systems express bulk work better than per-object callbacks.
- **Simpler first:** Keep object [Component](game-programming.md#component) composition until queries and data separation justify another runtime model.
- **Contract:** Identity is not an address: validate generations/world lifetime. Declare required/optional/excluded query data; scope shared resources and relationship ownership.
- **Traps:** Reused IDs can target new occupants; test despawn/reuse and asynchronous completion after world replacement. Relationship storage and reference stability vary by implementation.
- **Not:** ECS implies neither archetypes nor automatic parallelism; ordinary engine components need not be ECS.

## Storage Models
- **Choose when:** Query shapes and mutation rates justify choosing storage explicitly; measure rather than infer performance from model names.
- **Simpler first:** Use supported defaults; tune layouts/groups only after representative joins or churn miss the budget.
- **Contract:** Inspect relocation, pointer stability, and iteration order. Packed removal can move another element in either family.
- **Traps:** Many component combinations fragment archetypes; sparse-set joins add lookups. Frequently changing modes may be cheaper as values than add/remove markers. Benchmark payload size, selectivity, and composition churn.

| Model | Likely advantage | Main cost |
| --- | --- | --- |
| Archetype/table: component sets stored together | Streaming matching columns in stable populations | Set changes migrate data; small tables/chunks waste space |
| Sparse set: dense pools with entity mappings | Compact single-pool scans, independent mutations | Multi-component joins need membership/lookups or maintained groups |

## Structural Changes
- **Choose when:** Creation/destruction or component-set mutation can invalidate traversal, references, or concurrent work.
- **Simpler first:** Mutate directly only where supported; otherwise batch deferred commands at an explicit synchronization point.
- **Contract:** Define playback visibility/order, duplicate removals, modify-after-destroy, and stale-handle behavior. Finish readers/writers before playback; discard invalidatable references.
- **Cost:** Fewer barriers improve batching but delay visibility; deferred commands are not transactions or conflict resolution.
- **Traps:** Queued destruction still matches queries until playback. Use supported immediate logical filtering if necessary; test same-tick dependent systems and conflicting commands.

```text
iterate(query): recordStructuralCommands()
finishReadersAndWriters()
playbackCommandsInRequiredOrder()
runSystemsRequiringNewComposition()
```

## Scheduling and Change Detection
- **Choose when:** Disjoint bulk work can run concurrently, or unchanged inputs can skip expensive downstream work.
- **Simpler first:** Keep sequential phases/rebuilds until measured savings exceed dispatch/barrier/tracking costs.
- **Contract:** Declare component/resource access, semantic order, playback visibility, and external thread affinity; conflict-freedom is not gameplay order.
- **Not:** Change markers can track mutable access, ticks, or chunks, not value comparison; events preserve individual occurrences.
- **Traps:** Test equal-value writes, nested/external mutation, skipped observation windows, and cache invalidation under alternate legal schedules. Hidden globals escape scheduler guarantees.

```text
Perceive writes Observations; Decide reads Observations, writes Intent
Move reads Intent, writes Position
require Perceive before Decide before Move
require playback before consumers of structural changes
```

## Data-Oriented Design Techniques
- **Choose when:** Profiling identifies the transformation/access path, not merely a desire for contiguous arrays or ECS.
- **Simpler first:** Use a few arrays and loops; stop when they meet budget without new lifecycle/tooling machinery.
- **Contract:** Choose AoS/SoA from fields consumed together; split hot/cold data only if scans avoid cold fetches. Batch compatible work while budgeting latency, working set, and load balance.
- **Traps:** Pointer chasing, random relationship access, joins, and false sharing can defeat locality. Profile the whole path: conversion, synchronization, command playback, memory, and equivalent output checks.

## Implementations
Engine availability and versions live in the platform maps: [Unity](platforms/unity.md), [Unreal](platforms/unreal.md), [Godot](platforms/godot.md), [Roblox](platforms/roblox.md).
Standalone ECS libraries exist, including Flecs, EnTT, and Bevy ECS, with different storage models; compare the intended workload rather than treating availability as an adoption recommendation.
