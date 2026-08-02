# Low-allocation dependency decision

## Conclusion

Do not perform the proposed three-way substitution as a blanket rule. The
lowest-risk strategy for Unity 2022.3.12f1, IL2CPP, Android, and WebGL is a
selective, reversible migration:

1. Replace the inventory query with a direct, owner-controlled loop and a
   pre-sized result representation. Keep the existing ordering and eager
   materialization contract. Use ZLinq only as a measured, pinned alternative
   if the pipeline is sufficiently complex that the direct loop is materially
   less maintainable; ZLinq is not required to remove the `ToArray` result
   allocation.
2. Replace the 200 restartable cooldown coroutines with an explicit per-NPC
   state machine owned by the NPC system (deadline/remaining-time plus an active
   bit and generation). This is deterministic, WebGL-safe, and avoids coroutine,
   nested-enumerator, and restart churn. UniTask is a conditional tool for
   genuinely asynchronous composition, not the default for a timer that is
   already a per-frame state transition.
3. First keep DOTween and remove the captured completion allocation by using a
   cached non-capturing callback or a stateful callback/context table, then set
   DOTween capacity before sampling. Migrate to PrimeTween only if the warmed
   target-player capture still exceeds budget and an adapter proves identical
   sequence, overwrite, timing, and completion behavior. PrimeTween's exact
   package/license must be accepted before it is added.

Unity Awaitable is not a first choice here: its supported-version gate is Unity
2023.1+ in the applicable documentation, while this project is on 2022.3.12f1;
it also has pooled single-await and synchronous-continuation rules that are not
interchangeable with a coroutine. Keeping the current code remains valid for a
path that meets the measured budget after capacity and callback cleanup.

This is a recommendation from the supplied profiler finding, not a claim that
any target-player allocation window has already passed.

## Context and allocation contract

Evidence labels:

- **User-stated:** Unity 2022.3.12f1; IL2CPP; Android and WebGL shipping
  targets; one warmed inventory query using LINQ plus `ToArray`; 200 NPC
  cooldown coroutines that allocate on repeated restarts; combat UI tweens made
  with DOTween and captured completion lambdas.
- **Assumed for planning:** the three paths run during gameplay on the main
  Unity loop; inventory order and array eagerness are externally observable;
  cooldowns have a bounded update cadence; UI tweens are owner-bound.
- **Unknown:** exact package lock, source/tag/commit, licenses accepted by the
  project, device models, call-stack byte totals, maximum inventory result size,
  cooldown time-scale policy, tween capacities, and whether any callback runs
  off the main thread. These must be resolved before a dependency is pinned.

The contract for each slice is:

```text
Workload: one warmed inventory refresh; 200 NPC cooldown updates/restarts;
          representative combat UI tween create/overwrite/complete cycle.
Environment: Unity 2022.3.12f1, IL2CPP, Android and WebGL, Development for
             diagnostics and Release for acceptance, with the shipping
             optimization/stripping settings.
Warm-up: execute first-use generic/static initialization, query storage growth,
         callback/delegate creation, and tween capacity preparation before the
         measured window. Repeat cooldown/tween creation enough to reach the
         observed peak without growth during sampling.
Capacity: inventory result storage sized from observed peak plus margin;
          200 NPC slots; tween/sequence capacity set from a combat peak.
Window: a named marker around the warmed steady-state operation, repeated over
        a representative frame/iteration window, with all relevant threads.
Budget: default 0 managed bytes and 0 allocation count in the named warmed
        window. Give first-use, overflow, restart, cancellation, exception,
        and scene-transition paths separate reported budgets.
Behavior: preserve values, stable ordering and ties, eager/deferred boundary,
         result ownership, first coroutine step and yield phase, time-scale
         policy, cancellation/destruction timing, tween easing/delay/loops,
         overwrite and callback order, and exception propagation.
Other costs: record CPU/frame time, retained pool/list/tween memory, native
             memory, collection pauses, saturation, and outstanding leases.
```

The baseline and changed runs must use identical input data, frame settings,
backend, package versions, capacities, warm-up, sample marker, repetition count,
and device. Editor numbers may locate a source but are provisional; a
representative Android player and a WebGL player are the authority. A zero-byte
main-thread sample does not cover worker threads, rare exceptions, scene
transitions, or pool expansion.

