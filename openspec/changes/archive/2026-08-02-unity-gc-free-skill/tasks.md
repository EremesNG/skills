# Tasks: Unity GC-Free Skill

## Authoring contract

Task identifiers are globally sequential. Root is the sole product writer and
changes a task to `[~]` only while executing it, then to `[x]` only after the
named evidence exists. Independent evaluation agents write only their isolated
run directories. Oracle remains read-only; root persists review and verification
results.

The agreed public TDD seams are the Agent Skill entry/references, the read-only
inspector CLI, repository discovery/validation, and isolated behavioral outputs.
Tests observe stable public concepts, schemas, safety guarantees, and outcomes,
not private helper functions or incidental prose layout.

## MVP scope

US1 is the first independently testable slice: trigger metadata, the routed entry
workflow, allocation contract, measurement ladder, and source authority can turn
an unscoped “make this GC-free” request into a target-player budget and honest
evidence plan. Completion evidence is the focused US1 contract suite plus the
installed structural validator.

## Dependencies

`T001 -> T002 -> T003 -> T004`; `T002 -> T005 -> T006 -> T007 -> T008`;
`T003 + T005..T008 -> T009`; `T001 -> T010 -> T011 -> T012 -> T013`;
`T002 -> T014`; `T002 + T005..T009 -> T015`; `T014 -> T016 -> T017`;
`T003..T017 -> T018 -> T019 -> T020 -> T021`; `T022` can prepare objective
assertions while isolated runs from `T021` are active; `T021 + T022 -> T023 ->
T024 -> T025 -> T026 -> T027 -> T028`.

## Shared test-first contract

- [x] T001 Add one failing public-seam tracer for package absence, frontmatter, seven routed references, core workflow stages, and the response contract with FR-001/FR-012/SC-001 coverage in `tests/test_unity_gc_free.py` | Verify: the focused tracer fails for the expected reason that unity-gc-free/SKILL.md does not exist

## Story US1

- [x] T002 [US1] Initialize the package with the installed skill-creator initializer, then author the minimal evidence-first routed entry workflow and qualified response contract with FR-001/FR-002/FR-003/FR-009/FR-012/SC-001 coverage in `skills/unity-gc-free/SKILL.md` | Verify: the tracer turns green, frontmatter has only name and description, the body stays below 500 lines, and all seven links resolve
- [x] T003 [US1] Add a failing allocation-contract seam test, then define the cost taxonomy, budget template, baseline/warm-up/sample method, all-thread GC.Alloc interpretation, player-versus-Editor rules, and honest success gate with FR-002/FR-003/SC-001/SC-005 coverage in `skills/unity-gc-free/references/allocation-contract.md` | Verify: the new test is observed red then green and rejects unscoped zero-allocation, heap-size-only, or Editor-only claims
- [x] T004 [US1] Add a failing provenance seam test, then record at least twenty primary-source URLs, authority order, access date, current Unity 6 starting points, upstream project/license evidence, known conflicts, benchmark labels, and refresh triggers with FR-011/SC-008 coverage in `skills/unity-gc-free/references/sources.md` | Verify: the new test is observed red then green and counts at least twenty direct URLs while finding every freshness, version-conflict, license, and self-authored-benchmark guard

## Story US2

- [x] T005 [US2] Add a failing hotspot-catalog seam test, then cover strings, logging, closures, delegates, boxing, params, iterators, LINQ, arrays, collections, coroutines, async, exceptions, physics, collision, input, mesh, renderer, UI, reflection, and runtime object churn with qualified built-in alternatives and no blanket bans using FR-004/SC-001 coverage in `skills/unity-gc-free/references/hotspot-catalog.md` | Verify: the new test is observed red then green and every catalog family includes an allocation boundary, evidence check, and at least one version-sensitive counterexample
- [x] T006 [US2] Add a failing library-matrix seam test, then compare direct/built-in mechanisms with ZLinq, Awaitable, UniTask, PrimeTween, ZString, MemoryPack, MessagePack-CSharp, R3, and ObservableCollections across fit, allocation boundary, semantics, compatibility, lifecycle, platform/AOT/threading, provenance/license, avoid, and revisit dimensions with FR-005/FR-007/FR-011/SC-001/SC-008 coverage in `skills/unity-gc-free/references/library-matrix.md` | Verify: the new test is observed red then green and finds every named tool plus the documented single-await, PlayerLoop, closure, tween-reuse/overwrite, final-output, AOT, disposal, and license caveats
- [x] T007 [US2] Add a failing pool-ownership seam test, then define object, collection, array, and caller-buffer pooling with capacity/warm-up, get/release/reset/destroy, overflow/exhaustion, double-return/use-after-return, scene/domain/Addressables teardown, retained-reference clearing, telemetry, and memory caps using FR-006/FR-007/SC-001 coverage in `skills/unity-gc-free/references/pooling-and-buffers.md` | Verify: the new test is observed red then green and covers UnityEngine.Pool, ArrayPool, list reuse, NonAlloc full-buffer policy, subscriptions, cancellation, and reference-count ownership
- [x] T008 [US2] Add a failing unmanaged-boundary seam test, then define NativeArray/NativeList/native-container, allocator, disposal, alias, safety, job-dependency, Burst, and local-adoption rules without forcing ECS/DOTS using FR-008/SC-001 coverage in `skills/unity-gc-free/references/native-memory.md` | Verify: the new test is observed red then green and distinguishes GC from native allocation while enforcing Temp, TempJob, Persistent, disposal, safety, and job completion contracts

