# Conclusion

Treat this as a confirmed recurring managed-allocation problem in the reported warmed Development Player workload, but not yet as a source-level attribution or a project-wide “GC-free” result. The capture places approximately 1.6 KB of `GC.Alloc` on the main thread inside the `CombatHud.Refresh` call path every refresh; at 60 Hz that is roughly 96 KB per second, derived from the reported rate. It does **not** establish how those bytes are divided among the LINQ query, sorting/materialization, three labels, and logging.

Use a bounded attribution capture first, then make one reversible vertical slice: replace only `Where`/`OrderBy`/`ToList` with a direct filter into component-owned, pre-sized scratch storage and a stable, allocation-measured sort. Leave label construction and logging behavior unchanged during that slice so its allocation delta is attributable. Do not introduce ZLinq, ZString, an array pool, native containers, or a general-purpose pool for this 80-item local query.

A logging change is also justified, but as a separate policy slice: a 60 Hz diagnostic message should be explicitly enabled and its entire call, including argument construction, guarded; the production acceptance path should log on change, be rate-limited, or compile the diagnostic call out. Text-specific work should wait for allocation attribution and inspection of the actual text component and formatting requirements.

This is a diagnosis and implementation recommendation only. No source change, test, player build, Profiler capture, or memory comparison is claimed here.

# Evidence

## Observed as reported

The following are **user-stated observations from the supplied capture description**, not independently reproduced artifacts:

- Unity `6.0.15f1`, Windows player, IL2CPP, Development Player, target-like hardware.
- Approximately `1.6 KB GC.Alloc` occurs on the main thread during every `CombatHud.Refresh` at 60 Hz.
- The allocation call stack reaches `CombatHud.Refresh`.
- One refresh filters 80 status effects through `System.Linq.Where`, `OrderBy`, and `ToList`, constructs three interpolated labels, and calls `Debug.LogFormat` once.
- The reported sample starts after five seconds in which caches are populated. This makes a steady-state source more likely, but “caches populated” does not prove that every reusable collection, formatter, logger, generic/static path, or UI path had reached its final capacity.

The approximate 96 KB/s rate is **derived** from `1.6 KB × 60`; it is not a separately measured counter. It describes allocation traffic, not heap growth, retained memory, GC pause duration, or native memory.

## Still unknown

- Allocation bytes and allocation count for each of the query, ordering, `ToList`, individual labels, and `Debug.LogFormat` boundaries.
- The leaf allocation call stacks and whether the profiler attributed one large allocation or many small ones.
- Exact predicate, order key, comparer, tie behavior, key type, key-selector side effects, null/default behavior, and whether downstream code retains the materialized list.
- Text component/API, label inputs, culture/localization/rich-text rules, and whether label values actually change at 60 Hz.
- Whether the log is a required external diagnostic contract, its arguments and boxing behavior, and the production logging configuration.
- Expected and worst-case status-effect count beyond the reported 80.
- Worker/background-thread allocation during the workload. UI work is likely main-thread-affine, but that does not substitute for inspecting all relevant threads.
- Release Player allocation behavior, code-optimization settings, stripping differences, and production logging behavior.
- CPU duration before the change, so fewer managed bytes cannot yet be called faster.
- Retained-reference/high-water effects of reusable storage, native-memory behavior, first-use cost, exception paths, and collection-pause impact.
- Exact project package lock, compiler settings, source, tests, and any package provenance/license evidence. Therefore no third-party compatibility claim is established.

# Allocation contract

Use the following proposed contract for the bounded work. Record any product-approved change before implementation rather than silently weakening it.

