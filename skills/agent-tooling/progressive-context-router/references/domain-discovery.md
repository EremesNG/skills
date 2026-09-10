# Discovering useful context domains

Read this reference when repository folders do not map cleanly to product responsibilities, when routes overlap, or when a monorepo contains many packages.

## The goal

A context domain is the smallest stable body of project knowledge that repeatedly helps an agent make correct changes. It is not necessarily a folder, package, team, or deployable service, although any of those can be a strong signal.

Good boundaries reduce two errors at once:

- under-routing, where the agent misses a critical invariant;
- over-routing, where the agent loads unrelated documentation and loses focus.

## Evidence hierarchy

Prefer evidence in this order:

1. runtime and build entrypoints;
2. package or workspace manifests;
3. public interfaces and route registration;
4. tests and fixtures;
5. deployment units and CI jobs;
6. maintained architecture documentation;
7. ownership metadata and directory names;
8. comments or naming conventions without corroboration.

A directory name is a clue, not proof of a domain boundary.

## Boundary signals

Create or preserve a separate context when several of these are true:

- it has a distinct user or business responsibility;
- it owns important invariants, permissions, or data lifecycle rules;
- it has separate entrypoints, deployability, or runtime concerns;
- it uses a different toolchain or verification command;
- changes commonly require a particular set of tests or reviewers;
- mistakes in the area have a recognizably different risk profile;
- agents repeatedly need the same non-obvious explanation.

Merge candidates when they differ only by folder name, share the same invariants and tests, or would produce tiny documents containing mostly links.

## Primary domains and overlays

Use **primary domains** for the main owner of a change. Examples: authentication, billing, catalog, web application, API gateway, worker platform.

Use **overlays** for concerns that can apply to many primary domains. Examples:

- security and authorization;
- database schema and migrations;
- observability;
- public API compatibility;
- localization;
- performance-sensitive paths.

This avoids copying the same security or migration rules into every module document.

## Discovery procedure

1. List applications, packages, services, manifests, and runtime entrypoints.
2. Trace a few representative flows from request or event entrypoint to persistence and tests.
3. Group files that share responsibility, invariants, and verification.
4. Identify cross-cutting concerns that should become overlays.
5. Write a one-sentence responsibility statement for each proposed domain.
6. Test the model with realistic tasks. Each task should have one clear primary route and zero or more overlays.
7. Merge or split domains until route selection is understandable without reading all documents.

## Domain card

Use this compact card during planning:

```markdown
### <domain name>

- Responsibility:
- Trigger words and task shapes:
- Primary entrypoints:
- Code roots:
- Tests:
- Verification commands:
- Invariants:
- Dependencies:
- Cross-cutting overlays:
- First document:
- Escalate when:
```

## Routing precedence

Use deterministic precedence when a task matches several routes:

1. explicit path or package named by the user;
2. feature or behavior being changed;
3. owning runtime or deployable unit;
4. cross-cutting overlays implied by the change;
5. fallback evidence gathering.

For a cross-domain change, pick the domain that owns the public behavior as primary, then load the smallest documents for dependencies that must also change.

## Anti-patterns

### One document per folder

This mirrors storage rather than responsibility and usually creates many nearly empty files.

### One giant backend context

This makes every backend task pay for unrelated data, queues, billing, and authorization rules.

### Overlapping routes without precedence

If both “API” and “authentication” claim a login endpoint, agents need an explicit rule such as “authentication is primary; API compatibility is an overlay.”

### Documentation of obvious code

Do not explain that `controllers/` contains controllers or duplicate exported types. Document what an agent is likely to misunderstand: hidden coupling, lifecycle, ordering, ownership, or verification.

### Historical architecture presented as current

Prefer current imports, registrations, tests, and manifests. Label historical documents and avoid routing current work through them.

## Example

For a monorepo with `apps/web`, `apps/api`, `packages/auth`, and `packages/db`, reasonable routes may be:

- web experience — primary for pages, components, browser state;
- API surface — primary for transport, handlers, response contracts;
- identity — primary for login, sessions, permissions;
- persistence overlay — loaded when a change touches schema, queries, or migrations.

A task to “add MFA to login” routes primarily to identity, with API and persistence overlays only if the implementation changes those contracts.
