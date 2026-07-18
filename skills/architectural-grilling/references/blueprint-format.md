# Decision Blueprint Format

Use this format only after the user confirms the decision map is complete. Adapt section depth to the initiative, but preserve the distinction between evidence, decisions, commitments, and managed uncertainty.

# <Initiative or Decision Name>

## 1. Executive verdict

State one verdict: **proceed**, **proceed conditionally**, **pivot**, **pause**, or **stop**.

Summarize:

- the problem and intended outcome;
- the chosen direction;
- why it wins over the strongest alternative;
- the largest accepted trade-off;
- conditions that would change the verdict.

## 2. Outcomes and evidence

Record:

- target actors and current pain;
- evidence and current workaround;
- desired outcomes and measurable success signals;
- baseline, target, measurement window, and owner;
- kill, pause, and pivot criteria.

Do not present an aspiration as evidence.

## 3. Scope and boundaries

List:

- included outcomes and principal journeys;
- smallest valuable or learning slice;
- explicit non-goals;
- future possibilities that are not current commitments;
- organizational, system, and trust boundaries.

## 4. Constraints and managed uncertainty

Separate:

- verified hard constraints;
- preferences;
- accepted assumptions;
- evidence-gated decisions;
- approved deferrals.

For every evidence gate or deferral include owner, deadline or trigger, safe default, decision rule, and risk if unresolved. Never use this section to hide an open decision.

## 5. Domain and experience model

Capture:

- canonical actors, terms, entities, and responsibilities;
- permissions and decision authority;
- core and failure journeys;
- lifecycle states, transitions, invariants, and manual overrides;
- important edge cases and precedence rules.

Use a compact state or flow diagram only when it materially clarifies three or more relationships or transitions.

## 6. Architecture

Describe:

- system context and external dependencies;
- modules or bounded contexts and their responsibilities;
- interfaces, data ownership, and interaction style;
- source of truth, consistency, failure, retry, reconciliation, and recovery behavior;
- deployment units, scaling triggers, and operational ownership;
- selected frameworks, platforms, and vendors with version-sensitive facts cited;
- migration path and exit strategy.

Trace each nontrivial choice to a quality driver or constraint. Prefer a diagram plus concise prose when the relationships are otherwise hard to follow.

### Alternatives considered

For each serious alternative, record:

- what it optimizes;
- why it was rejected;
- when it would become the better option;
- reversibility and switching cost.

Always include the simplest credible baseline.

## 7. Quality, security, and operations

Record only relevant measurable commitments:

- performance, load, availability, durability, consistency, and recovery targets;
- privacy, threat, authorization, audit, abuse, and compliance controls;
- accessibility and interoperability commitments;
- telemetry, service-level indicators, alerts, runbooks, on-call, support, backup, and restore;
- cost ceilings and unit economics.

Identify the owner and verification method for every critical commitment.

## 8. Delivery plan

Use outcome-oriented milestones or thin vertical slices. For each include:

| Milestone | Outcome or risk retired | Dependencies | Owner | Estimate range and confidence | Acceptance evidence |
| --- | --- | --- | --- | --- | --- |

Then state:

- critical path and external lead times;
- team capacity and skill gaps;
- contingency and what triggers it;
- scope-removal order if time or budget is fixed;
- decision and stakeholder cadence.

Avoid false precision. Explain the assumptions behind ranges.

## 9. Verification and release

Define:

- test strategy at stable interfaces;
- contract, integration, migration, performance, resilience, security, accessibility, and manual validation as relevant;
- environments and production-like evidence;
- pilot, feature flags, canary stages, and go/no-go gates;
- data migration, compatibility, cutover, reconciliation, and rollback;
- adoption, documentation, training, and support readiness;
- legacy decommission conditions.

## 10. Risk register

| Risk | Probability | Impact | Early signal | Prevention or mitigation | Contingency | Owner |
| --- | --- | --- | --- | --- | --- | --- |

Call out accepted risks explicitly. Do not use generic mitigations such as "monitor closely" without a signal, threshold, action, and owner.

## 11. Decision ledger

| ID | Decision | Choice | Strongest rejected alternative | Rationale | Consequences | Owner | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |

Use `decided`, `delegated`, `evidence-gated`, `deferred`, or `out-of-scope`. A confirmed blueprint contains no `open` status.

## 12. Readiness statement

State:

- whether implementation is authorized or awaits separate approval;
- managed follow-ups that can proceed without reopening the blueprint;
- the precise conditions that would require reopening a decision.

End with `Open decisions: none` only when that is literally true. Otherwise label the artifact **incomplete** and return to the interview.
