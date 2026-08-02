# Unity low-allocation dependency decision

## Conclusion

Adopt a **minimal-dependency, hybrid strategy**. Do not replace every LINQ, coroutine, and DOTween call in one migration. First make the three hot paths allocation-free with code that is already compatible with Unity 2022.3.12f1, IL2CPP, Android, and WebGL:

1. Replace the inventory query with a deterministic imperative loop writing to a reusable, capacity-warmed buffer. Keep the original filter, ordering, and result ownership contract. Use ZLinq only as an opt-in pilot after its exact package version, API surface, WebGL build, and IL2CPP stripping/AOT behavior are accepted.
2. Replace the 200 independently restarted cooldown coroutines with one capacity-warmed scheduler/direct state machine (arrays or structs plus generation/version numbers). It must model the coroutine's synchronous first step, scaled/unscaled wait behavior, frame quantization, and cancellation boundary. Use UniTask only where the state machine is genuinely clearer and its cancellation/continuation allocations have passed device tests.
3. Keep DOTween initially, but remove captured completion lambdas (static callbacks, IDs, or a receiver dispatch table) and configure explicit overwrite/sequence/completion behavior. Pilot PrimeTween on one representative UI flow only if it preserves those semantics and proves a target-player win.

This leaves no new runtime dependency on the critical path unless measured evidence justifies it. A package may be added independently, with an exact pinned version and a reversible feature flag.

## Decision matrix

| Option | Inventory query | NPC cooldowns | Combat tweens | WebGL / IL2CPP-AOT fit | Semantic and operational risk | Decision |
| --- | --- | --- | --- | --- | --- | --- |
| Existing code unchanged | Retains LINQ and `ToArray` allocations | Retains restart allocations | Retains closure allocations | Known compatibility | Lowest migration risk, but fails the measured allocation objective | Reject as final state; keep as rollback baseline |
| Imperative loops + reusable managed buffer | Usually lowest and predictable; preserves source order explicitly | Not applicable | Not applicable | Built into Unity/C# profile; no package/linker risk | Buffer reuse is safe only when callers do not retain or mutate a later result; otherwise preserve the old ownership contract | **Baseline choice** |
| ZLinq | Potentially low allocation, but version/API/runtime dependent; query ordering must be tested | Not applicable | Not applicable | Must prove Unity 2022.3 compiler profile, WebGL IL2CPP build, generic AOT/linking, and browser behavior | Hidden iterator/fallback paths, unsupported APIs, package provenance/license, and semantic differences (deferred execution, nulls, ordering) | Pilot only; not a blanket replacement |
| Coroutine rewrite with direct scheduler/state machine | Not applicable | Lowest steady-state allocation when capacity is fixed; restart is a generation update rather than a new enumerator | Not applicable | Main-thread managed code has no thread dependency; straightforward for WebGL/IL2CPP | Highest semantic risk: first-step timing, cancellation, time scale, and frame boundaries must be specified and tested | **Preferred NPC implementation** |
| UniTask | Not applicable | Can reduce iterator allocations, but async state machines, cancellation registrations, and captured continuations may still allocate | Not applicable | Generally usable on IL2CPP/WebGL when configured for the supported player profile, but every await/cancellation path needs AOT and browser verification | Scheduler/cancellation timing can differ from coroutines; package and linker configuration become release dependencies | Fallback for complex flows, not the default for 200 simple timers |
| Unity Awaitable | Not applicable | Attractive only where the exact engine version exposes and supports the required API | Not applicable | Unity 2022.3 availability and behavior must be confirmed; do not assume APIs documented for newer Unity releases are present | Engine-version coupling and changed continuation semantics; migration would add uncertainty | Do not select as baseline; revisit only after an engine/API proof |
| Keep DOTween, remove captures | Not applicable | Not applicable | Often removes the observed closure allocation while retaining tuned sequence/overwrite behavior | Existing package is already in the project; still verify IL2CPP stripping and WebGL behavior | Lowest tween semantic risk; pooling/recyclability can change lifecycle if enabled carelessly | **Baseline tween choice** |
| PrimeTween | Not applicable | Not applicable | May lower setup/runtime allocations, but sequence/overwrite/completion mapping is not one-to-one by assumption | Must verify exact package release, Unity 2022.3 support, IL2CPP AOT, WebGL browser builds, and license | Migration can change update order, cancellation, overwrite, or completion-on-kill behavior | Pilot only after tests and provenance/license acceptance |

## Staged recommendation

### Stage 0: establish contracts and rollback

- Capture behavior tests before editing: inventory result order and duplicate/null handling; cooldown first-step timing, restart and cancellation timing, scaled versus unscaled time, and completion side effects; tween sequence ordering, overwrite rules, kill/cancel behavior, and whether completion runs once or on replacement.
- Put each path behind a small feature flag or strategy interface. Retain the current implementation as an immediate rollback path. Do not change all call sites until the replacement has passed the contract tests.
- Record package provenance (repository/registry URL, exact version, commit or package hash, transitive dependencies) and obtain explicit license/security acceptance. Pin the accepted version; do not float to “latest.”

