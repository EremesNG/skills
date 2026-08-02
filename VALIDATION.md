# Validation report

Generated on 2026-08-01 for the in-progress `unity-developer` change.

## Current scope

This checkpoint covers package structure, static contracts, the read-only Unity
project inspector, repository integration, Python compilation, local skill
discovery, one comparative behavioral-evaluation iteration, and the final
post-convergence validation following the first independent Oracle attempt. The
distribution manifest has been regenerated from the final checksum-scoped
content and independently audited below. Oracle re-verification and human
preference review remain pending and are not claimed here.

## Package checks

- The installed `skill-creator` structural validator returned `Skill is valid!`
  for `skills/unity-developer/`. It ran with local Python 3.10.19 and PyYAML
  6.0.3 after the bundled Python 3.12.13 runtime correctly reported that PyYAML
  was unavailable there.
- `SKILL.md` contains 174 lines and 9,258 characters, stays below the 500-line
  limit, and links exactly six focused references. The focused tests confirmed
  that every routed reference exists.
- Frontmatter contains only `name` and `description`; the name matches the
  `unity-developer` directory.
- `agents/openai.yaml` contains the `Unity Developer` display name, a 25-to-64
  character short description, and a default prompt that explicitly invokes
  `$unity-developer` for Unity + C# work.
- `evals/evals.json` parses as JSON and contains three unique, substantive
  scenarios for feature coupling/lifecycle, manager-heavy architecture, and
  server-authoritative squad AI, with 7, 8, and 8 objective assertions
  respectively. Each workspace metadata file contains the identical assertion
  set used by the independent grader.

## Unity project inspector

Ten CLI fixture cases currently pass:

1. a non-Unity root returns exit 2 and the versioned JSON shape;
2. a valid project reports Unity version, declared packages, assembly definitions,
   test assemblies, C# inventory, and bounded source-path signals;
3. malformed project, package, and assembly metadata produces warnings without
   aborting an otherwise inspectable project;
4. generated, cache, build, VCS, and IDE paths are excluded;
5. secret-like paths and all source values are absent from output;
6. URI userinfo in package dependency values is replaced by a stable marker;
7. token-bearing query/fragment assignments and credential-like fallback text
   are redacted while non-sensitive coordinates remain useful;
8. JSON output, key/list ordering, counts, and sample bounds are deterministic;
9. human-readable output summarizes the inventory and labels signals as
   investigation leads rather than diagnoses;
10. a size, modification-time, and SHA-256 snapshot is unchanged after inspection.

The helper uses only the Python standard library, reads `.cs` and `.asmdef` files
under `Assets/` and embedded `Packages/`, and emits counts plus capped relative
paths rather than source lines or matched values. Package-manifest dependency
values cross a separate sanitization boundary before JSON rendering; non-string
values are suppressed, URI userinfo is removed, and normalized sensitive
assignments receive the deterministic `REDACTED` marker.

## Automated checks observed

- Focused `unity-developer` suite with bundled Python 3.12.13: **21 passed**.
- Whole repository suite with bundled Python 3.12.13: **34 passed**.
- Explicit compilation of all four bundled Python scripts with Python 3.12.13:
  **PASS**.
- The GitHub Actions workflow still targets Python 3.9 and 3.13 and now names all
  four scripts explicitly instead of relying on shell glob expansion.
- Local discovery with the already cached `skills` CLI 1.5.21 found exactly four
  skills: `architectural-grilling`, `progressive-context-router`, `simplify`, and
  `unity-developer`.

### Final post-convergence checkpoint

After the behavior-preserving `simplify` pass:

- focused `unity-developer` tests: **21/21 passed**;
- whole repository tests: **34/34 passed**;
- explicit Python compilation of all four bundled scripts: **PASS**;
- `skill-creator` structural validation: **PASS** (`Skill is valid!`);
- cached local skill discovery: **4/4 expected skills found**;
- progressive local links: **6/6 present**;
- parsed skill/evaluation JSON artifacts: **22/22 valid**;
- primary grading artifacts: **6/6 valid**, with **23/23** with-skill
  assertions passing;
- benchmark contract: **6 runs**, **10 analyst notes**, and one run per
  configuration;
- static review viewer: **218,293 bytes** and non-empty.
- distribution checksum scope: **44/44 entries**, with **0** missing, extra,
  duplicate, forbidden, or mismatched paths after independent recomputation.

### Oracle attempt 1 and convergence

The initial 44-entry checksum audit passed before independent verification.
Oracle attempt 1 returned **FAIL** because package dependency versions could
still disclose URI userinfo or token values (F-001, major), and because this
report still described checksum generation as pending after that audit (F-002,
minor). No critical finding was reported.

Convergence reproduced the privacy defect before implementation in two isolated
tests: one exposed `SENTINEL_PASSWORD` from URI userinfo and one exposed query,
fragment, and fallback credential sentinels. Each test then passed after its
minimum sanitization change. The focused suite subsequently passed **21/21**,
the whole repository passed **34/34**, compilation and structural validation
passed, and the 44-entry manifest was regenerated and audited again. Final
Oracle approval is deliberately not claimed until the read-only re-verification
completes.

## Behavioral evaluation observed

