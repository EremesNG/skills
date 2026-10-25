# Creational Patterns

Read when construction varies by product, compatible family, assembly stages, or configured starting state; distinguish creation from ownership.

## Factory Method
- **Choose when:** An inherited workflow stays fixed while one product-creation hook must vary.
- **Simpler first:** Pass a creation function or use a lookup table; upgrade when a workflow needs an overridable creation seam.
- **Contract:** Keep the product contract small; specify who owns, disposes, or returns each product to a pool.
- **Traps:** Subclasses merely selecting types or configuration multiply maintenance; test product cleanup as well as successful creation.
- **Not:** [Template Method](behavioral.md#template-method) governs the workflow skeleton; Factory Method varies its creation step, not every function named `create`.

## Abstract Factory
- **Choose when:** Switching several product types together preserves a real compatibility rule; mixing families would be invalid.
- **Simpler first:** Use one configuration record; upgrade when families differ in behavior and cross-product compatibility, not just asset identifiers.
- **Contract:** Define compatible combinations and lifetime rules across products, not merely independent constructor signatures.
- **Traps:** Adding a product category changes every family; test cross-product behavior, including invalid mixtures, rather than non-null creation alone.
- **Not:** [Factory Method](creational.md#factory-method) varies a product-creation hook; Abstract Factory supplies a compatible family through one boundary.

## Builder
- **Choose when:** Staged assembly must keep partial results private until a final consistency check succeeds.
- **Simpler first:** Use named arguments or an options record; upgrade for meaningful validation stages or reused assembly recipes, not fluent setters.
- **Contract:** Publish only valid results; define whether build consumes, resets, or snapshots the builder, and release acquired resources on failure.
- **Traps:** Reuse can leak previous options; test failed assembly, subsequent reuse, and unfinished-object escape. A director is optional.
- **Not:** [Abstract Factory](creational.md#abstract-factory) selects compatible products rather than controlling staged assembly.

## Prototype
- **Choose when:** Runtime-selected, author-configured examples seed instances more clearly than constructor hierarchies.
- **Simpler first:** Use a spawn function plus configuration, or existing prefab tooling; upgrade when copying configured graphs supplies missing behavior.
- **Contract:** Set per-field copy/share/handle policies; preserve aliases and terminate cycles with a copy context. Reset identity, subscriptions, and ownership.
- **Traps:** Shallow copies alias mutable state; indiscriminate deep copies mishandle external resources. Test nested mutation, cycles, reference remapping, and handles.
- **Not:** [Type Object](game-programming.md#type-object) shares definitions; inherited content defaults do not automatically clone independent instances.

## Singleton
- **Choose when:** An external constraint requires one process-wide owner, and global discovery is independently required.
- **Simpler first:** Inject a scope-owned instance; upgrade for required global discovery, not to share references.
- **Contract:** Define initialization failure, concurrent construction/shutdown, and lifetime; access after shutdown must not resurrect the service.
- **Traps:** Hidden dependencies contaminate tests; scene changes create duplicates. Test multiple worlds, repeated initialization, and shutdown-time access.
- **Not:** [Service Locator](game-programming.md#service-locator) provides discovery, not enforced uniqueness; scoped engine services are not automatically Singletons. Uniqueness and global access are separate decisions.
