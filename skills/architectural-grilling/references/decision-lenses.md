# Decision Lenses

Use this as a coverage map, not a questionnaire. Select only branches material to the current decision, ask one question per turn, and let early answers reshape later branches.

## Routing order

Prefer this dependency order while allowing high-risk discoveries to jump the queue:

1. viability and authority;
2. outcome, actors, and scope;
3. domain and data;
4. quality drivers and architecture;
5. security, operations, and delivery;
6. integrated red-team and convergence.

Within a stage, prioritize decisions by irreversibility, uncertainty, blast radius, and downstream leverage.

## 1. Viability and strategy

Resolve:

- problem and affected actor;
- evidence the problem exists and its present cost;
- current workaround and why it is insufficient;
- desired behavioral or business outcome;
- measurable leading and lagging success signals;
- deadline source and consequence of missing it;
- build, buy, integrate, extend, automate partially, remain manual, and no-build alternatives;
- opportunity cost and what must stop to fund the effort;
- kill, pause, or pivot criteria.

Pressure tests:

- If the proposed solution vanished, would the problem still be worth solving?
- Is the requested feature actually a workaround for a policy, process, or ownership problem?
- What evidence would prove the project should not continue?
- Is a simple manual concierge process enough to test demand before software exists?

## 2. Governance, stakeholders, and constraints

Resolve:

- accountable sponsor and final decision maker;
- product, technical, security, legal, operational, and budget owners;
- users, buyers, operators, support teams, and parties bearing risk;
- hard constraints versus preferences and their evidence;
- budget envelope, team capacity, skills, availability, and maintenance ownership;
- contractual, regulatory, licensing, residency, accessibility, and procurement constraints;
- external dependencies, approval lead times, and organizational change.

Pressure tests:

- Who can veto this, and what would trigger the veto?
- Does the team that will operate the system agree with the team designing it?
- Which "constraint" disappears if the sponsor changes priority or budget?
- Which decision has no clearly accountable owner?

## 3. Product scope and domain

Resolve:

- actor segments, goals, permissions, and tenancy;
- primary end-to-end journey and valuable outcome;
- alternate, failure, cancellation, retry, recovery, and support journeys;
- lifecycle states, transitions, invariants, and forbidden states;
- canonical domain terms and overloaded language;
- business rules, precedence rules, manual overrides, and audit needs;
- MVP learning goal and smallest end-to-end slice;
- explicit non-goals and scope boundaries;
- localization, accessibility, offline, device, and channel needs when relevant.

Pressure tests:

- Name a concrete actor, starting state, action, and observable outcome.
- What happens on duplicate, late, partial, reordered, or conflicting input?
- Who may reverse a decision, and what must remain auditable afterward?
- Which promised MVP item can be removed without invalidating the learning goal?

## 4. Data and state

Resolve:

- source of truth and ownership for each material entity;
- data origin, classification, consent, rights, retention, deletion, and residency;
- schema and identity strategy;
- transaction, consistency, ordering, deduplication, idempotency, and reconciliation needs;
- read/write patterns, expected volume, growth, and archival;
- import, migration, backfill, validation, and rollback;
- analytics, reporting, audit trail, and lineage;
- cache authority and stale-data behavior.

Pressure tests:

- What happens when two systems disagree?
- Can the system explain who changed what, when, and why?
- Can deletion obligations be honored across replicas, logs, backups, and vendors?
- What invariant must survive retries, concurrent writes, and partial failure?

## 5. AI or probabilistic behavior

Use this lens whenever models, agents, recommendations, classifiers, generation, or embeddings influence the outcome.

Resolve:

- exact task assigned to the model and deterministic alternatives;
- data rights, sensitivity, residency, and vendor use;
- baseline and evaluation dataset;
- quality, safety, latency, and cost thresholds;
- false-positive and false-negative consequences;
- human review, appeal, correction, and feedback loops;
- prompt injection, tool authorization, data exfiltration, and abuse controls;
- model/version drift, observability, fallback, outage behavior, and provider exit;
- per-unit economics at expected and worst-case load.

Pressure tests:

- How will the team know the model is better than the non-AI baseline?
- What happens when output is plausible but wrong?
- Which action must the model never take without human approval?
- Can the product still deliver value when the model or vendor is unavailable?

## 6. Quality drivers

Prioritize and quantify only attributes capable of changing the design:

- throughput, concurrency, payload size, and growth horizon;
- user-visible and machine-to-machine latency percentiles;
- availability, durability, consistency, and degraded-mode expectations;
- recovery point and recovery time objectives;
- privacy, security, auditability, and compliance;
- maintainability, change frequency, deployability, and testability;
- accessibility, portability, interoperability, and vendor independence;
- infrastructure, vendor, support, and engineering cost ceilings.

Pressure tests:

- Which attribute wins when consistency, availability, latency, cost, and delivery speed conflict?
- What measured workload invalidates the simple architecture?
- Is a stated target a user need, a contract, or an aesthetic preference?
- What is the acceptable degraded behavior during dependency failure?

## 7. Architecture and boundaries

Resolve:

