# Server-authoritative squad AI recommendation

## Context and evidence

**User-stated constraints**

- Unity 6 cooperative shooter targeting consoles, with the server authoritative.
- At most 50 enemies form squads, share sightings, reserve cover, suppress, flank,
  retreat, navigate changing obstacles, and resume after save/load.
- Deterministic input replay is required for debugging.
- Designers need visual authoring and a live explanation of every choice.
- The whole AI has a 0.7 ms CPU frame budget on target hardware.
- There is no representative profile yet.

**Unknowns that must be captured before implementation**

- Exact Unity 6 editor, AI Navigation/behavior, and networking package versions;
  server tick rate; console SKUs; number and size of squads; current navigation and
  animation conventions; and whether the 0.7 ms envelope includes native
  navigation/avoidance work.
- Whether “deterministic replay” means repeatable AI decisions on the same
  build/platform or bitwise-identical world simulation across platforms. This
  design guarantees the former at the AI-domain boundary. Unity physics and
  navigation must not be assumed bitwise deterministic across console models.

**Working assumptions**

- All 50 agents may be active in the worst-case benchmark.
- The server owns perception facts, tactical choices, reservations, movement
  validity, and damage. Clients render replicated outcomes and cannot authorize a
  choice.
- The 0.7 ms figure is treated as an end-to-end AI constraint, not as evidence
  that the proposed architecture already meets it.

## Decision

Use a **server-owned squad coordinator plus deterministic Utility AI for tactical
intent, shallow visually-authored behavior trees for reactive orchestration, and
explicit finite-state action executors**, with direct rules enforcing safety and
authority.

Each layer has one responsibility:

- direct rules enforce non-negotiable validity and provide the degradation path;
- the squad coordinator owns shared knowledge, roles, and cover leases;
- Utility AI chooses among viable intents and explains the score;
- a shallow behavior tree visually sequences the selected intent but does not
  choose strategy independently;
- small action FSMs own resumable movement, aiming, firing, and animation
  handshakes.

The runtime contracts should not depend on one graph package. Use the installed
Unity behavior tooling only if a version/AOT/console spike proves its runtime,
serialization, and debugging fit. Otherwise compile the same constrained visual
graph into immutable runtime data behind the executor interface. This keeps a
package decision reversible without changing authoritative domain rules.

## Why this fits

This problem fails the “simple component” gate: decisions compete, state crosses
agent and squad lifetimes, cover is a contested resource, behavior must be
authored visually, and save/replay/network authority constrain ordering and
persistence. It does not, however, require unconstrained runtime planning or a
learned policy.

Utility AI maps well to competing tactical choices such as suppress, flank, take
cover, advance, and retreat. It can expose eligibility, each normalized
consideration, the final score, the tie-break, and hysteresis. A shallow behavior
tree supplies the visual, reactive sequence designers need without making its
blackboard a second strategic brain. Explicit action state machines give
interrupt, cleanup, persistence, and failure semantics to Unity-facing work.

Revisit the decision if either of these becomes true:

- designers need agents to discover materially new multi-step plans rather than
  select from an authored tactic set, and a bounded GOAP spike fits the measured
  budget; or
- target profiling shows the selected graph runtime or per-agent object model is
  the limiting cost, in which case replace that adapter or prototype a
  data-oriented scoring/scheduling core. Do not adopt jobs, Burst, or ECS based on
  agent count alone.

## Alternatives compared

