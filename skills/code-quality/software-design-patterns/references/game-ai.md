# Game AI Architectures
Compare decision models by authoring pressure, runtime cost, and interruption contracts; these solve different problems, not maturity stages: start with the smallest that fits.

## Choosing an AI Architecture
Use existing engine behavior tools before owning an editor, scheduler, or debugger; separate sensing, choosing, and execution before replacing the chooser.

| Observed signal | Architecture | Main added cost |
| --- | --- | --- |
| Few stable modes, explicit transitions | Enum FSM | Quadratic possible transition growth; guard upkeep |
| Related modes repeat transitions/setup | Hierarchical FSM | Ancestor entry/exit and event priority |
| Temporary behavior must resume its caller | Pushdown automaton | Suspended resources, stack bounds, resume validity |
| Reusable tasks with reactive priorities | Behavior tree | Traversal/re-evaluation and cancellation semantics |
| Several tasks share observations | Blackboard alongside a chooser | Hidden dependencies, ownership, freshness |
| Runtime facts require new action sequences | GOAP | Symbolic modeling, search branching, replanning budget |
| Designers can prescribe decompositions | HTN | Method authoring, recursion, backtracking |
| Continuously competing needs | Utility AI | Score calibration, evaluation frequency, oscillation |

Compare a representative encounter's authoring effort and runtime budget; trace inputs, rejected alternatives, and interruption reasons, including failure/recovery.

## Finite State Machine
- **Choose when:** Few persistent modes make behavior easy to trace, serialize, and test.
- **Simpler first:** Use conditionals or an enum; introduce state objects only when mode-specific work needs separate ownership.
- **Cost:** N states permit N² directed transitions including self-transitions: quadratic, not exponential. Sparse graphs can remain cheap; repeated guards signal [hierarchy](#hierarchical-state-machine).
- **Contract:** Specify transition priority, transitions allowed per update, and exit/entry order. Concurrent machines must arbitrate conflicting actions.
- **Traps:** Test simultaneous guards and interruption cleanup; separate state storage does not make actions independent.

## Hierarchical State Machine
- **Choose when:** Related modes repeat transitions or setup; parents consolidate rules that a flat FSM would duplicate.
- **Simpler first:** Keep small FSMs flat; choose a [tree](#behavior-tree) when reusable tasks, not mode families, dominate.
- **Cost:** Less guard duplication, but ancestor lifecycle, propagation, transition scope, and history are harder to trace.
- **Contract:** Define child-versus-parent priority, whether handled events propagate, and ancestor exit/entry ordering. History restores a child, not its valid execution context.
- **Traps:** Revalidate targets, timers, and actions on resume; test competing parent/child guards and interrupted history.

## Pushdown Automaton
- **Choose when:** Nested temporary behavior needs last-in-first-out resumption, avoiding return transitions to every caller.
- **Simpler first:** Save one previous-state value for one interruption level; upgrade when interruptions can nest.
- **Cost:** Fewer return edges than an FSM, but suspended resources and caller contexts persist until resumed or discarded.
- **Contract:** Assign push/pop ownership, maximum depth, empty-stack behavior, suspend-versus-exit semantics, and death/teardown cleanup. Revalidate before resume.
- **Traps:** Test nested interrupts and death while suspended; release invalid reservations. Use fresh selection instead when current needs should override remembered callers.

## Behavior Tree
- **Choose when:** Reactive priorities and reusable tasks outgrow FSM transition wiring.
- **Simpler first:** Keep a few stable modes as an FSM; upgrade for task reuse, not a visual diagram.
- **Cost:** Traversal/re-evaluation consumes CPU; memory versus reactive selectors trade continuation against responsiveness. Trace large trees.
- **Contract:** Define tick/event re-evaluation and abort rules for running branches; cancellation releases action resources. Parallel composites need completion thresholds and sibling cancellation, not necessarily threads.
- **Traps:** Test priority changes during running actions and cancellation cleanup; implicit blackboard-key dependencies undermine subtree reuse.

## Blackboard
- **Choose when:** Several tasks consume shared observations or sensing and decisions run at different cadences.
- **Simpler first:** Pass arguments or an immutable perception snapshot; upgrade when repeated sharing outweighs hidden dependencies.
- **Cost:** Decouples producers/consumers, unlike parameters, but requires ownership/freshness tooling; it does not choose actions.
- **Contract:** Use typed keys, declared writers/readers, timestamps/expiry, and unknown-versus-false semantics. Separate per-agent knowledge from deliberately shared observations.
- **Traps:** Stale sightings are not world truth; test expiry, destroyed targets, and conflicting writers. Never leak unobserved world truth into private knowledge.

## GOAP
- **Choose when:** Runtime facts require new goal-reaching sequences, not selection among authored tasks.
- **Simpler first:** Use a function, FSM, or tree; upgrade when action ordering varies with resources.
- **Cost:** Symbolic preconditions/effects and branching search cost more modeling/runtime than authored control flow; trace alternatives and costs.
- **Contract:** Budget/time-slice search, cap simultaneous replans, invalidate cached assumptions, and revalidate each action. Predicted effects are not confirmed outcomes.
- **Traps:** Replanning every tick exhausts budgets; define no-plan fallback and failure backoff. Test execution failure and mid-plan target loss.

## HTN Planning
- **Choose when:** Designers prescribe procedures but runtime conditions select decompositions; methods constrain search more than [GOAP](#goap).
- **Simpler first:** Use a sequence or tree for one procedure; upgrade when conditional task decomposition itself becomes reusable authoring knowledge.
- **Cost:** Method authoring and backtracking replace some open-ended search; HTN is not automatically cheaper than GOAP.
- **Contract:** Budget/time-slice decomposition; distinguish planning from execution failure. Specify retry-method, replan-parent, and abandon-goal policies.
- **Traps:** Recursive methods may never reach primitives; bound recursion/backtracking. Test exhausted budgets and failures after partial execution.

## Utility AI
- **Choose when:** Competing needs make priority ladders brittle; scores express trade-offs rather than fixed task order.
- **Simpler first:** Use priorities or an FSM; upgrade when choices depend on continuously varying preferences.
- **Cost:** Candidates × considerations × evaluation frequency, plus curve calibration; score products penalize extra considerations and zero can veto.
- **Contract:** Gate hard feasibility/safety before scoring; normalize deliberately and use reproducible tie-breaking/randomness. Log inputs, curve outputs, and totals.
- **Traps:** Near-equal scores oscillate: add commitment windows, inertia, hysteresis, or cooldowns. Test stability without sacrificing emergency interruption.

## Hybrid Architectures
- **Choose when:** Distinct problems need distinct owners: utility ranks goals, a planner sequences, a tree/FSM executes; this stack is optional.
- **Simpler first:** Keep one model until a demonstrated boundary or authoring bottleneck justifies another.
- **Cost:** Multiple clocks, stores, and abort policies complicate attribution; constituent costs remain.
- **Contract:** Assign action/resource authority, cadence, lifetime, cancellation, and completion per layer. Goal/plan IDs prevent late completion advancing obsolete work.
- **Traps:** Test target loss, destruction, and repeated failure across layers; never let planner and executor independently issue movement.
