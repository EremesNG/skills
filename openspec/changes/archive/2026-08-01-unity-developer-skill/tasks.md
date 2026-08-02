# Tasks: Unity Developer Skill

## Authoring contract

Task identifiers are globally sequential. Root is the sole product writer and
changes a task to `[~]` only while executing it, then to `[x]` only after the
named verification evidence exists. Oracle remains read-only; root persists its
final verdict.

## MVP scope

US1 is the first independently testable slice: the entry workflow, decision
framework, pattern-selection reference, and source provenance can analyze a
Unity coupling problem, prefer a direct solution when sufficient, compare
credible alternatives, and produce the response contract. Completion evidence
is the focused US1 package/behavior tests plus structural validation of the
partial package.

## Dependencies

`T001 -> T002 -> T003 -> T004 -> T005`; `T001 -> T006 -> T007`;
`T001 -> T008`; `T001 -> T009`; `T001 -> T010 -> T011 -> T012 -> T013`;
`T002..T013 -> T014 -> T015` while `T016` is completed during the active
evaluation runs; `T015 + T016 -> T017 -> T018 -> T019 -> T020 -> T021 -> T022
-> T023`.

## Shared test-first contract

- [x] T001 Add one failing public-seam tracer test for package frontmatter, the routed entry workflow, and the response contract with FR-001/FR-009/FR-010/SC-001 coverage in `tests/test_unity_developer.py` | Verify: the single focused tracer test fails for the expected reason that the unity-developer entry point does not exist

## Story US1

- [x] T002 [US1] Author the evidence-first routed entry workflow and actionable decision handoff with FR-001/FR-002/FR-003/FR-007/FR-009/FR-010/SC-001 coverage in `skills/unity-developer/SKILL.md` | Verify: frontmatter, line-limit, workflow-invariant, local-link, and response-contract tests pass
- [x] T003 [US1] Add a failing decision-reference seam test, then define force-based classification, the no-pattern ladder, alternative analysis, revisit triggers, and compact decision record with FR-003/FR-009/SC-001 coverage in `skills/unity-developer/references/decision-framework.md` | Verify: the new test turns red before authoring, then finds every proportional-decision invariant and a reachable reference
- [x] T004 [US1] Add a failing pattern-coverage seam test, then synthesize creational, structural, behavioral, architectural, and optimization selection with fit, avoid, Unity hazard, and composition guidance with FR-004/SC-001 coverage in `skills/unity-developer/references/design-patterns.md` | Verify: the new test turns red before authoring, then finds every required family and representative requested-source pattern
- [x] T005 [US1] Add a failing provenance seam test, then record source authority, caveats, and version-drift handling with FR-002/FR-004/FR-010/SC-001 coverage in `skills/unity-developer/references/sources.md` | Verify: the new test turns red before authoring, then confirms all three user sources, first-party source groups, access date, and current-version lookup rule

## Story US2

- [x] T006 [US2] Add a failing architecture seam test, then define composition-root, lifetime, dependency, messaging, UI, ScriptableObject, scene, assembly, DI, and ECS/DOTS trade-offs with FR-005/FR-009/SC-001 coverage in `skills/unity-developer/references/architecture.md` | Verify: the new test turns red before authoring, then finds ownership, teardown, pure-CSharp seams, authored-versus-runtime data, and framework gates
- [x] T007 [US2] Add a failing engine-safeguard seam test, then define lifecycle, destroyed-object, serialization, domain reload, events, pooling, async/threading, determinism, testing, and target-device profiling rules with FR-005/FR-007/FR-009/SC-001 coverage in `skills/unity-developer/references/unity-engine-constraints.md` | Verify: the new test turns red before authoring, then covers cleanup, static reset, cancellation, pool reset, test seams, and honest profiler evidence

## Story US3

- [x] T008 [US3] Add a failing AI-selection seam test, then define the perception-memory-decision-action-navigation pipeline and proportional selection among rules, FSM/HFSM, behavior trees, utility AI, GOAP, specifications, ML-Agents, inference, and hybrids with FR-006/FR-007/FR-009/SC-001 coverage in `skills/unity-developer/references/ai-systems.md` | Verify: the new test turns red before authoring, then finds determinism, networking, authoring, observability, scheduling, save/replay, and measurable-budget criteria

## Story US4

- [x] T009 [US4] For each inspector public behavior add one failing CLI fixture test before the minimum implementation, then complete the read-only stable JSON contract, defensive parsing, bounded signals, exclusions, and non-disclosure with FR-002/FR-008/SC-002 coverage in `skills/unity-developer/scripts/inspect_unity_project.py` | Verify: each case is observed red then green, at least seven cases pass, output ordering is stable, no source or secret value is emitted, and snapshots match

## Story US5

