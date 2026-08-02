# Unity Gc Free Guidance Specification

## Purpose

Durable behavioral contract for `unity-gc-free-guidance`.

## Requirements

### Requirement: Discoverable Unity GC expertise

The package MUST define `unity-gc-free` with triggering metadata covering Unity

#### Scenario: US1 - Establish a measurable allocation contract 1

- **GIVEN** a Profiler capture
- **WHEN** the skill evaluates allocations
- **THEN** it distinguishes `GC.Alloc` bytes and counts from managed-heap size, native allocations, retained pool capacity, CPU time, and collection pauses

#### Scenario: US1 - Establish a measurable allocation contract 2

- **GIVEN** only Editor measurements
- **WHEN** the user asks whether a player build is allocation-free
- **THEN** the skill labels the result provisional and identifies the exact target Development/Release build measurement still required

#### Scenario: US5 - Distribute and evaluate a valid Agent Skill 1

- **GIVEN** the repository root
- **WHEN** documented validation runs
- **THEN** `unity-gc-free` is discovered as the fifth skill and every routed resource and checksum entry is valid

#### Scenario: US5 - Distribute and evaluate a valid Agent Skill 2

- **GIVEN** realistic diagnosis, substitution, and migration prompts
- **WHEN** with-skill and baseline runs are compared
- **THEN** objective assertions and qualitative outputs are available in the skill-creator review format without baseline contamination

#### Scenario: US5 - Distribute and evaluate a valid Agent Skill 3

- **GIVEN** the completed implementation
- **WHEN** an independent Oracle verifies it
- **THEN** every functional requirement and buildable success criterion has evidence or the change is rejected with actionable findings

### Requirement: Evidence-first allocation contract

The skill MUST inspect available project/version/package/platform/backend and

#### Scenario: US1 - Establish a measurable allocation contract 1

- **GIVEN** a Profiler capture
- **WHEN** the skill evaluates allocations
- **THEN** it distinguishes `GC.Alloc` bytes and counts from managed-heap size, native allocations, retained pool capacity, CPU time, and collection pauses

#### Scenario: US1 - Establish a measurable allocation contract 2

- **GIVEN** only Editor measurements
- **WHEN** the user asks whether a player build is allocation-free
- **THEN** the skill labels the result provisional and identifies the exact target Development/Release build measurement still required

#### Scenario: US2 - Select proportionate GC-conscious substitutions 1

- **GIVEN** allocating LINQ in a measured hot path
- **WHEN** alternatives are evaluated
- **THEN** the skill compares a direct loop and data-layout change with ZLinq, identifies materialization, closure, interface, and pooled-result boundaries, and preserves query semantics

#### Scenario: US2 - Select proportionate GC-conscious substitutions 2

- **GIVEN** coroutine allocations
- **WHEN** async alternatives are evaluated
- **THEN** the skill compares cached yield instructions, direct state/update logic, Unity `Awaitable`, and UniTask according to Unity version, timing, cancellation, exception, PlayerLoop, WebGL, and multi-await behavior

#### Scenario: US2 - Select proportionate GC-conscious substitutions 3

- **GIVEN** a DOTween migration request
- **WHEN** PrimeTween is considered
- **THEN** the skill identifies delegate capture, capacity warm-up, non-reusable tween, overwrite, sequence, cancellation, material-property, package-version, and license differences before proposing migration

#### Scenario: US2 - Select proportionate GC-conscious substitutions 4

- **GIVEN** repeated `Instantiate`/`Destroy`
- **WHEN** pooling is considered
- **THEN** the design defines ownership, warm capacity, expansion/exhaustion policy, reset/cleanup, double-return protection, teardown, and retained-memory limits rather than treating pooling as automatic zero cost

#### Scenario: US3 - Refactor a hot path without changing behavior 1

- **GIVEN** an allocating Unity API with a caller-buffer alternative
- **WHEN** the skill migrates it
- **THEN** it defines capacity, truncation/ordering behavior, overflow telemetry or fallback, and tests the full-buffer case

