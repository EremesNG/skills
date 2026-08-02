# Recommended architecture

Use a deterministic, server-authoritative hybrid rather than one universal AI technique:

- **Direct rules** enforce safety and provide the overload/failure fallback.
- An **HFSM** controls coarse modes such as `Patrol`, `Investigate`, `Engage`, `Retreat`, and `Disabled`.
- **Utility scoring** selects the current tactical action inside a mode and naturally provides a ranked explanation.
- Small, bounded **behavior trees** execute authored multi-step actions such as flank, suppress, revive, and retreat.
- A **squad controller and shared blackboard** coordinate sightings, roles, cover claims, suppression lanes, and squad intent.

Do not put GOAP, ML-Agents, or runtime inference on the critical path initially. They add planning or inference cost, complicate deterministic replay, and are harder to explain. Keep clean interfaces so a measured experiment can add one later without replacing the whole stack.

The 0.7 ms target cannot be claimed as achievable until a representative 50-agent console scenario exists. Treat all update rates and sub-budgets below as provisional limits to validate on the slowest target console.

## Why this mix

| Technique | Strengths here | Weaknesses here | Recommended role |
|---|---|---|---|
| Direct rules | Cheapest, deterministic, easy to test | Becomes tangled when used for all tactics | Invariants, interrupts, and safe fallback only |
| FSM/HFSM | Predictable transitions, compact serialized state, low runtime cost | State explosion if every tactic is modeled as a state | Top-level mode and high-priority reactions |
| Behavior tree | Visual authoring and readable execution flow | Unbounded traversal and reactive reevaluation can waste budget; shared coordination is awkward | Short, bounded action execution trees |
| Utility AI | Selects among many context-dependent actions; scores explain decisions | Requires disciplined normalization and tie-breaking | Primary individual tactical selector |
| GOAP | Can synthesize flexible plans from goals and world state | Search cost, plan churn, save/load complexity, and less direct designer control | Optional later experiment for low-frequency squad planning only |
| ML-Agents | Useful for training policies or tuning behavior through simulation | Runtime policy is opaque, difficult to reproduce exactly, and costly to validate | Offline experimentation; not the authoritative decision layer |
| Sentis inference | Can run a trained model locally | Platform-dependent latency and weaker explainability/determinism | Optional non-authoritative hint later, always behind a deterministic fallback |

The important boundary is that coordination belongs to the squad layer, while individual agents choose and execute actions. Fifty independent planners negotiating through incidental events would be more expensive and harder to reason about.

## Measurable runtime pipeline

Run gameplay AI on a fixed server tick. Movement may update every simulation tick, but expensive sensing and decision work is time-sliced into deterministic buckets based on stable agent IDs. Urgent events can request an early update, subject to a hard per-tick cap.

### 1. Perception

- Feed hearing, damage, ally reports, and objective changes through events.
- Batch visual queries at a lower rate, with near/engaged agents refreshed more often than distant agents.
- Use a spatial index before line-of-sight checks; never compare every agent with every possible target.
- Write observations as compact facts: stable target ID, position, confidence, source, and server tick.
- Decay confidence by ticks, not wall-clock time. Sort query results and resolve equal-priority observations by stable ID.

Suggested starting cadence, subject to profiling: engaged visual sensing at 5-10 Hz, idle sensing at 1-2 Hz, with immediate damage/hearing events. Cache query buffers and avoid per-update allocations.

### 2. Squad memory and coordination

Each squad owns a server-only blackboard containing:

- sightings with confidence and expiry;
- current objective and squad posture;
- assigned roles and sectors;
- cover reservations with claimant, lease expiry, and generation number;
- suppression lanes and flank corridors;
- requests such as `NeedCover`, `NeedSuppressor`, or `Regroup`.

The squad controller merges reports and assigns broad intent at a low frequency, initially 1-2 Hz. Agents read an immutable snapshot for their decision tick. All writes go through explicit commands so reservation rules are testable. A cover claim must be an atomic server operation; it expires automatically and is released on death, state exit, path failure, or squad removal.

### 3. Decision

The HFSM first establishes what is legal. Hard guards such as dead, stunned, weapon unavailable, unreachable destination, or retreat threshold remove candidates before scoring.

Within the active mode, utility considerations score actions such as:

- hold and fire;
- suppress;
- claim cover;
- advance;
- flank left/right;
- retreat;
- regroup;
- reload or revive.