- [x] T010 [US5] Add a failing metadata seam test, then create repository-conformant display metadata and an explicit default invocation with FR-001/FR-011/SC-003 coverage in `skills/unity-developer/agents/openai.yaml` | Verify: the new test turns red before authoring, then enforces display name, 25-to-64-character description, and explicit skill invocation
- [x] T011 [US5] Add a failing evaluation-schema seam test, then define three realistic prompts and expected outputs for coupling/lifecycle, manager architecture, and networked squad AI before grading assertions are added with FR-012/SC-004 coverage in `skills/unity-developer/evals/evals.json` | Verify: the new test turns red before authoring, then JSON parses with unique IDs, three substantive scenarios, and observable expected results
- [x] T012 [US5] Add a failing catalog seam test, then document the fourth skill with install and usage examples while preserving existing content with FR-011/SC-003 coverage in `README.md` | Verify: the new test turns red before editing, then catalog count, discovery text, remote install command, and usage prompt name unity-developer
- [x] T013 [US5] Add a failing CI seam test, then compile every bundled Python script explicitly in the Python 3.9 and 3.13 matrix with FR-011/SC-003 coverage in `.github/workflows/validate.yml` | Verify: the new test turns red before editing, then finds both script surfaces and the existing unittest command
- [x] T014 [US5] Run focused tests, whole-repository tests, Python compilation, skill structural validation, and four-skill discovery, recording observed results with FR-011/SC-001/SC-002/SC-003 coverage in `VALIDATION.md` | Verify: every documented command has a current observed PASS and no prior validation claim is silently retained when stale
- [x] T015 [US5] Launch independent with-skill and no-skill runs for all three prompts in balanced host-constrained pairs and capture outputs/timing where available with FR-012/SC-004 coverage in `skills/unity-developer-workspace/iteration-1` | Verify: six isolated run directories contain prompt-corresponding outputs and available timing metadata without cross-configuration skill contamination
- [x] T016 [US5] While evaluation runs are active, add objective discriminating assertions for evidence, proportionality, lifecycle, AI decomposition, testing, profiling, and honesty with FR-012/SC-004/SC-005 coverage in `skills/unity-developer/evals/evals.json` | Verify: each of three cases has at least four clear assertions and matching eval metadata is updated before grading
- [x] T017 [US5] Grade every run, aggregate comparative metrics, analyze non-discriminating or high-variance checks, and generate the standard static review artifact with FR-012/SC-004/SC-005 coverage in `skills/unity-developer-workspace/iteration-1` | Verify: six grading files, benchmark JSON and Markdown, analyst observations, and review HTML exist and every with-skill run passes all critical assertions
- [x] T018 [US5] Update the validation report with behavioral benchmark facts, concurrency limitations, DOCX render limitation, and exact verification evidence with FR-011/FR-012/SC-003/SC-004/SC-005 coverage in `VALIDATION.md` | Verify: report statements match generated files and distinguish observed results, limitations, and unobserved human preference

## Parallel execution

- None: root is the single writer for a jointly coupled prompt package, while
  references feed shared tests and checksums; independent evaluation agents write
  isolated run directories only after the product draft is stable and are
  coordinated inside T015 rather than as concurrent product tasks.

## Final verification

- [x] T019 Apply the installed simplify workflow to the task-owned diff without changing behavior or expanding scope with FR-001/FR-002/FR-003/FR-004/FR-005/FR-006/FR-007/FR-008/FR-009/FR-010/FR-011/SC-001/SC-002/SC-003 coverage in `skills/unity-developer` | Verify: duplicated or ambiguous guidance is reduced, public contracts remain stable, and focused tests still pass
- [x] T020 Re-run all structural, focused, repository, compilation, discovery, and evaluation-grade checks after cleanup and record the final pre-checksum evidence with SC-001/SC-002/SC-003/SC-004/SC-005 coverage in `VALIDATION.md` | Verify: every buildable check except checksum and independent approval is green and evidence timestamps/results reflect the final product diff
- [x] T021 Regenerate the checksum manifest after every checksum-scoped product and validation-document write, then recompute it independently with FR-011/SC-003 coverage in `CHECKSUMS.sha256` | Verify: every scoped distribution file has one SHA-256 entry and recomputation reports zero missing, extra, or mismatched entries while openspec and generated evaluation workspaces remain explicitly out of scope
- [x] T022 Delegate read-only final verification to Oracle and persist its FR/SC evidence matrix with SC-006 coverage in `openspec/changes/unity-developer-skill/verify-report.md` | Verify: Oracle returns PASS with 100% FR and buildable-SC coverage and zero unresolved critical or major defects
- [x] T023 Prepare closeout evidence while retaining SC-007 as an honest outcome target rather than an artificial implementation claim with FR-012/SC-004/SC-005/SC-006 coverage in `openspec/changes/unity-developer-skill/archive-report.md` | Verify: closeout validator accepts completed tasks, Oracle PASS, buildable evidence, and explicit residual RISK if human preference feedback remains unobserved

## Convergence after Oracle verification attempt 1

Execute `T024 -> T025 -> T022` before closeout. Finding classifications use
the converge contract: F-001 is `partial` because file/source-value privacy was
implemented but dependency metadata crossed the output boundary unsanitized;
F-002 is `contradicts` because the validation narrative says checksum work is
pending after checksum evidence already exists.

- [x] T024 [F-001][partial][major] Add separate red/green regressions for URI userinfo and token-bearing query/fragment dependency values, then sanitize the package-manifest value boundary in skills/unity-developer/scripts/inspect_unity_project.py with FR-008/SC-002/SC-006 coverage anchored by `tests/test_unity_developer.py` | Verify: each regression is observed failing before its minimum fix, all credential sentinels are absent from JSON and human output, useful non-secret dependency structure remains, and the focused plus repository suites pass
- [x] T025 [F-002][contradicts][minor] Reconcile the checkpoint narrative with completed checksum and failed-first-verification evidence, then regenerate and independently audit CHECKSUMS.sha256 with FR-011/SC-003/SC-006 coverage recorded in `VALIDATION.md` | Verify: validation no longer says checksum generation is pending, records the convergence checks truthfully, and the checksum audit reports zero missing, extra, duplicate, forbidden, or mismatched entries before Oracle re-verification