#### Scenario: US3 - Refactor a hot path without changing behavior 2

- **GIVEN** a proposed third-party replacement
- **WHEN** the existing behavior depends on timing, ordering, cancellation, threading, exception propagation, reuse, or destruction semantics
- **THEN** those contracts are tested before the dependency is introduced

#### Scenario: US3 - Refactor a hot path without changing behavior 3

- **GIVEN** a completed optimization slice
- **WHEN** it is verified
- **THEN** functional tests pass and a representative warmed player measurement reports the allocation budget separately from CPU, native, and retained-memory results

#### Scenario: US4 - Inspect Unity allocation signals safely 1

- **GIVEN** a Unity project root
- **WHEN** the inspector runs
- **THEN** it reports Editor version, scripting backend hints when discoverable, declared relevant packages, C# file counts, and bounded paths for LINQ, coroutine, tween, spawn/destroy, query, array-return, collection, lambda, string/logging, and native-container signals

#### Scenario: US4 - Inspect Unity allocation signals safely 2

- **GIVEN** a signal match
- **WHEN** the report is rendered
- **THEN** it labels the match as an investigation lead and never emits source lines, matched values, or an automatic allocation diagnosis

#### Scenario: US4 - Inspect Unity allocation signals safely 3

- **GIVEN** generated/cache/build/VCS/IDE or secret-like paths
- **WHEN** the inspector scans
- **THEN** it excludes them and produces deterministic output without changing any project file

### Requirement: Reproducible measurement workflow

The skill MUST establish baseline, warm-up, capacity, sample window, relevant

#### Scenario: US1 - Establish a measurable allocation contract 1

- **GIVEN** a Profiler capture
- **WHEN** the skill evaluates allocations
- **THEN** it distinguishes `GC.Alloc` bytes and counts from managed-heap size, native allocations, retained pool capacity, CPU time, and collection pauses

#### Scenario: US1 - Establish a measurable allocation contract 2

- **GIVEN** only Editor measurements
- **WHEN** the user asks whether a player build is allocation-free
- **THEN** the skill labels the result provisional and identifies the exact target Development/Release build measurement still required

#### Scenario: US3 - Refactor a hot path without changing behavior 1

- **GIVEN** an allocating Unity API with a caller-buffer alternative
- **WHEN** the skill migrates it
- **THEN** it defines capacity, truncation/ordering behavior, overflow telemetry or fallback, and tests the full-buffer case

#### Scenario: US3 - Refactor a hot path without changing behavior 2

- **GIVEN** a proposed third-party replacement
- **WHEN** the existing behavior depends on timing, ordering, cancellation, threading, exception propagation, reuse, or destruction semantics
- **THEN** those contracts are tested before the dependency is introduced

#### Scenario: US3 - Refactor a hot path without changing behavior 3

- **GIVEN** a completed optimization slice
- **WHEN** it is verified
- **THEN** functional tests pass and a representative warmed player measurement reports the allocation budget separately from CPU, native, and retained-memory results

### Requirement: Allocation hotspot catalog

Progressively loaded guidance MUST cover strings/formatting/logging, closures

#### Scenario: US2 - Select proportionate GC-conscious substitutions 1

- **GIVEN** allocating LINQ in a measured hot path
- **WHEN** alternatives are evaluated
- **THEN** the skill compares a direct loop and data-layout change with ZLinq, identifies materialization, closure, interface, and pooled-result boundaries, and preserves query semantics

#### Scenario: US2 - Select proportionate GC-conscious substitutions 2

- **GIVEN** coroutine allocations
- **WHEN** async alternatives are evaluated
- **THEN** the skill compares cached yield instructions, direct state/update logic, Unity `Awaitable`, and UniTask according to Unity version, timing, cancellation, exception, PlayerLoop, WebGL, and multi-await behavior