## Decision matrix

| Candidate | Best fit and allocation boundary | Semantic/lifecycle gate | Android/WebGL, IL2CPP/AOT, provenance and license | Decision |
|---|---|---|---|---|
| Direct loop + reusable result | Inventory pipeline. Removes iterator/delegate churn and can avoid per-frame materialization when a caller-owned buffer or cached snapshot is legal. Capacity growth and any required final copy remain. | Lock result values, count, ordering/ties, comparer/equality, empty behavior, mutation visibility, and whether callers may retain the result. A reused mutable array cannot silently replace a fresh `ToArray` array. Define overflow (grow outside the window, tiered buffer, or explicit failure). | No new package or AOT surface; easiest to compile on both targets. Retained capacity is project-owned and must have a cap. | **Preferred first.** |
| ZLinq | LINQ-shaped hot query where composability is important. Value-enumerable chains can remove ordinary iterator allocations; captured selectors, interface conversions, sorting/grouping state, and `ToArray` still cost. | Compare against the direct loop. Preserve deferred versus eager execution, ordering/stability, numeric behavior, exceptions, repeated enumeration, and terminal-result ownership. A pooled terminal requires exactly-once return and no use after return. | Inspect the exact Unity package manifest and pin a tag/commit compatible with Unity 2022.3, its C# compiler, IL2CPP stripping/AOT, Android, and WebGL. Upstream ZLinq is documented as MIT, but the installed artifact and transitive dependencies still require approval. | **Conditional** for inventory only; never blanket-replace LINQ. |
| Explicit cooldown state machine | 200 deterministic timers. Stores deadline/remaining time, active state, and generation in pre-sized arrays/structs; no `IEnumerator`, nested yield objects, promise, or cancellation-registration churn on restart. | Match coroutine work before first yield (synchronous), exact first suspension and resume PlayerLoop phase, scaled/unscaled time, restart ordering, disable/destroy, cancellation-before-start/during-wait, exceptions, and late callbacks. Generation prevents an old completion from affecting a new restart. | Plain C# and Unity update code are safe for IL2CPP and WebGL; keep all access on the authorized Unity thread. No package provenance/license burden. | **Preferred for cooldowns.** |
| Existing coroutine, cleaned | May be acceptable if the measured path is below budget after reusing yield instructions and avoiding unnecessary restarts. Does not remove the state-machine allocation if repeated starts remain the source. | `WaitForSeconds` versus realtime/custom yield, nested enumerators, Stop/disable/destroy, first-step timing, and exception behavior must remain exact. Do not reuse a yield object whose semantics are mutable or time-dependent. | Built-in and compatible, but target-player evidence is required; no blanket coroutine ban. | **Keep only if it passes the contract.** |
| UniTask | Broader async composition, PlayerLoop timing, cancellation, and integration with async sources. Struct awaitables and pooled promises can reduce many `Task` costs, not all user captures/registrations/combinators. | Pin `PlayerLoopTiming`; test immediate cancellation, suspension, resume, completion race, exception observation, owner token disposal, and shutdown. Coroutine-to-UniTask adapters do not prove identical first-step or cancellation behavior. | Verify exact release in Unity 2022.3 IL2CPP/AOT with stripping on Android and WebGL. WebGL has no general worker-thread support: guard `RunOnThreadPool`/thread switches. Confirm PlayerLoop injection and reinjection if another system (including ECS) replaces it. Upstream license and package coordinate must be accepted. | **Not for this timer by default; conditional elsewhere.** |
| Unity Awaitable | Engine-provided pooled async operations on supported Unity versions. | Instances are single-await; continuations run synchronously when completion is triggered. Lock same-frame completion, thread affinity, cancellation, owner destruction, and exception behavior. | Applicable documentation gates Awaitable to Unity 2023.1+; this Unity 2022.3 project is outside that gate. Even after an editor upgrade, IL2CPP/AOT and WebGL behavior require proof. | **Reject for current target.** |
| DOTween with cached/stateful callbacks | Keeps existing sequence/tween semantics while removing the captured lambda/display-class boundary. Configure capacity so first-use growth is outside sampling. | Preserve easing, delay, loops, sequence insertion/order, update phase, scaled/unscaled time, target overwrite/concurrent behavior, kill/cancel/completion ordering, reentrancy, and owner teardown. Cached callbacks must not retain a released UI owner. | Existing dependency means no new license decision, but its exact lock and IL2CPP/WebGL build must be captured. | **First tween slice.** |
| PrimeTween | Candidate if DOTween remains above budget after callback/capacity work. Its core can be low allocation, but user callbacks/adapters can allocate and capacity growth is not free. | PrimeTween handles are non-reusable after completion/cancellation. Specify target overwrite versus concurrent behavior; prove sequence order, timing, loops, callbacks, cancellation, and pooled UI reset against DOTween. | Inspect exact package manifest/tag/commit and license. PrimeTween is **not MIT**; redistribution/repackaging restrictions require explicit legal/project acceptance. Build Android and WebGL IL2CPP with stripping before rollout. | **Conditional last resort for tween path.** |
| Animator/manual update | Simple, fixed-shape UI animation. An explicit update or Animator may avoid tween object/callback churn entirely. | Must reproduce ease, delay, loops, interruption/overwrite, time scale, completion ordering, and UI state reset; more bespoke code can increase semantic risk. | Built-in/AOT-safe; no package license. | **Revisit if tweens are simple and stable.** |

