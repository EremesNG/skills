# Feature Specification: Unity GC-Free Skill

**Change ID**: `unity-gc-free-skill`<br>
**Route**: Accelerated<br>
**Status**: Draft

## Intent and scope

**Why**: Unity developers need a reusable, evidence-based workflow for finding
managed allocations, defining a meaningful allocation budget, and choosing
low-allocation language patterns, Unity APIs, libraries, and ownership models
without replacing one source of GC pressure with semantic bugs, native-memory
leaks, retained pools, or unmeasured complexity.<br>
**Impact**: Adds a repository skill named `unity-gc-free`, progressively loaded
references, a bounded read-only Unity allocation-hotspot inspector, behavioral
evaluations, repository validation, and catalog documentation. Existing skills
and their behavior remain compatible.<br>
**Affected capabilities**: `unity-gc-free-guidance`, `unity-gc-hotspot-inspection`

## User stories

### US1 - Establish a measurable allocation contract (Priority: P1)

As a Unity performance engineer, I can define what “GC-free” means for one
representative workload and verify it in the correct player environment so that
optimization claims distinguish measured managed allocations from startup,
native-memory, retained-memory, and CPU costs.

**Independent test**: Ask the skill to diagnose a reported per-frame GC spike
without a profiler capture and verify that it requests or derives the material
Unity/backend/platform context, defines warm-up and measurement windows, uses
`GC.Alloc` evidence on all relevant threads, and refuses to claim success from
Editor-only or heap-size evidence.

**Covers**: FR-001, FR-002, FR-003, FR-011, FR-012, SC-001, SC-005

**Acceptance scenarios**:

1. **Given** a request to make a system “GC-free,” **When** the skill scopes the target, **Then** it defines the hot path, representative input, warm-up, pool-capacity state, frame window, target platform/backend, and an explicit managed-allocation budget.
2. **Given** a Profiler capture, **When** the skill evaluates allocations, **Then** it distinguishes `GC.Alloc` bytes and counts from managed-heap size, native allocations, retained pool capacity, CPU time, and collection pauses.
3. **Given** only Editor measurements, **When** the user asks whether a player build is allocation-free, **Then** the skill labels the result provisional and identifies the exact target Development/Release build measurement still required.

### US2 - Select proportionate GC-conscious substitutions (Priority: P1)

As a Unity developer, I can compare built-in mechanisms and maintained libraries
for a measured allocation source so that I choose the smallest compatible
solution and understand its behavioral, lifecycle, platform, package, and
license trade-offs.

**Independent test**: Present a Unity 6 project using LINQ, coroutines, DOTween,
runtime spawning, formatted UI text, and serialization in different frequency
domains; verify that the skill does not prescribe one package globally, compares
manual/reuse and built-in options first, and gives a qualified matrix including
ZLinq, Unity `Awaitable`/UniTask, PrimeTween, Unity pools, ZString, native
containers, and serialization/reactive options only where justified.

**Covers**: FR-002, FR-004, FR-005, FR-006, FR-007, FR-008, FR-011, FR-012, SC-001, SC-005

**Acceptance scenarios**:

1. **Given** allocating LINQ in a measured hot path, **When** alternatives are evaluated, **Then** the skill compares a direct loop and data-layout change with ZLinq, identifies materialization, closure, interface, and pooled-result boundaries, and preserves query semantics.
2. **Given** coroutine allocations, **When** async alternatives are evaluated, **Then** the skill compares cached yield instructions, direct state/update logic, Unity `Awaitable`, and UniTask according to Unity version, timing, cancellation, exception, PlayerLoop, WebGL, and multi-await behavior.
3. **Given** a DOTween migration request, **When** PrimeTween is considered, **Then** the skill identifies delegate capture, capacity warm-up, non-reusable tween, overwrite, sequence, cancellation, material-property, package-version, and license differences before proposing migration.
4. **Given** repeated `Instantiate`/`Destroy`, **When** pooling is considered, **Then** the design defines ownership, warm capacity, expansion/exhaustion policy, reset/cleanup, double-return protection, teardown, and retained-memory limits rather than treating pooling as automatic zero cost.

