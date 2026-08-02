# Unity artificial intelligence systems

Use this reference to design runtime game AI, not to select the most elaborate
algorithm. Begin with player-visible behavior, decision cadence, authority, and a
measurable budget. Confirm package APIs against the project's installed Unity and
package versions.

## Define the behavioral contract

Before choosing an approach, write observable examples:

- What can the agent sense, and with what delay or uncertainty?
- What facts may it remember, forget, or share?
- Which decisions must appear intentional to the player?
- Which actions can be interrupted, retried, or fail?
- Who is authoritative in multiplayer?
- What must save/load and replay reproduce?
- How many agents run, how often do they think, and on which target device?
- Which designer/debugger must understand and tune the behavior?

Translate subjective goals such as “smart” into metrics: reaction latency,
decision stability, path requests per second, planning nodes expanded, navigation
failures, action success rate, CPU time, allocation rate, or player-facing
outcomes.

## Complete AI pipeline

Treat AI as a pipeline with explicit contracts. A decision algorithm alone is not
an AI system.

```text
world -> perception -> memory / blackboard -> decision -> action execution
          ^                                       |             |
          |                                       v             v
          +---------------- feedback ---------- navigation -> animation
```

### Perception

Perception converts authoritative world state and sensor queries into facts. Use
events for discrete knowledge already available to the game; use budgeted physics,
visibility, or spatial queries only when simulation requires them.

Define range, field of view, occlusion, refresh cadence, confidence, affiliation,
and forgetting. Batch or stagger expensive sensors. A sensor reports evidence; it
does not decide an action.

### Memory and blackboard

Memory owns facts across decision ticks. Give facts provenance, timestamp,
confidence, expiry, and scope (agent, squad, faction, world). A blackboard is useful
when several decision/action nodes share typed state, but an untyped global map
becomes a hidden Service Locator.

Separate authored knowledge from runtime memory. Decide which facts save, replicate,
or replay and which may be recomputed.

### Decision

Decision policy maps current state and memory to an intent. Keep it separate from
movement, animation, and effects so it can be tested over plain C# inputs. Define
how often it runs, what preempts it, and how it resolves ties.

### Action

Actions turn intent into bounded work. Each action should expose preconditions,
start, progress, success, failure, cancellation, cleanup, and an observable reason
for termination. An interrupted action must release reservations, event handlers,
paths, and animation state.

### Navigation

Navigation owns path requests, path validity, local movement, avoidance, arrival,
stuck detection, and recovery. Keep strategic destination choice in decision policy
and locomotion mechanics in navigation/motor adapters. Validate Unity AI Navigation
or third-party package behavior against the installed version and target scene.

### Animation and presentation

Animation presents state but should not silently own authoritative decisions. Use
explicit signals for animation-gated actions, handle missing/interrupted events,
and define whether root motion or gameplay simulation owns displacement. Audio,
VFX, gaze, and bark systems consume intent/state through narrow presentation
contracts.

## Selection matrix

Choose the lowest mechanism that handles the real branching and authoring forces.

| Approach | Strong fit | Weak fit / cost | Authoring and observability |
|---|---|---|---|
| Direct rules | few decisions, clear priority, tutorial or prototype behavior | dense interacting branches | code/table is easy to trace while small |
| Finite State Machine (FSM) | small mutually exclusive modes with explicit transitions | transition explosion and cross-cutting conditions | state/transition log is straightforward |
| Hierarchical Finite State Machine (HFSM) | related states share parent behavior or transitions | deep hierarchy hides transition ownership | visualize active leaf plus parent chain |
| Behavior Tree | reactive hierarchical tasks and designer-authored composition | hidden blackboard coupling, abort complexity, per-node overhead | live node status and abort reason are essential |
| Utility AI | competing goals/actions need contextual scoring | opaque score curves or oscillation | expose normalized considerations and final score |
| GOAP | agents must compose action sequences toward symbolic goals | large or volatile search spaces, world-state modeling cost | show goal, plan, cost, failed precondition, expansions |
| Specification | complex reusable predicates and target filtering | side-effecting predicates or allocation-heavy combinators | report which predicate rejected a candidate |
| ML-Agents policy | behavior can be trained in a stable simulation with a measurable reward | reward hacking, sim-to-game drift, opaque failures, training operations | track reward, observations, action distribution, checkpoints |
| Sentis/runtime inference | a validated trained model must run locally in Unity | a hand-authored rule would be cheaper or explainability is mandatory | record model/version, input contract, latency, fallback |
| Hybrid | different layers have different strengths | unclear ownership and duplicated decisions | trace the boundary and arbitration between layers |

