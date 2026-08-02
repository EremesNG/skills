# Unity Development Guidance Specification

## Purpose

Durable behavioral contract for `unity-development-guidance`.

## Requirements

### Requirement: Discoverable Unity expertise

The package MUST define `unity-developer` with triggering metadata that covers

#### Scenario: US1 - Select the simplest professional solution 1

- **GIVEN** a Unity challenge with repository context
- **WHEN** the skill is invoked
- **THEN** it identifies the relevant engine version, packages, platform, lifecycle, scale, performance, team, and test constraints before prescribing a pattern

#### Scenario: US1 - Select the simplest professional solution 2

- **GIVEN** two or more plausible solutions
- **WHEN** the skill recommends one
- **THEN** it states the governing forces, rejected alternatives, trade-offs, and a condition that would justify revisiting the decision

#### Scenario: US1 - Select the simplest professional solution 3

- **GIVEN** a problem that needs no formal pattern
- **WHEN** a direct reference, event, component, or small conditional is sufficient
- **THEN** the skill recommends that simpler mechanism and explains why extra structure would not pay for itself

### Requirement: Evidence-first context intake

The skill MUST inspect available project evidence before asking for facts,

#### Scenario: US1 - Select the simplest professional solution 1

- **GIVEN** a Unity challenge with repository context
- **WHEN** the skill is invoked
- **THEN** it identifies the relevant engine version, packages, platform, lifecycle, scale, performance, team, and test constraints before prescribing a pattern

#### Scenario: US1 - Select the simplest professional solution 2

- **GIVEN** two or more plausible solutions
- **WHEN** the skill recommends one
- **THEN** it states the governing forces, rejected alternatives, trade-offs, and a condition that would justify revisiting the decision

#### Scenario: US1 - Select the simplest professional solution 3

- **GIVEN** a problem that needs no formal pattern
- **WHEN** a direct reference, event, component, or small conditional is sufficient
- **THEN** the skill recommends that simpler mechanism and explains why extra structure would not pay for itself

#### Scenario: US2 - Design maintainable Unity architecture 1

- **GIVEN** global managers and hidden scene lookups
- **WHEN** architecture is proposed
- **THEN** dependencies, ownership, lifetimes, initialization order, teardown, and assembly boundaries are explicit

#### Scenario: US2 - Design maintainable Unity architecture 2

- **GIVEN** ScriptableObjects or static events
- **WHEN** runtime state or cross-scene behavior is involved
- **THEN** the design distinguishes authored asset data from runtime state and defines reset and subscription cleanup

#### Scenario: US2 - Design maintainable Unity architecture 3

- **GIVEN** a small project
- **WHEN** manual Inspector or composition-root injection is sufficient
- **THEN** the skill does not require a third-party DI container

#### Scenario: US3 - Choose an appropriate game AI system 1

- **GIVEN** a small predictable behavior set
- **WHEN** the skill evaluates the AI
- **THEN** it prefers FSM or HFSM over a planner or learned policy unless another stated force requires the added complexity

#### Scenario: US3 - Choose an appropriate game AI system 2

- **GIVEN** dynamic goals and composable actions
- **WHEN** planning is justified
- **THEN** GOAP costs, world-state representation, invalidation, replanning budget, debugging, and deterministic/network implications are addressed

#### Scenario: US3 - Choose an appropriate game AI system 3

- **GIVEN** a request for "AI" that only requires pathfinding
- **WHEN** the skill analyzes it
- **THEN** it treats navigation as a separate subsystem and does not mislabel NavMesh pathfinding as decision intelligence

#### Scenario: US3 - Choose an appropriate game AI system 4

- **GIVEN** a request for ML-Agents or runtime model inference
- **WHEN** the desired behavior can be implemented deterministically with conventional game AI
- **THEN** the skill makes training/inference an explicit trade-off instead of a default

#### Scenario: US4 - Inspect an unfamiliar Unity project safely 1

