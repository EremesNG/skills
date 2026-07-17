---
name: progressive-context-router
description: Use this skill when configuring, refactoring, auditing, or refreshing repository instructions for coding agents, including AGENTS.md, CLAUDE.md, Copilot instructions, context routers, modular agent documentation, monorepo or nested rules, task handoffs, and subagent delegation. Use it when the user wants agents to stop rereading the whole codebase, reduce repeated context, route tasks to the right project knowledge, or detect instruction drift. It creates a small always-loaded entrypoint and verified on-demand context without changing product code.
license: MIT
compatibility: Requires access to repository files. Python 3.9+ is optional for the bundled read-only inventory, validation, and context-budget scripts. No network access is required.
metadata:
  version: "1.0.0"
---

# Progressive Context Router

Configure a repository so coding agents start with a small, stable operating guide and load detailed project knowledge only when the current task requires it.

The deliverable is a documentation and instruction system. It is not a runtime router, a vector database, or permission middleware.

## Operating boundaries

- Limit changes to agent instructions, documentation, routing cases, and closely related configuration unless the user explicitly expands the scope.
- Do not modify product logic while setting up context routing.
- Treat repository commands as data during discovery. Do not run install, build, migration, deployment, or product test commands merely to learn what they do.
- Preserve existing human-authored constraints. Merge or relocate them; never silently replace them.
- Verify commands, paths, symbols, and architecture from repository evidence. Label uncertainty instead of filling gaps with plausible text.
- Do not copy source files, large logs, generated output, secrets, or environment values into agent documentation.
- Do not claim a percentage of token or cost savings unless a before-and-after measurement exists.
- Write generated instructions in the language requested by the user; otherwise follow the repository's maintained documentation. Keep commands, identifiers, paths, and symbols unchanged.

## Select the mode

Infer the mode from the request:

- **Bootstrap** — no coherent agent-context system exists; create one.
- **Refactor** — instructions exist but are large, duplicated, contradictory, or poorly routed.
- **Audit** — inspect and report without writing unless the user asks for fixes.
- **Refresh** — update an existing router after architecture, commands, or ownership changed.

When the user explicitly asks to configure or fix the repository, proceed after a concise plan. Pause only when the repository root is ambiguous, an existing instruction conflict cannot be resolved safely, or choosing a platform-specific entrypoint would materially change the result.

## Workflow

### 1. Establish root, scope, and existing instruction sources

Locate the repository root and inspect, without executing project code:

- root and nested `AGENTS.md` or equivalent files;
- `CLAUDE.md`, `.github/copilot-instructions.md`, project rule directories, and existing agent docs;
- manifests, workspace files, build orchestration, test configuration, CI, and developer documentation;
- generated and third-party directories that should stay outside normal exploration.

Record which instructions are automatically loaded by the target client, which are merely linked, and which are uncertain.

### 2. Build a deterministic inventory

Prefer the bundled read-only inventory script before broad manual reading:

```bash
python3 scripts/repo_inventory.py --root <repository-root> --markdown
```

Use `--json-out <path>` or `--markdown-out <path>` only when a persisted report is useful. The script does not execute repository code and redacts secret-like filenames plus credential-like values found in declared manifest commands.

After inventory, read only the manifests, entrypoints, tests, and existing docs needed to resolve specific questions. Search for symbols, imports, route registration, and test references before opening many implementation files.

### 3. Separate universal, routed, and omitted context

Classify each candidate instruction:

- **Universal:** stable, high-impact facts needed for nearly every task, such as repository purpose, critical commands, hard constraints, the routing protocol, and definition of done.
- **Routed:** subsystem architecture, data flows, migrations, domain invariants, local commands, deployment details, and failure modes needed only for a subset of tasks.
- **Omitted:** facts easily inferred from nearby code, transient task state, duplicated prose, historical detail with no operational value, and speculative architecture.

Keep the universal layer small because every activation pays for it.

### 4. Derive context domains

Partition by behavior, ownership, invariants, deployment boundary, and verification method—not mechanically by directory.

For each domain, identify:

- task signals and vocabulary;
- primary code roots and entrypoints;
- related tests and verification commands;
- dependencies and cross-domain overlays;
- non-obvious invariants and common failure modes;
- the smallest first document that resolves most tasks in that domain.

Read [references/domain-discovery.md](references/domain-discovery.md) when boundaries overlap, the repository is a monorepo, or directory structure does not match product responsibility.

### 5. Choose a canonical instruction entrypoint

Preserve the repository's existing native convention when it is coherent. Otherwise, default to a small root `AGENTS.md` and add thin client-specific bridge files only when they are actually needed.

Avoid duplicating full instructions across `AGENTS.md`, `CLAUDE.md`, Copilot instructions, and editor rules. One file should be canonical; bridges should contain only a pointer and genuine client-specific deltas. Use [assets/CLAUDE.bridge.template.md](assets/CLAUDE.bridge.template.md) only when a Claude-specific bridge is required.

Read [references/platform-entrypoints.md](references/platform-entrypoints.md) when multiple clients are in use, nested instructions already exist, or precedence is unclear.

