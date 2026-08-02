# Implementation Plan: Unity GC-Free Skill

## Technical context

The repository currently distributes four Agent Skills under `skills/`, uses
Python `unittest` for public package/script contracts, compiles every bundled
Python helper explicitly in GitHub Actions, catalogs each skill in `README.md`,
and tracks distribution files in `CHECKSUMS.sha256`. `unity-developer` already
contains broad Unity lifecycle/performance guidance and a project inspector;
`unity-gc-free` will remain a focused companion for managed-allocation diagnosis,
low-allocation substitutions, migration, and evidence. It will not modify the
existing skill's behavior or claim generic Unity architecture ownership.

The implementation is documentation-heavy but behaviorally observable across
four public seams: skill triggering/routing, the `inspect_unity_gc.py` CLI,
repository discovery/integration, and realistic skill outputs. No Unity Editor
is available or required for package construction. Runtime allocation claims
must therefore be encoded as invocation-time verification protocols, never as
results observed while authoring this repository.

The shared TDD seams proposed for implementation are:

1. `skills/unity-gc-free/SKILL.md` plus routed references as the Agent Skill
   public guidance interface.
2. `python skills/unity-gc-free/scripts/inspect_unity_gc.py --root <path>
   [--json] [--max-samples N]` as a read-only CLI interface.
3. Repository `unittest`, structural validation, explicit Python compilation,
   local skill discovery, link/source checks, and checksum audit as the package
   distribution interface.
4. Three isolated with-skill/no-skill prompts and objective grading assertions
   as the behavioral evaluation interface.

No tests will target private functions or exact prose formatting beyond the
stable concepts, links, schema, metadata, and safety guarantees required by the
specification.

## Constitution Check (pre-design)

- **User-value first**: PASS — The requested deliverable is a discoverable `unity-gc-free` skill; every planned reference, script, test, and evaluation maps to an FR/SC and a concrete allocation-diagnosis or migration outcome.
- **Simplicity and bounded scope**: PASS — The design adds one focused skill, seven progressively loaded references, one dependency-free read-only helper, and repository integration; it excludes Unity project changes, package installation, automatic rewriting, and universal zero-allocation claims.
- **Testable contracts**: PASS — Skill routing, CLI JSON/text behavior, privacy/non-mutation, repository discovery, and behavioral guidance have named public seams and red-green verification; target-player claims remain invocation-time outcomes rather than fabricated local tests.
- **Independent assurance**: PASS — Root is the sole product writer; optional plan review and mandatory final verification are reserved for read-only Oracle agents, and root will only persist their evidence.
- **Traceable delivery**: PASS — `spec.md`, `research.md`, this plan, `tasks.md`, tests, validation evidence, `verify-report.md`, and `archive-report.md` provide durable requirement-to-result traceability.

## Design

### Package architecture

```text
skills/unity-gc-free/
├── SKILL.md
├── agents/openai.yaml
├── evals/evals.json
├── references/
│   ├── allocation-contract.md
│   ├── hotspot-catalog.md
│   ├── library-matrix.md
│   ├── pooling-and-buffers.md
│   ├── native-memory.md
│   ├── migration-playbook.md
│   └── sources.md
└── scripts/inspect_unity_gc.py
```

`SKILL.md` owns only the operating boundary and workflow:

1. classify the request and preserve authorization boundaries;
2. establish Unity/version/backend/platform/package and profiler context;
3. define the allocation contract and cost taxonomy;
4. run the inspector when a project is available and treat results as leads;
5. route only the references needed for the measured source;
6. select the smallest compatible direct/built-in/library solution;
7. migrate one allocation source in a functional-and-allocation red-green slice;
8. verify on the representative target and return an evidence contract.

The seven references separate stable concepts by task signal. Detailed examples,
matrices, version conflicts, install/provenance links, and licenses stay out of
the always-loaded entry point.

### Inspector contract

The dependency-free Python 3.9+ CLI accepts an explicit root and optional JSON
and sample-bound flags. It reads `ProjectVersion.txt`, `ProjectSettings.asset`,
`manifest.json`, and eligible `.cs` files under `Assets/` and embedded
`Packages/`. It excludes generated/cache/build/VCS/IDE directories and
secret-like path segments. It never follows arbitrary external package paths.

Exit codes:

- `0`: inspectable Unity root, including roots with malformed optional metadata;
- `2`: invalid arguments, unreadable root, or no Unity project marker.

JSON schema version 1 uses stable insertion and list ordering:

```text
schema_version
root
unity_detected
unity_version
scripting_backend_hints
relevant_packages
inventory
signals
warnings
```

`relevant_packages` contains only known allocation/profiling candidates and
sanitized declared coordinates. `signals` maps stable identifiers to a count and
bounded relative-path samples. Initial identifiers cover `system_linq`,
`coroutines`, `dotween`, `spawn_destroy`, `allocating_physics_queries`,
`array_return_apis`, `temporary_collections`, `lambdas`, `string_formatting`,
`logging`, and `native_containers`. Regex results are not C# semantic analysis;
human output states that they are investigation leads. Source lines, matches,
string values, and credential values never cross the output boundary.