These are alternatives and composition tools, not a maturity ladder.

## Direct rules

Start with direct rules when behavior has a handful of decisions. Keep priority
explicit and return a reason:

```text
if immediate threat and can evade -> Evade (reason: threat)
else if target visible and can fire -> Fire (reason: clear shot)
else -> Patrol (reason: no target)
```

Extract reusable predicates or a table only after duplication or tuning needs
appear. Direct rules are often the most professional answer for bounded behavior.

## Finite state machines

A Finite State Machine owns one active state and explicit transitions. Put entry,
tick, exit, and transition reasons behind a testable state context. Avoid states
directly reaching into arbitrary Unity objects.

Use a Hierarchical Finite State Machine when several states genuinely share parent
behavior, such as `Combat > Aim/Fire/Reload`. Define which level evaluates
transitions and how interruption propagates. If most logic is conditional task
sequencing rather than modes, a Behavior Tree may fit better.

## Behavior trees

A Behavior Tree composes conditions and tasks using control-flow nodes such as
sequence, selector, parallel, and decorators. Its strength is reactive hierarchical
execution; its risks are implicit blackboard dependencies, abort semantics,
per-frame traversal, and node lifecycle bugs.

- Define node statuses and cancellation/abort behavior.
- Make node memory ownership explicit.
- Use typed blackboard keys or generated bindings when available.
- Budget tree ticks; not every agent needs a full traversal every frame.
- Instrument the active path, last failure, and abort source.
- Validate the installed Unity Behavior package or chosen framework rather than
  assuming APIs from a different version.

## Utility AI

Utility AI scores candidate actions from considerations. Normalize inputs, make
curves authorable, and log every component of the winning score. Add hysteresis,
commitment time, cooldown, or switching cost to prevent oscillation.

Test monotonicity and boundary values of considerations. Keep action feasibility
separate from preference: first filter impossible actions, then score viable ones.
For squads, decide whether utility is computed per agent or by an authoritative
coordinator.

## GOAP

Goal-Oriented Action Planning searches over symbolic state using action
preconditions, effects, and costs. It is justified when useful plans must emerge
from reusable actions and cannot be enumerated economically.

- Keep the symbolic state compact and deterministic.
- Separate planning from action execution; the world can invalidate a plan.
- Replan on meaningful invalidation, not automatically every frame.
- Bound nodes, time, memory, and replans per scheduling budget.
- Run background planning only over thread-safe snapshots and marshal the result
  to the main thread.
- Log selected goal, plan, cost, search expansions, and failure reason.

A fixed action sequence, FSM, or Behavior Tree is preferable when plans are known
and designer control matters more than emergence.

## Specification and combinators

Specification encapsulates a predicate and may compose it with AND, OR, and NOT.
It is useful for target selection, rule eligibility, inventory constraints, or
planner preconditions shared across systems.

Keep specifications pure. Avoid hidden scene queries, mutable global dependencies,
and per-frame allocations. Provide diagnostic evaluation when designers need to
know which condition failed. A plain function is sufficient when the predicate is
local and not reused or composed.

## ML-Agents and learned policies

Use Unity ML-Agents when learning is part of the product strategy and the team can
own environment design, training, evaluation, model governance, and regression.
Before adoption, define:

- observations, normalization, action space, reward, episode reset, and curriculum;
- baseline scripted policy and acceptance metrics;
- training seeds, environment/package versions, and checkpoint provenance;
- adversarial and out-of-distribution tests;
- runtime inference budget and a safe fallback;
- who retrains and validates after gameplay changes.

Training success is not gameplay acceptance. Evaluate trained policies on held-out
seeds and player-relevant scenarios. Check the current ML-Agents documentation and
compatibility matrix for the installed Unity version.

## Sentis and runtime inference

Sentis/runtime inference is a deployment mechanism for supported trained models,
not an AI design by itself. Validate model import, operators, backend, numeric
behavior, memory, warm-up, latency, batching, and target-platform support in the
installed Unity version.

Version the model together with its input/output schema and preprocessing. Define
a timeout/failure fallback and never let a model output bypass authoritative game
rules. Do not claim target viability from Editor inference timings.

## Useful hybrid designs

Hybrids work when each boundary has one clear responsibility:

- **HFSM + Behavior Tree:** HFSM owns high-level mode; a tree executes the active
  mode's reactive tasks.
- **Utility AI + actions:** utility selects an intent; a bounded action state
  machine executes and reports outcome.
