# Implementation Plan: Unity Developer Skill

## Technical context

The repository currently packages three Agent Skills under `skills/`, uses
frontmatter-only `name`/`description` metadata, optional `agents/openai.yaml`,
JSON evaluations, standard-library Python helpers, `unittest`, Python 3.9/3.13
CI, documented local discovery, and a repository-wide checksum manifest. The
worktree was clean before SDD initialization; existing user files are not to be
rewritten outside the named integration surfaces.

The supplied DOCX was structurally read in full and the requested web sources
were reviewed. The design must retain their useful Unity-specific taxonomy while
correcting overbroad claims and avoiding version-pinned advice. The package must
be useful without an installed Unity Editor and become more precise when a Unity
project is available.

Implementation will use one product writer in this root task. Independent
with-skill/baseline agents will generate evaluation outputs, and an Oracle agent
will perform the mandatory read-only final verification. No child may delegate.

## Constitution Check (pre-design)

- **User-value first**: PASS — The user requested a professional Unity
  solution-selection skill; every planned surface directly improves discovery,
  grounding, decisions, implementation, or validation of that skill.
- **Simplicity and bounded scope**: PASS — The design uses one lean entry
  point, focused references, one read-only helper, and existing repository
  conventions; it excludes Unity-project delivery and framework installation.
- **Testable contracts**: PASS — Every story has observable scenarios, the
  helper has a CLI seam, package behavior has unit tests, and skill quality has
  three comparative evaluations.
- **Independent assurance**: PASS — Root owns implementation but cannot
  approve it; independent agents own evaluation runs and Oracle owns final
  verification.
- **Traceable delivery**: PASS — `spec.md`, this plan, `tasks.md`, evaluation
  metadata, benchmark outputs, `verify-report.md`, and archive artifacts provide
  durable evidence outside chat history.

## Design

### Component design

1. **Entry workflow — `skills/unity-developer/SKILL.md`**
   - Trigger on Unity/C# implementation, diagnosis, review, refactoring,
     architecture/pattern choice, AI behavior, lifecycle, testability, and
     performance trade-offs.
   - Classify the request as explanation, diagnosis, review, or change; do not
     infer mutation from a question.
   - Inspect repository instructions and Unity facts before asking discoverable
     questions. Run the bundled inspector when a project root is available.
   - Route to only the necessary references.
   - Produce a compact decision record: problem/forces, selected solution,
     rejected options, revisit trigger, ownership/lifetimes, validation.
   - For changes, use a failing test first, implement the minimum coherent
     solution, clean lifecycle boundaries, and verify without fabricating Editor,
     build, test, or profiler results.

2. **Decision knowledge — `references/decision-framework.md`**
   - Classify coupling, creation, state, variation, composition, communication,
     persistence, AI, scale, and performance problems.
   - Rank solutions from direct mechanisms to local patterns to subsystem
     architecture to project-wide frameworks.
   - Define decision forces, a no-pattern gate, compact ADR format, and
     proportionality/revisit rules.

3. **Pattern knowledge — `references/design-patterns.md`**
   - Provide a selection matrix across creational, structural, behavioral,
     architectural, and optimization patterns from the requested sources.
   - For each pattern family, record fit, avoid conditions, Unity hazards, and
     useful compositions. Avoid copying full tutorials or default implementations.

4. **Architecture knowledge — `references/architecture.md`**
   - Define a Unity-facing composition root, explicit lifetimes and teardown,
     pure C# domain seams, MonoBehaviour adapters, ScriptableObject authored data,
     scoped messaging, UI presentation boundaries, assembly dependency direction,
     scene/additive loading behavior, and an evidence gate for ECS/DOTS or DI
     frameworks.

5. **AI knowledge — `references/ai-systems.md`**
   - Decompose perception, memory/blackboard, decision, action, navigation, and
     presentation.
   - Compare direct rules, FSM/HFSM, behavior trees, utility AI, GOAP,
     specifications, ML-Agents training, local inference, and hybrids by
     authoring, observability, determinism, CPU/memory, network, replay, and save
     needs.
   - Require update budgets, instrumentation, failure behavior, and measurable
     acceptance scenarios.

6. **Engine safeguards — `references/unity-engine-constraints.md`**
   - Centralize lifecycle, destroyed-object semantics, serialization,
     ScriptableObject runtime-state, domain reload, events, pooling reset,
     threading/async cancellation, deterministic time/randomness, test seams,
     and target-device profiling checks.