### Behavioral evaluation

`evals/evals.json` defines three cases:

1. diagnose unexplained `GC.Alloc` in a mobile projectile/physics path and build
   a valid warmed target-player measurement contract;
2. choose among direct code, Unity `Awaitable`, UniTask, PrimeTween, ZLinq, and
   pooling for a WebGL/IL2CPP project without assuming drop-in equivalence;
3. migrate a pooled Addressables-backed gameplay/UI/data path while preserving
   buffer overflow, cancellation, reset, reference-count, native-disposal, and
   functional behavior.

Each case declares objective assertions before execution. Independent with-skill
and no-skill runners write only isolated evaluation directories. A separate
artifact-only grader applies the identical assertions, aggregates the benchmark,
and generates a static review page. One run per configuration is evidence of the
observed sample, not variance, causality, or human preference.

### Requirement mapping

| Requirement | Technical decision | Files/interfaces | Verification seam |
| --- | --- | --- | --- |
| FR-001 | Create precise trigger metadata for allocation diagnosis, implementation, and review without swallowing generic Unity work. | `skills/unity-gc-free/SKILL.md`, `skills/unity-gc-free/agents/openai.yaml` | Frontmatter/UI metadata tests plus structural validator and discovery. |
| FR-002 | Make the scoped cost taxonomy and evidence intake the first workflow stage. | `SKILL.md`, `references/allocation-contract.md` | Contract tests require Unity/backend/platform/workload/budget and managed/native/retained/CPU distinctions. |
| FR-003 | Define a baseline -> warm-up -> sample -> compare -> regress measurement ladder using target-player evidence. | `references/allocation-contract.md`, `references/migration-playbook.md` | Reference tests and evaluation assertions reject Editor-only or heap-size-only success claims. |
| FR-004 | Store a version-qualified catalog of C# and Unity allocation surfaces plus counterexamples to folklore. | `references/hotspot-catalog.md` | Catalog contract checks required language/API families, alternatives, and “measure; do not blanket-ban” guards. |
| FR-005 | Use a per-problem matrix whose rows record fit, allocation boundary, semantics, compatibility, lifecycle, provenance/license, and avoid/revisit rules. | `references/library-matrix.md` | Matrix tests require ZLinq, Awaitable, UniTask, PrimeTween, direct/built-in options, and named caveats. |
| FR-006 | Centralize capacity, ownership, reset, overflow, retained-memory, and teardown protocols. | `references/pooling-and-buffers.md` | Pool reference tests plus full-buffer/double-return/reset evaluation assertions. |
| FR-007 | Route advanced text/serialization/reactive tools only after a measured source is known. | `references/library-matrix.md`, `references/pooling-and-buffers.md` | Tests require final-output, AOT, disposal, event/error, and thread-affinity boundaries for named tools. |
| FR-008 | Separate unmanaged allocation from GC and require allocator/job/disposal evidence without forcing ECS. | `references/native-memory.md` | Tests require Temp/TempJob/Persistent, ownership, safety, Burst/Jobs, alias/dependency, and local-adoption guards. |
| FR-009 | Implement one behavior-preserving vertical slice per measured source. | `SKILL.md`, `references/migration-playbook.md` | Workflow tests and evaluation assertions require functional red, allocation red, minimum migration, lifecycle cleanup, and target remeasurement. |
| FR-010 | Add the stable read-only inspector contract described above. | `scripts/inspect_unity_gc.py`, `tests/test_unity_gc_free.py` | At least nine CLI fixtures cover validity, metadata, packages, exclusions/privacy, signals, determinism, text, bounds, and no mutation. |
| FR-011 | Record primary-source authority, access date, conflicts, licenses, and refresh triggers; no hardcoded latest recommendation. | `references/sources.md`, `references/library-matrix.md`, `research.md` | Source tests count direct URLs and require Unity 6/upstream/version/license/benchmark conflict markers. |
| FR-012 | Keep entry point compact, route seven direct references, and emit a stable evidence-oriented response contract. | `SKILL.md`, `references/*.md` | Line/link/workflow/return-field tests and forward evaluations. |
| FR-013 | Integrate the fifth skill without regressing four existing packages. | `README.md`, `.github/workflows/validate.yml`, `VALIDATION.md`, `CHECKSUMS.sha256`, existing catalog expectation in `tests/test_unity_developer.py` | Whole suite, compilation, discovery, source/link checks, and independent checksum recomputation. |
| FR-014 | Define and run three isolated comparative evaluations with artifact-only grading. | `skills/unity-gc-free/evals/evals.json`, `tests/unity-gc-free-workspace/iteration-1/` | Schema tests, six outputs/grades, benchmark JSON/Markdown, analyst notes, and static review artifact. |