| Field | Contract |
| --- | --- |
| Workload | One `CombatHud.Refresh` at 60 Hz with exactly 80 representative status effects, including the existing predicate, stable ordering, HUD consumption, and three label updates. The production acceptance path has combat-refresh diagnostics disabled by the explicit logging policy. |
| Environment | Unity `6.0.15f1`; Windows; IL2CPP; target-like hardware. Diagnose in a Development Player with allocation call stacks, then repeat acceptance in the production-equivalent Release Player. Record code-optimization, stripping, quality/frame settings, scene/data seed, and package lock. |
| Warm-up | Run the reported five-second warm-up, exercise every normal predicate/order/label branch, and prepare scratch capacity for at least 80 entries before measurement. Capture the first five seconds separately; do not use warm-up to hide growth that also occurs in normal play. |
| Capacity | Current steady-state input is 80. The query scratch owner reserves at least 80 entries before the acceptance window. If a later input exceeds prepared capacity, preserve every result by growing rather than truncating, record a capacity miss, and classify that frame as a separately reported transition-budget failure. Establish the real peak and margin before broad rollout. |
| Window | A stable marker around `CombatHud.Refresh` and child markers around query, labels, and diagnostics; 600 consecutive refreshes (10 seconds at 60 Hz) after warm-up, repeated at least three times under identical data/configuration. Capture byte total and allocation count, and inspect all relevant threads. |
| Overall managed budget | `0 B` and `0 managed allocation events` attributable to the warmed production-path `CombatHud.Refresh` over the window across all relevant threads. First-use, capacity growth, diagnostic-enabled logging, exceptions, and transitions are separate named paths with separately reported results, not hidden in the steady-state claim. |
| First-slice budget | `0 B` and `0 managed allocation events` inside the query/filter/order marker after capacity preparation. The whole refresh is expected to remain above zero if labels or logging still allocate; report that residual instead of calling the method GC-free. |
| Preserved behavior | Same filtered identities/count, same order and stable tie order, same comparer/culture/null/default behavior, same key/predicate evaluation expectations, same refresh timing and main-thread affinity, same three visible strings, and no truncation. During the query slice, logging content/frequency and exception behavior remain unchanged. |
| Other budgets | Record Refresh and query CPU duration before/after on the same hardware; until a project threshold exists, any repeatable CPU regression is a blocker rather than an accepted trade. Cap retained scratch capacity at the measured peak plus approved margin, clear references on lifecycle boundaries, and confirm no unexpected retained/native-memory increase. |
| Baseline | The supplied Development Player report is enough to prioritize diagnosis, but not enough for source-level acceptance because allocation count, leaf stacks, Release behavior, worker threads, CPU, and retained memory are missing. Reproduce and save the exact baseline before editing. |

If product requirements insist on a formatted log every refresh, that diagnostic path conflicts with the proposed zero-byte production contract unless the actual logger and arguments are proven to meet it. Give that path an explicit nonzero budget or choose a different logging contract; do not silently exclude a required effect.

# Bounded diagnosis

1. Add stable profiler markers around the entire refresh and three subregions: query/filter/order/materialization, label creation/application, and diagnostic logging. Create any recorder outside the measured window and dispose it after capture. Prefer allocation call stacks over Deep Profiling if Deep Profiling distorts the workload.
2. Reproduce the supplied Development Player workload with the same scene/data, 80 effects, 60 Hz, five-second warm-up, target-like hardware, and logging configuration. Capture 600 refreshes for at least three runs. Save bytes, allocation count, leaf call stacks, and marker CPU time.
3. Inspect every relevant thread in the capture. Do not infer worker-thread zero allocation from a main-thread-only sample.
4. If IL2CPP stacks do not separate the contributors, run explicitly labeled diagnostic A/B captures with logging enabled versus guarded-off and with label application isolated. These are attribution experiments, not interchangeable acceptance baselines.
5. Record the initial five seconds separately to characterize cache/static initialization and capacity growth. Verify that the later window contains no list or logger capacity growth.
6. Establish a production-equivalent Release Player baseline before final acceptance. Capture the exact build settings because Development instrumentation, logging, stripping, and optimization can change behavior.
7. Record a CPU baseline before refactoring and a retained-memory/high-water baseline before adding reusable storage. Memory Profiler evidence answers retained/native ownership questions; it does not replace `GC.Alloc` call stacks.

The decision gate for the first code slice is a repeated leaf stack or submarker showing that the LINQ/order/materialization region contributes recurring allocation. If it does not, do not refactor that query merely because LINQ appears in the source; take the first slice at the confirmed label or logging boundary instead.

# Decision

## Selected: direct loop plus component-owned reusable storage

For a confirmed local query over 80 effects, the smallest compatible mechanism is direct project code:

- Give `CombatHud` one private scratch collection, created once and reserved for the measured capacity outside the acceptance window. Keep it main-thread-owned and do not return or expose it as a stable result.
- At each refresh, clear the logical contents, loop over the source collection directly, apply the existing predicate, compute the existing order key once for each passing effect, and append a scratch entry containing the effect, key, and original source index.
- Sort with a cached, non-capturing comparer that uses the exact existing key comparer and then the original source index as the tie-breaker. `OrderBy` is stable; replacing it with an ordinary `List<T>.Sort` on the key alone could reorder equal keys and is not behavior-preserving. Adding the source index makes the output order explicit. Verify the exact IL2CPP allocation behavior rather than assuming the sort is free.
- Render/process directly from the scratch entries within `Refresh`; remove `ToList` and do not create a snapshot. If a downstream consumer retains the old list beyond the call, stop and define ownership before using mutable scratch storage.
- Preserve all results on capacity overflow. Allow a controlled growth/telemetry path outside the zero-allocation contract rather than silently truncating status effects.

