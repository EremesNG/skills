# Feature Specification: Unity Developer Skill

**Change ID**: `unity-developer-skill`<br>
**Route**: Accelerated<br>
**Status**: Draft

## Intent and scope

**Why**: Unity developers need a reusable expert workflow that diagnoses the
actual game-development forces before selecting design patterns, architectural
frameworks, or AI systems, then carries the decision through production-quality
C# implementation and evidence-based verification.<br>
**Impact**: Adds a repository skill named `unity-developer`, its progressively
loaded references, a safe Unity-project inspection helper, behavioral
evaluations, repository validation, and catalog documentation. Existing skills
and their behavior remain compatible.<br>
**Affected capabilities**: `unity-development-guidance`, `unity-project-inspection`

## User stories

### US1 - Select the simplest professional solution (Priority: P1)

As a Unity developer, I can present a gameplay or architecture challenge and
receive one context-grounded recommendation with explicit trade-offs so that I
solve the actual problem without pattern cargo culting or speculative
infrastructure.

**Independent test**: Give the skill a coupled health/UI/audio feature with
project constraints and verify that it inspects available evidence, compares
viable communication patterns, recommends one bounded design, and explains why
the rejected options are less suitable.

**Covers**: FR-001, FR-002, FR-003, FR-004, FR-009, SC-001, SC-005

**Acceptance scenarios**:

1. **Given** a Unity challenge with repository context, **When** the skill is invoked, **Then** it identifies the relevant engine version, packages, platform, lifecycle, scale, performance, team, and test constraints before prescribing a pattern.
2. **Given** two or more plausible solutions, **When** the skill recommends one, **Then** it states the governing forces, rejected alternatives, trade-offs, and a condition that would justify revisiting the decision.
3. **Given** a problem that needs no formal pattern, **When** a direct reference, event, component, or small conditional is sufficient, **Then** the skill recommends that simpler mechanism and explains why extra structure would not pay for itself.

### US2 - Design maintainable Unity architecture (Priority: P1)

As a Unity team, I can design or refactor system boundaries that respect Unity's
component, serialization, scene, and lifecycle semantics so that the codebase is
testable, debuggable, and resilient to change.

**Independent test**: Ask the skill to refactor a manager-heavy project and
verify that it separates pure C# domain logic from Unity adapters, defines a
composition root and lifetimes, addresses scene/domain reload behavior, and
proposes dependency and test seams without blindly introducing a framework.

**Covers**: FR-002, FR-004, FR-005, FR-007, FR-009, SC-001, SC-005

**Acceptance scenarios**:

1. **Given** global managers and hidden scene lookups, **When** architecture is proposed, **Then** dependencies, ownership, lifetimes, initialization order, teardown, and assembly boundaries are explicit.
2. **Given** ScriptableObjects or static events, **When** runtime state or cross-scene behavior is involved, **Then** the design distinguishes authored asset data from runtime state and defines reset and subscription cleanup.
3. **Given** a small project, **When** manual Inspector or composition-root injection is sufficient, **Then** the skill does not require a third-party DI container.

### US3 - Choose an appropriate game AI system (Priority: P1)

As an AI/gameplay programmer, I can select and compose decision-making,
perception, memory, navigation, and execution systems so that NPC behavior meets
design, determinism, performance, networking, and authoring needs.

**Independent test**: Present a squad-AI scenario with target-platform and
multiplayer constraints and verify that the skill compares FSM/HFSM, behavior
trees, utility scoring, GOAP, and learning/inference approaches, then proposes a
measurable hybrid only where justified.

**Covers**: FR-002, FR-006, FR-007, FR-009, SC-001, SC-005

**Acceptance scenarios**:

1. **Given** a small predictable behavior set, **When** the skill evaluates the AI, **Then** it prefers FSM or HFSM over a planner or learned policy unless another stated force requires the added complexity.
2. **Given** dynamic goals and composable actions, **When** planning is justified, **Then** GOAP costs, world-state representation, invalidation, replanning budget, debugging, and deterministic/network implications are addressed.
3. **Given** a request for "AI" that only requires pathfinding, **When** the skill analyzes it, **Then** it treats navigation as a separate subsystem and does not mislabel NavMesh pathfinding as decision intelligence.
4. **Given** a request for ML-Agents or runtime model inference, **When** the desired behavior can be implemented deterministically with conventional game AI, **Then** the skill makes training/inference an explicit trade-off instead of a default.

### US4 - Inspect an unfamiliar Unity project safely (Priority: P2)

As a developer or agent, I can obtain a bounded, read-only inventory of a Unity
project so that recommendations use real version, package, assembly, test, and
source-layout evidence without exposing secrets or modifying the project.

**Independent test**: Run the bundled inspector against representative Unity,
minimal, malformed, and non-Unity fixtures and verify stable JSON/text output,
clear warnings, no source contents, and no filesystem mutation.

**Covers**: FR-002, FR-008, SC-002

**Acceptance scenarios**:

1. **Given** a Unity project root, **When** the inspector runs, **Then** it reports the Editor version, declared packages, assembly definitions, test assemblies, C# file counts, and bounded architectural risk signals with source paths.
2. **Given** malformed or missing metadata, **When** the inspector runs, **Then** it returns an actionable warning and nonzero status only when the requested root cannot be inspected as a Unity project.
3. **Given** secret-like files or arbitrary source code, **When** the inspector scans, **Then** it excludes secret-like paths and emits counts and paths only, never file contents or credential values.

### US5 - Distribute and evaluate a valid Agent Skill (Priority: P1)

As a skill consumer or maintainer, I can discover, install, and evaluate
`unity-developer` using repository conventions so that its behavior and package
integrity are reproducible.

**Independent test**: Run structural validation, repository tests, skill
discovery, and realistic with-skill versus baseline evaluations, then inspect the
generated review artifact and independent verification report.

**Covers**: FR-010, FR-011, FR-012, SC-003, SC-004, SC-006, SC-007

**Acceptance scenarios**:

1. **Given** the repository root, **When** its documented validation commands run, **Then** `unity-developer` is discovered and all referenced resources exist.
2. **Given** realistic architecture and AI prompts, **When** with-skill and baseline runs are compared, **Then** objective assertions and qualitative outputs are available in the skill-creator review format.
3. **Given** the completed implementation, **When** an independent Oracle verifies it, **Then** every functional requirement and buildable success criterion has evidence or the change is rejected with actionable defects.

## Edge cases

- The working directory is not a Unity project, contains more than one candidate
  project, or lacks `ProjectSettings/ProjectVersion.txt`.
- The Unity Editor is unavailable, headless, or cannot safely open the user's
  project; static inspection must remain useful and limitations must be explicit.
- The project targets a legacy or prerelease Unity/package version whose API
  differs from current documentation.
- Repository evidence conflicts with the user's description or with secondary
  sources; observed project facts and official version-matched documentation
  take precedence, while inference remains labeled.
- A requested pattern is mandated by the user or existing architecture even when
  another option appears cleaner; the skill preserves the constraint and reports
  its consequences rather than silently redesigning the system.
- Performance is alleged without a profiler capture, target-device measurement,
  frame/memory budget, or reproducible symptom.
- Static events, disabled domain reload, additive scenes, `DontDestroyOnLoad`,
  pooled objects, asynchronous work, or destroyed `UnityEngine.Object` references
  create lifetime and cleanup hazards.
- AI behavior must be deterministic, authoritative over a network, replayable,
  saveable, or debuggable by non-programmer designers.
- The prompt asks for broad Unity implementation unrelated to architecture,
  patterns, AI, testability, or performance; the skill remains helpful without
  forcing every reference file into context.

## Functional requirements

- **FR-001 — Discoverable Unity expertise**: `[ADDED unity-development-guidance]`
  The package MUST define `unity-developer` with triggering metadata that covers
  Unity and C# gameplay architecture, design-pattern selection, game AI systems,
  lifecycle/testability/performance problems, and relevant implementation or
  review tasks without claiming unrelated 3D-art or generic C# ownership.
- **FR-002 — Evidence-first context intake**: `[ADDED unity-development-guidance]`
  The skill MUST inspect available project evidence before asking for facts,
  capture material version/package/platform/team/performance/network/authoring
  constraints, use official version-matched documentation for unstable APIs when
  available, and label facts, assumptions, and inferences distinctly.
- **FR-003 — Proportional decision method**: `[ADDED unity-development-guidance]`
  The skill MUST select the smallest coherent solution by evaluating forces and
  failure modes, compare credible alternatives, explain the chosen trade-off,
  state a revisit condition, and explicitly allow no-pattern solutions.
- **FR-004 — Pattern selection knowledge**: `[ADDED unity-development-guidance]`
  Progressively loaded guidance MUST cover the relevant creational, structural,
  behavioral, architectural, and optimization patterns synthesized from the
  provided document and `unitydesignpatterns.com`, including when to use, when
  not to use, Unity-specific hazards, and useful pattern compositions.
- **FR-005 — Unity architecture safeguards**: `[ADDED unity-development-guidance]`
  The skill MUST guide composition roots, dependency direction, lifetimes,
  assembly boundaries, pure C# domain seams, MonoBehaviour/ScriptableObject
  adapters, data-versus-runtime state, messaging scope, UI presentation, scene
  transitions, serialization, initialization, teardown, and domain reload while
  treating Singleton, Service Locator, event buses, SOAP, DI, MVP, and ECS/DOTS as
  trade-offs rather than universal defaults.
- **FR-006 — Game AI selection and composition**: `[ADDED unity-development-guidance]`
  The skill MUST distinguish perception, blackboard/memory, decision-making,
  navigation, action execution, and animation; compare FSM, HFSM, behavior trees,
  utility AI, GOAP, rule/specification systems, ML-Agents, local model inference,
  and hybrids; and account for authoring, debugging, performance, determinism,
  replay/save, and network authority.