### Success-criterion mapping

| Criterion | Implementation/evidence | Verification seam |
| --- | --- | --- |
| SC-001 | Compact routed package with qualified alternatives. | Focused contract suite and installed `quick_validate.py`. |
| SC-002 | Python inspector plus at least nine fixture cases. | Focused CLI tests, Python compile, deterministic/no-mutation snapshots. |
| SC-003 | Repository integration and final distribution manifest. | Whole suite, cached discovery, explicit compile, independent checksum audit. |
| SC-004 | Three evaluated cases and standard review artifacts. | Eval schema plus six isolated run/grade files, benchmark, review HTML. |
| SC-005 | All critical with-skill assertions pass. | Artifact-only grader and benchmark summary. |
| SC-006 | Independent Oracle approval. | Read-only final verify and persisted FR/SC matrix. |
| SC-007 | Human preference target. | Retain as residual outcome RISK unless feedback is actually observed. |
| SC-008 | At least twenty direct primary-source URLs with conflicts/freshness. | Source-reference URL count and semantic markers. |

## Optional support artifacts

- `research.md`: Included because the requested deep research exposes concrete
  version, semantic, benchmark, maintenance, and license conflicts that the
  implementation must preserve.
- `data-model.md`: Not needed; the only data shape is the small inspector JSON
  contract defined here and asserted at its public CLI seam.
- `contracts/`: Not needed; no network or cross-service API is introduced, and a
  separate schema file would duplicate the CLI tests and plan.
- `quickstart.md`: Not needed; repository install/usage belongs in `README.md`,
  while invocation workflow belongs in `SKILL.md`.

## Risks and migrations

- **Skill overlap**: `unity-developer` also discusses performance. Mitigation:
  narrow `unity-gc-free` metadata to managed allocations and route generic
  architecture to the existing skill; test both metadata contracts. Rollback:
  remove the new package/catalog row without changing `unity-developer`.
- **Folklore encoded as policy**: Static or remembered rules can go stale.
  Mitigation: primary-source provenance, version-matching, counterexamples, and
  measurement-first language. Rollback: remove a disputed matrix row while
  preserving the evidence workflow.
- **Regex false positives/negatives**: The inspector is not a parser. Mitigation:
  emit path-level leads only, stable signal definitions, no severity or automatic
  fix. Rollback: disable a noisy signal independently without changing schema.
- **Inspector privacy**: Reading source/package values could expose secrets.
  Mitigation: exclude secret-like paths, sanitize dependency coordinates, emit
  no source/match values, and test sentinel non-disclosure plus no mutation.
- **Buffer truncation bugs**: NonAlloc APIs can silently alter results.
  Mitigation: make overflow policy and full-buffer tests mandatory; never present
  caller-buffer conversion as a mechanical rewrite.
- **Dependency/license drift**: Package docs, minimum Unity versions, or license
  terms can conflict. Mitigation: record conflicts, pin exact installed artifact,
  require user/project acceptance, and avoid vendoring packages or license text.
- **Evaluation contamination**: Baselines could see the skill or expected answer.
  Mitigation: isolated task prompts, minimal context, separate output directories,
  assertions declared before grading, and artifact-only reviewers.
- **Unavailable Unity runtime**: Local tests cannot prove player allocations.
  Mitigation: test the skill's honesty and protocols; mark target performance as
  invocation-time evidence and never claim local Unity compilation/profiling.
- **Catalog migration**: Existing `unity-developer` test expects four skills.
  Mitigation: change only the catalog-count expectation to five and keep all
  existing unity-developer assertions intact. Rollback restores that single
  expectation with removal of the new skill.
- **Checksum churn**: Late writes can stale the manifest. Mitigation: generate it
  only after all distribution/validation writes, then independently enumerate
  scope and recompute every hash; repeat after any scoped correction.

## Constitution Check (post-design)

- **User-value first**: PASS — The completed design turns the user's examples and deeper research into a measurable diagnose/select/migrate/verify workflow, a safe evidence helper, and reusable qualified references; no component lacks an FR/SC owner.
- **Simplicity and bounded scope**: PASS — Progressive disclosure keeps the entry point small, one script supplies repeatable evidence, and explicit non-goals prevent Unity project mutation, package installation, automatic rewriting, and dependency cargo culting.
- **Testable contracts**: PASS — Every buildable criterion maps to a public guidance, CLI, distribution, source, or evaluation seam; runtime-only allocation outcomes are explicitly separated from locally buildable evidence.
- **Independent assurance**: PASS — Design ownership remains with root, behavioral runners/graders are isolated, the user controls optional plan review, and mandatory final acceptance remains Oracle-only.
- **Traceable delivery**: PASS — Exact files, interfaces, requirement/criterion mappings, TDD seams, migration risks, rollback paths, evaluation evidence, and closeout ownership are recorded for task generation and independent verification.