### US3 - Refactor a hot path without changing behavior (Priority: P1)

As a Unity programmer, I can migrate one allocation source in vertical,
test-first slices so that the observable behavior and lifecycle remain correct
and the allocation regression is demonstrated rather than assumed.

**Independent test**: Give the skill a projectile query/update path with array
APIs, closures, physics queries, temporary lists, strings, logging, and pooled
objects; verify that it first locks behavior and buffer-overflow semantics, then
changes one allocation source at a time and supplies functional plus allocation
evidence.

**Covers**: FR-002, FR-003, FR-004, FR-005, FR-006, FR-007, FR-008, FR-009, FR-012, SC-001, SC-005

**Acceptance scenarios**:

1. **Given** an allocating Unity API with a caller-buffer alternative, **When** the skill migrates it, **Then** it defines capacity, truncation/ordering behavior, overflow telemetry or fallback, and tests the full-buffer case.
2. **Given** a proposed third-party replacement, **When** the existing behavior depends on timing, ordering, cancellation, threading, exception propagation, reuse, or destruction semantics, **Then** those contracts are tested before the dependency is introduced.
3. **Given** a completed optimization slice, **When** it is verified, **Then** functional tests pass and a representative warmed player measurement reports the allocation budget separately from CPU, native, and retained-memory results.

### US4 - Inspect Unity allocation signals safely (Priority: P2)

As a developer or agent, I can obtain a bounded read-only inventory of likely
allocation surfaces and relevant installed packages so that deeper inspection
starts from project evidence without exposing source contents or declaring
regex matches to be defects.

**Independent test**: Run the bundled inspector against representative Unity,
minimal, malformed, secret-containing, generated-path, and non-Unity fixtures
and verify stable JSON/text output, bounded signal samples, package/version
inventory, no source contents, no credential values, and no filesystem mutation.

**Covers**: FR-002, FR-010, SC-002

**Acceptance scenarios**:

1. **Given** a Unity project root, **When** the inspector runs, **Then** it reports Editor version, scripting backend hints when discoverable, declared relevant packages, C# file counts, and bounded paths for LINQ, coroutine, tween, spawn/destroy, query, array-return, collection, lambda, string/logging, and native-container signals.
2. **Given** a signal match, **When** the report is rendered, **Then** it labels the match as an investigation lead and never emits source lines, matched values, or an automatic allocation diagnosis.
3. **Given** generated/cache/build/VCS/IDE or secret-like paths, **When** the inspector scans, **Then** it excludes them and produces deterministic output without changing any project file.

### US5 - Distribute and evaluate a valid Agent Skill (Priority: P1)

As a skill consumer or maintainer, I can discover, install, validate, and
evaluate `unity-gc-free` using repository conventions so that its package and
behavior are reproducible.

**Independent test**: Run structural validation, repository tests, script
compilation, local skill discovery, source-link validation, and realistic
with-skill versus baseline evaluations; then inspect the independent verification
report.

**Covers**: FR-001, FR-011, FR-012, FR-013, FR-014, SC-001, SC-003, SC-004, SC-006, SC-007, SC-008

**Acceptance scenarios**:

1. **Given** the repository root, **When** documented validation runs, **Then** `unity-gc-free` is discovered as the fifth skill and every routed resource and checksum entry is valid.
2. **Given** realistic diagnosis, substitution, and migration prompts, **When** with-skill and baseline runs are compared, **Then** objective assertions and qualitative outputs are available in the skill-creator review format without baseline contamination.
3. **Given** the completed implementation, **When** an independent Oracle verifies it, **Then** every functional requirement and buildable success criterion has evidence or the change is rejected with actionable findings.

## Edge cases

- The project, Unity Editor, representative player build, target device, or
  profiler capture is unavailable; static guidance remains useful but no runtime
  allocation result is claimed.
