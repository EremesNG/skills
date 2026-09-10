# Unity Design Pattern Selection

Use this catalog only after identifying the dominant force in the decision
framework. A pattern name is vocabulary, not proof that the pattern is needed.
Prefer the direct mechanism in the first row of a family when it satisfies the
same contract with clearer ownership and fewer failure modes.

The tables describe selection boundaries. Adapt implementation to the project's
Unity/C# version, lifecycle, serialization rules, and profiler evidence.

## Creational patterns

| Pattern | Use when | Avoid when | Unity hazards | Useful composition |
| --- | --- | --- | --- | --- |
| Direct creation or serialized reference | One owner creates one stable type, or a scene/prefab already owns the reference | Creation logic repeats, varies at runtime, or needs centralized validation | `new` cannot create `MonoBehaviour`; scene references can be missing after unload | Composition root for explicit ownership |
| Factory Method | Callers need an abstraction over prefab/data selection and setup varies by concrete product | There is one simple type and one call site | Factories that only wrap `Instantiate` add indirection; validate prefab/component contracts | Object Pool for reuse; Strategy for selection policy |
| Abstract Factory | A coherent family must switch together, such as platform UI, control hints, or themed assets | Products vary independently or the family has only one member | Asset families can drift or be partially configured; fail validation before runtime | Adapter at platform SDK edge; ScriptableObject family configuration |
| Builder | Construction has ordered steps, optional parts, validation, or a readable procedural recipe | A constructor/object initializer remains clear and invalid partial state is impossible | Do not build Unity objects off the main thread; make `Build` ownership and failure atomic | Factory selects a builder; Prototype supplies templates |
| Prototype | A configured prefab or data template is the source of new instances | Deep-copy semantics are ambiguous or shared references would be unsafe | `Instantiate` clones serialized data but nested managed references and asset references have different identity rules | Factory for selection; Object Pool for frequent reuse |
| Singleton | Exactly one application-lifetime instance is an invariant and global access cost is accepted | Scene/session scopes differ, tests need substitution, or dependencies should be visible | `Awake` order, duplicates, `DontDestroyOnLoad`, shutdown resurrection, disabled domain reload, hidden global state | Prefer a composition root and injected interface; use a reset hook if static state is unavoidable |

Singleton is a last-mile lifetime decision, not the default way to make something
easy to reach. "Manager" in a class name does not establish singleton semantics.

## Structural patterns

| Pattern | Use when | Avoid when | Unity hazards | Useful composition |
| --- | --- | --- | --- | --- |
| Adapter | Gameplay expects a stable interface while an SDK, plugin, legacy API, or platform implementation differs | You control both sides and can align the interface directly | Keep platform directives and SDK types inside the adapter; test real integration separately | Dependency Injection supplies the adapter; Facade groups several adapters |
| Bridge | Two dimensions must vary independently and inheritance would create a type cross-product | Only one dimension varies or composition already expresses it directly | Inspector serialization of interfaces/polymorphic data may need ScriptableObjects or `SerializeReference` | Factory creates implementations; Strategy handles one algorithmic axis |
| Composite | Leaves and groups must support the same operation, such as effects, objectives, UI nodes, or ability trees | Parent and child behavior is materially different | Guard cycles, recursion depth, shared mutable nodes, and destructive traversal of Transform hierarchies | Command for executable leaves; Decorator for optional node behavior |
| Decorator | Independent behaviors stack dynamically without a subclass for every combination | Order is irrelevant and a flat data calculation is clearer | Wrapper order changes results; lifecycle/disposal and allocations can become invisible | Factory assembles chains; Broker Chain for numeric modifiers |
| Facade | A client needs a stable high-level operation over a complex subsystem such as save, loading, audio, or SDK flow | It merely renames one method or becomes a god object | Do not hide partial failure, cancellation, progress, or ownership behind `void` methods | Adapter behind external edges; Mediator for coordinated peers |
| Flyweight | Many instances share immutable intrinsic data while keeping unique runtime state separately | Data is frequently mutated per instance or identity must be unique | ScriptableObject assets can be accidentally used as mutable runtime state; material/mesh mutation can instantiate copies | Factory/Prototype for instances; Dirty Flag for derived shared data |
| Proxy | Access needs lazy loading, caching, authority, validation, remoting, or a placeholder with the same contract | Direct access is cheap and requires no policy | Addressable/network proxies are asynchronous and may outlive scenes; expose cancellation and missing assets | Facade for subsystem API; Adapter for third-party handles |

Treat Unity Prefabs and Transform hierarchies as engine mechanisms that resemble
Prototype and Composite. Do not add parallel class hierarchies merely to make the
analogy literal.

## Behavioral patterns

