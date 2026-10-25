# Game Programming Patterns
Selection conditions and runtime contracts for game systems; use engine-owned loops, updates, components, and content mechanisms before building replacements.

## Game Loop
- **Choose when:** You own simulation scheduling, or must separate simulation cadence from rendering through engine hooks.
- **Simpler first:** Use the engine loop; add fixed stepping for integration stability or required simulation cadence.
- **Contract:** Retain previous/current states; bound catch-up. This sketch discards excess elapsed time; never use that policy for protocol-required ticks.
- **Traps:** Test long frames against catch-up limits. Fixed steps do not ensure determinism: input order, arithmetic, RNG, and iteration still matter.
- **Not:** Previous/current interpolation trails simulation; [extrapolation](#dead-reckoning) predicts beyond known state and can be wrong.

```text
accumulator = min(accumulator + elapsed, step * maxSteps)
while accumulator >= step:
    previous = copy(current)
    current = simulate(current, inputsForTick(), step)
    accumulator -= step
render(interpolate(previous, current, accumulator / step))
```

## Update Method
- **Choose when:** Many independently stateful behaviors need recurring progress; cost grows with the active population.
- **Simpler first:** Use engine update hooks, or events/timers for occasional work; centralize only after measuring callback overhead.
- **Contract:** Declare phases, time units, and cancellation. Iterate a stable set; stage additions/removals at boundaries and specify their first/last update.
- **Traps:** Sequential mutation makes behavior container-order-dependent; use snapshots or explicit dependencies where needed. Test reversed iteration order and self-removal; per-object searches multiply frame cost.

## Double Buffer
- **Choose when:** Readers need a coherent snapshot, or simultaneous reactions must all read the same old state.
- **Simpler first:** Mutate directly when order is intentional; stage only affected fields if a full second copy is too expensive.
- **Contract:** Finish writers before atomic publication with required memory synchronization. Track reader lifetimes before reusing the old buffer; a reference swap alone is insufficient.
- **Traps:** Reused buffers contain stale generations: overwrite or refresh unchanged fields. Test a slow reader across publication and fields untouched for several frames.

## Component
- **Choose when:** Capabilities vary independently enough that inheritance combinations obscure ownership; communication overhead replaces hierarchy complexity.
- **Simpler first:** Use the engine component/node model; keep one cohesive object until domains genuinely vary independently.
- **Contract:** Define initialization, teardown, dependencies, and update order. Shared owner state couples domains; direct references expose coupling; messages loosen references but hide control flow.
- **Traps:** Cyclic lookups and activation-order assumptions break startup. Test missing dependencies and teardown with messages pending.
- **Not:** Object composition is not [archetype ECS](ecs-data-oriented.md#core-concepts) or a locality guarantee.

## Type Object
- **Choose when:** Runtime kinds differ in parameters/assets rather than algorithms; shared definitions reduce class proliferation.
- **Simpler first:** Use engine data assets/resources or a small table; upgrade when authors need independently validated catalog entries.
- **Contract:** Validate before instantiation; separate instance state from shared defaults. Declare definition ownership, reload/type-change behavior, and data-inheritance override rules, cycle rejection, and depth limits.
- **Traps:** Mutating a definition changes every instance; inherited defaults can conceal missing data. Test reloads, invalid parents, and explicit overrides.
- **Not:** [Prototype](creational.md#prototype) copies instances; Type Object shares kind definitions.

## Subclass Sandbox
- **Choose when:** Related extensions compose invariant-preserving primitives, and inheritance already fits.
- **Simpler first:** Use direct methods or a small strategy; upgrade only when repeated safe primitives need a shared contract.
- **Contract:** Keep protected capabilities narrow; pass dependencies explicitly and state which errors extensions handle. Each helper enlarges every subclass's dependency surface.
- **Traps:** A universal base becomes a hidden service hub; test extensions with unavailable capabilities. Protected access does not contain untrusted code.
- **Not:** [Template Method](behavioral.md#template-method) fixes the base algorithm; here subclasses compose it.

## Bytecode
- **Choose when:** Replaceable behavior-as-data needs a controlled execution contract, and existing scripting cannot meet measured constraints.
- **Simpler first:** Use engine scripting/visual tools or functions; own a VM only when their limits justify tooling and migration costs.
- **Contract:** Validate and version instructions; bound execution, memory, and host capabilities. Define suspension, cancellation, diagnostics, and failure behavior.
- **Traps:** Small interpreters are not automatically secure or fast; test malformed instructions and budget exhaustion. Source mapping and authoring tools can cost more than dispatch.
- **Not:** [Interpreter](behavioral.md#interpreter) need not use bytecode.

## Event Queue
- **Choose when:** Deferred processing, coalescing, or batching matters more than an immediate answer; queue latency is acceptable.
- **Simpler first:** Call directly for results or use synchronous [Observer](behavioral.md#observer); upgrade when producers must decouple processing time.
- **Contract:** Distinguish facts/requests and broadcast/work distribution. Own or copy payloads; define capacity, overflow, order, consumer failure, cancellation, and shutdown. Capture delivery-stable context.
- **Traps:** Live references and assumptions can expire before delivery; revalidate identities. Bound handler feedback loops. Test overflow, destroyed targets, and handlers that enqueue their own triggers.

## Service Locator
- **Choose when:** Existing globals cannot yet become explicit injection, or an engine's scoped registry fits.
- **Simpler first:** Pass collaborators directly; upgrade only when that migration or discovery boundary actually requires lookup.
- **Contract:** Own registration/replacement at startup, before consumers run; scope services to world/session lifetimes. Required absence must fail clearly; optional absence may use a deliberate null service.
- **Traps:** Registration order and retained services couple tests/scopes. Test missing bindings and teardown; null persistence must not conceal data loss.
- **Not:** See the [DI trade-off](principles.md#dependency-injection-and-composition-root), not a synonym for injection.

## Data Locality
- **Choose when:** A measured hot loop is memory-access-bound at representative scale, and the runtime exposes useful layout control.
- **Simpler first:** Reduce algorithmic work and use supported arrays/batching; reshape data only when profiling still identifies traversal cost.
- **Contract:** Choose AoS/SoA and hot/cold splits from fields consumed together. Define relocation ownership and stable generation-checked handles before compaction.
- **Traps:** Compaction invalidates raw references; test escaped handles after slot reuse. Benchmark conversion, joins, allocation, and false sharing: contiguous storage alone proves nothing.

## Dirty Flag
- **Choose when:** Several source mutations usually precede a read of expensive derived data; freshness can be checked at a known boundary.
- **Simpler first:** Recompute directly; upgrade when measured repeated derivation dominates and every mutation can invalidate reliably.
- **Contract:** Invalidate on every write path and dependent descendant. Declare clean-on-read versus scheduled rebuild, modifier order, and synchronization/versioning so a rebuild cannot erase newer invalidation.
- **Traps:** One missed mutation serves stale values indefinitely; test all write paths. Simultaneous first reads create deferred spikes: measure and budget rebuild bursts.

## Object Pool
- **Choose when:** Repeated allocation, initialization, or collection is a measured cost; idle memory is affordable.
- **Simpler first:** Use normal engine creation/destruction or its pool; add custom pooling only after representative profiling.
- **Contract:** Own acquire/release/reset; clear physics, timers, subscriptions, replication, and retained resources across engine lifecycles. Invalidate leases with generation handles. Define exhaustion: reject, skip optional work, recycle eligible objects, or bounded growth.
- **Traps:** Hiding an object is not reset; stale references can affect a new occupant. Test repeated reuse, delayed callbacks, double release, and exhaustion.

## Spatial Partition
- **Choose when:** Repeated spatial scans dominate at scale and no existing index answers the custom query.
- **Simpler first:** Use physics-engine queries, or linear scans for small populations; add an index only when measured query savings exceed maintenance.
- **Contract:** Choose grid/hash versus hierarchy from density and motion; define movement-update boundaries, multi-region membership, removal, deduplication, and exact candidate tests.
- **Traps:** Stale membership misses results; dense clusters and large objects erase gains. Test cell boundaries, teleports, removals, and worst-case clustering, including maintenance cost.

## Multiplayer Architecture
- **Choose when:** Real-time shared simulation has explicit responsiveness, fairness, and bandwidth requirements despite loss and jitter.
- **Simpler first:** Use local/asynchronous play or engine networking; replace mechanisms only after a measured requirement fails.
- **Contract:** Assign authority/trust first, then techniques per interaction. Track ticks, input acknowledgments, and snapshot timestamps; budget history and resimulation separately.
- **Traps:** Prediction, interpolation, and historical hit tests use different timelines. Test jitter, loss, reconnects, and adversarial inputs. [Backend services](distributed-systems.md#game-backend-applications) are a separate concern; synchronization is not cheat resistance.

### Authoritative Server
- **Choose when:** Shared outcomes cannot trust client state; accept validated intents and replicate server-owned results.
- **Simpler first:** Trusted local peers suffice only when the trust model permits them.
- **Traps:** Authority is not comprehensive anti-cheat; test illegal inputs and disconnect recovery. Round trips alone make fast controls sluggish.

### Client-Side Prediction and Reconciliation
- **Choose when:** Local controls need immediate response and client/server simulations match closely enough for replay.
- **Contract:** Sequence/save inputs; restore authoritative state, discard acknowledged inputs, then replay the remainder. Smooth presentation separately.
- **Traps:** Mismatches cause repeated corrections; test delayed acknowledgments. Do not present irreversible outcomes before confirmation.

### Entity Interpolation
- **Choose when:** Remote snapshots are sparse/jittery; render between timestamped samples on a deliberately delayed timeline.
- **Contract:** Budget buffer delay and define missing-snapshot behavior; unlike [dead reckoning](#dead-reckoning), do not project beyond known samples.
- **Traps:** Added smoothness costs latency. Test loss and jitter; never blend across teleports, respawns, or reused identities.

### Dead Reckoning
- **Choose when:** Motion is inertial enough to extrapolate from the last known position/velocity; sparse snapshots justify error.
- **Simpler first:** Use buffered [interpolation](#entity-interpolation) for abrupt motion; define a prediction horizon and correction thresholds otherwise.
- **Traps:** Unseen collisions/inputs invalidate projections; test sudden turns and prolonged snapshot gaps. Error grows with prediction age.

### Lag Compensation
- **Choose when:** Authoritative hit tests should reflect a shooter's plausible historical view rather than current positions.
- **Contract:** Retain bounded history, validate view timestamps including interpolation delay, isolate rewind queries, and apply accepted results to present state.
- **Traps:** Fairness shifts toward shooters: victims can be hit after cover. Test history limits; never trust claimed hits.

### Deterministic Lockstep
- **Choose when:** Exchanging inputs is much cheaper than replicating a large state, and waiting for missing inputs is acceptable.
- **Contract:** Require bit-exact simulation: arithmetic/builds, RNG consumption, iteration, and input order; compare periodic checksums.
- **Traps:** Fixed timestep is insufficient. Test cross-build/platform replays and delayed peers; one missing input stalls progression.

### Rollback Netcode
- **Choose when:** Responsive controls justify deterministic simulation plus cheap, complete save/load and bounded resimulation.
- **Contract:** Save state, predict inputs, restore on disagreement, replay to present; budget history/window and permit simulation without rendering.
- **Traps:** Deduplicate/suppress replayed audio/VFX; defer irreversible effects until confirmed. Test maximum rollback depth and state completeness; peer rollback does not establish authority.

### Interest Management
- **Choose when:** Full replication exceeds bandwidth or exposes unnecessary information; combine distance with ownership/team/gameplay rules.
- **Contract:** Define priorities, enter/leave lifecycle, and hysteresis; use [spatial queries](#spatial-partition) only to generate candidates.
- **Traps:** Relevance is not visibility or authorization. Test boundary churn and late entrants; reducing replicated information is not anti-cheat.