| Candidate | Role in this design | Why it is not the complete solution |
| --- | --- | --- |
| Direct rules | Selected for authority guards, emergency reactions, and safe fallback | Fifty coordinated agents and designer-authored competing tactics would become a dense priority chain. |
| FSM | Selected for bounded actions such as `MoveToCover`, `Suppress`, and `Flank` | A single tactical FSM would accumulate cross-transitions and make contextual preference difficult to tune. |
| HFSM | Optional only for truly shared lifecycle modes such as Alive/Disabled/Dead | As the primary chooser it still produces transition pressure; do not add it when a small lifecycle FSM is enough. |
| Behavior tree | Selected as a shallow visual executor for an already-selected intent | A monolithic tree would hide strategic competition in selector order/blackboard state and add abort/tick cost. |
| Utility AI | Selected for explainable intent and role selection | It should select, not perform long-running Unity operations; hysteresis and feasibility filtering are mandatory. |
| GOAP | Rejected initially | The named tactics are enumerable. Search expansions, world-state modeling, replanning, persistence, and debugging add risk inside a 0.7 ms envelope. |
| ML-Agents | Rejected for authoritative decisions | Training operations, reward failure, regression governance, and opaque decisions conflict with present explainability/replay needs. It could later assist offline balancing, never bypass rule guards. |
| Sentis inference | Rejected | Inference deploys a trained model; it is not a decision architecture. Latency, memory, model compatibility, and explainability are unproven and unnecessary here. |

## Architecture, ownership, and lifetimes

```text
authoritative world events / budgeted queries
                    |
                    v
        agent perception snapshots
                    |
                    v
 typed agent memory ---> typed squad memory ---> cover reservation service
                    |                |
                    +-------+--------+
                            v
              hard validity / authority rules
                            v
        squad role assignment + per-agent Utility AI
                            v
                 Intent + DecisionExplanation
                            v
            shallow visual behavior-tree executor
                            v
        finite-state action -> navigation/motor adapter
                            |             |
                            v             v
             gameplay result       presentation state
                                          |
                                    replicated clients
```

Use a feature composition root rather than globals or a service locator:

| Owner | Lifetime | Mutable responsibility | Teardown |
| --- | --- | --- | --- |
| `AiSessionRoot` | match/session | authoritative tick, scheduler, deterministic random streams, save/replay and network adapters | cancel scheduled work, flush/close traces, dispose registrations |
| `SquadRuntime` | squad spawn to disband | typed squad memory, role assignment, cover leases, coordinator cadence | release every lease and detach members |
| `AgentBrain` | one server-side agent lease | local memory, current intent, utility state, executor/action resume token | cancel action/path requests, unsubscribe, release cover, clear pooled state |
| Unity adapters | enabled component/scene | physics sensing, navigation, motor, animation handoff | symmetric enable/disable registration and post-cancel validity checks |
| Authored assets | project content | immutable tactic definitions, utility curves, thresholds, graph data | no mutable session state stored in the asset |

Create plain C# runtime instances from read-only authored assets. Stable entity,
squad, target, cover, and configuration IDs cross save and network boundaries;
scene-object references do not. Initialize agents only after the authoritative
world and navigation adapters report readiness. On disable, despawn, pooling, or
scene unload, cancel pending work before returning the object and ignore stale
results by request/version token.

### Perception and squad memory

- Prefer authoritative game events for facts already known, such as gunfire,
  damage, ally-down, and door state. Schedule spatial, field-of-view, occlusion,
  and line-of-sight queries only where simulation needs them.
- Produce immutable `PerceptionSnapshot` values. A fact contains type, subject,
  position or stable reference, source, observed tick, confidence, expiry tick,
  and visibility scope.
- `SquadMemory` is typed and squad-scoped, not a global string-key blackboard.
  Merge observations in a stable order and specify conflict rules: newer
  authoritative observation wins, ties resolve by stable source ID, and expired
  facts are removed at a deterministic tick.
- Cover is a lease, not a boolean. A reservation includes cover ID, agent ID,
  squad ID, purpose, claim tick, expiry, and generation. Claim/release is atomic
  within the authoritative scheduler. Cancellation, death, despawn, action
  failure, and load reconciliation release or revalidate it.

### Decision and action execution

Filter impossible actions before scoring: dead/disabled agents cannot choose,
invalid targets cannot be attacked, unavailable cover cannot be claimed, and
network authority is never negotiable. Immediate survival rules may preempt the
current intent, but each preemption emits a reason.