The three prompts were executed as independent with-skill/no-skill pairs. The host
allowed two evaluation workers alongside the root, so each pair launched together
and the pairs ran in three successive balanced batches. Six non-empty
`recommendation.md` files were produced, and a contamination scan found no
`unity-developer` skill reference in any baseline artifact.

An independent artifact-only grader applied the 23 predeclared assertions to both
configurations:

| Evaluation | With skill | Without skill | Observed separation |
| --- | ---: | ---: | ---: |
| Coupling and lifecycle | 7/7 | 6/7 | +1 |
| Manager architecture | 8/8 | 5/8 | +3 |
| Networked squad AI | 8/8 | 6/8 | +2 |

- All three with-skill runs passed every critical assertion: **23/23**.
- Baselines passed **17/23** assertions. The benchmark's unweighted mean of the
  three per-eval pass rates is **74.4%**, compared with **100%** with skill.
- Six assertions uniquely favored the skill and none favored the baseline. They
  concern evidence classification, additive-scene readiness and return-to-menu
  lifecycle coverage, reproducible target-build baselines, action cancellation and
  despawn/pool cleanup, and a complete PlayMode/verification boundary.
- Seventeen assertions passed in both configurations and therefore do not
  discriminate in this single-run sample.
- With-skill artifacts contained 56.7% more characters on average. That
  accompanies six additional passes but does not establish causal efficiency.
- One run per configuration cannot support claims about variance or flakiness.
  Collaboration notifications exposed neither `duration_ms` nor total tokens, so
  timing and token comparisons are explicitly unavailable rather than estimated.

The standard `skill-creator` artifacts exist at
`skills/unity-developer-workspace/iteration-1/`: six primary grading files,
`benchmark.json`, `benchmark.md`, ten evidence-grounded analyst notes, and a
218,293-byte static `review.html`. A compatibility-only `runs/` projection was
needed because the installed aggregator discovers `eval-*/*/run-*` while the
current skill-creator execution instructions use descriptive direct-output
directories.

Human preference has not been observed. SC-007 remains an outcome risk until a
reviewer compares the paired recommendations in `review.html`; the automated
assertion result is not presented as a substitute for that judgment.

## Source and capability limitations

- The supplied DOCX was structurally extracted as 241 paragraphs, one 9-by-5
  table, and zero inline images. LibreOffice/`soffice` is unavailable, so visual
  page rendering was not verified; no layout conclusion is used by the skill.
- Unity package/API advice is intentionally version-sensitive. The skill requires
  project metadata and current version-matched first-party documentation rather
  than treating the research snapshot as timeless.
- `npx skills add . --list` was not invoked during the SDD because the repository
  instructions prohibit that command and network fetches during a change. The
  equivalent read-only discovery used the already cached CLI directly and made no
  package installation or repository write.
- No Unity Editor, target console, profiler capture, or representative game project
  was available. The skill therefore provides verification protocols and does not
  claim Unity compilation or runtime-performance results.
- Executor transcripts, timing, total-token counts, and tool-call metrics were not
  exposed by the collaboration host. Grades therefore assess final artifacts only.

## Commands executed at this checkpoint

From the repository root on this machine:

```powershell
& 'C:\Users\EremesNG\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m unittest tests.test_unity_developer -v
& 'C:\Users\EremesNG\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m unittest discover -s tests -v
& 'C:\Users\EremesNG\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m py_compile skills/progressive-context-router/scripts/context_budget.py skills/progressive-context-router/scripts/repo_inventory.py skills/progressive-context-router/scripts/validate_context_setup.py skills/unity-developer/scripts/inspect_unity_project.py
python 'C:\Users\EremesNG\.agents\skills\skill-creator\scripts\quick_validate.py' skills/unity-developer
& 'C:\Users\EremesNG\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe' 'C:\Users\EremesNG\AppData\Local\npm-cache\_npx\ac0ed6aa23b37c1e\node_modules\skills\bin\cli.mjs' add . --list
python 'C:\Users\EremesNG\.agents\skills\skill-creator\scripts\aggregate_benchmark.py' 'C:\DEV\Proyectos\Webstorm\skills\skills\unity-developer-workspace\iteration-1' --skill-name unity-developer --skill-path 'C:\DEV\Proyectos\Webstorm\skills\skills\unity-developer' --output 'C:\DEV\Proyectos\Webstorm\skills\skills\unity-developer-workspace\iteration-1\benchmark.json'
python 'C:\Users\EremesNG\.agents\skills\skill-creator\eval-viewer\generate_review.py' 'C:\DEV\Proyectos\Webstorm\skills\skills\unity-developer-workspace\iteration-1' --skill-name unity-developer --benchmark 'C:\DEV\Proyectos\Webstorm\skills\skills\unity-developer-workspace\iteration-1\benchmark.json' --static 'C:\DEV\Proyectos\Webstorm\skills\skills\unity-developer-workspace\iteration-1\review.html'
```

Each command above has a current observed PASS; the aggregator consumes the
persisted `iteration-1/runs/` compatibility adapter. Human preference, execution
time, and token usage are deliberately omitted because none has been measured at
this checkpoint. A separate read-only PowerShell audit enumerated the checksum
scope independently from the manifest, rejected forbidden `openspec/`, generated
workspace, cache, and bytecode paths, and recomputed every SHA-256 digest.