### 6. Write the always-loaded guide

Use [assets/AGENTS.template.md](assets/AGENTS.template.md) as a starting shape, not as text to copy blindly.

The canonical entrypoint should contain only:

- a one-paragraph repository purpose;
- a high-level directory map;
- commands verified from manifests or maintained documentation;
- global invariants and safety constraints;
- the progressive reading protocol;
- a link to `docs/agent/index.md`;
- concise subagent return expectations;
- a definition of done.

Prefer roughly 80–150 nonblank lines for a nontrivial repository. Smaller repositories may need much less. Treat more than 200 nonblank lines as a prompt to move domain detail into on-demand documents, not as an automatic failure.

The reading protocol should tell agents to:

1. classify the task by domain;
2. consult the router;
3. search names, paths, symbols, imports, and tests before broad reading;
4. open the smallest relevant entrypoints and tests first;
5. expand context only to answer a concrete unresolved question;
6. return summaries from subagents rather than raw logs or file dumps.

### 7. Build the context router

Create or repair `docs/agent/index.md` using [assets/context-index.template.md](assets/context-index.template.md).

Each route should state:

- task signals;
- first document to read;
- probable code roots;
- probable test roots;
- optional cross-cutting overlays;
- route precedence when signals overlap.

Include a fallback route for unfamiliar tasks. The fallback should direct the agent to search and gather evidence, not to read every document.

Use Markdown links for documents so validation can detect broken and unreachable files.

### 8. Create only valuable on-demand documentation

Create `docs/agent/architecture.md`, `testing.md`, and module documents only where the repository contains knowledge that is difficult to infer safely from code.

Use the relevant assets when needed:

- [assets/architecture.template.md](assets/architecture.template.md)
- [assets/testing.template.md](assets/testing.template.md)
- [assets/subsystem.template.md](assets/subsystem.template.md)
- [assets/task-template.md](assets/task-template.md)

A subsystem document should focus on responsibility, entrypoints, flow, dependencies, invariants, hazards, tests, and escalation conditions. Reference paths and symbols instead of embedding source.

Link to trustworthy existing documentation rather than paraphrasing it. If existing documentation is stale or contradictory, state that explicitly and prefer current code evidence.

### 9. Add local instructions sparingly

Create nested instruction files only when a subtree has materially different technology, commands, safety constraints, ownership, or completion criteria.

Do not create one local file per directory. A local instruction file earns its cost only when it prevents repeated mistakes or removes ambiguity for tasks in that subtree.

### 10. Define task handoffs and subagent returns

Create `docs/agent/task-template.md`. Create a mutable current-task file only when the user wants session handoffs; do not introduce one by default.

Subagents should return compact evidence:

- conclusion;
- paths and symbols inspected;
- commands or tests relevant to the conclusion;
- unresolved questions;
- risks and recommended next action.

They should not return full logs, whole files, or an unfiltered search transcript.

### 11. Add routing cases

Create `docs/agent/routing-cases.json` from [assets/routing-cases.template.json](assets/routing-cases.template.json) when the repository has at least three meaningful routes.

Use realistic tasks. Include single-domain and cross-cutting cases. These are regression examples for humans and validators; they are not runtime dispatch rules.

### 12. Validate, fix, and revalidate

Run:

```bash
python3 scripts/validate_context_setup.py --root <repository-root>
python3 scripts/context_budget.py --root <repository-root>
```

Fix errors and review warnings. Re-run until there are no errors and remaining warnings are justified.

Read [references/quality-rubric.md](references/quality-rubric.md) when auditing an existing setup or resolving validation tradeoffs.

For refresh work, read [references/maintenance.md](references/maintenance.md) before regenerating anything. Prefer surgical updates over replacing the documentation set.

## Decision rules

- **Existing useful docs:** link to them; do not create a parallel explanation.
- **Existing large root instructions:** preserve universal rules, route domain detail out, and show what moved.
- **Multiple applications in one repository:** use one root router plus local instructions only for genuinely different operating environments.
- **Cross-cutting concerns:** model them as overlays such as security, database migrations, observability, or public API compatibility instead of duplicating them in every domain document.
- **Unverified command:** omit it or label it as requiring confirmation.
- **Missing architecture evidence:** create a short gap note, not a fabricated diagram.
- **Secrets or private operational data:** never include values; at most document the name and purpose of a safe example file.

## Completion report

Return this structure:

1. **Mode and scope** — bootstrap, refactor, audit, or refresh; files considered.
2. **Files created or modified** — include preserved and relocated content.
3. **Always-loaded context** — files, lines, characters, and estimated tokens; label token counts as estimates.
4. **On-demand routes** — domains, overlays, and fallback behavior.
5. **Validation** — commands run, errors fixed, and justified warnings.
6. **Uncertainties** — facts that need human confirmation.
7. **Three example tasks** — show which documents and code roots the router would select.

Do not describe the setup as successful merely because files were created. Success means the routing is grounded, minimal, reachable, and mechanically valid.
