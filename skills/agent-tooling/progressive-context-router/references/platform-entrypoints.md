# Choosing instruction entrypoints

Read this reference when more than one coding-agent client is used, native instruction files already overlap, or nested precedence is unclear.

## Strategy

Choose one canonical source for universal repository instructions. Keep it small. Add client-specific files only to bridge to that source or record behavior unique to that client.

The exact automatic-loading behavior varies by client and can change. Prefer existing repository conventions and current client documentation over assumptions.

## Common entrypoints

| Client or convention | Common project entrypoint | Guidance |
|---|---|---|
| Agents that support the AGENTS convention, including Codex-oriented workflows | `AGENTS.md` | Good default canonical file when several agents share the repository. |
| Claude Code | `CLAUDE.md` | Keep as the canonical file only for a Claude-only repository; otherwise use a thin bridge to the shared guide. |
| GitHub Copilot repository instructions | `.github/copilot-instructions.md` | Keep concise and point to the canonical router when the client follows repository links. |
| Editor-specific rule systems | Existing native rule directory | Preserve the established mechanism; create new rules only when the user targets that editor. |

Do not create every possible entrypoint “for compatibility.” Each always-loaded bridge has a context and maintenance cost.

## Canonical plus bridge pattern

A shared `AGENTS.md` can contain universal rules. A client-specific bridge should contain only:

- a pointer to the canonical guide;
- client-specific tool or workflow differences;
- an instruction not to preload every routed document.

Example shape for `CLAUDE.md`:

```markdown
# Claude Code entrypoint

Follow the repository operating guide in `AGENTS.md`.
Use `docs/agent/index.md` to select task-specific context.
Do not import or read every file under `docs/agent/` at session start.

## Claude-specific notes

- <only genuine client-specific behavior>
```

Use an import directive only when the client supports it and loading the canonical guide is intended. Do not import all subsystem documents merely because the syntax makes that convenient.

## Merging existing files

1. Read every existing root and nested instruction file.
2. Classify each rule as universal, domain-specific, client-specific, obsolete, duplicate, or uncertain.
3. Preserve user constraints and safety rules verbatim when wording carries legal or operational significance.
4. Move verified domain detail to the appropriate routed document.
5. Keep client deltas in the native client file.
6. Replace duplicate prose with a link to one canonical location.
7. Report conflicts and the resolution chosen.

Never delete a rule solely to meet a line target.

## Nested instructions

Nested files are useful when a subtree has a different runtime, toolchain, risk model, or completion standard. They are harmful when they repeat the root guide or exist only because the directory is large.

Before creating one, answer:

- What mistake would an agent make without this local file?
- Why can the router not solve it with an on-demand document?
- Which tasks should inherit the local rule?
- Does the target client actually load nested instructions, and with what precedence?

If the last answer is uncertain, document the local guidance in the router rather than relying on automatic precedence.

## Multi-client conflict rules

- Universal safety and repository constraints should agree across clients.
- When a tool command differs, identify the client explicitly rather than presenting both as generic.
- When one client cannot follow the shared mechanism, duplicate only the minimum operational rule and mark the canonical source.
- Keep a single owner for updates to each fact.

## Audit questions

- Can a human identify the canonical file in under a minute?
- Does each bridge add unique value?
- Are domain details absent from always-loaded client files?
- Are there contradictory completion criteria?
- Would deleting one bridge change actual client behavior, or is it unused?
