# Research: Unity Developer Skill

## Questions

1. What knowledge from the supplied document and `unitydesignpatterns.com` is
   durable enough to encode in a reusable skill?
2. What makes the user-provided example skill too shallow for professional
   solution selection?
3. Which current Unity constraints and first-party systems must shape the
   workflow without making the skill version-bound?
4. What package structure best balances breadth with progressive disclosure?

## Evidence reviewed

- `C:\Users\EremesNG\Downloads\Patrones de Programación de Videojuegos en Unity.docx`
  - Structurally inspected in full: 241 paragraphs, 1 comparison table, 1
    section, and 0 inline images.
  - LibreOffice was unavailable, so the packaged DOCX-to-PNG render gate could
    not run. Text styles, all paragraphs, and every table cell were extracted
    with the bundled document runtime; no visual claims are made.
- `https://www.unitydesignpatterns.com/`
  - Reviewed its pattern inventory and detailed pages for representative
    behavioral, creational, structural, architectural, and optimization
    patterns, including Observer, State, Command, Strategy, Singleton, Factory,
    Object Pool, Adapter, Decorator, Dependency Injection, MVP, and Service
    Locator.
- User-provided baseline:
  `https://raw.githubusercontent.com/rmyndharis/antigravity-skills/refs/heads/main/skills/unity-developer/SKILL.md`
  - Reviewed all 206 lines.
- First-party Unity documentation and resources available on 2026-08-01:
  ScriptableObject and ScriptableObject architecture, serialization and
  `SerializeReference`, domain reload, assembly definitions, Test Framework,
  target-device profiling, `UnityEngine.Pool.ObjectPool<T>`, AI Navigation,
  Unity Behavior, ML-Agents, and local neural-network inference.
- Repository conventions in `README.md`, `VALIDATION.md`, `.github/workflows`,
  existing skills, UI metadata, evaluation files, and unit tests.

## Findings

### F1 - A catalog is not a decision system

The baseline skill is a broad capability list. It does not require inspecting a
real Unity project, identifying the forces that make a pattern suitable,
considering a no-pattern solution, recording rejected alternatives, defining
lifetimes, or obtaining behavioral/performance evidence. Its version and package
claims can also become stale. Copying that shape would produce confident but
generic answers.

**Decision**: Make `unity-developer` a context-to-evidence workflow. Pattern and
AI catalogs live in references and are loaded only after classifying the
problem.

### F2 - The supplied document is broad but not uniformly authoritative

The document supplies a useful taxonomy: GoF reinterpretations, ScriptableObject
architecture, event buses, broker chains, specifications/combinators, MVP,
service location, data-driven design, FSM/HFSM, behavior trees, blackboards, and
GOAP. It also exposes high-value Unity concerns such as `Awake` order, scene
lifetimes, event cleanup, serialization, allocation, and planner cost.

Several claims require qualification rather than transcription:

- Service Locator is not inherently "better" than Singleton; both can hide
  dependencies and global state.
- Behavior trees are common, but not a universal industry-standard answer.
- Pooling is related to reuse and creation cost but should not be treated as a
  subtype of Prototype without context.
- A central update manager does not automatically improve cache coherence;
  measurement, data layout, and workload matter.
- Background planning may use jobs or managed threads only when Unity API access
  and synchronization boundaries are safe.
- The extracted document omits the attribute name in two polymorphic
  serialization passages; official `SerializeReference` rules fill that gap.

**Decision**: Preserve the taxonomy and decision forces, correct overbroad
claims, and route unstable details to version-matched official documentation.

### F3 - Unity-specific lifetimes are architectural requirements

First-party documentation confirms that ScriptableObjects are shared asset data
containers, not a build-time save system; `SerializeReference` has scope and
performance trade-offs; disabled domain reload leaves static fields and handlers
alive; assembly definitions create real compilation boundaries; EditMode and
PlayMode tests cover different seams; and profiler measurements are most accurate
on target hardware.

**Decision**: Treat serialization, authored-versus-runtime state, scene and
domain reload, event teardown, destroyed-object semantics, main-thread access,
and target-device evidence as mandatory review dimensions.

### F4 - "AI" must be decomposed

The provided material and first-party packages cover different concerns:
behavior/decision graphs, navigation/pathfinding, reinforcement/imitation
training, and local model inference. Calling all of them "AI" obscures ownership,
budgets, determinism, and debugging.

**Decision**: Route AI work through perception -> memory/blackboard -> decision
-> action -> navigation/animation. Compare rule logic, FSM/HFSM, behavior trees,
utility scoring, GOAP, learned policies, inference, and hybrids at the decision
layer; never use ML merely because the prompt says AI.

### F5 - A bounded inspector improves grounding

Unity projects expose useful, stable evidence in `ProjectVersion.txt`, package
manifests, assembly definitions, test assemblies, and C# source layout. A
read-only standard-library script can report this context without opening the
Editor, installing packages, or exposing source contents.

**Decision**: Bundle `inspect_unity_project.py`. Its static source matches are
signals for investigation, never automatic defects. JSON is stable for agents;
human text is concise for developers.

### F6 - Progressive disclosure is necessary

Pattern, architecture, AI, engine/lifecycle, and source material together exceed
a responsible always-loaded prompt. The repository already favors self-contained
skills with focused references and deterministic scripts.

**Decision**: Keep `SKILL.md` focused on intake, routing, decision, implementation,
verification, and response. Put detailed knowledge into six purpose-specific
references.

## Resulting package shape

```text
skills/unity-developer/
├── SKILL.md
├── agents/openai.yaml
├── evals/evals.json
├── references/
│   ├── decision-framework.md
│   ├── design-patterns.md
│   ├── architecture.md
│   ├── ai-systems.md
│   ├── unity-engine-constraints.md
│   └── sources.md
└── scripts/inspect_unity_project.py
```

## Unresolved research

None blocks implementation. Package names and versions remain invocation-time
evidence rather than hardcoded recommendations.