- A warmed path reports 0 B on the main thread while a worker thread allocates,
  or a per-frame counter hides first-use, scene-transition, pool-growth, or
  exception-path allocations.
- Editor instrumentation creates allocations absent from a player, Debug and
  Release async state machines differ, or Mono and IL2CPP produce different
  allocation/call-stack behavior.
- The target is WebGL or another constrained platform where incremental GC,
  thread-pool APIs, Burst, reflection, dynamic code generation, or package
  behavior differs.
- A NonAlloc query fills its caller buffer; returned hits may be truncated or
  unordered and must not silently change gameplay selection.
- Reusing a `List`, pool, tween capacity, `ArrayPool` buffer, or native container
  avoids steady-state GC but retains excessive memory, leaks state/references,
  grows beyond capacity, double-returns, or is accessed after release.
- A value-enumerable, span, pooled result, awaitable, tween handle, or native
  alias is copied, boxed, stored, awaited twice, used across `await`/`yield`, or
  outlives its owner.
- Library marketing says “zero allocation” while the call site captures a
  closure, formats a string, materializes a result, throws/cancels, grows a pool,
  enables debug tracking, or converts to an allocating compatibility interface.
- Migrating coroutines, DOTween, Rx/UniRx, serialization, or LINQ changes update
  timing, ordering, cancellation, error, thread, reuse, serialization, AOT, or
  numeric semantics.
- PrimeTween package provenance or version documentation conflicts across its
  README, changelog, and registry, or its non-MIT redistribution terms conflict
  with the consuming project.
- Package manifests and READMEs disagree about minimum Unity versions; the
  installed release artifact and project compiler/backend take precedence.
- Pooling a `UnityEngine.Object` conflicts with scene unload, Addressables
  reference counts, destroyed-object semantics, static events, cancellation,
  or domain reload settings.
- A blanket rule such as “never use `foreach`, LINQ, coroutines, strings, or
  allocations” would make cold/editor/setup code less clear without improving a
  measured player hot path.

## Functional requirements

- **FR-001 — Discoverable Unity GC expertise**: `[ADDED unity-gc-free-guidance]`
  The package MUST define `unity-gc-free` with triggering metadata covering Unity
  managed-allocation diagnosis, zero/low-allocation implementation and review,
  GC spikes, pooling, hot paths, non-alloc APIs, performance tests, and named
  alternatives including ZLinq, UniTask, PrimeTween, and Unity pools without
  claiming ownership of generic Unity architecture or all performance work.
- **FR-002 — Evidence-first allocation contract**: `[ADDED unity-gc-free-guidance]`
  The skill MUST inspect available project/version/package/platform/backend and
  profiler evidence, define the exact workload and budget, label facts and
  assumptions, and distinguish managed allocation, GC collection, managed-heap
  size, native allocation, retained memory, asset lifetime, and CPU cost.
- **FR-003 — Reproducible measurement workflow**: `[ADDED unity-gc-free-guidance]`
  The skill MUST establish baseline, warm-up, capacity, sample window, relevant
  threads, profiler markers/call stacks, target-player configuration, and
  functional plus allocation regression checks before declaring an optimization
  successful; Editor-only evidence MUST remain provisional.
- **FR-004 — Allocation hotspot catalog**: `[ADDED unity-gc-free-guidance]`
  Progressively loaded guidance MUST cover strings/formatting/logging, closures
  and delegates, boxing/interfaces, `params`, iterators/enumerators, LINQ and
  materialization, arrays and Unity array-return APIs, collection growth,
  coroutines/async/exceptions, physics/collision/input/mesh/renderer/UI APIs,
  reflection, runtime creation/destruction, and version-sensitive counterexamples
  that prevent blanket rules.