7. **Provenance — `references/sources.md`**
   - Record the supplied DOCX, requested site and baseline, first-party Unity
     sources, access date, and explicit cautions. Tell future invocations to
     inspect the project's version and current official docs instead of assuming
     stored package versions remain current.

8. **Project inspector — `scripts/inspect_unity_project.py`**
   - CLI: `python inspect_unity_project.py --root <path> [--json]
     [--max-samples N]`.
   - Exit `0` for an inspectable Unity project (even with metadata warnings), `2`
     for invalid/non-Unity roots, and `3` for an unexpected inspection failure.
   - JSON contract: `schema_version`, `root`, `unity_detected`, `unity_version`,
     `packages`, `inventory`, `signals`, and `warnings`, with deterministic key
     and list ordering.
   - Parse `ProjectSettings/ProjectVersion.txt`, `Packages/manifest.json`, and
     `.asmdef` JSON defensively. Scan only `.cs` files under `Assets/` and embedded
     `Packages/`; exclude generated/cache/build/VCS/IDE and secret-like paths.
   - Treat dependency versions as untrusted metadata: preserve useful package
     coordinates while replacing URI userinfo and credential-bearing
     query/fragment assignments with one deterministic redaction marker before
     either JSON or human rendering.
   - Report counts and capped sample paths for scene lookup, global lifetime,
     static events, frame callbacks, spawn/destroy, resource loading, and
     `async void`. These are investigation signals, not severity ratings or
     diagnoses. Never emit source lines or values.

9. **Repository integration and tests**
   - Add `tests/test_unity_developer.py` through vertical red/green slices. Begin
     with one package/entry tracer test, implement the minimum entry point, then
     add one failing public-seam test before each reference, inspector, metadata,
     evaluation, README, CI, and checksum implementation. Never pre-write the
     whole imagined suite. Final coverage includes frontmatter/routes, workflow
     invariants, inspector fixtures, privacy, deterministic JSON, non-mutation,
     integration documentation, CI, and checksums.
   - Update `.github/workflows/validate.yml` to compile both bundled script
     surfaces without relying on shell glob behavior across platforms.
   - Update `README.md`, `VALIDATION.md`, and `CHECKSUMS.sha256` consistently.
     The checksum scope is the distributable repository surface (root metadata,
     workflow, skills, tests, and validation documentation); it intentionally
     excludes SDD coordination under `openspec/` and generated evaluation
     workspaces so later verification/archive evidence cannot stale the package
     manifest.

10. **Behavioral evaluation workspace**
    - Define three prompts: event/lifecycle coupling, manager-heavy architecture,
      and networked squad AI under a frame budget.
    - Store run outputs in sibling
      `skills/unity-developer-workspace/iteration-1/` using descriptive eval
      directories and `with_skill`/`without_skill` variants.
    - Because the host has only three child slots in addition to root, launch
      independent runs in balanced batches while preserving identical prompts and
      clean skill/no-skill isolation; record this host constraint in analysis.
    - Draft assertions while runs execute, capture available timing data, grade
      against outputs, aggregate with skill-creator's script, analyze
      discriminating value, and generate a static review HTML with the standard
      viewer.

### Requirement mapping

| Requirement | Technical decision | Files/interfaces | Verification seam |
| --- | --- | --- | --- |
| FR-001 | Pushy but bounded Unity trigger and explicit non-ownership | `skills/unity-developer/SKILL.md`, `agents/openai.yaml` | Frontmatter/metadata unit tests; trigger prompt review |
| FR-002 | Evidence intake plus inspector and current-doc rule | `SKILL.md`, `scripts/inspect_unity_project.py`, `references/sources.md` | Fixture JSON; evaluation evidence assertions |
| FR-003 | Force-based no-pattern-first decision ladder | `SKILL.md`, `references/decision-framework.md` | Pattern-selection evaluation |
| FR-004 | Selection matrices with fit/avoid/hazard/composition | `references/design-patterns.md` | Reference reachability and coverage tests |
| FR-005 | Explicit composition, lifetime, data, messaging, UI, assembly, and ECS gates | `references/architecture.md`, `references/unity-engine-constraints.md` | Architecture evaluation and invariant tests |
| FR-006 | Layered AI selector and hybrid rules | `references/ai-systems.md` | Squad-AI evaluation assertions |
| FR-007 | Test-first changes and honest Editor/profiler evidence | `SKILL.md`, `references/unity-engine-constraints.md` | Required-phrase tests and all three evaluations |
| FR-008 | Standard-library read-only bounded inspector | `scripts/inspect_unity_project.py` | At least seven CLI/unit fixture cases |
| FR-009 | Fixed recommendation handoff fields | `SKILL.md`, `references/decision-framework.md` | Evaluation output assertions |
| FR-010 | Lean entry point plus six routed references | `SKILL.md`, `references/*.md` | Under-500-lines and local-link tests |
| FR-011 | Catalog, CI, validation, checksums, UI metadata | `README.md`, `.github/workflows/validate.yml`, `VALIDATION.md`, `CHECKSUMS.sha256`, `agents/openai.yaml` | Repository tests, discovery, checksum verification |
| FR-012 | Three with-skill/baseline evaluations and standard viewer | `evals/evals.json`, `skills/unity-developer-workspace/iteration-1/` | Grading, benchmark JSON/Markdown, static review HTML |
| SC-001 | Structural validator plus focused package tests | Package and tests above | `quick_validate.py`; `unittest` |
| SC-002 | Inspector matrix and Python compatibility | Inspector and test file | `py_compile`; focused tests |
| SC-003 | Whole-repository validation and four-skill discovery | CI/readme/checksums | Documented commands and checksum verifier |
| SC-004 | Complete eval artifacts | Eval JSON/workspace | Aggregator and viewer generation |
| SC-005 | Critical assertion pass in every with-skill run | Grading JSON | Per-run grades and benchmark analysis |
| SC-006 | Independent final judgment | `verify-report.md` | Oracle PASS with FR/SC evidence |
| SC-007 | Human preference in at least 2/3 cases | Review HTML/feedback | Outcome observation; residual RISK if not reviewed |

