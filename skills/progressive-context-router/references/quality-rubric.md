# Quality and validation rubric

Read this reference for audits, review of generated files, or tradeoffs that the mechanical validator cannot decide.

## Hard failures

Treat these as errors that must be fixed:

- existing human instructions were overwritten or silently discarded;
- commands, paths, ownership, or architecture were invented;
- secrets, private keys, tokens, credentials, or sensitive values were copied into docs;
- the root entrypoint instructs the agent to read all project docs or the whole repository before every task;
- links to required routed documents are broken;
- the router has no fallback for unknown tasks;
- product code was changed during a context-only setup without user authorization;
- the final report claims measured savings without a baseline.

## Scoring guide

Use this 100-point rubric for a qualitative audit.

### Safety and preservation — 15

- 5: scope stayed within instructions and documentation.
- 5: existing constraints were preserved or their relocation was documented.
- 5: no sensitive or generated content was embedded.

### Always-loaded layer — 20

- 5: repository purpose and map are useful and concise.
- 5: commands are verified and clearly scoped.
- 5: global invariants and definition of done are present.
- 5: domain-specific prose is routed out.

### Routing quality — 25

- 5: routes use recognizable task signals.
- 5: every route names a first document, code roots, and tests.
- 5: primary domains and overlays are distinguishable.
- 5: precedence and fallback behavior are explicit.
- 5: realistic routing cases cover common and cross-cutting tasks.

### Grounded project knowledge — 20

- 5: entrypoints and flows are supported by code evidence.
- 5: non-obvious invariants are documented without source dumps.
- 5: tests and verification are linked correctly.
- 5: uncertainty and stale existing docs are labeled.

### Maintainability — 10

- 5: one canonical source owns each fact; duplication is low.
- 5: file names, links, and document scope make updates obvious.

### Mechanical validation — 10

- 5: validator reports no errors and broken-link checks pass.
- 5: context budget is recorded and remaining warnings are justified.

## Size heuristics

These are review prompts, not universal limits:

- canonical root instructions: often 80–150 nonblank lines; investigate above 200;
- router: often under 120 nonblank lines;
- subsystem document: often 40–120 nonblank lines;
- task handoff: brief enough to read before resuming work;
- always-loaded bridges: preferably under 20 nonblank lines plus genuine client deltas.

A shorter file is not automatically better. Preserve a critical invariant even when it costs several lines.

## Reachability

Every on-demand document should be reachable from `docs/agent/index.md` directly or through one clearly justified link. Avoid reference chains deeper than necessary.

Use Markdown links for document navigation. Inline code paths are appropriate for code roots, but document references should remain machine-checkable links.

## Duplication review

Duplicate facts are especially risky when they can drift:

- commands and required flags;
- supported runtime versions;
- data ownership;
- security constraints;
- public compatibility promises;
- test requirements.

Choose one canonical owner and link to it from other documents.

## Route review scenarios

Test at least these shapes when relevant:

1. a narrow bug in one domain;
2. a schema or migration change;
3. a UI or API contract change;
4. a cross-cutting security or observability change;
5. a task using an explicit path but ambiguous vocabulary;
6. an unfamiliar task that must use fallback discovery.

For each case, ask:

- Which document is loaded first?
- Which documents are unnecessary?
- Which code and tests are searched first?
- What condition justifies loading another domain?

## Context budget interpretation

The bundled budget script estimates tokens from character count. It is useful for relative comparison, not billing or exact model context accounting.

Record both:

- always-loaded total;
- on-demand total and representative route bundle.

A large on-demand library can be acceptable when each task loads only a small, coherent subset.

## Final human review

Before declaring completion, ask whether:

- the route names match the team's language;
- the commands are safe and current;
- ownership and invariants need domain-expert confirmation;
- any documentation should remain private or outside the repository;
- the proposed local instruction precedence matches the actual client.