| Pattern | Use when | Avoid when | Unity hazards | Useful composition |
| --- | --- | --- | --- | --- |
| Chain of Responsibility | Ordered handlers may transform, reject, or consume a request without the sender choosing one | Every handler always runs and a simple pipeline/list is clearer | Handler order must be deterministic and inspectable; avoid silent fall-through | Broker Chain for stats; Command as the request |
| Command | Actions need queueing, rebinding, undo/redo, replay, scheduling, logging, or deterministic transport | A direct one-shot call needs none of those capabilities | Capture enough state for undo/replay; bound history; avoid per-frame allocation; distinguish intent from result in multiplayer | Memento for snapshots; Factory/Pool for command creation |
| Interpreter | Designers/users need a small grammar for console commands, formulas, conditions, or dialogue expressions | The language is not stable enough to justify parser/security/versioning work | Never evaluate arbitrary C#; validate grammar, limits, culture, errors, and save compatibility | Composite for syntax tree; Visitor for analysis/evaluation |
| Iterator | A caller needs controlled traversal without exposing storage, or work must be yielded across frames | A normal collection loop is already the public contract | Unity coroutines use iterators but do not create threads; cancellation follows GameObject/lifetime rules | Composite traversal; scheduler/time slicing |
| Mediator | Several peer systems interact and direct references would form a dependency mesh | One publisher-to-listener relationship fits an event or direct call | A level/game manager can become a god mediator; make message types and routing visible | Observer for notifications; Facade for external clients |
| Memento | State must be restored for undo, checkpoints, save/load, or experimentation | Recomputing state is cheaper and authoritative sources already exist | Deep versus shallow copy, `UnityEngine.Object` references, schema versioning, storage size, and snapshot frequency | Command for undo history; serializer/version migration |
| Observer | One subject change has independent, changing listeners | There is one stable receiver, request/response is required, or event order is critical | Pair subscribe/unsubscribe; static handlers survive disabled domain reload; UnityEvent adds serialized/reflection behavior | MVP model notifications; scoped Event Bus for cross-feature events |
| State | One object's behavior and valid transitions change by explicit mode | Two stable branches fit an enum/switch or states do not own cohesive behavior | Cache reusable states, define Enter/Exit, avoid transition races, coordinate Animator state separately | HFSM for shared parents; Strategy inside a state; Command for inputs |
| Strategy | One goal has interchangeable algorithms selected at composition or runtime | Algorithms do not share a meaningful contract or only one variant exists | Define enter/exit/reset if strategies carry runtime state; avoid per-frame allocation | State selects a strategy; ScriptableObject stores authored strategy configuration |
| Template Method | A stable algorithm skeleton has a few controlled subclass extension steps | Steps must combine freely, change at runtime, or inheritance couples unrelated state | MonoBehaviour inheritance can obscure Unity messages and serialized fields | Strategy replaces variable steps; composition preferred for reusable gameplay |
| Visitor | Many stable element types need new type-specific operations and double dispatch is valuable | Element types change often or a switch/polymorphic method is clearer | Adds boilerplate; avoid tag/type-check chains disguised as visitors | Composite traversal; Interpreter AST operations |

For Observer, distinguish a local typed C# event from a project-wide Event Bus.
The latter adds naming, lifecycle, tracing, and ownership obligations; use it only
for genuinely cross-boundary facts, not every method call.

## Architectural patterns

