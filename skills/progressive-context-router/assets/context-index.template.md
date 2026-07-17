# Agent context router

Use this index to select the smallest useful project context for the current task. Do not read every linked document by default.

## Routing procedure

1. Prefer an explicit path or package named by the user.
2. Otherwise select the route that owns the behavior being changed.
3. Add a cross-cutting overlay only when the change touches that concern.
4. Search the listed code and test roots before widening scope.
5. Use the fallback route when no route matches clearly.

## Primary routes

| Task signals | Read first | Probable code roots | Probable tests | Optional overlays |
|---|---|---|---|---|
| `<feature words, concepts>` | [`modules/<domain>.md`](modules/<domain>.md) | `<path>/`, `<path>/` | `<tests>/` | `<overlay or none>` |
| `<feature words, concepts>` | [`modules/<domain>.md`](modules/<domain>.md) | `<path>/` | `<tests>/` | `<overlay or none>` |

Remove placeholder rows and add only verified routes.

## Cross-cutting overlays

| Concern | Read when | Document or evidence roots |
|---|---|---|
| Database and migrations | Schema, query, persistence, or migration changes | [`database.md`](database.md), `<migration path>/` |
| Security and authorization | Trust boundaries, permissions, credentials, or sensitive data change | [`security.md`](security.md), `<security tests>/` |
| Public compatibility | API, event, schema, CLI, or package contract changes | [`architecture.md`](architecture.md), `<contract tests>/` |

Keep only overlays that exist in the repository.

## Route precedence

- `<specific route>` is primary over `<broad route>` when `<condition>`.
- Explicit package paths take precedence over vocabulary alone.
- For cross-domain changes, choose the owner of public behavior as primary and load dependency documents only when they must change.

## Fallback route

When no route matches:

1. search for user-provided terms, paths, symbols, route registrations, and tests;
2. inspect the nearest manifest and entrypoint;
3. identify the likely owner and return to this index;
4. add a new route only when the responsibility is durable and recurring.

## Shared references

- [`architecture.md`](architecture.md): high-level boundaries and flows that are not obvious from the code.
- [`testing.md`](testing.md): test layout, scopes, and verified commands.
- [`task-template.md`](task-template.md): compact handoff for work spanning sessions.
- [`routing-cases.json`](routing-cases.json): regression examples for route selection.

Remove links to files that are not needed.
