# Sources and Freshness Rules

This skill synthesizes the user's requested material, but its recommendations
must remain grounded in the project being changed. Stored links are starting
points, not timeless API contracts.

## Authority order

Use evidence in this order:

1. **Observed project/runtime evidence**: repository instructions, Unity version
   and package manifests, source and tests, Editor/Player logs, builds, profiler
   captures, and target-device behavior.
2. **Official version-matched sources**: Unity Manual, Scripting API, package
   documentation/changelogs, release notes, and first-party samples for the exact
   Editor/package family in the project.
3. **Accepted project decisions**: ADRs, architecture documents, conventions,
   compatibility commitments, and user-stated constraints.
4. **Secondary educational sources**: the supplied document,
   `unitydesignpatterns.com`, books, talks, articles, and community examples.
5. **Generic skill examples**: useful for coverage ideas, never proof of current
   Unity behavior.

Secondary sources do not override observed project facts, accepted contracts, or
official version-matched documentation. When official sources conflict across
versions, match the installed version rather than choosing the newest page.

## User-supplied sources

Accessed 2026-08-01.

### Shared document

- `C:/Users/EremesNG/Downloads/Patrones de Programación de Videojuegos en Unity.docx`
- Title: *Advanced Architectural Paradigms in Unity Game Development: An
  Exhaustive Analysis of Design Patterns, Architectural Frameworks, and
  Artificial Intelligence Systems*.
- Complete structural inspection found 241 paragraphs, one comparison table,
  one section, and no inline images. LibreOffice was unavailable, so page-image
  visual QA could not run; all styled paragraphs and table cells were extracted
  with the bundled document runtime.
- Useful coverage: GoF adaptations; event buses; ScriptableObject architecture;
  broker chains; specifications/combinators; MVP; service location; data-driven
  design; FSM/HFSM; behavior trees; blackboards; GOAP; lifecycle and performance
  concerns.

Qualify these document claims instead of repeating them:

- Service Locator is not categorically better than Singleton; both can hide
  dependencies and global lifetime.
- Behavior trees are common, not a universal industry-standard answer.
- Object Pooling is a reuse optimization that can use Prototype/Prefab creation;
  treating it as simply a Prototype subtype obscures reset and capacity concerns.
- A central Update Manager does not automatically improve CPU cache locality;
  data layout, workload, scheduling, and measurements determine the result.
- Planner work can be time-sliced or scheduled in jobs only when managed data,
  Unity API, synchronization, and determinism boundaries are safe.
- Two extracted passages omit the attribute name for polymorphic managed
  serialization; official `SerializeReference` documentation supplies the rule.

### Requested website

- <https://www.unitydesignpatterns.com/>
- Representative detailed pages reviewed: Observer, State, Command, Strategy,
  Singleton, Factory, Builder, Prototype, Object Pool, Adapter, Decorator,
  Facade, Dependency Injection, MVP, and Service Locator.
- Strength: concise Unity examples plus use/avoid and trade-off guidance.
- Limitation: examples are educational baselines. Validate lifecycle,
  serialization, package availability, API age, failure behavior, and target
  performance before adapting code.

### Requested baseline skill

- <https://raw.githubusercontent.com/rmyndharis/antigravity-skills/refs/heads/main/skills/unity-developer/SKILL.md>
- Repository path: `rmyndharis/antigravity-skills`,
  `skills/unity-developer/SKILL.md`.
- Strength: broad inventory of Unity responsibilities.
- Limitation: a capability list does not inspect a project, select by forces,
  allow no-pattern solutions, define ownership/lifetimes, or require test and
  profiler evidence. Version/package statements can drift.

## First-party Unity starting points

Accessed 2026-08-01. Follow each page's version switcher or the package version
declared in the project.

### Architecture, data, and serialization

- ScriptableObject manual:
  <https://docs.unity3d.com/6000.1/Documentation/Manual/class-ScriptableObject.html>
- ScriptableObject architecture article:
  <https://unity.com/how-to/architect-game-code-scriptable-objects>
- `SerializeReference` Scripting API:
  <https://docs.unity3d.com/6000.0/Documentation/ScriptReference/SerializeReference.html>
- Domain Reload behavior and static reset:
  <https://docs.unity3d.com/6000.0/Documentation/Manual/domain-reloading.html>
- Assembly Definitions:
  <https://docs.unity3d.com/6000.0/Documentation/Manual/assembly-definitions.html>
- Unity's game programming pattern resource:
  <https://unity.com/resources/level-up-your-code-with-game-programming-patterns>

### Testing and performance

- Unity Test Framework package documentation:
  <https://docs.unity3d.com/Packages/com.unity.test-framework@latest/>
- Profiling applications, with target device as the authoritative performance
  environment:
  <https://docs.unity3d.com/2022.2/Documentation/Manual/profiler-profiling-applications.html>
- `UnityEngine.Pool.ObjectPool<T>` Scripting API:
  <https://docs.unity3d.com/6000.0/Documentation/ScriptReference/Pool.ObjectPool_1.html>

### Artificial intelligence systems

- AI Navigation package overview:
  <https://docs.unity3d.com/6000.0/Documentation/Manual/com.unity.ai.navigation.html>
- Unity Behavior, the first-party graph/behavior-tree tool:
  <https://docs.unity3d.com/6000.0/Documentation/Manual/com.unity.behavior.html>
- ML-Agents package overview:
  <https://docs.unity3d.com/6000.0/Documentation/Manual/com.unity.ml-agents.html>
- Sentis/local neural inference package overview:
  <https://docs.unity3d.com/6000.0/Documentation/Manual/com.unity.ai.inference.html>

AI Navigation addresses navigation and pathfinding. Unity Behavior addresses
graph-authored behavior. ML-Agents addresses training learned policies. Sentis
addresses local model inference. Do not substitute one category for another.

## Refresh when

Refresh version-sensitive guidance when any of these is true:

- `ProjectVersion.txt`, `manifest.json`, or `packages-lock.json` differs from the
  version family used by an example;
- a page is marked preview, experimental, prerelease, deprecated, legacy, or
  redirects `latest` to a new major version;
- a package was renamed, split, moved from core to a package, or changes its
  authoring/runtime model;
- an API signature, serialization rule, player-loop behavior, platform support,
  IL2CPP behavior, or test-runner CLI affects correctness;
- the user asks for current package recommendations, supported versions,
  pricing/licensing, platform certification, or roadmap status;
- a copied code sample does not compile against the project's assemblies.

When browsing, prefer the official page for the installed version and record its
URL/version near the decision. If lookup is unavailable, state the uncertainty
and provide the exact fact that must be checked instead of presenting memory as
evidence.