## Story US3

- [x] T009 [US3] Add a failing migration-workflow seam test, then define one-source vertical red-green slices that lock functional behavior, timing/order/error/cancellation/thread/lifecycle semantics, caller-buffer overflow, allocation workload, rollback, and representative target remeasurement with FR-003/FR-005/FR-006/FR-008/FR-009/FR-012/SC-001/SC-005 coverage in `skills/unity-gc-free/references/migration-playbook.md` | Verify: the new test is observed red then green and the workflow requires both functional and allocation evidence before success

## Story US4

- [x] T010 [US4] Add a failing CLI test for an invalid root and stable JSON error shape, then implement the minimum Python 3.9 argument/root detection and schema-version behavior with FR-010/SC-002 coverage in `skills/unity-gc-free/scripts/inspect_unity_gc.py` | Verify: the test is observed red then green, a non-Unity root exits 2, and JSON keys and warning text are stable
- [x] T011 [US4] Add failing valid/malformed metadata and relevant-package tests, then parse Unity version, backend hints, sanitized allocation/profiling package coordinates, and warnings defensively with FR-002/FR-010/SC-002 coverage in `skills/unity-gc-free/scripts/inspect_unity_gc.py` | Verify: each case is observed red then green, malformed optional metadata does not abort, relevant packages are sorted, and credential sentinels never appear
- [x] T012 [US4] Add failing signal/exclusion/privacy tests, then scan eligible Assets and embedded Packages C# paths for the eleven bounded investigation signal families while excluding generated/cache/build/VCS/IDE and secret-like paths with FR-010/SC-002 coverage in `skills/unity-gc-free/scripts/inspect_unity_gc.py` | Verify: each case is observed red then green, counts and paths match fixtures, and no source line, matched value, secret path, or credential value is emitted
- [x] T013 [US4] Add failing deterministic-bound, human-output, and no-mutation tests, then finalize stable ordering, max-sample validation, concise lead labeling, and read-only behavior with FR-010/SC-002 coverage in `skills/unity-gc-free/scripts/inspect_unity_gc.py` | Verify: at least nine total inspector cases pass, repeated JSON is byte-identical, samples are bounded, human output rejects diagnosis language, and before/after filesystem snapshots match

## Story US5