#### Scenario: US2 - Select proportionate GC-conscious substitutions 3

- **GIVEN** a DOTween migration request
- **WHEN** PrimeTween is considered
- **THEN** the skill identifies delegate capture, capacity warm-up, non-reusable tween, overwrite, sequence, cancellation, material-property, package-version, and license differences before proposing migration

#### Scenario: US2 - Select proportionate GC-conscious substitutions 4

- **GIVEN** repeated `Instantiate`/`Destroy`
- **WHEN** pooling is considered
- **THEN** the design defines ownership, warm capacity, expansion/exhaustion policy, reset/cleanup, double-return protection, teardown, and retained-memory limits rather than treating pooling as automatic zero cost

#### Scenario: US3 - Refactor a hot path without changing behavior 1

- **GIVEN** an allocating Unity API with a caller-buffer alternative
- **WHEN** the skill migrates it
- **THEN** it defines capacity, truncation/ordering behavior, overflow telemetry or fallback, and tests the full-buffer case

#### Scenario: US3 - Refactor a hot path without changing behavior 2

- **GIVEN** a proposed third-party replacement
- **WHEN** the existing behavior depends on timing, ordering, cancellation, threading, exception propagation, reuse, or destruction semantics
- **THEN** those contracts are tested before the dependency is introduced

#### Scenario: US3 - Refactor a hot path without changing behavior 3

- **GIVEN** a completed optimization slice
- **WHEN** it is verified
- **THEN** functional tests pass and a representative warmed player measurement reports the allocation budget separately from CPU, native, and retained-memory results

### Requirement: Substitution decision matrix

The skill MUST compare direct loops/reuse and built-in Unity mechanisms before

#### Scenario: US2 - Select proportionate GC-conscious substitutions 1

- **GIVEN** allocating LINQ in a measured hot path
- **WHEN** alternatives are evaluated
- **THEN** the skill compares a direct loop and data-layout change with ZLinq, identifies materialization, closure, interface, and pooled-result boundaries, and preserves query semantics

#### Scenario: US2 - Select proportionate GC-conscious substitutions 2

- **GIVEN** coroutine allocations
- **WHEN** async alternatives are evaluated
- **THEN** the skill compares cached yield instructions, direct state/update logic, Unity `Awaitable`, and UniTask according to Unity version, timing, cancellation, exception, PlayerLoop, WebGL, and multi-await behavior

#### Scenario: US2 - Select proportionate GC-conscious substitutions 3

- **GIVEN** a DOTween migration request
- **WHEN** PrimeTween is considered
- **THEN** the skill identifies delegate capture, capacity warm-up, non-reusable tween, overwrite, sequence, cancellation, material-property, package-version, and license differences before proposing migration

#### Scenario: US2 - Select proportionate GC-conscious substitutions 4

- **GIVEN** repeated `Instantiate`/`Destroy`
- **WHEN** pooling is considered
- **THEN** the design defines ownership, warm capacity, expansion/exhaustion policy, reset/cleanup, double-return protection, teardown, and retained-memory limits rather than treating pooling as automatic zero cost

#### Scenario: US3 - Refactor a hot path without changing behavior 1

- **GIVEN** an allocating Unity API with a caller-buffer alternative
- **WHEN** the skill migrates it
- **THEN** it defines capacity, truncation/ordering behavior, overflow telemetry or fallback, and tests the full-buffer case

#### Scenario: US3 - Refactor a hot path without changing behavior 2

- **GIVEN** a proposed third-party replacement
- **WHEN** the existing behavior depends on timing, ordering, cancellation, threading, exception propagation, reuse, or destruction semantics
- **THEN** those contracts are tested before the dependency is introduced

#### Scenario: US3 - Refactor a hot path without changing behavior 3

- **GIVEN** a completed optimization slice
- **WHEN** it is verified
- **THEN** functional tests pass and a representative warmed player measurement reports the allocation budget separately from CPU, native, and retained-memory results