- **GIVEN** a Unity project root
- **WHEN** the inspector runs
- **THEN** it reports the Editor version, declared packages, assembly definitions, test assemblies, C# file counts, and bounded architectural risk signals with source paths

#### Scenario: US4 - Inspect an unfamiliar Unity project safely 2

- **GIVEN** malformed or missing metadata
- **WHEN** the inspector runs
- **THEN** it returns an actionable warning and nonzero status only when the requested root cannot be inspected as a Unity project

#### Scenario: US4 - Inspect an unfamiliar Unity project safely 3

- **GIVEN** secret-like files or arbitrary source code
- **WHEN** the inspector scans
- **THEN** it excludes secret-like paths and emits counts and paths only, never file contents or credential values

### Requirement: Proportional decision method

The skill MUST select the smallest coherent solution by evaluating forces and

#### Scenario: US1 - Select the simplest professional solution 1

- **GIVEN** a Unity challenge with repository context
- **WHEN** the skill is invoked
- **THEN** it identifies the relevant engine version, packages, platform, lifecycle, scale, performance, team, and test constraints before prescribing a pattern

#### Scenario: US1 - Select the simplest professional solution 2

- **GIVEN** two or more plausible solutions
- **WHEN** the skill recommends one
- **THEN** it states the governing forces, rejected alternatives, trade-offs, and a condition that would justify revisiting the decision

#### Scenario: US1 - Select the simplest professional solution 3

- **GIVEN** a problem that needs no formal pattern
- **WHEN** a direct reference, event, component, or small conditional is sufficient
- **THEN** the skill recommends that simpler mechanism and explains why extra structure would not pay for itself

### Requirement: Pattern selection knowledge

Progressively loaded guidance MUST cover the relevant creational, structural,

#### Scenario: US1 - Select the simplest professional solution 1

- **GIVEN** a Unity challenge with repository context
- **WHEN** the skill is invoked
- **THEN** it identifies the relevant engine version, packages, platform, lifecycle, scale, performance, team, and test constraints before prescribing a pattern

#### Scenario: US1 - Select the simplest professional solution 2

- **GIVEN** two or more plausible solutions
- **WHEN** the skill recommends one
- **THEN** it states the governing forces, rejected alternatives, trade-offs, and a condition that would justify revisiting the decision

#### Scenario: US1 - Select the simplest professional solution 3

- **GIVEN** a problem that needs no formal pattern
- **WHEN** a direct reference, event, component, or small conditional is sufficient
- **THEN** the skill recommends that simpler mechanism and explains why extra structure would not pay for itself

#### Scenario: US2 - Design maintainable Unity architecture 1

- **GIVEN** global managers and hidden scene lookups
- **WHEN** architecture is proposed
- **THEN** dependencies, ownership, lifetimes, initialization order, teardown, and assembly boundaries are explicit

#### Scenario: US2 - Design maintainable Unity architecture 2

- **GIVEN** ScriptableObjects or static events
- **WHEN** runtime state or cross-scene behavior is involved
- **THEN** the design distinguishes authored asset data from runtime state and defines reset and subscription cleanup

#### Scenario: US2 - Design maintainable Unity architecture 3

- **GIVEN** a small project
- **WHEN** manual Inspector or composition-root injection is sufficient
- **THEN** the skill does not require a third-party DI container

### Requirement: Unity architecture safeguards

The skill MUST guide composition roots, dependency direction, lifetimes,

#### Scenario: US2 - Design maintainable Unity architecture 1

- **GIVEN** global managers and hidden scene lookups
- **WHEN** architecture is proposed
- **THEN** dependencies, ownership, lifetimes, initialization order, teardown, and assembly boundaries are explicit

#### Scenario: US2 - Design maintainable Unity architecture 2

- **GIVEN** ScriptableObjects or static events
- **WHEN** runtime state or cross-scene behavior is involved
- **THEN** the design distinguishes authored asset data from runtime state and defines reset and subscription cleanup

