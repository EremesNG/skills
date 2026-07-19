# Validation report

Generated on 2026-07-19.

## Package checks

- `npx skills add . --list` validated the local source and discovered exactly three skills: `architectural-grilling`, `progressive-context-router`, and `simplify`.
- The `skill-creator` structural validator accepted both `skills/architectural-grilling/` and `skills/simplify/` without errors.
- `architectural-grilling` contains five package files: `SKILL.md`, UI metadata, two on-demand references, and one evaluation set.
- Its name matches the containing directory, uses lowercase-hyphen format, and stays within the required length.
- Its frontmatter contains only `name` and `description`; the description is within the 1,024-character limit.
- Its `SKILL.md` contains 147 lines, 12,169 characters, and approximately 3,042 tokens using the deliberately rough `characters / 4` estimate.
- `simplify` contains three package files: `SKILL.md`, UI metadata, and one evaluation set. Its `SKILL.md` contains 95 lines, 4,113 characters, and approximately 1,028 tokens using the same estimate.
- `simplify` explicitly constrains work to the recent diff, preserves observable behavior and unrelated changes, uses small verified cleanup steps, and stops before API or architecture redesign.
- Every runtime reference named by both skills exists. All three repository JSON files parse successfully.
- `agents/openai.yaml` contains a valid display name, a 25–64 character short description, and a default prompt that explicitly invokes `$architectural-grilling`.

## Behavioral forward tests

Three independent agents used the packaged skill without receiving the intended answer:

1. an over-architected global AI marketplace constrained to two developers and four weeks;
2. a payment-service extraction whose claimed source repository was unavailable;
3. an autonomous refund agent with undefined error tolerance and excessive write authority.

Each agent then received a deliberately ambiguous follow-up such as "everything is a priority," "use best practices," or "the error rate should be very low." Across all six turns, the agents:

- asked exactly one material question per turn;
- supplied a clear recommendation and trade-off;
- challenged the premise or missing evidence instead of accepting vague language;
- used conservative baselines and explicit delegation where appropriate;
- investigated the working directory before asking for repository facts in the migration case;
- performed no implementation or external mutation.

## Automated checks

- Unit tests run locally with Python 3.10.19: **13 passed**.
- All three bundled Python scripts compile successfully and parse with Python 3.9 grammar.
- The repository CI matrix remains configured for Python 3.9 and 3.13.

The four `simplify` tests cover:

1. frontmatter, package layout, and bounded skill length;
2. diff scope, behavior preservation, verification, stop, and return-contract invariants;
3. evaluation coverage for unrelated edits, deep nesting, and public API boundaries;
4. README catalog and remote installation instructions.

The four `architectural-grilling` tests cover:

1. `architectural-grilling` frontmatter and package layout;
2. explicit one-question, recommendation, evidence, non-implementation, red-team, and convergence invariants;
3. reference reachability plus UI metadata consistency;
4. evaluation coverage for over-architecture, legacy migration, delegated decisions, autonomous AI, and early termination.

The existing five tests continue to cover:

1. `progressive-context-router` frontmatter and package layout;
2. safe inventory and credential redaction;
3. acceptance of a grounded context router;
4. rejection of broken links;
5. context-budget snapshot comparison.

## Commands

From the repository root:

```bash
python -m py_compile skills/progressive-context-router/scripts/*.py
python -m unittest discover -s tests -v
npx skills add . --list
```

On PowerShell, expand the compile glob explicitly:

```powershell
Get-ChildItem skills/progressive-context-router/scripts -Filter *.py |
  ForEach-Object { python -m py_compile $_.FullName }
```

The structural package checks were also run with `quick_validate.py` from the installed `skill-creator` skill. Token values in this report are estimates for relative comparison, not model, billing, or client measurements.