## Staged red-green migration

### Stage 0 — evidence and seams

Keep each old path behind a narrow adapter or feature flag. Capture a functional
red contract before changing code and a baseline allocation red capture only if
the warmed path demonstrably exceeds the stated budget. Place profiler markers
around one query refresh, one cooldown batch, and one tween lifecycle; create and
dispose any recorder outside the measured window. Record main and worker-thread
samples, first-use separately, and the exact Android device/WebGL browser and
build settings.

Before adding a package, inspect the installed/package-lock coordinate, exact
version and source, upstream tag/commit, Unity minimum, compiler API surface,
IL2CPP/AOT and stripping behavior, transitive dependencies, and license. A
README benchmark or newest release is only a hypothesis until reproduced on this
workload.

### Stage 1 — inventory query

First write a functional seam that compares the current query with the proposed
loop over empty, one-item, ties, maximum-capacity, mutation-between-refresh,
repeated-enumeration, and exception cases. Preserve the current order exactly;
do not add a sort merely because a different enumerator changes order.

Prefer `RefreshInto(destination, capacity)` or an owner-held result object whose
logical count is separate from its array capacity. If callers currently retain a
fresh `ToArray`, either keep that compatibility wrapper off the per-frame path or
change the contract explicitly to a scoped/caller-owned view. Detect a full
buffer and choose a tested policy: grow/retry outside the steady-state window,
use a prepared larger tier, or fail with telemetry. Never truncate silently.

Only after the functional red turns green, compare allocation with the same
prepared capacity. If the direct loop is clear and passes, stop. If a complex
pipeline still justifies composability, run a separate ZLinq slice: pin the
artifact, avoid captures, test the terminal materializer, and compare direct loop
versus ZLinq on both players. ZLinq does not make a required final array free.

### Stage 2 — cooldown state machine

Model each NPC with pre-sized state: active, deadline/remaining value, time mode,
and a generation/token. On `Restart`, perform the coroutine's pre-first-yield
work synchronously, set the same deadline, and increment generation. In the
authorized update phase, process due entries once, in the original NPC/order,
then invoke completion and clear active state. A disabled/destroyed NPC cancels
and invalidates its generation before teardown. Test restart-before-first-step,
restart-during-wait, exact-boundary time, scaled/unscaled time, cancellation,
simultaneous expirations, exception propagation, and scene unload.

The state machine is green only when those functional cases match the coroutine.
Then warm all 200 slots and repeated restart patterns; no array/state capacity
may grow in the sample. Report CPU cost and retained state separately. Keep the
coroutine fallback until Android and WebGL captures pass and no late completion
can target a reused NPC. UniTask may be revisited for a separate operation with
real async composition, but its PlayerLoop and WebGL thread guards are not a
reason to wrap a deterministic timer.

### Stage 3 — combat UI tween

