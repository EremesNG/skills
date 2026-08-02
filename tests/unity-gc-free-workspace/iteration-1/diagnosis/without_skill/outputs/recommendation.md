# Recommendation

## conclusion

Treat the 1.6 KB as confirmed recurring main-thread churn, not yet as a proven single-source leak. The likely contributors in `CombatHud.Refresh` are the LINQ iterator/sort/list path, the three interpolated strings (or the UI setter behind them), and `Debug.LogFormat`'s formatted/`params` path. Make the first bounded slice a semantics-preserving direct refresh: filter with a loop into a capacity-80 list owned by the HUD, sort that list in place with a cached comparer (preserving `OrderBy`'s stable tie behavior), and gate the per-refresh log behind a disabled-by-default diagnostic flag. Keep label construction unchanged for this slice unless measurement isolates it; then use the text component's allocation-conscious API (for example, a TextMeshPro `SetText` overload) rather than introducing a new text package.

## evidence

- Observed: a Development Player on target-like Windows hardware reports 1.6 KB `GC.Alloc` on the main thread on every combat HUD refresh at 60 Hz, with the stack reaching `CombatHud.Refresh`.
- Observed code shape: 80 effects pass through `Where`/`OrderBy`/`ToList`; three interpolated labels are created; one `Debug.LogFormat` call runs per refresh.
- The sample starts after the first five seconds, when caches are populated, so this is consistent with steady-state per-refresh churn rather than cache warm-up alone.
- Still unknown: which child marker accounts for each byte; whether interpolation reaches a text setter that allocates; whether `LogFormat` is enabled/stripped in the intended build; sort-key ties and required ordering semantics; and whether the 1.6 KB is identical in a Release Player.
- There is no worker-thread capture, retained-memory comparison, or CPU baseline, so this evidence does not establish a leak, cross-thread allocation, or a performance regression.

## allocation contract

After an explicit warm-up, with one HUD refresh per frame on the main thread, the steady-state managed allocation delta for `CombatHud.Refresh` is **0 bytes per refresh** in the target configuration (Development for diagnosis and Release for acceptance). One-time setup allocations before the measurement window are allowed; recurring arrays, iterator objects, sort helpers, delegate creation, boxing, interpolated strings, and log formatting are not. Functional output—including filter membership, stable ordering, label text, and diagnostic behavior when enabled—must remain unchanged.

## first implementation slice

1. Add a HUD-owned scratch `List<StatusEffect>` with capacity for the 80-effect maximum and clear/add through an indexed loop. Sort it in place with a cached static comparer. Because LINQ `OrderBy` is stable, preserve input order for equal keys (a stable insertion sort for this small list, or an explicit original-index tie break, is acceptable).
2. Make the per-refresh `Debug.LogFormat` conditional on a diagnostic setting that is false in normal/release play. Ensure the call and its interpolated/`params` arguments are inside the branch, so the disabled path allocates nothing. Retain an opt-in equivalent for troubleshooting.
3. Do not add ZLinq in this slice. It adds a dependency and still requires proof that its path beats a simple bounded loop for 80 items under IL2CPP. Do not introduce text-specific tooling yet; first isolate label/UI-setter cost. If labels are the remaining allocation, switch to an allocation-conscious API already supplied by the current text component (e.g., TMP `SetText` with format arguments or a reusable buffer) and re-test.

## verification

- Functional: run a comparison test over representative 80-effect sets (zero/all matches, unsorted input, duplicate sort keys, long and empty labels) and assert the new filter/order/three label values equal the current behavior. Verify diagnostics are silent when disabled and equivalent when enabled.
- Allocation: capture a Development Player on target-like hardware with deep profiling off; warm up for at least five seconds, then record 300+ refreshes. Inspect the `CombatHud.Refresh` subtree and require no recurring `GC.Alloc` (and specifically no 1.6 KB/frame). Repeat in a Release Player. A temporary `ProfilerRecorder`/allocation counter may corroborate the capture, but the player profiler timeline is the source of attribution.
- Isolate causes with short A/B captures (loop only, labels only, logging only) if the zero-allocation contract is not met; keep CPU timing as a secondary check so sorting or text changes do not violate the 60 Hz budget.

## risks

- A non-stable replacement for `OrderBy` can change equal-key display order; test and enforce stability.
- Reused storage must not be exposed to code that retains it after refresh; copy only where ownership requires it.
- UI text APIs may allocate internally depending on component/version, so the loop/log change alone may not reach 0 B.
- Disabling logs can hide useful diagnostics; retain an explicit opt-in switch and avoid enabling it during allocation acceptance.
- Development instrumentation and logging can distort both allocations and CPU, hence Release confirmation is required.

## openQuestions

- Which text implementation (TMP, legacy UI, or custom) receives the labels, and does it offer a no-intermediate-string setter?
- What is the exact filter/sort key and are equal-key ties required to retain input order?
- Is the diagnostic log required in production, and can its flag be compile-time or runtime disabled there?
- Can a child capture or marker breakdown be obtained to attribute the 1.6 KB before changing label construction?

## nextAction

Implement only the reusable-loop, stable in-place ordering, and disabled-by-default logging gate. Add the functional equivalence cases and the post-warm-up Development/Release capture described above. Use the resulting marker breakdown to decide whether a text API change is warranted; defer ZLinq and broader refactoring until that evidence exists.
