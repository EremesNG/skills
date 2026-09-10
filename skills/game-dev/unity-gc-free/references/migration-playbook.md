# Migration playbook

Change one proven allocation source at a time. A migration is complete only when
functional behavior and the scoped allocation contract both pass; reduced
allocation cannot compensate for a semantic regression.

## One-source vertical slice

1. **Name the source.** Record one profiler call stack/path, its frequency and
   thread, the workload/capacity state, and why it is inside the budgeted window.
2. **Lock behavior.** Add focused tests for public outcomes and lifecycle at this
   source, not implementation details.
3. **Observe functional red.** Add at least one meaningful behavior test that
   fails for the missing migration contract (for example full-buffer overflow or
   cancellation on release). Do not manufacture a failure by breaking code.
4. **Observe allocation red.** Capture the unchanged representative workload
   exceeding the declared managed-allocation budget after warm-up. If automation
   is unavailable, preserve a dated profiler artifact/protocol and label the
   evidence pending rather than fabricating a test.
5. **Select the smallest mechanism.** Compare removal, reuse/caller buffer,
   direct code/built-in API, then a version-pinned dependency. Record rejected
   alternatives and the semantic/lifecycle boundary that decides.
6. **Implement the slice.** Touch only the source, its explicit owner, and tests.
   Keep an easy rollback path; avoid simultaneous unrelated substitutions.
7. **Green functional.** Run the new behavior tests plus affected regression
   tests in the supported configurations.
8. **Green allocation.** Repeat the identical allocation protocol in a
   representative target player, with prepared capacity and all relevant threads.
9. **Roll out and observe.** Use a feature flag/adaptor or small reversible commit
   where risk warrants it. Watch correctness, pool saturation, retained/native
   memory, CPU, exceptions, and cancellation/leaks before expanding the slice.

## Behavior contract to lock

Record applicable invariants before choosing a replacement:

- result values, count, precision, null/default behavior, mutation, and aliases;
- ordering and stability, including tie/order behavior and partial results;
- timing: immediate work, first suspension/yield, update phase, time scale,
  same-frame completion, callback order, and reentrancy;
- exception type/propagation, logging, async failure observation, and recovery;
- cancellation trigger, callback/completion policy, registration disposal, and
  race with normal completion;
- thread affinity and synchronization: caller, main thread, PlayerLoop phase,
  worker/job completion, and continuation thread;
- owner lifecycle: enable/disable, pooled get/release, scene unload, domain
  reload configuration, application shutdown, and late callback;
- capacity/ownership: warm-up, full-buffer detection, truncation, ordering,
  overflow/fallback, double return, use after return, and teardown;
- compatibility: installed Unity/compiler/package, Mono/IL2CPP, AOT/stripping,
  target platform, dependency/license approval, and build configuration.

## Allocation evidence pair

Use the allocation contract verbatim for before/after comparison: same commit
apart from the slice, hardware, target, player type, backend, profiler settings,
input dataset, capacity, warm-up, sample window, repetition count, and all
relevant threads.

- The before capture is **allocation red** only if it demonstrably exceeds the
  named `GC.Alloc` budget at this source.
- The after capture is **green allocation** only if the scoped budget passes.
- A functional suite is **green functional** only if all preserved/changed
  semantics and lifecycle scenarios pass.
- Separately compare native allocation, retained memory, CPU/frame time, pool or
  buffer saturation, and error paths. Do not move an unacceptable cost domains.
- Editor data can locate the source but is provisional. A representative target
  player is the authority; use Development Player call stacks during diagnosis
  and confirm Release Player behavior when the contract demands it.

## Substitution checklists

### LINQ / ZLinq / direct loop

- Lock result values, count, ordering/stability, equality/comparer, numeric
  behavior, deferred versus eager execution, repeated enumeration, mutations,
  empty/default/exception cases, and terminal result ownership.
- Inspect captured lambdas, interface conversions, sorting/grouping state, and
  materializers. If a pooled result is used, test dispose exactly once, copies,
  exceptional exits, and use-after-return.
- Compare a plain direct loop. ZLinq is justified by the complete readability,
  compatibility, and allocation contract—not the package name.

### Coroutine / async

- Lock when work starts, every PlayerLoop/yield phase, same-frame completion,
  nesting/composition, owner disable/destroy, time scale, exceptions, cancellation,
  and thread affinity.
- For Awaitable, enforce single-await and synchronous-continuation implications.
  For UniTask, pin PlayerLoop injection/timing, cancellation strategy, WebGL/thread
  guards, and ECS loop-reset behavior where relevant.
- Exercise cancellation-before-start, during suspension, simultaneous completion,
  and shutdown; dispose registrations and observe late callbacks.

### DOTween / PrimeTween

- Characterize ease, duration/delay, loops, sequence insertion/order, update
  phase, scaled/unscaled time, overwrite/concurrent target behavior, getters/
  setters, completion/kill/cancel callbacks, and await/coroutine adapters.
- Configure capacity before measurement; use stateful callbacks where supported
  and prove no captured closure in the measured path.
- PrimeTween handles are non-reusable. Cancel/reset owner-bound tweens and visual/
  material state on pool release and scene unload. Approve the exact license.

### Pooling

- Test create/get/release/reset/destroy, dirty-object reuse, peak warm-up, empty
  exhaustion, max-size overflow, subscriptions, async cancellation, retained
  references, reference-count handles, and owner teardown.
- For caller buffers, force full-buffer results and assert the documented
  truncation, ordering, telemetry, and fallback behavior.
- Include double-return, foreign return, use after return, scene unload, domain
  reload, and Addressables late completion. Measure retained memory and misses.

### Native container

- Lock allocator, capacity, root owner and every alias, reader/writer access, job
  dependency, completion, disposal, safety configuration, and Burst fallback.
- Test `Temp`/`TempJob` deadlines, Persistent teardown, resize invalidation,
  dispose-after-job, repeated lifecycle leak behavior, and target IL2CPP/AOT.
- Report native allocation and CPU cost separately; zero managed bytes does not
  prove a native design is bounded or faster.

## Rollback and rollout

Keep the old path behind a narrow seam until functional and allocation evidence
is reproducible. Define rollback triggers: behavior mismatch, unsupported build,
license/provenance issue, saturation above threshold, retained/native-memory cap,
CPU regression, unobserved exception/cancellation, safety violation, or leak.
Remove the fallback only after representative soak evidence and project approval.

## Success gate

Report success only when both are true:

1. **Functional evidence:** all locked result, ordering, timing, exception,
   cancellation, thread affinity, owner lifecycle, capacity, and compatibility
   behaviors pass in affected configurations.
2. **Allocation evidence:** after declared warm-up and capacity preparation, the
   named steady-state workload meets its managed-allocation budget over the
   representative target-player sample window across all relevant threads.

If either side is unavailable or fails, return the result as provisional, failed,
or blocked with the exact missing evidence and next action—not “GC-free.”
