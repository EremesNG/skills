# Agent Skills

This repository contains reusable Agent Skills. Each skill is self-contained under
`skills/<skill-name>/` and keeps its instructions, supporting files, and validation
context together.

## Available skills

The catalog currently contains one skill:

| Skill | Use it for | Documentation |
| --- | --- | --- |
| `progressive-context-router` | Configure, refactor, audit, or refresh repository instructions and progressive context for coding agents without changing product logic. | [`SKILL.md`](skills/progressive-context-router/SKILL.md) |

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

It currently discovers `progressive-context-router`. For installation, point your
Agent Skills-compatible installer at this repository and select that skill. Its
package root is `skills/progressive-context-router/`, which contains `SKILL.md`
and the supporting files needed by the skill. Client-specific installer options
are intentionally not prescribed here.

## Read and use a skill

Start with the skill's `SKILL.md`:

1. Read its frontmatter for the skill name, description, license, and compatibility.
2. Read the body for the workflow, boundaries, and expected behavior.
3. Follow links to `assets/`, `references/`, `scripts/`, or `evals/` only when the
   current task needs them.

The [`progressive-context-router` documentation](skills/progressive-context-router/SKILL.md)
is the authoritative guide for that skill's operation and bundled tools.

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