#### Scenario: US2 - Design maintainable Unity architecture 3

- **GIVEN** a small project
- **WHEN** manual Inspector or composition-root injection is sufficient
- **THEN** the skill does not require a third-party DI container

### Requirement: Game AI selection and composition

The skill MUST distinguish perception, blackboard/memory, decision-making,

#### Scenario: US3 - Choose an appropriate game AI system 1

- **GIVEN** a small predictable behavior set
- **WHEN** the skill evaluates the AI
- **THEN** it prefers FSM or HFSM over a planner or learned policy unless another stated force requires the added complexity

#### Scenario: US3 - Choose an appropriate game AI system 2

- **GIVEN** dynamic goals and composable actions
- **WHEN** planning is justified
- **THEN** GOAP costs, world-state representation, invalidation, replanning budget, debugging, and deterministic/network implications are addressed

#### Scenario: US3 - Choose an appropriate game AI system 3

- **GIVEN** a request for "AI" that only requires pathfinding
- **WHEN** the skill analyzes it
- **THEN** it treats navigation as a separate subsystem and does not mislabel NavMesh pathfinding as decision intelligence

#### Scenario: US3 - Choose an appropriate game AI system 4

- **GIVEN** a request for ML-Agents or runtime model inference
- **WHEN** the desired behavior can be implemented deterministically with conventional game AI
- **THEN** the skill makes training/inference an explicit trade-off instead of a default

### Requirement: Production implementation workflow

For behavior changes, the skill MUST establish observable contracts, add a

#### Scenario: US2 - Design maintainable Unity architecture 1

- **GIVEN** global managers and hidden scene lookups
- **WHEN** architecture is proposed
- **THEN** dependencies, ownership, lifetimes, initialization order, teardown, and assembly boundaries are explicit

#### Scenario: US2 - Design maintainable Unity architecture 2

- **GIVEN** ScriptableObjects or static events
- **WHEN** runtime state or cross-scene behavior is involved
- **THEN** the design distinguishes authored asset data from runtime state and defines reset and subscription cleanup

#### Scenario: US2 - Design maintainable Unity architecture 3

- **GIVEN** a small project
- **WHEN** manual Inspector or composition-root injection is sufficient
- **THEN** the skill does not require a third-party DI container

#### Scenario: US3 - Choose an appropriate game AI system 1

- **GIVEN** a small predictable behavior set
- **WHEN** the skill evaluates the AI
- **THEN** it prefers FSM or HFSM over a planner or learned policy unless another stated force requires the added complexity

#### Scenario: US3 - Choose an appropriate game AI system 2

- **GIVEN** dynamic goals and composable actions
- **WHEN** planning is justified
- **THEN** GOAP costs, world-state representation, invalidation, replanning budget, debugging, and deterministic/network implications are addressed

#### Scenario: US3 - Choose an appropriate game AI system 3

- **GIVEN** a request for "AI" that only requires pathfinding
- **WHEN** the skill analyzes it
- **THEN** it treats navigation as a separate subsystem and does not mislabel NavMesh pathfinding as decision intelligence

#### Scenario: US3 - Choose an appropriate game AI system 4

- **GIVEN** a request for ML-Agents or runtime model inference
- **WHEN** the desired behavior can be implemented deterministically with conventional game AI
- **THEN** the skill makes training/inference an explicit trade-off instead of a default

### Requirement: Actionable response contract

Recommendations MUST report context/evidence, the decision and rationale,

#### Scenario: US1 - Select the simplest professional solution 1

- **GIVEN** a Unity challenge with repository context
- **WHEN** the skill is invoked
- **THEN** it identifies the relevant engine version, packages, platform, lifecycle, scale, performance, team, and test constraints before prescribing a pattern

#### Scenario: US1 - Select the simplest professional solution 2