Utility candidates should be explicit (`Hold`, `TakeCover`, `Suppress`, `Flank`,
`Advance`, `Retreat`, `Regroup`). Each candidate declares:

- eligibility specifications;
- normalized, clamped considerations and authored curves;
- a deterministic aggregate and stable tie-break key;
- minimum commitment, switching cost/hysteresis, cooldown, and expiration;
- the squad role or lease it requires.

Run squad-level scoring first to choose a tactic and role envelope, then score
viable agent actions within the assignment. This avoids 50 independent agents
all deciding to flank or claiming the same cover.

Each intent owns a shallow visual tree. For example, `Flank` can validate its
lease, request a route, move, reacquire line of sight, signal readiness, and
engage. Tree nodes may read typed decision context and action results, but may not
query arbitrary services. Instrument node status, active path, last failure, and
abort source. Tick only the active branch at its scheduled cadence.

Leaf actions expose `CanStart`, `Start`, `Tick`, `Cancel`, `Succeeded`, `Failed`,
and a serializable resume token. They clean up navigation, animation waits,
subscriptions, and leases on every exit. An invalid or missing action/graph falls
back to the direct safe policy: seek valid cover if under immediate threat,
otherwise hold/regroup and report the configuration failure.

### Navigation and animation

- Strategic destination selection remains in the decision layer. A server-side
  navigation adapter owns path requests, validity, local movement, arrival,
  dynamic-obstacle invalidation, stuck detection, and recovery.
- Cap new and replacement paths through the scheduler. On failure: try a local
  repath, then alternate reserved cover, then regroup/hold. Never spin on a path
  request every frame.
- Unity navigation and physics calls remain on the supported main-thread
  boundary. Only immutable plain-data scoring may move to jobs after profiling,
  with deterministic result reduction.
- The authoritative motor owns displacement and gameplay timing. Animation,
  audio, and VFX consume a replicated presentation state. Animation events that
  gate gameplay need an explicit timeout/failure path; clients cannot turn an
  animation event into authoritative damage.

## Network authority and deterministic replay

The server owns facts, squad memory, random streams, intent selection, cover
claims, paths, action state, movement validity, and gameplay effects. Replicate a
compact presentation contract—stable agent ID, intent, target/cover ID when
needed, action phase, motor state, and animation tag—not the whole blackboard or
utility table. Full explanations can use a development-only, rate-limited debug
stream.

Make the AI decision layer deterministic by construction:

- advance on an integer authoritative `AiTick`, not render time;
- give each squad/agent a versioned deterministic random stream;
- iterate candidates and agents by stable ID, never unordered collection order;
- quantize decision inputs/scores where cross-runtime floating-point ties could
  alter the winner, and use an explicit final tie-break;
- record configuration/schema hashes and every external authoritative input;
- emit a per-decision trace/hash containing tick, input snapshot hash, viable
  candidates, scores, selected intent, tie-break, preemption, and result.

Provide two replay modes:

1. **Same-build authoritative input replay:** restore tick/config/seeds and feed
   the recorded server inputs. The AI decision-hash stream must match.
2. **Portable AI trace replay:** feed recorded canonical perception and
   navigation outcomes directly into the plain C# AI harness. This isolates AI
   determinism when physics or NavMesh results differ between hardware/builds.

Do not promise bitwise cross-platform world replay. If that is the actual
requirement, it changes the simulation and networking architecture and must be
specified separately.

## Save/load contract

Take the save at an authoritative tick barrier and persist a versioned DTO, not
Unity objects or a service graph. Store:

- AI schema/config hash, authoritative tick, squad and agent stable IDs;
- durable agent/squad facts with provenance and remaining expiry ticks;
- squad tactic, role assignments, validated cover lease IDs/generations;
- selected intent, commitment/cooldown timers in ticks, action kind, bounded
  action phase/progress, and deterministic random-stream state;
- scheduler next-due ticks and any external state required to reproduce choices.