Before this replacement, lock the predicate/key/comparer as pure or test their side effects and exception timing. A different sorting algorithm can invoke comparisons in a different order; a stateful or inconsistent comparer makes mechanical substitution unsafe.

## Rejected for the first slice

- **ZLinq:** not justified for one small measured pipeline when a direct loop is local and clear. Value-enumerable composition may remove iterator-chain allocation, but captured state, ordering storage, and terminal materialization still need explicit ownership. Revisit only if several measured hot pipelines need composability and the team first pins and validates the exact package coordinate/tag, compiler minimum, license, Unity 6/IL2CPP build, AOT/stripping behavior, and pooled-result lifecycle.
- **General pool or `ArrayPool<T>`:** unnecessary lifetime complexity for one component-owned, fixed-small scratch list. Renting introduces return-once, exceptional-exit, retained-reference, larger-than-requested-array, and use-after-return obligations without a demonstrated benefit. Revisit only if measurements show variable, much larger transient arrays whose ownership cannot be component-local.
- **Native containers/Jobs/Burst:** not justified for 80 main-thread HUD items. It would move ownership into native memory and add allocator/disposal/job-safety contracts without evidence that scheduling or scale requires it.
- **Update-only-on-change as the first slice:** potentially the highest-leverage design because status effects and labels may change far less often than 60 Hz, but it changes invalidation and timing semantics. Revisit when every mutation source exposes a trustworthy version/dirty signal and tests prove update timing, reentrancy, enable/disable, and scene-lifecycle behavior.

## Deferred text decision

The three interpolated labels are credible recurring allocation candidates, but their contribution and consumer are unknown. Do not add text tooling in the query slice.

If attribution points to labels, first stop rebuilding unchanged labels. Then inspect the installed UI/text API: use a version-matched direct numeric/format writer or supported TextMeshPro setter when it preserves exact culture, rounding, localization, rich-text escaping, fallback-font, and layout behavior. A pooled builder such as ZString can remove intermediate formatting, but producing a final `string` still allocates; it is justified only when the actual sink can consume the scoped buffer directly and exact package provenance, compatibility, license, disposal, and IL2CPP behavior are approved. Keep each label as its own later slice so its residual allocation is measurable.

## Logging decision

A 60 Hz `Debug.LogFormat` call is not an appropriate default production-path diagnostic. It is a known allocation-risk boundary because formatting, `params` argument arrays, value-type boxing, and stack handling may occur; the supplied capture does not quantify which of these applies.

Make logging a separate reversible slice after the query comparison:

- Put the **entire call and its argument evaluation** behind an explicit diagnostic guard or compile-time removal mechanism; merely filtering the emitted log downstream may still pay argument construction cost.
- Prefer an on-change or rate-limited diagnostic with the same useful fields. Keep an opt-in full-frequency mode only for deliberate diagnosis and measure it under its own budget.
- Do not replace `LogFormat` with interpolation and assume improvement; profile the actual build/logger configuration.
- Test that required diagnostic content remains correct when enabled and that Release policy matches the allocation contract.

# Ownership and lifecycle

- **Owner:** the `CombatHud` component (or its existing view-model owner if that is the only object with the correct lifecycle).
- **Access:** main thread only, during `Refresh`; no sharing with jobs, callbacks, or delayed consumers.
- **Capacity:** reserve the current 80-entry workload before measurement, then size from an observed peak plus approved margin. Track capacity misses/growth; do not claim steady state for a window that grew.
- **Reset:** clear logical entries at the start/end boundary chosen by the component. Ensure old object references and keys cannot retain obsolete status-effect graphs across disable or scene changes.
- **Overflow:** preserve behavior by growing and report the transition; never truncate silently. If growth is unacceptable, establish a higher fixed project bound before enforcing it.
- **Teardown:** clear references and detach the scratch storage from external consumers on disable/destroy/scene teardown as appropriate. A normal managed list needs no pool return or native disposal.
- **Result lifetime:** scratch entries are valid only within the refresh. Any consumer that needs a persistent snapshot requires an explicit separate ownership/allocation contract.

# Implementation slice

Keep the slice narrow and reversible:

1. Add functional characterization tests around the current query output before changing it.
2. Preserve a reproducible allocation-red baseline for the query marker under the contract above.
3. Introduce the private scratch-entry type, component-owned prepared collection, and cached comparer.
4. Replace only `Where`/`OrderBy`/`ToList` with fill, stable sort, and in-call consumption. Do not change labels, refresh frequency, or logging in this commit/slice.
5. Run functional evidence first, then the query allocation comparison. Report whole-refresh residual allocation by leaf source.
6. Roll back the slice if ordering, exception behavior, CPU, retained references, IL2CPP build behavior, or query allocation does not meet the contract. The old LINQ body is the narrow rollback seam.

