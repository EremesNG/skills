# General Stacks Caveats

Load only when a TypeScript/web, Python, Java, or .NET caveat could change the design; mappings are not equivalences.
Stack-specific skills and project framework conventions win on API details; read only the relevant subsection.

## Design-Changing Caveats

### TypeScript and Web

- **Observer** — DOM EventTarget and Node EventEmitter → listeners need scope-bound cleanup; Node emit invokes listeners synchronously, not through a deferred event queue.
- **Prototype** — Spread and structuredClone → spread is shallow; structuredClone deeply clones supported values, not arbitrary application objects. See [Prototype](../creational.md#prototype).
- **Validation** — TypeScript declarations and JSON input → static types do not validate runtime shape, authorization, or domain constraints; validate at trust boundaries.
- **Concurrency** — Promises, Web Workers, and Node worker_threads → awaiting is not parallel execution; synchronous I/O or CPU work still blocks an event loop unless moved to a suitable execution boundary.

### Python

- **Prototype** — copy.copy and copy.deepcopy → shallow copies retain nested aliases; deep copying has type-specific hooks, not an unconditional isolation contract.
- **Concurrency** — asyncio, threads, and processes → blocking calls remain blocking inside async tasks; choose execution and cancellation deliberately, accounting for GIL-enabled versus optional free-threaded builds.
- **Persistence** — json and pickle → parsing is not domain validation, and pickle is unsafe for untrusted input.

### Java

- **Service scope** — Static state and Spring IoC → statics follow class loading; a Spring singleton is per container, not a language-level process singleton.
- **Concurrency** — Virtual threads (Java 21+) → scale blocking I/O, not CPU-bound computation; increasing concurrent blocking capacity does not accelerate CPU work.

### .NET

- **Dependency injection** — Microsoft.Extensions.DependencyInjection → singleton lifetime is per container; capturing scoped services extends their effective lifetime. See [Dependency Injection](../principles.md#dependency-injection-and-composition-root).
- **Prototype** — Record with expressions → referenced members are copied shallowly; a new record does not imply independent mutable state.
- **Concurrency** — async/await and TPL → asynchronous completion does not guarantee parallel execution; avoid sync-over-async waits and preserve asynchronous call chains.
- **Object pooling** — ArrayPool and Microsoft.Extensions.ObjectPool → specialized reuse does not transfer responsibility for reset or return ownership. See [Object Pool](../game-programming.md#object-pool).

## ECS

No native ECS identified (verified 2026-10); libraries supply implementations.

## Version Notes

Docs verified 2026-10-25: living web/current Node, rolling Python 3, Java SE 25, and version-selectable .NET references.
Check browser/Node support, Python build, Spring scope/version, and target .NET framework/package versions before applying API details.