## Optional support artifacts

- `research.md`: Created because source authority, version drift, the DOCX render
  limitation, and baseline-skill weaknesses materially affect the design.
- `data-model.md`: Not needed; the inspector schema is small and specified in
  this plan plus executable tests.
- `contracts/`: Not needed; there is no external network/API contract and the CLI
  schema is local and versioned in code/tests.
- `quickstart.md`: Not needed; README usage and the skill entry workflow are
  sufficient.

## Risks and migrations

- **Prompt bloat**: Broad Unity coverage could make the skill indiscriminate.
  Mitigation: keep the entry point under 500 lines and route to focused
  references. Rollback: remove low-value reference sections without changing the
  public skill name.
- **Version drift**: Unity packages and APIs change. Mitigation: inspect project
  metadata, avoid fixed current-version promises, and require official
  version-matched lookup for unstable claims. Rollback: sources are advisory and
  can be refreshed independently.
- **Static-analysis false positives**: Token matches can be comments, tests, or
  justified code. Mitigation: call them signals, cap samples, expose paths only,
  and require human/source inspection. Rollback: disable individual signal rules
  without changing inventory output.
- **Source privacy**: Project scanning could expose proprietary or secret data.
  Mitigation: restrict to `.cs`, exclude secret-like paths, emit no source text or
  matched values, and test non-disclosure. Any privacy regression blocks release.
- **Evaluation contamination or constrained concurrency**: Root authored the
  skill and only three child slots are available. Mitigation: independent agents
  receive bounded with-skill or no-skill tasks, never both, and run in balanced
  batches with identical prompts; disclose timing comparability limits.
- **DOCX visual uncertainty**: LibreOffice is unavailable. Mitigation: the source
  had no inline images and all styled paragraphs/table cells were structurally
  extracted; the limitation is recorded and no layout conclusion affects the
  skill.
- **Repository integration drift**: Catalog counts, CI, validation prose, and
  checksums can diverge. Mitigation: tests assert the four-skill catalog and
  checksum verification is part of closeout. Rollback is a single-package removal
  plus restoration of the three named integration files.
- **Migration**: This is additive. No existing public skill or runtime data format
  changes; users opt into `unity-developer` through normal skill discovery.

## Constitution Check (post-design)

- **User-value first**: PASS — Every component maps to an FR/SC and the design
  converts the requested research into a decision-and-delivery workflow rather
  than unrelated Unity infrastructure.
- **Simplicity and bounded scope**: PASS — Detailed knowledge is isolated in
  six references, the only executable helper is read-only and dependency-free,
  and no optional framework or Unity project is introduced.
- **Testable contracts**: PASS — The inspector has explicit inputs, outputs,
  exit codes, privacy rules, and fixture coverage; skill behavior has three
  objective comparative scenarios.
- **Independent assurance**: PASS — Evaluation generation is isolated from
  root implementation and the plan reserves final approval exclusively for an
  Oracle agent.
- **Traceable delivery**: PASS — Exact files, requirement mappings, test seams,
  risk controls, rollback, evaluation evidence, and closeout artifacts are named
  in the durable change set.
