# Agent Skills

This repository contains reusable Agent Skills. Each skill is self-contained under
`skills/<skill-name>/` and keeps its instructions, supporting files, and validation
context together.

## Available skills

The catalog currently contains five skills:

| Skill | Use it for | Documentation |
| --- | --- | --- |
| `architectural-grilling` | Interview one decision at a time to resolve product and delivery risks and recommend a concrete architecture and tech stack proportional to real needs and operating capacity. | [`SKILL.md`](skills/architectural-grilling/SKILL.md) |
| `progressive-context-router` | Configure, refactor, audit, or refresh repository instructions and progressive context for coding agents without changing product logic. | [`SKILL.md`](skills/progressive-context-router/SKILL.md) |
| `simplify` | Refine the current diff for clarity and maintainability while preserving observable behavior and unrelated workspace changes. | [`SKILL.md`](skills/simplify/SKILL.md) |
| `unity-developer` | Select and implement proportional Unity + C# design patterns, architecture, lifecycle safeguards, and game AI systems from project evidence. | [`SKILL.md`](skills/unity-developer/SKILL.md) |
| `unity-gc-free` | Diagnose and migrate measured Unity managed-allocation hot paths with behavior-safe reuse, pooling, libraries, and target-player evidence. | [`SKILL.md`](skills/unity-gc-free/SKILL.md) |