| Pattern | Use when | Avoid when | Unity hazards | Useful composition |
| --- | --- | --- | --- | --- |
| Manual Dependency Injection | Dependencies should be visible/substitutable and a composition root can wire them with Inspector fields, constructors for plain C#, or explicit initialization | A stable local component reference already communicates ownership clearly | `MonoBehaviour` construction is engine-owned; validate before use and do not depend on arbitrary `Awake` order | Composition root plus Adapter/Strategy interfaces |
| DI container | Many graphs/scopes/repeated bindings are already costly and the team owns container debugging and lifecycle | Small/medium projects can wire dependencies manually or adoption is speculative | Reflection/code generation, IL2CPP stripping, scene scopes, installer order, package lock-in | Keep domain independent of container; use a Facade at the composition boundary |
| Service Locator | Legacy/global service access must be centralized temporarily or dynamic optional service discovery is a real requirement | Dependencies should be compile-time visible and missing registration must not be a runtime surprise | Hidden dependencies, stale destroyed objects, duplicate registrations, domain reload, test leakage | Composition root registers; Adapter supplies platform service; prefer migration to injection |
| MVP | UI logic, validation, or flows need plain-C# tests and the View should remain replaceable/passive | A tiny static HUD has no meaningful presentation logic | Dispose presenter subscriptions; keep Unity UI types out of Model; split oversized presenters | Observer between Model and Presenter; Facade for use cases |
| ScriptableObject Architecture | Designers need shared authored configuration, event assets, runtime sets, or scene-independent references | Per-instance mutable runtime state or save data is being hidden in assets | Asset values can persist in Editor, runtime state can leak between plays, event listeners need cleanup, builds cannot save asset mutations as player save data | Flyweight for immutable data; runtime service for mutable state; Observer for event channels |
| Event Bus / publish-subscribe | Facts cross feature boundaries and publishers cannot own a growing listener list | Local direct calls/events are sufficient, order/result matters, or tracing is absent | Static buses survive reload, retain listeners, hide flow, and can allocate; scope by lifetime and instrument | Mediator for coordinated workflows; typed events; composition root owns bus lifetime |
| Broker Chain | RPG/stat values need ordered flat/additive/multiplicative modifiers with source removal and caching | A direct formula or small fixed modifier set is clearer | Define deterministic ordering/rounding, duplicate sources, dirty invalidation, save schema, and debugging output | Chain of Responsibility plus Dirty Flag; Factory creates modifiers |
| Specification / Combinator | Rules must compose with And/Or/Not, be named/tested independently, and feed abilities, targeting, achievements, or AI | A short condition is stable and readable | Avoid allocating rule graphs in hot loops; expose failure reasons when designers/debuggers need them | Builder for readable assembly; Composite for rule trees; Strategy for evaluators |
| Data-driven composition | Content variants should be authored as data and executed by stable code | Data becomes an untyped scripting language without validation/tooling | Unity serialization, managed-reference identity, asset migration, missing types, and validation UX | ScriptableObjects for assets; Factory/Strategy for runtime executors |

### ScriptableObject architecture boundary

ScriptableObjects can implement Flyweight-like shared data, policy assets, event
channels, runtime sets, or systems, but those roles have different lifetime and
mutation rules. Name the role explicitly. Keep initial/authored values separate
from runtime values, reset mutable state deterministically, and do not treat an
asset reference as automatic dependency injection.

## Optimization patterns

Choose an optimization pattern only after a reproducible measurement on relevant
hardware identifies the cost.

| Pattern | Use when | Avoid when | Unity hazards | Useful composition |
| --- | --- | --- | --- | --- |
| Dirty Flag | Derived data is expensive, read often, and changes less often than it is read | Calculation is cheap, values change every read, or stale data is unacceptable | Every mutation path must invalidate; define eager/lazy refresh and thread ownership | Broker Chain cache; rendering/layout recalculation |
| Object Pool | Profiling shows frequent compatible create/destroy cost and reset is cheaper than recreation | Objects are rare, long-lived, memory-heavy, or unsafe to reset | Reset physics, coroutines, events, transforms, IDs, effects, and ownership; size/prewarm from measurements; built-in pools are not thread-safe | Factory chooses type; Prototype/Prefab creates new capacity |
| Spatial Partition | Nearby/range queries scan too many objects and spatial locality is stable enough to exploit | Counts are small, queries are rare, or physics broadphase already provides the needed query | Cell size, moving updates, world bounds, uneven density, memory, determinism, and duplicate query results | Object Pool for nodes; Dirty Flag for moved regions |
| Update Manager | Profiling shows callback overhead or scheduling needs across many homogeneous objects | A modest number of lifecycle callbacks is clear and within budget | Central loops can become global god systems, break enable/disable semantics, and do not guarantee cache locality | Data-oriented arrays; time slicing; spatial visibility sets |
| Data-oriented ECS/Jobs/Burst | Measured work is large, homogeneous, parallelizable, and benefits from contiguous data and batch scheduling | Object-rich gameplay, low counts, team/tooling constraints, or hybrid conversion cost dominates | Structural changes, sync points, managed components, main-thread Unity APIs, baking, debugging, package/version compatibility | Spatial partition, command buffers, authoring GameObject adapters |

## Common useful compositions

- **Spawn system**: Factory chooses a validated prefab/product; Object Pool owns
  capacity and reset; a composition root owns lifetime. Do not let the factory
  silently become the pool.
- **Data-driven ability**: ScriptableObject stores authored data; Specification
  checks conditions; Command executes intent; Strategy varies targeting/effect;
  runtime state lives outside the asset.
- **UI screen**: MVP separates Model/View/Presenter; Observer carries model
  changes; Facade exposes application use cases. Keep navigation ownership clear.
- **Save/replay**: Command records deterministic intent; Memento captures
  necessary state; versioned serialization owns migration. Avoid serializing raw
  scene references.
- **NPC behavior**: State/HFSM handles high-level modes; behavior tree or utility
  chooses local actions; Blackboard holds scoped knowledge; navigation handles
  paths. Each layer needs a separate update budget and debug view.

Stop adding patterns when every accepted force has one clear owner. More names do
not produce more architecture.