- **FR-005 — Substitution decision matrix**: `[ADDED unity-gc-free-guidance]`
  The skill MUST compare direct loops/reuse and built-in Unity mechanisms before
  recommending ZLinq, Unity `Awaitable`, UniTask, PrimeTween, or another package,
  and MUST record compatibility, install/provenance, allocation boundary,
  semantic differences, lifecycle, platform/AOT/threading limits, maintenance,
  license, rejected alternatives, and revisit criteria.
- **FR-006 — Pool and buffer ownership**: `[ADDED unity-gc-free-guidance]`
  The skill MUST guide object, collection, array, and reusable-buffer pooling
  with a single owner, capacity/warm-up, get/release/reset/destroy contracts,
  overflow and exhaustion behavior, double-release/use-after-return protection,
  scene/domain/addressable teardown, retained-reference clearing, observability,
  and memory caps.
- **FR-007 — Text, serialization, and reactive choices**: `[ADDED unity-gc-free-guidance]`
  Detailed guidance MUST qualify StringBuilder/TMP reuse, ZString, MemoryPack,
  MessagePack-CSharp, R3, ObservableCollections, `ArrayPool`, and similar tools by
  final-result allocations, pooled ownership, source generation/AOT, event/error
  semantics, disposal, thread affinity, and installed-version evidence rather
  than recommending them globally.
- **FR-008 — Unmanaged-memory boundary**: `[ADDED unity-gc-free-guidance]`
  The skill MUST treat NativeArray/NativeList/native containers, Jobs, and Burst
  as unmanaged allocation and scheduling tools rather than free memory; require
  allocator/lifetime/disposal/job-dependency/safety ownership; and avoid requiring
  ECS/DOTS when a local data-oriented or managed reuse solution is sufficient.
- **FR-009 — Semantically safe migration**: `[ADDED unity-gc-free-guidance]`
  For behavior changes, the skill MUST lock the public seam and allocation
  workload, add a failing functional or allocation tracer at the narrowest
  practical EditMode/PlayMode/player seam, migrate one measured source at a time,
  preserve timing/ordering/error/cancellation/thread/lifecycle contracts, and
  roll back or qualify changes that lack representative evidence.
- **FR-010 — Safe allocation-hotspot inspector**: `[ADDED unity-gc-hotspot-inspection]`
  The package MUST provide a dependency-free Python 3.9+ read-only inspector that
  validates a Unity root, parses project/package metadata defensively, inventories
  relevant packages and bounded C# signal paths, excludes generated and
  secret-like paths, emits deterministic text/JSON without source or secret
  values, and labels every static match as a lead rather than a diagnosis.
- **FR-011 — Source authority and freshness**: `[ADDED unity-gc-free-guidance]`
  The skill MUST prioritize observed target-player evidence, official
  version-matched Unity/package documentation, installed artifacts, and upstream
  project sources; record access/version/license caveats; label project-authored
  benchmarks; and refresh unstable APIs, releases, licenses, and compatibility
  instead of hardcoding “latest.”
- **FR-012 — Progressive workflow and response contract**: `[ADDED unity-gc-free-guidance]`
  `SKILL.md` MUST stay below 500 lines, route only relevant focused references,
  and return context, allocation contract, measured hotspots, selected changes,
  rejected alternatives, ownership/lifetimes, implementation, functional and
  allocation evidence, native/retained/CPU trade-offs, residual risks, and the
  exact next measurement.
- **FR-013 — Repository integration**: `[ADDED unity-gc-free-guidance]` The change MUST add repository-conformant UI metadata, catalog/install/usage
  documentation, explicit CI script compilation, checksum coverage, validation
  documentation, and automated tests without regressing or rewriting existing
  skills.
- **FR-014 — Behavioral evaluation**: `[INTERNAL]` The change MUST define three
  realistic evaluations spanning allocation diagnosis, library selection, and a
  lifecycle-safe migration; run isolated with-skill and no-skill baselines as
  host capacity permits; grade objective assertions; aggregate results; and
  generate the standard skill-creator review artifact for human inspection.

## Success criteria