### Requirement: Pool and buffer ownership

The skill MUST guide object, collection, array, and reusable-buffer pooling

#### Scenario: US2 - Select proportionate GC-conscious substitutions 1

- **GIVEN** allocating LINQ in a measured hot path
- **WHEN** alternatives are evaluated
- **THEN** the skill compares a direct loop and data-layout change with ZLinq, identifies materialization, closure, interface, and pooled-result boundaries, and preserves query semantics

#### Scenario: US2 - Select proportionate GC-conscious substitutions 2

- **GIVEN** coroutine allocations
- **WHEN** async alternatives are evaluated
- **THEN** the skill compares cached yield instructions, direct state/update logic, Unity `Awaitable`, and UniTask according to Unity version, timing, cancellation, exception, PlayerLoop, WebGL, and multi-await behavior

#### Scenario: US2 - Select proportionate GC-conscious substitutions 3

- **GIVEN** a DOTween migration request
- **WHEN** PrimeTween is considered
- **THEN** the skill identifies delegate capture, capacity warm-up, non-reusable tween, overwrite, sequence, cancellation, material-property, package-version, and license differences before proposing migration

#### Scenario: US2 - Select proportionate GC-conscious substitutions 4

- **GIVEN** repeated `Instantiate`/`Destroy`
- **WHEN** pooling is considered
- **THEN** the design defines ownership, warm capacity, expansion/exhaustion policy, reset/cleanup, double-return protection, teardown, and retained-memory limits rather than treating pooling as automatic zero cost

#### Scenario: US3 - Refactor a hot path without changing behavior 1

- **GIVEN** an allocating Unity API with a caller-buffer alternative
- **WHEN** the skill migrates it
- **THEN** it defines capacity, truncation/ordering behavior, overflow telemetry or fallback, and tests the full-buffer case

#### Scenario: US3 - Refactor a hot path without changing behavior 2

- **GIVEN** a proposed third-party replacement
- **WHEN** the existing behavior depends on timing, ordering, cancellation, threading, exception propagation, reuse, or destruction semantics
- **THEN** those contracts are tested before the dependency is introduced

#### Scenario: US3 - Refactor a hot path without changing behavior 3

- **GIVEN** a completed optimization slice
- **WHEN** it is verified
- **THEN** functional tests pass and a representative warmed player measurement reports the allocation budget separately from CPU, native, and retained-memory results

### Requirement: Text, serialization, and reactive choices

Detailed guidance MUST qualify StringBuilder/TMP reuse, ZString, MemoryPack,

#### Scenario: US2 - Select proportionate GC-conscious substitutions 1

- **GIVEN** allocating LINQ in a measured hot path
- **WHEN** alternatives are evaluated
- **THEN** the skill compares a direct loop and data-layout change with ZLinq, identifies materialization, closure, interface, and pooled-result boundaries, and preserves query semantics

#### Scenario: US2 - Select proportionate GC-conscious substitutions 2

- **GIVEN** coroutine allocations
- **WHEN** async alternatives are evaluated
- **THEN** the skill compares cached yield instructions, direct state/update logic, Unity `Awaitable`, and UniTask according to Unity version, timing, cancellation, exception, PlayerLoop, WebGL, and multi-await behavior

#### Scenario: US2 - Select proportionate GC-conscious substitutions 3

- **GIVEN** a DOTween migration request
- **WHEN** PrimeTween is considered
- **THEN** the skill identifies delegate capture, capacity warm-up, non-reusable tween, overwrite, sequence, cancellation, material-property, package-version, and license differences before proposing migration

#### Scenario: US2 - Select proportionate GC-conscious substitutions 4

- **GIVEN** repeated `Instantiate`/`Destroy`
- **WHEN** pooling is considered
- **THEN** the design defines ownership, warm capacity, expansion/exhaustion policy, reset/cleanup, double-return protection, teardown, and retained-memory limits rather than treating pooling as automatic zero cost