- **GIVEN** two or more plausible solutions
- **WHEN** the skill recommends one
- **THEN** it states the governing forces, rejected alternatives, trade-offs, and a condition that would justify revisiting the decision

#### Scenario: US1 - Select the simplest professional solution 3

- **GIVEN** a problem that needs no formal pattern
- **WHEN** a direct reference, event, component, or small conditional is sufficient
- **THEN** the skill recommends that simpler mechanism and explains why extra structure would not pay for itself

#### Scenario: US2 - Design maintainable Unity architecture 1

- **GIVEN** global managers and hidden scene lookups
- **WHEN** architecture is proposed
- **THEN** dependencies, ownership, lifetimes, initialization order, teardown, and assembly boundaries are explicit

#### Scenario: US2 - Design maintainable Unity architecture 2

- **GIVEN** ScriptableObjects or static events
- **WHEN** runtime state or cross-scene behavior is involved
- **THEN** the design distinguishes authored asset data from runtime state and defines reset and subscription cleanup

#### Scenario: US2 - Design maintainable Unity architecture 3

- **GIVEN** a small project
- **WHEN** manual Inspector or composition-root injection is sufficient
- **THEN** the skill does not require a third-party DI container

#### Scenario: US3 - Choose an appropriate game AI system 1

- **GIVEN** a small predictable behavior set
- **WHEN** the skill evaluates the AI
- **THEN** it prefers FSM or HFSM over a planner or learned policy unless another stated force requires the added complexity

#### Scenario: US3 - Choose an appropriate game AI system 2

- **GIVEN** dynamic goals and composable actions
- **WHEN** planning is justified
- **THEN** GOAP costs, world-state representation, invalidation, replanning budget, debugging, and deterministic/network implications are addressed

#### Scenario: US3 - Choose an appropriate game AI system 3

- **GIVEN** a request for "AI" that only requires pathfinding
- **WHEN** the skill analyzes it
- **THEN** it treats navigation as a separate subsystem and does not mislabel NavMesh pathfinding as decision intelligence

#### Scenario: US3 - Choose an appropriate game AI system 4

- **GIVEN** a request for ML-Agents or runtime model inference
- **WHEN** the desired behavior can be implemented deterministically with conventional game AI
- **THEN** the skill makes training/inference an explicit trade-off instead of a default

### Requirement: Progressive disclosure package

`SKILL.md` MUST remain below 500 lines and route to focused references for the

#### Scenario: US5 - Distribute and evaluate a valid Agent Skill 1

- **GIVEN** the repository root
- **WHEN** its documented validation commands run
- **THEN** `unity-developer` is discovered and all referenced resources exist

#### Scenario: US5 - Distribute and evaluate a valid Agent Skill 2

- **GIVEN** realistic architecture and AI prompts
- **WHEN** with-skill and baseline runs are compared
- **THEN** objective assertions and qualitative outputs are available in the skill-creator review format

#### Scenario: US5 - Distribute and evaluate a valid Agent Skill 3

- **GIVEN** the completed implementation
- **WHEN** an independent Oracle verifies it
- **THEN** every functional requirement and buildable success criterion has evidence or the change is rejected with actionable defects

### Requirement: Repository integration

The change MUST add repository-conformant UI metadata, catalog/install/usage

#### Scenario: US5 - Distribute and evaluate a valid Agent Skill 1

- **GIVEN** the repository root
- **WHEN** its documented validation commands run
- **THEN** `unity-developer` is discovered and all referenced resources exist

#### Scenario: US5 - Distribute and evaluate a valid Agent Skill 2

- **GIVEN** realistic architecture and AI prompts
- **WHEN** with-skill and baseline runs are compared
- **THEN** objective assertions and qualitative outputs are available in the skill-creator review format

#### Scenario: US5 - Distribute and evaluate a valid Agent Skill 3

- **GIVEN** the completed implementation
- **WHEN** an independent Oracle verifies it
- **THEN** every functional requirement and buildable success criterion has evidence or the change is rejected with actionable defects