Normalize all considerations to a documented range, clamp outputs, and use stable tie-breaking. Add hysteresis, minimum commitment time, and explicit interrupt rules to prevent oscillation. Recompute ordinary decisions at roughly 2-5 Hz; allow damage, invalid cover, target loss, or squad-order changes to trigger bounded reevaluation.

Record a compact decision trace: tick, HFSM mode, eligible and rejected actions, scores, decisive inputs, winner, tie-break, and interruption reason. A development-only live inspector can show the top candidates and the active behavior-tree path. Sample traces into a fixed-size ring buffer so observability cannot allocate or grow without bound.

### 4. Action execution

Each selected action starts a small behavior tree or explicit task sequence. Nodes return `Running`, `Success`, or a typed failure such as `NoPath`, `ReservationLost`, `TargetInvalid`, or `TimedOut`. Trees must have traversal and node-execution limits per tick. Long operations yield instead of spinning.

Designers author data assets for score curves, thresholds, HFSM transitions, and action trees. Runtime state lives per squad or per agent, never in a shared authoring asset. Validate assets in the editor for missing blackboard keys, impossible transitions, invalid action references, and unbounded loops.

### 5. Navigation and dynamic obstacles

- Use a server-owned navigation service. Actions submit requests; they do not call pathfinding opportunistically from every decision node.
- Queue and cap new path requests per tick. Prioritize agents whose current path is invalid or whose action is urgent.
- Reuse a valid corridor until its destination, obstacle generation, or tactical constraint changes materially.
- Use cover points with stable IDs and accessibility metadata. Validate reachability before completing a reservation.
- Use local avoidance for moving agents; reserve obstacle carving for obstacles that are sufficiently stationary, because frequent carving can cause expensive rebakes and path churn.
- On path failure, invalidate the candidate, release its reservation, and choose a bounded alternative. Never retry indefinitely in the same tick.

Navigation and physics may prevent bit-identical cross-platform replay. For reliable debugging, record relevant path results, obstacle-generation changes, and perception facts, or restrict exact replay to the same build and platform. Do not describe whole-simulation replay as deterministic until it has been measured and hash-verified.

### 6. Animation and presentation

AI emits semantic commands such as desired velocity, stance, aim target, fire request, and action phase. A movement/weapon authority validates gameplay consequences on the server. Animation consumes replicated semantic state on clients; animation events must not be the sole authority for shots, damage, reservations, or state transitions.

Replicate stable action and phase IDs where useful for coherent presentation. Let clients interpolate authoritative motion rather than run a second tactical brain.

## Networking, replay, and persistence

The server owns perception, blackboards, cover claims, decisions, navigation intent, weapon authorization, and outcomes. Clients receive only the state needed for presentation: entity transform snapshots, stance, aim/fire state, current semantic action, and significant cues. Do not replicate the entire blackboard or utility table every frame; expose those through authenticated development diagnostics when needed.

For deterministic decision replay:

- run decisions on a fixed tick;
- seed independent RNG streams by match, squad, and agent;
- use stable iteration order and stable tie-breaking;
- avoid frame time, unordered collections, and global random state in authoritative decisions;
- quantize or otherwise define score comparisons at boundaries;
- record player inputs plus exogenous facts that the AI consumes;
- periodically store a canonical state hash and diagnostic checkpoint.

If pathfinding or physics results are not deterministic, capture those inputs in the replay log. This yields a reproducible **AI decision replay** even when the entire Unity simulation is not bit-identical.

Save versioned, engine-independent DTOs identified by stable IDs. Persist squad objective/posture, useful memory facts, agent HFSM mode, current action ID and resumable action data, cooldowns, health/loadout state, and deterministic RNG state. Do not serialize component references or active navigation paths. Load in stages:

1. Restore entities and stable IDs.
2. Restore squad and agent logical state.
3. Resolve references.
4. Revalidate targets, cover, and world facts.
5. Rebuild paths and reservations.
6. Resume a compatible action or enter a documented safe state.

A stale or missing cover point after load should not corrupt the tree: release the old claim, emit a typed restore reason, and select cover again.

## Scheduling and the 0.7 ms budget

Use a budgeted scheduler with instrumentation around every stage. A provisional envelope for the complete server AI tick is:

| Stage | Provisional CPU cap |
|---|---:|
| Perception filtering and LOS dispatch | 0.18 ms |
| Squad memory and reservations | 0.08 ms |
| HFSM and utility decisions | 0.16 ms |
| Action execution | 0.10 ms |
| Navigation request management | 0.08 ms |
| Animation/network intent packaging | 0.03 ms |
| Diagnostics and headroom | 0.07 ms |
| **Total** | **0.70 ms** |