#### Scenario: US3 - Refactor a hot path without changing behavior 1

- **GIVEN** an allocating Unity API with a caller-buffer alternative
- **WHEN** the skill migrates it
- **THEN** it defines capacity, truncation/ordering behavior, overflow telemetry or fallback, and tests the full-buffer case

#### Scenario: US3 - Refactor a hot path without changing behavior 2

- **GIVEN** a proposed third-party replacement
- **WHEN** the existing behavior depends on timing, ordering, cancellation, threading, exception propagation, reuse, or destruction semantics
- **THEN** those contracts are tested before the dependency is introduced

#### Scenario: US3 - Refactor a hot path without changing behavior 3

- **GIVEN** a completed optimization slice
- **WHEN** it is verified
- **THEN** functional tests pass and a representative warmed player measurement reports the allocation budget separately from CPU, native, and retained-memory results

### Requirement: Unmanaged-memory boundary

The skill MUST treat NativeArray/NativeList/native containers, Jobs, and Burst

#### Scenario: US2 - Select proportionate GC-conscious substitutions 1

- **GIVEN** allocating LINQ in a measured hot path
- **WHEN** alternatives are evaluated
- **THEN** the skill compares a direct loop and data-layout change with ZLinq, identifies materialization, closure, interface, and pooled-result boundaries, and preserves query semantics

#### Scenario: US2 - Select proportionate GC-conscious substitutions 2

- **GIVEN** coroutine allocations
- **WHEN** async alternatives are evaluated
- **THEN** the skill compares cached yield instructions, direct state/update logic, Unity `Awaitable`, and UniTask according to Unity version, timing, cancellation, exception, PlayerLoop, WebGL, and multi-await behavior

#### Scenario: US2 - Select proportionate GC-conscious substitutions 3

- **GIVEN** a DOTween migration request
- **WHEN** PrimeTween is considered
- **THEN** the skill identifies delegate capture, capacity warm-up, non-reusable tween, overwrite, sequence, cancellation, material-property, package-version, and license differences before proposing migration

#### Scenario: US2 - Select proportionate GC-conscious substitutions 4

- **GIVEN** repeated `Instantiate`/`Destroy`
- **WHEN** pooling is considered
- **THEN** the design defines ownership, warm capacity, expansion/exhaustion policy, reset/cleanup, double-return protection, teardown, and retained-memory limits rather than treating pooling as automatic zero cost

#### Scenario: US3 - Refactor a hot path without changing behavior 1

- **GIVEN** an allocating Unity API with a caller-buffer alternative
- **WHEN** the skill migrates it
- **THEN** it defines capacity, truncation/ordering behavior, overflow telemetry or fallback, and tests the full-buffer case

#### Scenario: US3 - Refactor a hot path without changing behavior 2

- **GIVEN** a proposed third-party replacement
- **WHEN** the existing behavior depends on timing, ordering, cancellation, threading, exception propagation, reuse, or destruction semantics
- **THEN** those contracts are tested before the dependency is introduced

#### Scenario: US3 - Refactor a hot path without changing behavior 3

- **GIVEN** a completed optimization slice
- **WHEN** it is verified
- **THEN** functional tests pass and a representative warmed player measurement reports the allocation budget separately from CPU, native, and retained-memory results

### Requirement: Semantically safe migration

For behavior changes, the skill MUST lock the public seam and allocation

#### Scenario: US3 - Refactor a hot path without changing behavior 1

- **GIVEN** an allocating Unity API with a caller-buffer alternative
- **WHEN** the skill migrates it
- **THEN** it defines capacity, truncation/ordering behavior, overflow telemetry or fallback, and tests the full-buffer case

#### Scenario: US3 - Refactor a hot path without changing behavior 2

- **GIVEN** a proposed third-party replacement
- **WHEN** the existing behavior depends on timing, ordering, cancellation, threading, exception propagation, reuse, or destruction semantics
- **THEN** those contracts are tested before the dependency is introduced

