# Distributed Systems Patterns
Select remote-call, messaging, and service-boundary patterns from explicit failure, consistency, latency, and recovery requirements—not a target architecture.

## Choosing Distributed Patterns

Distribution itself costs correctness and operations work; a single service plus a database transaction is simpler when sufficient.
- Transient failure → [Timeout](#timeout), then conditional [Retry](#retry-with-backoff) + [Idempotency](#idempotent-consumer); persistent outage → [Circuit Breaker](#circuit-breaker).
- Resource starvation → [Bulkhead](#bulkhead)/[Rate Limiting](#rate-limiting); divergent reads/writes → [CQRS](#cqrs).
- Independent-store workflow → [Saga](#saga); required durable publication → [Outbox](#transactional-outbox); legacy replacement → [Strangler](#strangler-fig)/[ACL](#anti-corruption-layer).
- Stack timeouts first; retries only for transient, idempotent work, with exactly one retry owner. Share an end-to-end deadline; define unavailable/stale behavior and recovery ownership.

## CQRS

- **Choose when:** Read shapes, access controls, or scaling materially conflict with write invariants and projection lag is acceptable.
- **Simpler first:** Queries and indexes over one model; split code responsibilities when repeated query assembly becomes costly.
- **Contract:** Define read-after-write behavior and projection recovery before separating stores. CQRS requires neither event sourcing nor messaging, separate services, or separate databases.
- **Traps:** Separate stores add lag, rebuilds, and reconciliation. Test immediate reads after writes and projection loss; expose pending changes or provide explicit read-your-writes behavior.

## Event Sourcing

- **Choose when:** Reconstructing historical decisions or rebuilding new projections is a core requirement worth permanent replay governance.
- **Simpler first:** Current state plus an audit log; upgrade only when authoritative event history must derive state, not merely explain changes.
- **Contract:** Govern event schemas, concurrency checks, deterministic replay, snapshots, and rebuilds; decide retention/erasure before recording personal data.
- **Traps:** Replays must not resend payments or notifications. Test old schemas and side-effect suppression; historical records prove what was recorded, not legitimacy—validate invariants before append.

## Saga

- **Choose when:** Independent stores cannot share a transaction and the business accepts visible intermediate states and meaningful remediation.
- **Simpler first:** Co-locate the invariant in one database transaction; distribute only when an actual ownership/deployment constraint prevents it.
- **Contract:** Persist correlated progress, recovery ownership, and reservations/concurrency protections. Choose explicit orchestration or event choreography without hiding who completes recovery.
- **Traps:** Compensation is a new business action, not rollback; it can fail or need manual repair. Test partial-state visibility, failed compensation, and irreversible steps before promising all-or-nothing behavior.

## Transactional Outbox

- **Choose when:** Committed changes must eventually publish despite process/broker failure; delay is acceptable.
- **Simpler first:** Local calls unless publication requires durability; existing change streams if their contract suffices.
- **Contract:** Atomically commit state and a stable-ID outbox record; operate relay lag, cleanup, concurrency, and per-entity ordering.
- **Traps:** Publish-before-mark permits duplicates; require idempotent consumers. Crash-test this window and relay reordering; remote effects are not transactionally protected.

```text
transaction: update state + insert outbox(messageId); commit
relay: publish -> mark published
crash after publish, before mark -> publish again
```

## Idempotent Consumer

- **Choose when:** Redelivery or lost responses can repeat charges, grants, or assignments.
- **Simpler first:** An intrinsically idempotent/versioned update; add a ledger when repeated logical operations otherwise repeat effects.
- **Contract:** Scope stable keys by consumer/tenant/operation; reject changed payloads and retain keys through the retry/replay window. Atomically claim a unique key, apply the effect, and store its result; acknowledge after commit. Return saved results for duplicates.
- **Traps:** Check-then-write races; crash-test concurrent duplicates. Local dedup cannot atomically protect remote effects: use the remote idempotency contract or reconcile.

## Retry with Backoff

- **Choose when:** Failures are transient, work is idempotent or keyed, and another attempt fits the remaining deadline and recovery capacity.
- **Simpler first:** Surface the failure; add retries only after evidence identifies recoverable faults, never for validation/authorization failures.
- **Contract:** Exactly one retry owner; bounded attempts, capped delays, jitter, and a total deadline; respect server guidance within that budget.
- **Traps:** Layered retries multiply load. Test outage request volume and lost responses: a timeout does not prove the effect failed; reconcile or reuse the same key.

## Circuit Breaker

- **Choose when:** Persistent dependency failures waste resources and explicit unavailability or a safe fallback is useful.
- **Simpler first:** Timeouts and a small conditional retry budget; add a breaker when repeated failures justify admission suppression.
- **Contract:** Match breaker scope to the dependency's failure boundary; define thresholds, open duration, limited half-open probes, and caller-visible failure.
- **Traps:** False opens and recovery surges can prolong outages. Test flapping and concurrent probes. A breaker blocks attempts; [retry](#retry-with-backoff) repeats them, and neither replaces a timeout.

## Bulkhead

- **Choose when:** One dependency, tenant, or workload exhausts resources needed by critical work.
- **Simpler first:** Shared capacity with bounded concurrency; partition only after contention demonstrates a need for protected allocations.
- **Contract:** Size pools against downstream capacity, reserve critical headroom, bound waiting queues, and define admission/rejection behavior; monitor utilization and queue delay.
- **Traps:** Hard partitions strand idle capacity; shared hosts/databases may still fail together. Saturate one partition and verify critical traffic remains within its budget without overloading shared downstream limits.

## Timeout

- **Choose when:** A remote wait can outlive its caller's useful response window or retain scarce resources.
- **Simpler first:** Ordinary control flow for bounded local work; persist an async job if work must outlive the request.
- **Contract:** Propagate a finite end-to-end deadline covering connection setup and response waits; propagate cancellation where supported.
- **Traps:** Short budgets create false failures; long ones exhaust resources. Delay responses in tests and check resource release. Timeout leaves the remote outcome ambiguous; query/reconcile or deduplicate, never assume cancellation undid an effect.

## Rate Limiting

- **Choose when:** Bursts, abuse, tenant imbalance, or downstream time quotas need authoritative admission control.
- **Simpler first:** Bounded concurrency or cooperative client shaping; add shared accounting only when a time-based quota requires it.
- **Contract:** Define identity, operation cost, burst allowance, clock/accounting semantics, retry guidance, and fail-open/closed policy.
- **Traps:** Client cooperation is not enforcement; per-process limits multiply with instances and shared counters become hot. Test scale-out totals and limiter failure. Request count alone may misrepresent expensive work; quotas do not replace resource isolation.

## Cache-Aside

- **Choose when:** Repeated reads are expensive and explicit staleness bounds are acceptable; misses can reach the authority safely.
- **Simpler first:** Indexed source queries; cache only after measured latency/load warrants invalidation complexity, not for freshness-critical authorization or balances.
- **Contract:** Define expiry, write invalidation, tenant/authorization-aware keys, and cold-cache source capacity.
- **Traps:** Readers can repopulate stale data after invalidation; concurrent misses stampede. Use request coalescing/bounded refresh and version-aware policies where needed; test a read spanning a write and a fully cold cache.

## API Gateway

- **Choose when:** Clients coordinate many service endpoints or duplicate meaningful routing, aggregation, and edge policies.
- **Simpler first:** One service or an existing reverse proxy; add a gateway only when it reduces client coupling or operational duplication.
- **Contract:** Budget hop latency, redundancy, and partial aggregation failure; owning services still enforce resource authorization.
- **Traps:** Gateways accumulate domain workflows and become shared bottlenecks. Test one failed aggregation dependency and direct service access; keep business decisions in owning services rather than edge routing.

## Backends for Frontends

- **Choose when:** Clients materially diverge in payloads, latency budgets, interactions, or API evolution needs.
- **Simpler first:** One API with response shaping; split only after client-specific compromises repeatedly impede delivery.
- **Contract:** Client teams own added deployment, compatibility tests, and security surface; authoritative domain rules stay in core services.
- **Traps:** Duplicated business policy drifts; universal shared aggregation recreates one backend. Test invariant enforcement across clients. Share stable capabilities without erasing the divergence that justified a BFF.

## Strangler Fig

- **Choose when:** A risky legacy replacement has a routable capability seam and must proceed incrementally.
- **Simpler first:** One controlled replacement if safe; otherwise establish a local [facade](structural.md#facade) before distributed coexistence.
- **Contract:** Per slice, assign authoritative writes, synchronization/reconciliation, routing, rollback, and retirement criteria.
- **Traps:** Uncontrolled dual writes diverge; switching traffic back does not reverse migrated data. Test coexistence and rollback after new writes, then remove obsolete routes rather than operating both systems indefinitely.

## Anti-Corruption Layer

- **Choose when:** External terminology, invariants, or lifecycle semantics genuinely conflict with the local model.
- **Simpler first:** A thin [Adapter](structural.md#adapter) or mapping; add an ACL only when translation protects a real semantic boundary, not field names.
- **Contract:** Own translation of states, identifiers, and failures; define lossy-mapping policy and compatibility as both systems evolve.
- **Traps:** External semantics leak through local-looking types; conversion code hides new business policy. Contract-test unknown states and errors, and make unsupported meanings explicit rather than silently approximating them.

## Competing Consumers

- **Choose when:** Independent queued jobs need parallel throughput and bounded burst absorption, with redelivery tolerance.
- **Simpler first:** Direct calls or one worker; scale consumers after measured queue delay, not when work requires strict global sequence.
- **Contract:** One worker per delivery attempt; acknowledge after durable completion, renew leases, bound retries, and quarantine poison messages. Serialize per-entity partitions when ordering matters.
- **Traps:** Parallel completion reorders work and expired leases duplicate it. Test a slow worker, crash-after-effect, and poison messages without blocking healthy jobs indefinitely.

## Publisher-Subscriber

- **Choose when:** Independent deployed consumers need the same fact and accept delayed propagation with separately operated lifecycles.
- **Simpler first:** An in-process [Event Bus](application-architecture.md#event-bus) for local notifications; direct calls for required immediate answers or a local transaction for atomic work.
- **Contract:** Specify broker durability, acknowledgements, retention, ordering, redelivery, schema evolution, and subscriber idempotency as required.
- **Traps:** Publication does not complete subscribers' workflows. Test offline/slow subscribers and duplicate deliveries; observe lag and propagation traces. Broker pub-sub is not automatically durable and is not an in-process bus.

## Sidecar

- **Choose when:** Mixed runtimes need independently packaged infrastructure and the platform can coordinate companion lifecycle/health.
- **Simpler first:** A library or existing platform facility; add a process only when packaging or isolation benefits outweigh per-instance overhead.
- **Contract:** Budget CPU/memory and local-hop latency; define startup readiness, configuration/version compatibility, shutdown draining, and failure policy.
- **Traps:** Locality is not reliability; a failed companion can disable every application instance. Test startup races, companion loss, and draining rather than assuming a nearby process is always ready.

## Game Backend Applications

Prefer one authoritative service and transaction when sufficient; these mappings are not a stack.
- **Matchmaking:** Bound queues/deadlines; use authoritative reservations to prevent duplicate assignments.
- **Leaderboards:** CQRS/cache only if needed; define rank lag, ordering, and server-side score validation.
- **Inventory/economy:** Stable idempotency keys plus server-side validation, atomic balance/uniqueness checks; test concurrent/replayed grants. Outbox only for required publication; saga only across stores.
- **Live-ops:** Validate/version configuration; authorize edits and define propagation, expiry, and rollback. Test mixed versions.
- **Not:** A substitute for real-time ticks, prediction, or replication—see [Multiplayer Architecture](game-programming.md#multiplayer-architecture).
