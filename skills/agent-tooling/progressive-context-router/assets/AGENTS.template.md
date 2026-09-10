# Agent operating guide

## Repository purpose

<One paragraph describing what the repository delivers and its major runtime shape.>

For task-specific project knowledge, start with [`docs/agent/index.md`](docs/agent/index.md).

## Progressive context protocol

1. Classify the task by product domain or subsystem.
2. Consult the context router before opening broad areas of the repository.
3. Search for named paths, symbols, imports, registrations, and related tests.
4. Read the smallest relevant entrypoints and tests first.
5. Load another routed document only to answer a concrete unresolved question.
6. Do not scan generated, vendored, build, coverage, or dependency directories unless the task specifically requires them.
7. Ask subagents for concise evidence summaries rather than raw logs or complete files.

## Repository map

- `<path>/`: <responsibility>
- `<path>/`: <responsibility>
- `docs/agent/`: routed documentation for coding agents

## Verified commands

| Purpose | Command | Scope or notes |
|---|---|---|
| Install | `<verified command>` | <root/package/platform> |
| Development | `<verified command>` | <root/package/platform> |
| Tests | `<verified command>` | <root/package/platform> |
| Lint | `<verified command>` | <root/package/platform> |
| Type check | `<verified command>` | <root/package/platform> |

Remove rows that cannot be verified. Do not invent placeholders in the final file.

## Global constraints

- <Invariant or safety rule that applies to nearly every task.>
- <Public compatibility or dependency rule.>
- <Generated files or directories that must not be edited directly.>
- <Dependency, migration, or security policy that is truly universal.>

## Change workflow

1. Confirm scope and identify the primary route plus any overlays.
2. Inspect existing tests and public contracts before editing.
3. Keep changes limited to the requested behavior.
4. Run the smallest relevant validation first, then broader checks when justified.
5. Review the diff for unrelated changes, generated output, and accidental secrets.
6. Update routed documentation only when a durable, non-obvious fact changed.

## Subagent return contract

Return:

- conclusion;
- paths and symbols inspected;
- relevant tests or commands;
- unresolved questions;
- risks and recommended next action.

Do not return full logs, complete source files, or an unfiltered search transcript.

## Definition of done

- Requested behavior or analysis is complete and stays within scope.
- Relevant tests and static checks pass, or failures are reported with evidence.
- Public contracts, migrations, and documentation are updated when required.
- The final diff contains no unrelated, generated, or secret material.
- Remaining uncertainty and unexecuted validation are stated explicitly.