#### Scenario: US3 - Refactor a hot path without changing behavior 3

- **GIVEN** a completed optimization slice
- **WHEN** it is verified
- **THEN** functional tests pass and a representative warmed player measurement reports the allocation budget separately from CPU, native, and retained-memory results

### Requirement: Source authority and freshness

The skill MUST prioritize observed target-player evidence, official

#### Scenario: US1 - Establish a measurable allocation contract 1

- **GIVEN** a Profiler capture
- **WHEN** the skill evaluates allocations
- **THEN** it distinguishes `GC.Alloc` bytes and counts from managed-heap size, native allocations, retained pool capacity, CPU time, and collection pauses

#### Scenario: US1 - Establish a measurable allocation contract 2

- **GIVEN** only Editor measurements
- **WHEN** the user asks whether a player build is allocation-free
- **THEN** the skill labels the result provisional and identifies the exact target Development/Release build measurement still required

#### Scenario: US2 - Select proportionate GC-conscious substitutions 1

- **GIVEN** allocating LINQ in a measured hot path
- **WHEN** alternatives are evaluated
- **THEN** the skill compares a direct loop and data-layout change with ZLinq, identifies materialization, closure, interface, and pooled-result boundaries, and preserves query semantics

#### Scenario: US2 - Select proportionate GC-conscious substitutions 2

- **GIVEN** coroutine allocations
- **WHEN** async alternatives are evaluated
- **THEN** the skill compares cached yield instructions, direct state/update logic, Unity `Awaitable`, and UniTask according to Unity version, timing, cancellation, exception, PlayerLoop, WebGL, and multi-await behavior

#### Scenario: US2 - Select proportionate GC-conscious substitutions 3

- **GIVEN** a DOTween migration request
- **WHEN** PrimeTween is considered
- **THEN** the skill identifies delegate capture, capacity warm-up, non-reusable tween, overwrite, sequence, cancellation, material-property, package-version, and license differences before proposing migration

#### Scenario: US2 - Select proportionate GC-conscious substitutions 4

- **GIVEN** repeated `Instantiate`/`Destroy`
- **WHEN** pooling is considered
- **THEN** the design defines ownership, warm capacity, expansion/exhaustion policy, reset/cleanup, double-return protection, teardown, and retained-memory limits rather than treating pooling as automatic zero cost

#### Scenario: US5 - Distribute and evaluate a valid Agent Skill 1

- **GIVEN** the repository root
- **WHEN** documented validation runs
- **THEN** `unity-gc-free` is discovered as the fifth skill and every routed resource and checksum entry is valid

#### Scenario: US5 - Distribute and evaluate a valid Agent Skill 2

- **GIVEN** realistic diagnosis, substitution, and migration prompts
- **WHEN** with-skill and baseline runs are compared
- **THEN** objective assertions and qualitative outputs are available in the skill-creator review format without baseline contamination

#### Scenario: US5 - Distribute and evaluate a valid Agent Skill 3

- **GIVEN** the completed implementation
- **WHEN** an independent Oracle verifies it
- **THEN** every functional requirement and buildable success criterion has evidence or the change is rejected with actionable findings

### Requirement: Progressive workflow and response contract

`SKILL.md` MUST stay below 500 lines, route only relevant focused references,

#### Scenario: US1 - Establish a measurable allocation contract 1

- **GIVEN** a Profiler capture
- **WHEN** the skill evaluates allocations
- **THEN** it distinguishes `GC.Alloc` bytes and counts from managed-heap size, native allocations, retained pool capacity, CPU time, and collection pauses

#### Scenario: US1 - Establish a measurable allocation contract 2

- **GIVEN** only Editor measurements
- **WHEN** the user asks whether a player build is allocation-free
- **THEN** the skill labels the result provisional and identifies the exact target Development/Release build measurement still required

#### Scenario: US2 - Select proportionate GC-conscious substitutions 1