- **FR-007 — Production implementation workflow**: `[ADDED unity-development-guidance]`
  For behavior changes, the skill MUST establish observable contracts, add a
  failing EditMode/PlayMode test at the narrowest useful seam, implement the
  minimum change, preserve Unity lifecycle cleanup, run applicable validation,
  and require profiler evidence on target hardware before asserting performance
  improvement.
- **FR-008 — Safe project inspector**: `[ADDED unity-project-inspection]` The package MUST provide a dependency-free Python 3.9+ read-only inspector that
  validates a Unity root, parses project/package metadata defensively, inventories
  assemblies/tests/C# layout, reports bounded architectural signals as evidence
  rather than diagnoses, excludes generated and secret-like paths, supports
  human-readable and JSON output, and never emits source or secret contents.
- **FR-009 — Actionable response contract**: `[ADDED unity-development-guidance]`
  Recommendations MUST report context/evidence, the decision and rationale,
  rejected alternatives, boundaries and ownership, implementation steps or code
  at the requested depth, tests and profiler/validation evidence, lifecycle and
  performance risks, and remaining uncertainties or next checks.
- **FR-010 — Progressive disclosure package**: `[ADDED unity-development-guidance]`
  `SKILL.md` MUST remain below 500 lines and route to focused references for the
  decision framework, pattern catalog, architecture, AI systems, engine
  constraints/testing, and source provenance, loading only the files relevant to
  the current challenge.
- **FR-011 — Repository integration**: `[ADDED unity-development-guidance]` The change MUST add repository-conformant UI metadata, catalog/install/usage
  documentation, checksum coverage, validation documentation, and automated tests
  without regressing existing skills or overwriting unrelated work.
- **FR-012 — Behavioral evaluation**: `[INTERNAL]` The change MUST define three
  realistic evaluations spanning pattern selection, architecture/lifecycle, and
  AI/performance trade-offs; run with-skill and no-skill baselines as independently
  as host concurrency permits; grade objective assertions; aggregate results; and
  generate the standard skill-creator review artifact for human inspection.

## Success criteria

- **SC-001** `[buildable]`: `SKILL.md` is under 500 lines, every local link exists,
  all named decision/architecture/AI/lifecycle/test workflows are present, and the
  installed skill-creator structural validator reports success.
- **SC-002** `[buildable]`: At least seven inspector unit-test cases cover a valid
  Unity fixture, missing and malformed metadata, generated/secret-like
  exclusions, signal reporting, stable JSON, and no project mutation; 100% of
  those tests pass on Python 3.9+ compatible syntax.
- **SC-003** `[buildable]`: 100% of repository unit tests and Python compilation pass,
  local skill discovery lists exactly the four expected skills including
  `unity-developer`, and all package paths/checksums are current.
- **SC-004** `[buildable]`: 3 evaluation definitions contain realistic
  prompts, expected outputs, and objective assertions; with-skill and baseline
  outputs are graded and aggregated into a benchmark plus a generated static
  review HTML artifact.
- **SC-005** `[buildable]`: In every with-skill evaluation, all critical
  assertions for evidence-first diagnosis, proportional pattern/AI selection,
  Unity lifecycle correctness, test strategy, and verification honesty pass.
- **SC-006** `[buildable]`: One independent Oracle returns PASS and the persisted
  verification report maps 100% of FRs and buildable SCs to concrete evidence
  with zero unresolved critical or major defects.
- **SC-007** `[outcome]`: In at least two of three evaluation scenarios, human
  review prefers the with-skill recommendation over its no-skill baseline for
  actionability, justification, and proportionality.

## Assumptions

- The skill will be authored in English for interoperability with Unity/C#
  terminology while remaining usable from Spanish or other-language prompts.
- `C:\DEV\Proyectos\Webstorm\skills\skills\unity-developer\` is the intended
  package location and `unity-developer` is the accepted final name.
- The supplied DOCX is a research input, not an authority for time-sensitive API
  or package claims; official version-matched Unity documentation wins when facts
  conflict.
- No live Unity project or installed Unity Editor is required to create and test
  this reusable skill; project-specific code compilation remains an invocation-
  time responsibility.
- The project inspector uses only the Python standard library so the skill has no
  runtime installation step.

## Dependencies

- The supplied `Patrones de Programacion de Videojuegos en Unity.docx` content,
  structurally extracted because LibreOffice is unavailable for visual rendering.
- `https://www.unitydesignpatterns.com/`, the user-provided baseline skill, and
  official Unity documentation used as research sources.
- Locally installed `skill-creator`, `tdd`, `simplify`, `thoth-sdd`,
  `thoth-archive`, and independent Oracle capabilities.

## Out of scope

- Building, opening, migrating, or shipping a Unity game project.
- Installing Unity, packages, Asset Store assets, DI containers, behavior-tree
  frameworks, or ML training environments.
- Reproducing every source article, all 23 GoF patterns as full tutorials, or
  copyrighted source code beyond concise synthesis.
- Mandating a universal folder architecture, third-party framework, render
  pipeline, networking stack, or AI technique for all Unity projects.
- Optimizing the skill description through the external Claude-only trigger loop;
  the description will instead receive repository-local and evaluation coverage.
