# Testing context

## Test layout

| Scope | Location | Framework or runner | Notes |
|---|---|---|---|
| Unit | `<path>/` | `<verified runner>` | <ownership or naming convention> |
| Integration | `<path>/` | `<verified runner>` | <required services or fixtures> |
| End-to-end | `<path>/` | `<verified runner>` | <environment constraints> |

Remove unverified rows.

## Verified commands

| Purpose | Command | Working directory | Expected prerequisites |
|---|---|---|---|
| Narrow test | `<command>` | `<path>` | `<prerequisite>` |
| Full test | `<command>` | `<path>` | `<prerequisite>` |
| Lint | `<command>` | `<path>` | `<prerequisite>` |
| Type check | `<command>` | `<path>` | `<prerequisite>` |

## Selection rules

- Start with tests closest to the changed behavior.
- Add contract, integration, migration, or end-to-end checks when the change crosses that boundary.
- Do not report a command as passed unless it was actually run.
- Distinguish pre-existing failures from failures introduced by the change.

## Fixtures and test data

- `<fixture path>` represents <purpose>.
- <Mutation, isolation, clock, network, or cleanup rule that is not obvious.>

## Common failure modes

- <Failure symptom> usually means <likely cause>; inspect `<path or log>`.

## Evidence and uncertainty

- Verified from: `<manifests, CI, test configs>`
- Needs confirmation: `<uncertain environment requirement>`
