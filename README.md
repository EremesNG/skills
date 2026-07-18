# Agent Skills

This repository contains reusable Agent Skills. Each skill is self-contained under
`skills/<skill-name>/` and keeps its instructions, supporting files, and validation
context together.

## Available skills

The catalog currently contains two skills:

| Skill | Use it for | Documentation |
| --- | --- | --- |
| `architectural-grilling` | Relentlessly challenge an ambiguous product, architecture, or delivery idea until every material decision is explicit and the plan is safe to execute. | [`SKILL.md`](skills/architectural-grilling/SKILL.md) |
| `progressive-context-router` | Configure, refactor, audit, or refresh repository instructions and progressive context for coding agents without changing product logic. | [`SKILL.md`](skills/progressive-context-router/SKILL.md) |

The core interview loop in `architectural-grilling` is inspired by the
MIT-licensed [`grilling` skill from mattpocock/skills](https://github.com/mattpocock/skills/tree/main/skills/productivity/grilling). This version expands it with explicit decision states, architecture and project-management lenses, convergence criteria, red-team checks, and an implementation-ready blueprint.

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

## Discover and install from this repository

To inspect the skills discovered from the repository root, run the validated
discovery command:

```bash
npx skills add . --list
```

It currently discovers `architectural-grilling` and `progressive-context-router`.
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

## Read and use a skill

Start with the skill's `SKILL.md`:

1. Read its frontmatter for the skill name and description, plus optional license
   or compatibility fields when present.
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

When more skills are added, keep this per-skill pattern: a labeled installation
subsection in discovery/install and a concise usage subsection in read/use.

## Validation and CI

Run the repository checks locally from the repository root:

```bash
python3 -m py_compile skills/progressive-context-router/scripts/*.py
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
   `SKILL.md` consistent with that directory.
3. Add supporting directories or files only when the skill needs them.
4. Update this catalog and any relevant tests or validation documentation.
5. Run the checks above and verify that every path referenced by the skill exists.

Keep a contribution focused on the skill and its documentation. Do not invent
release, checksum, or publication steps that are not documented by the repository.

## License

This repository is licensed under the [MIT License](LICENSE).
