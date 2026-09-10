# Maintaining an existing context router

Read this reference during refresh work or when validation indicates drift. Do not regenerate the entire documentation set by default.

## Refresh triggers

Review the router after any of these changes:

- a new application, service, package, or deployable unit;
- moved entrypoints or renamed code roots;
- new test, lint, type-check, migration, or deployment commands;
- changes to public contracts, authorization, or data ownership;
- repeated agent mistakes that reveal missing or misleading context;
- a root instruction file growing because temporary detail was added;
- broken links or unreachable routed documents;
- ownership or workflow changes that alter completion criteria.

## Surgical refresh procedure

1. Run the inventory and validator against the current repository.
2. Compare findings with the existing router and routed documents.
3. Identify facts that are stale, missing, duplicated, or no longer worth loading.
4. Preserve human notes that remain valid.
5. Update the smallest canonical source for each changed fact.
6. Add or revise routing cases for new behavior.
7. Re-run validation and context-budget measurement.
8. Report exactly what changed and why.

Avoid rewriting unchanged documents, because large regeneration diffs hide meaningful changes and erase editorial knowledge.

## Drift categories

### Path drift

Files, packages, tests, or docs moved. Fix links and route roots, then search for all references to the old path.

### Command drift

Scripts or flags changed. Verify against manifests, CI, or maintained developer docs. Never preserve an old command merely because it appears in an agent file.

### Responsibility drift

A capability moved between services or packages. Re-evaluate the primary domain and overlays rather than updating only the path column.

### Invariant drift

Security, data lifecycle, compatibility, or operational assumptions changed. This deserves domain-owner review because stale invariants can be worse than missing documentation.

### Instruction bloat

Task-specific notes accumulated in always-loaded files. Move durable domain knowledge to routed docs; remove completed transient state.

## Task state lifecycle

Use `docs/agent/task-template.md` to create a short handoff when work spans sessions.

A handoff should record:

- current objective and scope;
- confirmed decisions;
- files and symbols that matter;
- work completed;
- validation already run;
- unresolved questions and next action.

Do not use a task file as a permanent architecture document. Promote durable knowledge to the correct routed document, then clear or archive the transient handoff according to team practice.

## Measuring change

Capture context-budget snapshots before and after a significant refactor. Compare:

- always-loaded lines and estimated tokens;
- number of files read for representative routing cases;
- duplicate command or invariant statements;
- broken or stale references;
- time or turns before the agent reaches the relevant implementation;
- mistakes caused by missing context.

Label token counts as estimates unless measured by the actual client and model.

## Removing a route

Delete a route only after confirming that:

- its responsibility no longer exists or has a clear new owner;
- its useful invariants were migrated or intentionally removed;
- no routing case or other document still points to it;
- the validator reports no unreachable or broken references.

## Adding a route

A new route should demonstrate repeated value. Before adding it, try extending an existing domain or adding an overlay. New routes are justified when task signals, invariants, code roots, and verification differ enough that the existing route routinely loads noise or misses important context.