Characterize one representative sequence and its overwrite cases: easing,
duration/delay, loops, update phase, scaled/unscaled time, concurrent target
policy, kill/cancel behavior, completion order, reentrancy, and pooled-view
release. Replace captured completion lambdas with a cached static delegate plus
an owner/context lookup or an exact stateful overload. Make callback ownership
explicit and clear it on release. Configure DOTween capacity from observed peak
concurrency, warm it, and rerun functional then allocation evidence.

If the warmed DOTween path passes, retain it; there is no benefit in paying a
semantic and license migration cost. If it fails, prototype PrimeTween behind
the same adapter. PrimeTween handles cannot be replayed after completion or
cancellation, so create a new handle per activation, cancel/reset on UI pool
release and scene unload, and test overwrite/completion parity. Pin and approve
the exact non-MIT license before merging. A manual Animator/curve update is an
alternative for a small fixed set of effects.

### Stage 4 — target-player rollout

Run functional and allocation evidence on Android IL2CPP Development players,
then repeat the acceptance window in Release. Repeat on WebGL with its actual
browser/runtime and no worker-thread assumptions. Compare first-use, warmed
steady state, restart/cancellation, overflow/capacity growth, exceptions, scene
transition, and teardown. Inspect retained managed objects, native memory, pool
high-water marks, CPU/frame time, and collection pauses. Expand the feature flag
only after a soak covering repeated scene loads and UI pool reuse.

Rollback immediately on any ordering/timing/cancellation/completion mismatch,
unsupported IL2CPP/AOT or stripping failure, WebGL thread/PlayerLoop issue,
license/provenance uncertainty, buffer saturation above the agreed threshold,
retained/native-memory cap breach, CPU regression, unobserved exception, stale
callback, double return, use-after-return, or leak. Remove the old path only
after representative target-player evidence is reproducible and the project
accepts the dependency and license.

## Capacity, ownership, and lifecycle rules

Inventory storage is owned by the inventory service, cleared at the documented
refresh boundary, and never exposed as a mutable long-lived result. Track logical
count separately from capacity, clear stale references, cap retained memory, and
telemetry for growth/saturation. If a caller needs ownership beyond the frame,
copy or publish a snapshot at the explicit transition point rather than making a
per-frame copy.

Cooldown state belongs to the NPC system; one slot per NPC is warmed before the
window. Disable/destroy/scene unload invalidates the generation and settles all
callbacks. No task, coroutine, or callback may outlive the owner. A restart is a
new lease, not a continuation of the old one.

Tween capacity is prepared before sampling. UI pool release cancels tweens,
resets visual/material/text state, clears callback context and subscriptions,
and prevents late completion from touching a newly leased view. Scene unload
stops new activations, settles active tweens, and then tears down storage.

## Risks and open questions

The largest risk is an ownership change hidden by “replace `ToArray`”: a reused
buffer may invalidate callers that retain the old array. The second is timing
drift from replacing a coroutine with an update tick or from changing tween
overwrite semantics. Package compatibility, exact licenses, Unity package lock,
and browser/device behavior are presently unknown. A captured callback may also
be only one allocation boundary; measure the entire create/overwrite/complete
path, including exception and pool-growth edges.

Open questions that materially change the design are:

- What is the maximum and percentile inventory result size, and may callers
  retain a query result beyond the current frame?
- Do cooldowns use scaled time, unscaled time, custom yield instructions, or
  nested coroutines, and which PlayerLoop phase is their first resume?
- What are DOTween's exact sequence/overwrite/update settings and peak
  concurrency, and is its current warmed path still allocating after callback
  cleanup?
- Which exact ZLinq, UniTask, DOTween, and PrimeTween artifacts are in or
  proposed for the lock, and has PrimeTween's non-MIT license been accepted?
- Which Android devices and WebGL browsers define the shipping acceptance
  window, and what managed-byte, CPU, retained-memory, and saturation budgets
  apply to transition paths?

## Next action

Create the three narrow adapters and capture the baseline contract first. Then
land the inventory direct-loop slice, followed by the cooldown state-machine
slice, followed by DOTween callback/capacity cleanup. At each slice, functional
red must turn green before allocation evidence is collected. Consider ZLinq,
UniTask, or PrimeTween only when the corresponding direct/built-in slice fails
the named warmed target-player budget and the exact package, AOT/WebGL, lifecycle,
semantic, and license gates above are satisfied.