- **GIVEN** allocating LINQ in a measured hot path
- **WHEN** alternatives are evaluated
- **THEN** the skill compares a direct loop and data-layout change with ZLinq, identifies materialization, closure, interface, and pooled-result boundaries, and preserves query semantics

#### Scenario: US2 - Select proportionate GC-conscious substitutions 2

- **GIVEN** coroutine allocations
- **WHEN** async alternatives are evaluated
- **THEN** the skill compares cached yield instructions, direct state/update logic, Unity `Awaitable`, and UniTask according to Unity version, timing, cancellation, exception, PlayerLoop, WebGL, and multi-await behavior

#### Scenario: US2 - Select proportionate GC-conscious substitutions 3

- **GIVEN** a DOTween migration request
- **WHEN** PrimeTween is considered
- **THEN** the skill identifies delegate capture, capacity warm-up, non-reusable tween, overwrite, sequence, cancellation, material-property, package-version, and license differences before proposing migration

#### Scenario: US2 - Select proportionate GC-conscious substitutions 4

- **GIVEN** repeated `Instantiate`/`Destroy`
- **WHEN** pooling is considered
- **THEN** the design defines ownership, warm capacity, expansion/exhaustion policy, reset/cleanup, double-return protection, teardown, and retained-memory limits rather than treating pooling as automatic zero cost

#### Scenario: US3 - Refactor a hot path without changing behavior 1

- **GIVEN** an allocating Unity API with a caller-buffer alternative
- **WHEN** the skill migrates it
- **THEN** it defines capacity, truncation/ordering behavior, overflow telemetry or fallback, and tests the full-buffer case

#### Scenario: US3 - Refactor a hot path without changing behavior 2

- **GIVEN** a proposed third-party replacement
- **WHEN** the existing behavior depends on timing, ordering, cancellation, threading, exception propagation, reuse, or destruction semantics
- **THEN** those contracts are tested before the dependency is introduced

#### Scenario: US3 - Refactor a hot path without changing behavior 3

- **GIVEN** a completed optimization slice
- **WHEN** it is verified
- **THEN** functional tests pass and a representative warmed player measurement reports the allocation budget separately from CPU, native, and retained-memory results

#### Scenario: US5 - Distribute and evaluate a valid Agent Skill 1

- **GIVEN** the repository root
- **WHEN** documented validation runs
- **THEN** `unity-gc-free` is discovered as the fifth skill and every routed resource and checksum entry is valid

#### Scenario: US5 - Distribute and evaluate a valid Agent Skill 2

- **GIVEN** realistic diagnosis, substitution, and migration prompts
- **WHEN** with-skill and baseline runs are compared
- **THEN** objective assertions and qualitative outputs are available in the skill-creator review format without baseline contamination

#### Scenario: US5 - Distribute and evaluate a valid Agent Skill 3

- **GIVEN** the completed implementation
- **WHEN** an independent Oracle verifies it
- **THEN** every functional requirement and buildable success criterion has evidence or the change is rejected with actionable findings

### Requirement: Repository integration

The change MUST add repository-conformant UI metadata, catalog/install/usage

#### Scenario: US5 - Distribute and evaluate a valid Agent Skill 1

- **GIVEN** the repository root
- **WHEN** documented validation runs
- **THEN** `unity-gc-free` is discovered as the fifth skill and every routed resource and checksum entry is valid

#### Scenario: US5 - Distribute and evaluate a valid Agent Skill 2

- **GIVEN** realistic diagnosis, substitution, and migration prompts
- **WHEN** with-skill and baseline runs are compared
- **THEN** objective assertions and qualitative outputs are available in the skill-creator review format without baseline contamination

#### Scenario: US5 - Distribute and evaluate a valid Agent Skill 3

- **GIVEN** the completed implementation
- **WHEN** an independent Oracle verifies it
- **THEN** every functional requirement and buildable success criterion has evidence or the change is rejected with actionable findings