Do not serialize raw NavMesh paths, delegates, tasks, or an arbitrary behavior
tree object graph. On load, rebuild runtime objects, remap stable IDs, validate
cover and target references, recompute paths, and resume from the action token.
If the saved branch no longer exists after a content migration, cancel it
cleanly, release its lease, and enter `Regroup` with a visible migration reason.
Resolve conflicting restored cover claims deterministically before any agent
ticks. The same snapshot also forms the basis of a late-join server state.

## Authoring and live explanations

Give designers immutable, validated assets for tactic definitions, utility
considerations/curves, thresholds, cadences, cooldowns, and shallow intent trees.
The editor should reject missing actions, duplicate stable IDs, unreachable
nodes, invalid score ranges, cycles that the runtime cannot execute, and save
schema incompatibility. Runtime copies own all mutable state, so one agent cannot
mutate shared authoring data.

The live inspector should show, for a selected squad/agent:

- current authoritative tick, scheduler priority, and last/next think tick;
- perceived facts and squad facts with source, age, confidence, and expiry;
- role and cover lease owner/generation;
- rejected candidates with the failed eligibility condition;
- every utility consideration, normalized value, weighted score, switching cost,
  winner, and human-readable reason;
- active visual-tree path, action state/progress, last failure/abort, navigation
  status, and fallback level;
- the trace/config hash used by replay.

Make this structured diagnostic data first; render it in an Editor window or
in-development overlay second. Compile verbose strings and remote debug streaming
out of release builds, while retaining inexpensive counters and profiler markers.

## Scheduling and measurable budget

Use one authoritative budgeted scheduler with stable ordering and starvation
limits. A reasonable **starting hypothesis**, to be tuned by profiling, is:

- world events and action/motor safety: every authoritative simulation tick;
- expensive visibility sensing: 5 Hz per active agent, staggered by stable ID;
- per-agent utility selection: 5 Hz, with bounded urgent-event preemption;
- squad tactic/role coordination: 2–4 Hz per squad;
- visual-tree/action progress: 10 Hz unless the active action needs a tick-level
  safety check; animation presentation remains client/frame driven;
- path requests: token-bucket limited and prioritized, initially no more than two
  new/repath requests per server frame until a target profile establishes a
  better limit.

Proposed provisional partition of the 0.7 ms envelope:

| Stage | Soft cap per server frame |
| --- | ---: |
| Perception queries/event ingestion | 0.15 ms |
| Memory expiry, merge, and reservations | 0.04 ms |
| Squad coordination and Utility AI | 0.10 ms |
| Behavior-tree/action progression | 0.08 ms |
| Navigation request orchestration | 0.10 ms |
| Trace/network bookkeeping | 0.03 ms |
| Native navigation variance and headroom | 0.20 ms |
| **Total** | **0.70 ms** |

These allocations are design targets, not measurements. Put profiler markers
around every stage and also capture native navigation/avoidance cost outside
custom markers. Record P50/P95/P99/max time, steady-state allocation bytes,
queries, candidate evaluations, tree nodes, path requests, queue depth, oldest
deferred work, decision latency, reservation conflicts, and fallback counts.

When the budget is exhausted, preserve correctness in this order:

1. run authority and immediate safety rules;
2. continue a still-valid current action;
3. defer low-priority sensing and re-evaluation in stable order;
4. reduce distant/non-engaged cadence without starving an agent;
5. cap replans and use hold/regroup rather than issue an invalid path;
6. emit a budget-degradation reason and metric.

The scheduler must specify maximum latency as well as CPU. Proposed initial gates
are one server tick for safety events, 200 ms for engaged-agent tactical response,
and 500 ms for non-engaged reevaluation; validate these against gameplay.

## Implementation sequence

1. Define plain C# facts, stable IDs, tick/random sources, decision/action
   contracts, and structured explanation/trace records.
2. Build squad memory and deterministic cover reservation with replayable unit
   tests.