- **GOAP + FSM actions:** GOAP selects symbolic action sequence; FSMs execute each
  action safely.
- **Behavior Tree + Specification:** pure specifications implement reusable
  conditions and target filters.
- **Squad coordinator + individual AI:** server-authoritative coordinator assigns
  roles/targets; each agent executes locally within that assignment.
- **Learned policy + rule guardrails:** inference proposes; deterministic rules
  validate safety, authority, and feasibility.

A hybrid must say which layer wins on disagreement and how the decision appears in
a trace. Avoid stacking mechanisms merely to showcase patterns.

## Cross-cutting selection dimensions

Evaluate every candidate against:

- **Authoring:** Who changes behavior, in which tool, with what validation and
  merge-conflict cost?
- **Observability:** Can a developer inspect sensor facts, memory, chosen option,
  score/plan, action status, and failure reason at runtime?
- **Determinism:** Are ordering, random seed, time source, and numeric assumptions
  explicit enough for tests, replay, or networking?
- **Network authority:** Which peer selects intent, validates action, owns
  navigation, and replicates presentation state?
- **Scheduling budget:** What runs on events, fixed ticks, staggered updates,
  background snapshots, or every frame?
- **Save and replay:** Which memory, active state, goals, plan/action progress,
  random state, and model/version identifiers must persist?
- **Measurable budget:** What CPU time, allocation, path requests, planner
  expansions, inference latency, and agent count must be met on target hardware?

## Scheduling and scale

Assign separate cadences to sensing, thinking, navigation, and presentation. Near
or important agents may update more often; distant agents may use reduced
simulation only if gameplay correctness permits it.

Use a scheduler only when profiling or scale requires one. It must define:

- priority and starvation behavior;
- maximum work per frame/tick;
- deterministic ordering when required;
- cancellation when agents despawn or pool;
- what happens when the budget is exceeded;
- metrics for queue depth, latency, and dropped/deferred work.

Do not move Unity physics or navigation APIs to worker threads without documented
thread safety. Jobs may process compatible data snapshots; apply results at a safe
main-thread boundary.

## Multiplayer authority

For networked AI, decide explicitly:

- the server/host usually owns authoritative perception, decision, damage, and
  durable state;
- clients receive compact state/intent and present interpolation, animation, and
  effects;
- client prediction, if any, has reconciliation and cannot grant authority;
- shared squad memory has one conflict-resolution policy;
- random seeds and command ordering are owned by the authority;
- bandwidth and update-rate budgets are part of the AI design.

Replicate meaningful state or intent, not an entire blackboard by default. Test
latency, packet loss, join-in-progress, authority migration if supported, and
despawn during an action.

## Save and replay

Persist only state required to resume the contract. Depending on the approach,
that may include the active state path, durable memory, current goal, action
progress, reservations, random state, and model/schema version. A plan can often
be recomputed after load, but only if recomputation is deterministic enough and
has the same world facts.

Version serialized AI state and provide migration/fallback behavior. Replays must
record authoritative inputs and version metadata; do not assume engine physics is
bitwise identical across platforms.

## Testing and evidence

Build a plain C# test harness for perception facts, decision inputs, and action
contracts. Then add the minimum engine integration tests.

- Direct rules/FSM/HFSM: transition table, invalid transitions, interruption,
  enter/exit symmetry.
- Behavior Tree: statuses, aborts, running-node memory, failure propagation.
- Utility AI: score boundaries, dominance, ties, hysteresis, impossible-action
  filtering.
- GOAP: expected plan, no-plan case, bounded search, invalidation, action failure.
- Specification: truth tables, composition, diagnostics, allocation behavior where
  hot.
- Navigation/action: unreachable destination, partial path, stuck recovery,
  cancellation, despawn, pooled reuse.
- Learned/inference: held-out scenarios, deterministic preprocessing, model
  compatibility, latency/memory, fallback.
- Network: authority, reconciliation, late join, loss/latency, replay/save schema.

Profile a representative build on the target device with representative agent and
content counts. Report Editor-only numbers as exploratory. If measurement cannot
be run, label performance conclusions as hypotheses and give a concrete capture
plan.

## AI decision record

Return an AI recommendation with:

```text
Behavioral contract:
Pipeline ownership:
Selected approach and why:
Rejected simpler/complex alternatives:
Authoring and observability:
Determinism and network authority:
Scheduling budget and measurable budget:
Save and replay contract:
Tests and target-device evidence:
Risks and revisit triggers:
```
