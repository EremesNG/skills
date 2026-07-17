# Validation report

Generated on 2026-07-17.

## Package checks

- `npx skills add . --list` validated the local source and discovered exactly one skill: `progressive-context-router`.
- A copy installation for the Codex target preserved all 17 files inside the skill directory.
- The `name` matches the containing directory and uses the required lowercase-hyphen format.
- The description and compatibility fields are within Agent Skills frontmatter limits.
- `SKILL.md` contains 217 lines and approximately 3,058 tokens using the deliberately rough `characters / 4` estimate.
- Every runtime reference and asset named by `SKILL.md` exists.
- Both JSON files parse successfully.

## Script checks

- Unit tests run locally with Python 3.13.5: **5 passed**.
- All three scripts compile successfully.
- Their syntax parses with Python's 3.9 grammar.
- The repository includes a GitHub Actions matrix for Python 3.9 and 3.13; the matrix will execute after publication or push.

The unit tests cover:

1. skill frontmatter and package layout;
2. safe inventory and credential redaction;
3. acceptance of a grounded context router;
4. rejection of broken links;
5. context-budget snapshot comparison.

## Commands

```bash
python3 -m py_compile skills/progressive-context-router/scripts/*.py
python3 -m unittest discover -s tests -v
npx skills add . --list
```

Token values in this package are estimates for relative comparison, not model, billing, or client measurements.