These are investigation targets, not evidence. Establish exactly whether navigation/physics work charged elsewhere is included in the 0.7 ms accounting.

Track per stage and per agent: invocation count, elapsed CPU, maximum queue depth, deferred jobs, LOS queries, paths requested, tree nodes visited, utility candidates scored, action churn, failed reservations, and allocation bytes. Acceptance should be based on target-console captures with 50 active agents, dynamic obstacle churn, combat effects, networking, and a representative scene—not editor measurements.

For the hot path, prefer compact data, preallocated buffers, cached lookups, and pure scoring functions. Avoid LINQ, reflection, per-tick delegates/closures, string-keyed lookups, and logs in release builds. Jobify or Burst-compile only data-oriented work that profiling shows is material; Unity object access remains on the appropriate engine thread.

Suggested acceptance gate:

- 0.70 ms or less at the agreed percentile and frame window on the slowest target console;
- zero steady-state managed allocations in the AI hot path;
- no scheduler backlog growing across a sustained worst-case encounter;
- bounded maximum path requests, LOS tests, and BT node visits per tick;
- no gameplay divergence in decision-replay hashes for the supported replay configuration.

The team must choose and document whether 0.70 ms means maximum, p99, or p95. I would use p95 as the normal gate plus a separate hard scheduler cap and report p99/max spikes.

## Degradation and fallback behavior

When the scheduler exhausts its budget, degrade predictably:

1. Defer distant/non-engaged visual refreshes.
2. Reuse a still-valid decision and path.
3. Reduce squad and utility reevaluation frequency.
4. Skip optional flank replans and cosmetic look/gesture choices.
5. Enter a cheap direct-rule behavior: maintain valid cover, face the last credible threat, fire only when authorized, or retreat toward a known reachable rally point.

Never defer death/stun processing, reservation release, weapon authority, network ownership changes, or save consistency. Every deferred item needs an age limit; starvation should be visible in telemetry. GOAP or inference experiments must have a timeout/circuit breaker and fall back to the same deterministic utility/HFSM route.

## Testing and rollout

Build most of the decision layer as plain C# so it can be tested without scenes.

### Automated correctness tests

- HFSM transition guards, priority, interrupts, and serialization.
- Utility normalization, clamping, hysteresis, stable ties, and trace reasons.
- Blackboard merge/decay and atomic cover-lease invariants.
- Behavior-tree node limits, cancellation, timeout, and typed failure propagation.
- Save/load round trips, schema migration, stale reference recovery, and mid-action resume.
- Seeded RNG and stable ordering across repeated decision runs.
- Navigation-service behavior for no path, moved obstacle, lost reservation, and queued timeout.

### Integration and simulation tests

- Headless server scenarios for 1, 10, and 50 agents.
- Two squads contesting the same cover; suppression enabling a flank; leader death; late join; disconnect; and save/load during each action phase.
- Dynamic obstacle churn, blocked exits, missing targets, and all cover unavailable.
- Network latency/loss tests confirming that clients cannot claim cover or authorize damage.
- Recorded replay runs checked against per-tick state hashes and the first divergent decision trace.
- Long soak tests for memory growth, reservation leaks, stuck actions, decision oscillation, and scheduler starvation.

### Performance tests

Create a reproducible benchmark scene before locking the architecture. Capture warm and cold runs on each target console, with development instrumentation separated from release measurements. Report distributions rather than a single average, including per-stage p50/p95/p99/max, allocations, query counts, and deferred work. The current absence of a representative profile is an explicit release risk and prevents declaring the 0.7 ms requirement met.

## Implementation sequence

1. Build the benchmark scenario, telemetry, fixed-tick scheduler, and deterministic trace format.
2. Implement squad memory, cover leasing, direct-rule fallback, and persistence DTOs.
3. Add HFSM plus utility decisions as pure C# with unit and replay tests.
4. Add bounded visual behavior trees for only the multi-step actions that need them.
5. Integrate navigation, movement, animation intent, and network replication.
6. Profile on target consoles and adjust rates/budgets based on measured bottlenecks.
7. Only then run isolated GOAP or inference experiments against the same quality, explainability, replay, and CPU gates.

This architecture gives designers visual control and live explanations while keeping the authoritative path cheap, bounded, serializable, and debuggable. Its central contract is that every sophisticated layer can fail or be deferred without losing a deterministic, testable fallback.