- system context, trust boundaries, and owned versus external capabilities;
- bounded contexts or modules and their responsibilities;
- stable interfaces, invariants, error modes, and versioning;
- synchronous versus asynchronous interaction and why;
- workflow coordination, state machines, queues, retries, timeouts, backpressure, and dead letters;
- data ownership and cross-boundary consistency;
- scaling model, hotspots, caching, partitioning, and capacity trigger points;
- deployment units and whether their independence is actually required;
- failure isolation, redundancy, reconciliation, and disaster recovery;
- observability and operational ownership at every critical boundary.

Compare at least:

1. the simplest credible baseline, usually the existing architecture or a modular monolith;
2. a materially different alternative optimized for the dominant driver;
3. the proposed design, if it differs from both.

Compare complexity, delivery speed, operating burden, failure modes, cost, reversibility, and migration path. Do not introduce distributed systems merely for theoretical scale or organizational fashion.

## 8. Frameworks, platforms, and vendors

Resolve:

- fit with current code, runtime, deployment, and team capability;
- maturity, maintenance cadence, security response, ecosystem, and documentation;
- testing and debugging ergonomics;
- operational footprint and observability;
- accessibility and performance implications for client frameworks;
- licensing, procurement, pricing curve, quotas, and support;
- proprietary surface area, data portability, and exit plan;
- migration cost from the current system and to the next likely option;
- explicit trigger for revisiting the choice.

Pressure tests:

- Which requirement cannot be met by the repository's existing stack?
- Is the choice driven by measured need or résumé/novelty value?
- What breaks if the maintainer, vendor, price, or license changes?
- Can a new team member diagnose a production issue without specialist knowledge?

Verify volatile claims against current primary documentation before recommending a specific version, product, or service.

## 9. Security, privacy, and abuse

Resolve:

- assets, adversaries, entry points, trust boundaries, and plausible abuse;
- identity, authentication, authorization, least privilege, and separation of duties;
- tenant isolation and object-level access control;
- secrets, keys, encryption, rotation, and recovery;
- input validation, output encoding, supply chain, dependency, and build integrity;
- logging, audit, detection, alerting, incident response, and forensics;
- rate limits, fraud, spam, denial of service, and cost-amplification attacks;
- privacy notice, consent, minimization, retention, deletion, export, and legal basis;
- security review and compliance evidence required before release.

Pressure tests:

- What is the highest-impact action an ordinary authenticated user could abuse?
- Which internal identity or service has more access than it needs?
- What sensitive value might leak through logs, analytics, prompts, or support tools?
- How would the team contain and explain a breach?

## 10. Testing, operations, and support

Resolve:

- acceptance evidence for each outcome and critical rule;
- test seams at stable interfaces and representative environments;
- contract, integration, migration, performance, resilience, security, and accessibility tests as relevant;
- release gates and ownership of failing gates;
- service-level indicators, objectives, error budget, dashboards, alerts, and traces;
- runbooks, on-call, incident severity, escalation, and communication;
- backups, restore tests, disaster recovery exercises, and dependency outages;
- support tooling, manual repair, data correction, and audit controls;
- maintenance, patching, deprecation, and end-of-life responsibility.

Pressure tests:

- Which failure would pass unit tests but harm users in production?
- Can the team detect the failure before a customer reports it?
- Has rollback been tested with changed schemas and partially processed work?
- Who owns the system at 03:00 and what evidence will they have?

## 11. Delivery and project management

Resolve:

- outcome-oriented milestones and demonstrable vertical slices;
- dependencies, blocking edges, critical path, and external lead times;
- accountable owner for every milestone and critical risk;
- team capacity, skill gaps, onboarding, and competing commitments;
- estimates as ranges with confidence and named assumptions;
- contingency sized to uncertainty rather than an arbitrary percentage;
- research, prototypes, or spikes with time boxes and decision criteria;
- acceptance authority and definition of done;
- stakeholder cadence, change control, and escalation path;
- cost profile across build, migration, operation, support, and exit.

Pressure tests:

- What is the earliest slice that proves the riskiest assumption end to end?
- Which dependency has the longest lead time or weakest owner?
- What scope is removed first if the deadline is fixed?
- What work is missing because it belongs to security, data, operations, support, or change management rather than feature coding?

## 12. Rollout, migration, and adoption

Resolve:

- pilot cohort, feature flags, canary stages, and exposure controls;
- backward and forward compatibility;
- data migration, backfill, dual-write/read, cutover, and reconciliation;
- go/no-go criteria, abort thresholds, rollback mechanics, and maximum recovery time;
- user communication, training, documentation, and support readiness;
- legacy coexistence, decommission criteria, and cleanup ownership;
- measurement window and decision after each stage.

Pressure tests:

- Can the release be stopped without losing or corrupting data?
- What happens to work started before cutover?
- How long can old and new behavior safely coexist?
- What evidence advances the rollout, pauses it, or reverses it?

## 13. Integrated red-team

Assume the initiative failed 6–12 months after launch. Explore:

- solved the wrong problem or no adoption;
- underestimated workflow and edge-case complexity;
- architecture or vendor choice blocked change;
- data loss, security incident, compliance failure, or abuse;
- dependency outage or cascading failure;
- costs exceeded unit economics;
- key-person loss, skill mismatch, or unsustainable operations;
- schedule slip caused by hidden approvals, migration, or integration work;
- successful launch but harmful second-order effects;
- better opportunity displaced by this investment.

Convert each material failure into a design change, validation step, monitored signal, contingency, explicit accepted risk, or reason to stop.