- **SC-001** `[buildable]`: `SKILL.md` is below 500 lines, all focused references
  and required workflows exist, all external recommendations are qualified by an
  allocation boundary and compatibility/lifecycle rule, and the installed
  skill-creator structural validator reports success.
- **SC-002** `[buildable]`: At least nine inspector unit-test cases cover valid,
  non-Unity, malformed, generated/secret-like, signal, relevant-package,
  deterministic/bounded JSON, human-output, and no-mutation behavior; 100% pass
  with Python 3.9-compatible syntax.
- **SC-003** `[buildable]`: 100% of repository tests and Python compilation pass,
  local discovery lists exactly five expected skills including `unity-gc-free`,
  and an independent checksum audit reports zero missing, extra, duplicate,
  forbidden, or mismatched distribution entries.
- **SC-004** `[buildable]`: Exactly 3 evaluation definitions contain substantive
  prompts, expected outputs, and objective assertions; isolated with-skill and
  baseline outputs are graded and aggregated into a benchmark plus static review
  artifact.
- **SC-005** `[buildable]`: 100% of with-skill evaluations pass all critical
  assertions for evidence classification, steady-state allocation scope,
  semantic migration safety, lifecycle/ownership, compatibility, and verification
  honesty.
- **SC-006** `[buildable]`: One independent Oracle returns PASS and the persisted
  report maps 100% of FRs and buildable SCs to evidence with zero unresolved
  critical or major defects.
- **SC-007** `[outcome]`: In at least 2 of 3 evaluation scenarios, human
  review prefers the with-skill answer over its baseline for correctness,
  actionability, qualification, and avoidance of GC folklore.
- **SC-008** `[buildable]`: The source reference contains at least twenty direct
  primary-source URLs spanning current Unity 6 documentation and upstream
  projects, records access date and authority/freshness rules, and explicitly
  flags known version, benchmark, maintenance, and license conflicts.

## Assumptions

- The skill will be authored in English for interoperability with Unity, C#,
  package, and profiler terminology while responding in the user's language.
- `C:\DEV\Proyectos\Webstorm\skills\skills\unity-gc-free\` is the intended
  repository package location and `unity-gc-free` is the accepted final name.
- “GC-free” is a scoped engineering target: zero managed bytes in a named warmed
  steady-state workload unless the user defines a different measurable budget.
- No Unity Editor or real game project is required to author and structurally
  test the reusable skill; runtime compilation and performance remain
  invocation-time responsibilities.
- The inspector uses only the Python standard library, reads metadata and source
  paths defensively, and never requires package installation.

## Dependencies

- Current Unity 6 Manual, Scripting API, package documentation, and profiler
  contracts accessed 2026-08-02.
- Upstream repositories, manifests, changelogs, releases, and licenses for
  ZLinq, UniTask, PrimeTween, MemoryPack, MessagePack-CSharp, ZString, R3,
  ObservableCollections, and selected .NET buffer APIs accessed 2026-08-02.
- Locally installed `skill-creator`, `tdd`, `simplify`, `thoth-sdd`,
  `thoth-archive`, and independent Oracle capabilities.

## Out of scope

- Modifying, opening, profiling, migrating, or shipping a specific Unity game.
- Installing Unity, UPM/NuGet/Asset Store packages, or accepting third-party
  licenses on behalf of a consuming project.
- Guaranteeing that an entire application, all frames, startup, loading,
  exceptions, Editor tooling, native code, or operating-system work allocates no
  memory.
- Publishing independent performance rankings for libraries without a
  reproducible target-project benchmark.
- Vendoring third-party source, binary packages, benchmark results, or license
  text into this skill.
- Building a full C# parser, Roslyn analyzer, automatic rewriter, or universal
  replacement for Unity Profiler, Memory Profiler, and target-device tests.
- Mandating Burst, Jobs, ECS/DOTS, reactive programming, binary serialization,
  pooling, or any third-party package for cold paths or projects that do not need
  them.