- [x] T014 [US5] Add a failing UI-metadata seam test, then generate repository-conformant display metadata with a 25-to-64-character summary and explicit default invocation using FR-001/FR-013/SC-003 coverage in `skills/unity-gc-free/agents/openai.yaml` | Verify: the new test is observed red then green and metadata names Unity GC-Free and invokes $unity-gc-free explicitly
- [x] T015 [US5] Add a failing evaluation-schema seam test, then define three substantive diagnosis, selection, and lifecycle-safe migration prompts with expected outputs and predeclared objective assertions using FR-014/SC-004/SC-005 coverage in `skills/unity-gc-free/evals/evals.json` | Verify: the new test is observed red then green, JSON parses, IDs/prompts are unique, and every case includes at least eight observable assertions
- [x] T016 [US5] Add a failing catalog seam test, update the existing four-skill expectation, then document the fifth skill with discovery, remote install, and usage examples while preserving all existing entries using FR-013/SC-003 coverage in `README.md` | Verify: the new test is observed red then green and both focused unity skill suites find five catalog entries plus the unchanged unity-developer content
- [x] T017 [US5] Add a failing CI seam test, then explicitly compile the new inspector in the existing Python 3.9 and 3.13 matrix without shell globs using FR-013/SC-003 coverage in `.github/workflows/validate.yml` | Verify: the new test is observed red then green and the workflow still compiles every existing script and runs repository unittest discovery
- [x] T018 [US5] Run focused tests, whole-repository tests, explicit Python compilation, structural validation, local five-skill discovery, line/link/source checks, and inspector fixtures, recording only current observed facts with FR-013/SC-001/SC-002/SC-003/SC-008 coverage in `VALIDATION.md` | Verify: every recorded command has a current observed result and no target-player, evaluation, checksum, or Oracle result is claimed before it exists
- [x] T019 [US5] Forward-test the completed draft on the three realistic prompts with independent skill-enabled agents writing isolated artifacts and no expected-answer leakage using FR-014/SC-004 coverage in `tests/unity-gc-free-workspace/iteration-1` | Verify: three non-empty with-skill recommendation files answer the assigned prompts and contain no test-harness diagnosis or unrelated edits
- [x] T020 [US5] Run matching no-skill baselines in isolated contexts with no skill path, skill contents, expected answer, or prior conclusion supplied using FR-014/SC-004 coverage in `tests/unity-gc-free-workspace/iteration-1` | Verify: three non-empty baseline recommendations exist and a contamination scan finds no unity-gc-free skill reference
- [x] T021 [US5] Persist run metadata and available timing/token fields for each isolated execution without inventing unavailable telemetry using FR-014/SC-004 coverage in `tests/unity-gc-free-workspace/iteration-1/run-manifest.json` | Verify: the manifest names six runs, prompt/configuration/output paths, and uses explicit unavailable markers for host metrics that were not exposed
- [x] T022 [US5] Finalize objective assertion metadata while runs are active, preserving the exact pre-grading assertions for diagnosis, scope, semantic safety, lifecycle, compatibility, and verification honesty using FR-014/SC-004/SC-005 coverage in `skills/unity-gc-free/evals/evals.json` | Verify: each case has at least eight clear assertions and each run metadata file receives an identical assertion set before artifact grading
- [x] T023 [US5] Grade six artifacts independently, aggregate comparative metrics, analyze non-discriminating checks, and generate benchmark plus static review output without claiming causality or human preference using FR-014/SC-004/SC-005 coverage in `tests/unity-gc-free-workspace/iteration-1/benchmark.json` | Verify: six grading files, benchmark JSON/Markdown, evidence-grounded analyst notes, and a non-empty review HTML exist and all critical with-skill assertions pass
- [x] T024 [US5] Update the validation report with observed evaluation results, source/host/runtime limitations, and exact evidence while retaining human preference as an unobserved outcome risk using FR-013/FR-014/SC-003/SC-004/SC-005/SC-007/SC-008 coverage in `VALIDATION.md` | Verify: every statement reconciles with generated artifacts and cleanly separates observed facts, inference, limitations, and pending evidence

Outcome SC-007 remains a verification target; no implementation task may mark
human preference observed without actual reviewer feedback.

## Parallel execution

- None: root is the single writer for the coupled skill, tests, catalog, and distribution manifest; evaluation agents may execute isolated run directories concurrently during forward-testing, but those host-level runs do not create independent product-writing tasks.

## Final verification

- [x] T025 Apply the installed simplify workflow to task-owned product and test changes without changing public behavior, allocation semantics, safety guarantees, source qualifications, or unrelated files with FR-001/FR-002/FR-003/FR-004/FR-005/FR-006/FR-007/FR-008/FR-009/FR-010/FR-011/FR-012/FR-013/SC-001/SC-002/SC-003/SC-008 coverage in `skills/unity-gc-free/SKILL.md` | Verify: duplicated or ambiguous guidance is reduced, public contracts remain stable, and focused tests still pass
- [x] T026 Re-run structural, focused, repository, compilation, discovery, source/link, inspector, and evaluation-grade checks after cleanup and persist final pre-checksum evidence with SC-001/SC-002/SC-003/SC-004/SC-005/SC-008 coverage in `VALIDATION.md` | Verify: every buildable check except checksum and independent approval is green and report values match the final product diff
- [x] T027 Regenerate the distribution checksum manifest after every scoped write and independently enumerate and recompute its scope with FR-013/SC-003 coverage in `CHECKSUMS.sha256` | Verify: every scoped distribution file has exactly one digest and audit reports zero missing, extra, duplicate, forbidden, or mismatched entries while openspec and generated evaluation workspaces remain excluded
- [x] T028 Delegate read-only final verification to Oracle and persist its complete FR/buildable-SC evidence matrix with SC-006 coverage in `openspec/changes/unity-gc-free-skill/verify-report.md` | Verify: Oracle returns PASS with 100% FR and buildable-SC coverage and zero unresolved critical or major defects
- [x] T029 Prepare closeout evidence while retaining SC-007 as a residual outcome target unless human feedback exists with FR-014/SC-004/SC-005/SC-006/SC-007 coverage in `openspec/changes/unity-gc-free-skill/archive-report.md` | Verify: closeout validator accepts completed tasks, Oracle PASS, buildable evidence, and an explicit PASS or RISK disposition for every outcome criterion