### Stage 1: remove measured allocations without adding packages

- Inventory: use an explicit ordered loop and a reusable buffer whose capacity is warmed to the largest expected inventory. If a fresh array is part of the public contract, copy only at the ownership boundary; otherwise document that the returned view is transient and never retained. Verify zero growth after warm-up.
- NPCs: use a single update pass over a fixed-capacity table of active cooldowns. On restart, write the new deadline and increment a generation/version so the prior schedule cannot fire. Execute the coroutine's pre-first-yield work at the same call site and preserve cancellation at the same frame/call boundary. Match `WaitForSeconds`/`WaitForSecondsRealtime` semantics deliberately.
- Tweens: keep DOTween and replace captured lambdas with static callbacks plus an ID/receiver lookup or an existing component method. Preserve sequence construction, overwrite mode, update type, and completion-once behavior. Do not enable recyclable pooling until lifecycle tests cover kill/reuse races.

### Stage 2: targeted package pilots

- ZLinq pilot: one inventory query behind the strategy flag. Build both Android IL2CPP and WebGL release players, run ordering/ownership tests, and inspect generated code/linker warnings. Keep the imperative loop if ZLinq is not strictly better on the target player.
- UniTask pilot: one representative cooldown flow only if direct scheduling cannot express required composition. Avoid per-restart `CancellationTokenSource` creation; use a bounded token/generation design and test every cancellation path for allocations and timing.
- PrimeTween pilot: one combat UI sequence. Explicitly map overwrite, sequence nesting, delay/update mode, cancellation/kill, and completion callback behavior. Compare against the DOTween baseline under repeated create/overwrite/complete cycles.

### Stage 3: ship decision and rollback

Promote a pilot only when correctness tests pass and target-player evidence shows a meaningful reduction in GC and frame cost without unacceptable binary size, startup, or memory regressions. Keep the feature flag through at least one release candidate; reverting a package or strategy must be a one-change configuration switch (and package lock rollback), not a code scramble.

## Capacity warm-up and evidence plan

Warm a representative scene before measuring: maximum expected inventory size plus headroom, all 200 NPC cooldown slots active with repeated restarts, and the largest combat UI tween sequences with overwrite/kill/restart cycles. Run several frames after warm-up and assert that capacities do not grow. Measure Development and Release IL2CPP players separately, then repeat with Android hardware tiers (low/mid/high) and WebGL in supported browsers. Collect Unity Profiler `GC.Alloc` per frame, managed/native memory snapshots, frame-time percentiles, startup/build size, and allocation call stacks where available. Repeat cold start and steady state; a headline benchmark or editor result is insufficient evidence.

For correctness, compare old and new strategies in a deterministic harness over randomized inventory contents, cooldown restart/cancel schedules, and tween overwrite sequences. Pay special attention to the frame in which the first cooldown step executes, cancellation immediately before/after a yield, and whether a replaced tween invokes completion. Treat any difference as a migration blocker until intentionally specified.

## Risks and gates

- Unity 2022.3's C#/.NET profile and WebGL restrictions can exclude a package API even when it works in a newer Unity release. Compile and run both player targets before acceptance.
- IL2CPP generic/AOT stripping can hide failures until a non-editor build. Preserve required generic types or link metadata only when a concrete build demonstrates the need; inspect build/linker output.
- Reusable buffers and schedulers can introduce stale data, aliasing, or capacity spikes. Add bounds, clear only the used range, and test callers that retain results.
- Async packages may move continuation/cancellation timing relative to coroutines and can allocate through registrations or closures. Instrument restart-heavy paths rather than trusting struct-return marketing claims.
- Tween pooling/replacement can alter callback cardinality or allow callbacks from a reused instance. Test kill, overwrite, completion, and object-disable/destroy races.
- Package provenance, transitive licenses, maintenance status, and source availability are release gates, not post-migration paperwork.

## Verification

The recommendation is complete when: (a) the three Stage 1 paths have contract tests and a reversible implementation design, (b) warm-up plus target-player runs show no unexpected steady-state allocations and quantify any remaining ones, (c) Android IL2CPP and WebGL release builds pass, and (d) any ZLinq/UniTask/PrimeTween pilot has an accepted exact version, provenance/license record, and measured win. No command, profiler session, or package compatibility result is assumed to have been run for this recommendation.

## Open questions

- Does the inventory result escape the frame or get mutated by callers, requiring a copy rather than a reusable view?
- Are cooldown waits scaled, unscaled, or mixed, and what exact first-step/cancel timing is relied upon by gameplay code?
- Which DOTween overwrite modes, sequence nesting, update types, and completion-on-kill behaviors are contractual?
- What package registry/source and license policy will accept ZLinq, UniTask, or PrimeTween, and which exact versions are candidates?
- Which Android device tiers and WebGL browsers define the target-player acceptance matrix?

## Next action

Implement Stage 0 contracts and Stage 1 behind feature flags, then run the warm-up and target-player evidence plan. Only after those results should the team decide whether a narrowly scoped ZLinq, UniTask, or PrimeTween pilot is justified.