3. Implement direct guards, squad role assignment, Utility AI, hysteresis, and a
   minimal safe fallback before adding visual tooling.
4. Implement one vertical tactic (`TakeCover`) through a shallow visual tree and
   resumable action FSM; then add suppress, flank, retreat, and regroup.
5. Connect server-side perception, navigation, motor, animation, and networking
   adapters behind the tested contracts.
6. Add versioned save/load and both replay modes, including migration/fallback.
7. Run the graph-runtime/package spike and the representative console benchmark;
   retain or replace the visual runtime through its adapter based on evidence.

This order keeps the architecture usable if the graph package or performance
hypothesis fails.

## Verification plan

No Unity compilation, network test, console build, or target-device profile was
available for this recommendation. The following evidence is required before the
0.7 ms claim or production readiness can be accepted.

**Plain C# tests**

- fact merge/expiry/provenance; deterministic ordering; stable random streams;
- atomic cover claim/release, simultaneous claims, lease expiry, despawn, and
  load reconciliation;
- Utility AI boundaries, monotonic curves, impossible-action filtering,
  hysteresis, switching cost, and stable tie-breaks;
- squad composition scenarios proving bounded suppress/flank/retreat role counts;
- action success/failure/interruption and cleanup; scheduler fairness,
  starvation, overload fallback, and cancellation;
- save round-trip, schema migration, invalid reference fallback, and restoration
  of timers/action tokens;
- golden same-build decision hashes and portable trace replay with deliberate
  divergence reporting.

**EditMode and PlayMode tests**

- authored graph/asset validation, serialization round-trip, and missing-node
  diagnostics;
- sensor visibility/occlusion, dynamic obstacles, unreachable/partial paths,
  stuck recovery, action cancellation, animation timeout, scene reload,
  disable/destroy, and pooled second lease;
- save during each resumable action phase and load with a moved/invalid target or
  cover point.

**Network tests**

- only the server can choose an intent, claim cover, move authoritatively, or
  apply damage;
- latency, loss, duplication, reordering, reconnect/late join, despawn during an
  action, and compact replication behavior;
- clients can animate/interpolate but cannot alter the decision trace;
- same-build authoritative input replay produces the same decision hashes.

**Target-device performance gate**

Create a representative console build with 50 simultaneously engaged agents,
the worst expected squad distribution, visibility queries, dynamic obstacles,
cover contention, path invalidation, save/load, and network replication. After
warm-up and under a documented thermal/build configuration, capture repeatable
windows on every material console SKU. If 0.7 ms is a hard worst-frame ceiling,
the maximum sample must stay below it; if it is a percentile budget, agree the
percentile first and at minimum report P50/P95/P99/max. Require zero steady-state
managed allocations from decision ticks and compare the Utility-only executor
with the proposed shallow visual-tree executor before selecting the graph
runtime.

## Risks and next checks

- **Budget feasibility is unknown.** The 0.7 ms envelope may be dominated by
  navigation/avoidance rather than decision logic. The first production gate is
  a 50-agent target-console spike with stage markers, not a framework rollout.
- **Visual package fit is unknown.** Verify the installed Unity/package versions,
  console AOT/stripping, graph serialization, live debug API, and runtime cost.
- **Replay scope is ambiguous.** Confirm same-build decision determinism versus
  cross-platform bitwise simulation before promising the latter.
- **Save migration can invalidate running graphs.** Stable action IDs, bounded
  resume tokens, validation, and a safe `Regroup` fallback are mandatory.
- **Over-composition is a real risk.** Keep strategic choice only in Utility AI,
  orchestration only in the shallow tree, and engine progress only in action
  FSMs. Remove any layer that starts duplicating another layer's decision.

The immediate next step is a vertical `TakeCover` spike on the actual server
build: one squad memory, deterministic cover leases, Utility choice with a live
reason trace, one visually-authored executor, save/replay, and target-console
markers. Its profile and designer review decide whether the visual runtime and
provisional cadences are retained.
