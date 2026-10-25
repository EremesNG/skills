# Structural Patterns

Read when a boundary, variation matrix, nested structure, wrapper order, or measured sharing problem needs an explicit contract.

## Adapter
- **Choose when:** Provider-specific semantics are leaking into consumers that need one application-owned contract.
- **Simpler first:** Use a boundary translation function; upgrade when recurring call, data, and error translations need a cohesive owner.
- **Contract:** Translate units, coordinates, identity, retries, and errors honestly; preserve asynchronous completion, cancellation, ownership, and subscription cleanup.
- **Traps:** Matching names can conceal incompatible semantics or secretly blocking calls; contract-test unsupported operations and failure mapping, not just successful conversion.
- **Not:** [Facade](structural.md#facade) simplifies subsystem use; Adapter reconciles an existing contract mismatch without inventing unsupported capabilities.

## Bridge
- **Choose when:** Two independently changing dimensions already produce duplicated subclasses or branches for real combinations.
- **Simpler first:** Compose one collaborator; upgrade when both axes vary, not because a second axis appears on a roadmap.
- **Contract:** Keep the mechanism contract narrow; high-level variants must not inspect concrete backend types. Validate supported pairs explicitly.
- **Traps:** Theoretical combinations may violate invariants; test representative cross-axis behavior and unsupported pairs before claiming interchangeability.
- **Not:** [Strategy](behavioral.md#strategy) replaces one algorithm role; Bridge preserves independent variation across abstraction and implementation dimensions.

## Composite
- **Choose when:** Genuine recursive part-whole nesting lets groups meaningfully honor the same operation contract as leaves.
- **Simpler first:** Use a list and loop; upgrade when clients duplicate recursive traversal and leaf/group checks.
- **Contract:** Define ownership, parent/sharing rules, cycle rejection, execution order, and partial-failure behavior before allowing side-effecting children.
- **Traps:** Shared children can execute twice; deep nesting can overflow traversal. Test cycles, depth bounds, and failure midway through a group; keep child-editing methods off leaves.
- **Not:** [Iterator](behavioral.md#iterator) hides traversal bookkeeping, not the leaf/group operation distinction.

## Decorator
- **Choose when:** Independent optional behaviors must stack under the wrapped object's contract.
- **Simpler first:** Use a function for one feature; use an explicit ordered modifier pipeline when priorities, exclusions, or numeric stages interact.
- **Contract:** Specify layer order; preserve cancellation, errors, ownership, and operation counts. Retain handles when layers need runtime removal.
- **Traps:** Add/multiply order changes stats; retries duplicate effects. Test ordering and dirty-cache invalidation for stat pipelines rather than nesting more wrappers.
- **Not:** [Chain of Responsibility](behavioral.md#chain-of-responsibility) searches or stops propagation; Decorator layers behavior around delegation.

## Facade
- **Choose when:** Callers repeat a cohesive subsystem sequence whose ordering should remain behind a stable boundary.
- **Simpler first:** Use an orchestration function; upgrade when callers need a task-oriented contract, not a universal manager.
- **Contract:** Preserve cancellation, progress, and useful failures; distinguish local durability from pending cloud synchronization rather than implying cross-system atomicity.
- **Traps:** Vague success flags hide partial completion; test synchronization failure after local commit. Keep business rules with their owning collaborators.
- **Not:** [Adapter](structural.md#adapter) reconciles incompatible interfaces; Facade simplifies orchestration without necessarily changing underlying contracts.

## Flyweight
- **Choose when:** Measurements show duplicated intrinsic data that can remain immutable while instance state stays separate.
- **Simpler first:** Verify native asset sharing and measure memory; upgrade only when duplicate storage remains a meaningful cost.
- **Contract:** Interning keys cover intrinsic differences; bound registry growth and define shared-resource release or version replacement.
- **Traps:** Mutating shared data assets affects every user. Test instance-state isolation; compare memory and lookup/locality costs, not object counts alone.
- **Not:** [Object Pool](game-programming.md#object-pool) reuses instances over time; Flyweight shares data concurrently, not merely GPU instancing.

## Proxy
- **Choose when:** Lazy, cached, remote, or authorized access needs a boundary honestly exposing latency, staleness, and failure.
- **Simpler first:** Use explicit fetch/authorize functions; upgrade when access policy recurs.
- **Contract:** Define cancellation, freshness, invalidation, security-context cache partitioning, concurrent-load synchronization, and ownership/unload behavior.
- **Traps:** Blind write retries duplicate effects; client ghosts are not authority. Test concurrent loads, cross-context cache leaks, and unload races; remote access is not local merely because signatures match.
- **Not:** [Decorator](structural.md#decorator) adds optional behavior; Proxy controls access rather than promising transparent local execution.