# Verification

## Functional verification to perform

- Compare old and new ordered effect identities, counts, and rendered rows for empty input, one item, all filtered out, all 80 included, mixed inclusion, duplicate keys, already sorted, reverse sorted, and randomized representative sets.
- Include equal-key cases and assert original source order is retained. Use the exact existing comparer, including descending/secondary ordering if present, null/default values, culture, and any custom equality behavior.
- Assert predicate and key evaluation counts where they are observable requirements. Characterize exception propagation before promising identical exception behavior.
- Verify three label strings remain exactly unchanged during the query slice, including localization/culture/rounding/rich text, and verify the existing log content/frequency remains unchanged.
- Exercise repeated refreshes, source mutation between refreshes, enable/disable, scene teardown, and a consumer-lifetime check proving scratch data is not retained after the call.
- Force 81 or more inputs (or the project’s real next boundary) and prove there is no truncation, stale entry, or duplicate; record that capacity growth is a transition allocation until it is prewarmed.
- Compile and run the affected tests in the supported Unity configuration, then build Windows IL2CPP Development and Release players to catch AOT/stripping/compiler differences.

## Allocation and cost verification to perform

- First reproduce the allocation-red Development Player baseline with the same workload and marker hierarchy. Record bytes **and count**, leaf stacks, build settings, hardware, run count, and CPU timing.
- After capacity preparation, measure 600 refreshes for at least three identical runs. The first-slice query marker must report `0 B / 0 allocations`; do not require the whole refresh to be zero until label/log slices meet their own contracts.
- Compare before/after whole-refresh totals to show the exact residual contribution rather than estimating removed bytes from source inspection.
- Repeat the acceptance window in a production-equivalent Windows IL2CPP Release Player and inspect all relevant threads. A zero main-thread query marker alone does not prove global or worker-thread zero allocation.
- Measure the initial five seconds, first capacity overflow, diagnostics-enabled path, and exception path separately. Do not average these into warmed steady state or omit them.
- Compare query and refresh CPU distributions on the same target-like hardware. The direct stable sort may trade allocations for comparisons/copies, so no CPU improvement should be claimed without results.
- Compare scratch-list high-water capacity and retained references across refresh, disable, and scene teardown. Inspect native/retained memory separately; the change is not a native-memory optimization.
- Keep recorder creation, test delegates, assertions, result formatting, and profiler setup outside the measured body so the verification harness does not become the allocation source.

No PASS or “GC-free” label is warranted until these functional and allocation checks produce matching target-player evidence.

# Risks

- A naive `List.Sort` replacement can violate LINQ `OrderBy` stability for equal keys.
- Key/predicate/comparer side effects or exception timing can differ when the implementation and sorting algorithm change.
- The old `ToList` may be an ownership boundary; reusing mutable storage is unsafe if any consumer retains it.
- Prepared storage removes recurring growth only up to its observed capacity and retains that capacity/references for the owner’s lifetime.
- A stable direct sort can increase CPU even while reducing managed bytes; no CPU baseline currently bounds that trade.
- Disabling or sampling logging can reduce diagnostic visibility unless its policy and opt-in path are explicit.
- Text-specific substitution can change culture, rounding, localization, rich text, layout rebuilds, or final-string allocation.
- Development Player evidence can differ from Release because of instrumentation, logging, optimization, and stripping.
- The current main-thread report omits worker/background activity and cannot establish an across-thread zero-allocation contract.
- A retained-memory snapshot/high-water comparison is absent, so reusable-storage retention has not been bounded yet.

# Open questions

1. What are the exact filter predicate, order key(s), comparer/direction, tie semantics, and downstream lifetime of the `ToList` result?
2. Is 80 a hard maximum, a representative value, or only the current capture? What peak and overflow behavior are product-correct?
3. Which UI/text component consumes the three labels, what values change each frame, and which culture/localization/rich-text rules are contractual?
4. Is the 60 Hz log required in any shipping configuration, and what content/frequency must remain available when diagnostics are enabled?
5. What Release build settings, production device class, CPU non-regression threshold, and retained-memory cap should gate acceptance?
6. Can status/label inputs provide a complete version or dirty signal so a later update-on-change slice can safely eliminate unnecessary refresh work?

# Next action

Reproduce one saved Development Player baseline under the proposed marker hierarchy and contract, with allocation call stacks, allocation count, CPU timing, all relevant threads, and separate query/label/log attribution. If the query region repeatedly allocates, implement only the direct-loop/reused-stable-sort slice above, verify its functional behavior first, then require `0 B / 0 allocations` in that query marker and report the remaining whole-refresh allocation. Follow with independent logging and label slices only where the new leaf evidence points.