The core interview loop in `architectural-grilling` is inspired by the
MIT-licensed [`grilling` skill from mattpocock/skills](https://github.com/mattpocock/skills/tree/main/skills/productivity/grilling). This version expands it with explicit decision states, architecture and project-management lenses, convergence criteria, red-team checks, and an implementation-ready blueprint.

Its [architecture and stack guide](skills/architectural-grilling/references/architecture-and-stack.md) adapts decision criteria from `architecture-pattern-selector`, `architecture-designer`, and `tech-stack-recommender`. It weighs current needs, credible growth, team expertise, operating burden, and the cost of changing later; the source links are included in the guide. These skills do not need to be installed separately.

## Repository layout

```text
.
├── skills/
│   └── <skill-name>/
│       ├── SKILL.md
│       ├── assets/       # optional supporting templates
│       ├── references/   # optional reference documents
│       ├── scripts/      # optional helper scripts
│       └── evals/        # optional evaluations
├── tests/                # repository-level tests
├── VALIDATION.md         # validation report and commands
├── LICENSE
└── README.md
```

Supporting directories are included when a skill needs them; `SKILL.md` is the
entry point for every skill.

## Skill metadata

Every skill follows the [Agent Skills frontmatter specification](https://agentskills.io/specification).
Keep `name` and `description` at the top level, alongside `license: MIT`.
Put author, version, repository, and any additional custom information inside
`metadata`, whose keys and values must be strings:

```yaml
---
name: simplify
description: Simplify recently changed code while preserving behavior. Use for focused cleanup of the current diff.
license: MIT
metadata:
  author: EremesNG
  version: "1.0.1"
  repository: https://github.com/EremesNG/skills
---
```

Each skill has its own version. All five current skills declare `"1.0.1"`. This identifies
the skill package, not a Git tag or a supported tool version. Keep versions
quoted so YAML reads them as strings.

Use the optional top-level `compatibility` field only for actual environment
requirements. Keep `allowed-tools` optional and specific to a real tool policy;
metadata additions do not require changing a skill's tool permissions.

## Discover and install from this repository

To inspect the skills discovered from the repository root, run the validated
discovery command:

```bash
npx skills add . --list
```

It currently discovers `architectural-grilling`, `progressive-context-router`,
`simplify`, `unity-developer`, and `unity-gc-free`.
For installation, point your Agent Skills-compatible installer at this repository
and select the required skill. Each package root under `skills/` contains its
`SKILL.md` and supporting files. Client-specific installer options are
intentionally not prescribed here.

### Remote installation: `architectural-grilling`

Install this skill from the repository with:

```bash
npx skills add https://github.com/EremesNG/skills --skill architectural-grilling
```

### Remote installation: `progressive-context-router`

Install this skill from the repository with:

```bash
npx skills add https://github.com/EremesNG/skills --skill progressive-context-router
```

### Remote installation: `simplify`

Install this skill from the repository with:

```bash
npx skills add https://github.com/EremesNG/skills --skill simplify
```

### Remote installation: `unity-developer`

Install this skill from the repository with:

```bash
npx skills add https://github.com/EremesNG/skills --skill unity-developer
```

### Remote installation: `unity-gc-free`

Install this skill from the repository with:

```bash
npx skills add https://github.com/EremesNG/skills --skill unity-gc-free
```

## Read and use a skill

Start with the skill's `SKILL.md`:

1. Read its frontmatter for the skill name, description, license, and metadata,
   plus compatibility requirements when present.
2. Read the body for the workflow, boundaries, and expected behavior.
3. Follow links to `assets/`, `references/`, `scripts/`, or `evals/` only when the
   current task needs them.

Each skill's `SKILL.md` is the authoritative guide for its operation and bundled
resources.

### Usage example: `architectural-grilling`

Use this copyable prompt to turn a vague software idea into a decision-complete
blueprint:

```text
Use architectural-grilling to challenge this idea relentlessly before any implementation.

Expose assumptions, investigate facts available in the repository, and ask one decision at a time with your recommended answer. Challenge whether we should build it at all, then resolve product scope, domain rules, architecture, data, security, operations, delivery dependencies, ownership, estimates, rollout, and risks.

When the harness supports interactive questions, wait for each answer and continue with the next question within the same execution. Keep only one question pending. In ordinary chat, include the next question when responding to my answer; do not require me to say "continue".

Recommend a concrete architecture and tech stack that fit the next useful release, my team's skills, budget, and operating capacity. Separate what to build now, what to prepare cheaply, and what to defer until an observable trigger. Challenge speculative future scale without ignoring credible commitments or necessary safeguards.

Do not accept vague qualities such as "scalable" or "secure" without measurable targets. Do not start implementation until every material branch is closed and I explicitly confirm the resulting blueprint.
```

### Usage example: `progressive-context-router`

Use this copyable prompt when configuring this repository:

```text
Use progressive-context-router to configure this repository.

I want a small, stable entry point for agents, a router at docs/agent/index.md, and task-specific documentation loaded on demand.

Analyze the repository's actual structure and divide context by behavior, ownership, invariants, and verification method; do not create one document per directory.

Preserve all existing human-authored constraints. Do not modify product code, invent commands or architecture, or load all documentation at the start of each task.

Add routing cases, run validation, and report the approximate context budget for the always-loaded layer.
```

### Usage example: `simplify`

Use this copyable prompt after an implementation is working:

```text
Use simplify for a final cleanup pass over the files changed by this task.

Reduce accidental duplication, nesting, and indirection, but preserve public behavior, errors, ordering, performance constraints, and test meaning. Do not touch unrelated working-tree changes or redesign APIs. Run the nearest relevant checks and report any cleanup left out of scope.
```

### Usage example: `unity-developer`

Use this copyable prompt for a Unity gameplay, architecture, or AI challenge:

```text
Use unity-developer to diagnose and implement this Unity + C# challenge.

Inspect the available project version, packages, source layout, ownership, lifecycle, platform, networking, authoring, test, and performance evidence before selecting a solution. Recommend the smallest coherent mechanism; compare credible alternatives and state when the decision should be revisited.

For behavior changes, establish a failing test at the narrowest useful seam, preserve Unity initialization and teardown, and verify honestly. Treat performance as unverified until it is measured in a representative build on target hardware.
```

### Usage example: `unity-gc-free`

Use this copyable prompt for a measured Unity allocation hot path:

```text
Use unity-gc-free to diagnose and reduce managed allocations in this Unity hot path.

Inspect the Unity and package versions, profiler evidence, target platform, scripting backend, workload, warm-up, capacities, and all relevant threads. Define the managed-allocation budget before recommending a direct loop, caller-owned buffer, pool, native container, or library such as ZLinq, UniTask, or PrimeTween.

Preserve results, ordering, timing, cancellation, thread affinity, overflow, and owner teardown. Implement one measured source at a time with functional tests first, then verify the same representative workload in a target player. Report native memory, retained memory, and CPU separately; do not call the result GC-free without scoped evidence.
```

When more skills are added, keep this per-skill pattern: a labeled installation
subsection in discovery/install and a concise usage subsection in read/use.

## Validation and CI

Run the repository checks locally from the repository root:

```bash
python3 -m py_compile \
  skills/progressive-context-router/scripts/context_budget.py \
  skills/progressive-context-router/scripts/repo_inventory.py \
  skills/progressive-context-router/scripts/validate_context_setup.py \
  skills/unity-developer/scripts/inspect_unity_project.py \
  skills/unity-gc-free/scripts/inspect_unity_gc.py
python3 -m unittest discover -s tests -v
npx skills add . --list
```

The [validation report](VALIDATION.md) records the current results. The
[GitHub Actions workflow](.github/workflows/validate.yml) compiles the bundled
scripts and runs the unit tests with Python 3.9 and 3.13.

## Contributing a skill

To add a skill:

1. Create `skills/<skill-name>/` and add its `SKILL.md` entry point.
2. Use a lowercase, hyphen-separated directory name and keep the `name` in
   `SKILL.md` consistent with that directory. Follow the metadata convention above.
3. Add supporting directories or files only when the skill needs them.
4. Update this catalog and any relevant tests or validation documentation.
5. Run the checks above and verify that every path referenced by the skill exists.

Keep a contribution focused on the skill and its documentation. Do not invent
release, checksum, or publication steps that are not documented by the repository.

## License

This repository is licensed under the [MIT License](LICENSE).
