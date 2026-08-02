# Allocation hotspot catalog

Use this as an investigation index, not a lint rule. A construct outside the
named measured workload is not automatically a defect. Confirm the installed
Unity/package implementation and the target-player trace before changing it.

## Locate the measured hot path

1. Start from the workload and sample window in the allocation contract.
2. Use `GC.Alloc` call stacks or a reproducible `ProfilerRecorder` measurement
   to find an allocation boundary. Inspect every relevant thread.
3. Read the source at that boundary and determine whether it is first-use,
   capacity growth, an exception path, or recurring steady-state work.
4. Prefer removing work, retaining/reusing storage, or a built-in caller-buffer
   overload. Add a dependency only when it improves the complete contract.
5. Preserve behavior and remeasure. A lower heap size, fewer collections, or an
   allocation-free microbenchmark does not by itself prove the workload.

## Managed-language hotspots

Each row names the usual allocation boundary, the smallest candidate change,
and the evidence check including a version-sensitive exception.

| Family | Allocation boundary and smaller option | Evidence check / version-sensitive qualification |
|---|---|---|
| Strings and formatting | Concatenation, interpolation formatting, numeric conversion, and `StringBuilder.ToString` create strings. Cache stable text, update only when data changes, use TMP numeric setters or a scoped builder when supported. | Verify the final consumer: `StringBuilder.ToString` still allocates the final string, while a direct TMP writer can avoid it. Constant folding and compiler interpolation handlers vary. |
| Logging | Arguments may be formatted or boxed even when the log is filtered; stack traces also cost. Compile/guard noisy hot-path logging and use structured/cached messages where the project logger supports them. | Profile the actual build and logging configuration. Removing a log can hide diagnostics and exception logs are intentionally cold-path in many projects. |
| Closures | A lambda that captures state can allocate a display class and delegate; repeated method-group conversion can also create delegates. Pass state explicitly, cache a non-capturing callback, or use a library state overload. | Inspect generated behavior or the call stack: non-capturing lambdas and cached delegates may allocate once, and compiler/runtime versions differ. |
| Delegates and events | Delegate construction and invocation-list changes allocate; abandoned subscriptions retain targets. Cache stable delegates and pair subscribe/unsubscribe with ownership. | Measure registration and invocation separately. Static handlers are not automatically lifetime-safe, and a library may pool callback promises while user captures still allocate. |
| Boxing, interfaces, and `params` | Converting a value type to `object` or an interface can box; `params` often creates an array. Use generic/concrete overloads and explicit reusable arguments where APIs permit. | Confirm IL/AOT and call stacks. Interface conversion is a risk boundary, not proof; compiler specialization and API overloads are version-sensitive. |
| Iterators and enumeration | `yield` creates iterator state; enumerating through `IEnumerable<T>` may box a struct enumerator. Prefer a direct loop or concrete collection/value-enumerable in a proven hot path. | `foreach` over a concrete array or `List<T>` can be allocation-free. Do not ban `foreach`; interface conversion and custom enumerator implementation decide the result. |
| LINQ and materialization | Iterator chains, delegates, captures, `ToArray`, `ToList`, ordering, and grouping can allocate. A direct loop, reusable result, or ZLinq value-enumerable may fit. | Measure the entire chain and terminal operation. ZLinq does not erase captured closures, result materialization, pool ownership, or semantic differences. |
| Arrays | APIs/properties that return a fresh array allocate each call. Cache immutable results or choose an overload accepting an array, span, list, or caller buffer. | Do not cache data whose contents are live/versioned. Array-return behavior and availability of caller-buffer overloads vary by Unity version. |
| Collections | Construction, capacity expansion, snapshots, hash resizing, and iterator/interface paths can allocate. Retain, `Clear`, pre-size, and use concrete iteration when ownership permits. | `Clear` retains capacity and can retain references until cleared by the implementation; a reused list still allocates when it grows. Balance retained memory against peak capacity. |
| Coroutines | An `IEnumerator` state machine, yielded objects, nested enumerators, and start/stop patterns can allocate. Reuse yield instructions only when semantics allow, use an explicit update state machine, Awaitable, or UniTask for a measured source. | Unity versions and yield type determine costs. Replacing a coroutine changes start timing, cancellation, exception, order, and object-lifetime semantics unless locked by tests. |
| Async | `Task`, captured state, continuations, cancellation registrations, exception paths, and combinators can allocate. Consider Unity Awaitable or UniTask only after defining thread and cancellation semantics. | Unity Awaitable is pooled and single-await; UniTask has PlayerLoop and promise-pool constraints. Synchronous completion versus suspension changes observed cost. |
| Exceptions | Throwing builds exception/stack data and async failures can allocate. Validate expected states before a hot loop and reserve exceptions for exceptional behavior. | Do not suppress or replace correctness failures merely to hit a budget. Usually test exception paths outside the steady-state window and report them separately. |
| Reflection and dynamic activation | Metadata queries, attribute arrays, invocation argument arrays, generic construction, and expression compilation can allocate. Cache immutable metadata or generate/register code at startup. | Cache invalidation, domain reload, stripping, and IL2CPP/AOT behavior are version-sensitive. Preserve first-use and failure semantics. |

## Unity API hotspots

| Family | Allocation boundary and smaller option | Evidence check / version-sensitive qualification |
|---|---|---|
| Physics | Array-return queries such as `RaycastAll` allocate results. Use a correctly sized reused buffer and a NonAlloc overload when its truncation/order contract is accepted. | A full buffer can mean truncated results and does not necessarily contain the nearest hits. Record saturation and confirm documentation for the installed Unity version. |
| Collision | Accessing contact arrays or copying contacts can allocate depending on API/version. Use current `Collision.GetContacts` caller-buffer overloads and pre-sized storage. | Contact reuse and callbacks changed across Unity versions. Verify buffer fullness and target-player call stacks instead of copying old optimization folklore. |
| Input | Legacy properties that return arrays can allocate. Use indexed access such as touch count plus `Input.GetTouch`, or the installed Input System's event/state APIs. | Input backends and package versions have different lifetime/thread rules; do not mix semantics during an allocation-only refactor. |
| Mesh | Properties such as vertex/index arrays can return copies. Prefer `GetVertices(List<T>)`, caller-owned native data, or direct mesh-data APIs with prepared capacity. | Read/write mesh data and native views have explicit lifetime and job dependencies. Reused lists grow if undersized. |
| Renderer and materials | `renderer.material` may instantiate a material; repeated property retrieval and per-frame arrays can allocate. Cache immutable components and use a reused `MaterialPropertyBlock` for per-renderer values. | Shared versus instanced material semantics differ. Clear/reset property blocks deliberately; some APIs copy data even when managed allocation is absent. |
| UI and text | Per-frame label construction, layout rebuilds, tween callbacks, and collection snapshots create churn. Update on change, cache formatting state, use TMP setters/scoped builders, and reduce rebuild frequency. | Final string output can still allocate; localization, rich text, fallback fonts, and layout behavior must remain correct. Measure the real canvas and target. |
| Component/object lookup | Search result arrays, repeated component queries, and hierarchy traversal can allocate or consume CPU. Cache references with a defined invalidation lifetime and use caller-list overloads where available. | Unity documents Editor-only allocation for some `GetComponent` profiling cases. A target player is authoritative, and caching can become stale. |
| Runtime object churn | `Object.Instantiate`, `Object.Destroy`, particle/projectile/UI item creation, and transient managed models generate managed and native work. Reuse through a bounded pool only when reset and teardown are correct. | Empty pools still instantiate; over-capacity releases may destroy; retained objects consume memory. Pooling shifts costs and is not automatically faster. |
| Resources and Addressables | Repeated loads, handles, callbacks, and premature release can create objects or retain bundles. Cache with explicit reference ownership and mirror every load/instance acquisition with the matching release. | Addressables package versions differ. Ref-count zero enables unload but bundle dependencies and asset churn can still cause memory spikes. |

## Qualification rules

- No blanket bans: LINQ, coroutines, strings, reflection, allocation, or
  Instantiate/Destroy can be reasonable outside a measured hot path.
- A concrete array or concrete `List<T>` `foreach` is not the same boundary as
  enumeration after interface conversion.
- Unity 6 may provide allocation-free enumerators or caller-buffer APIs that an
  older rule overlooks; an older supported editor may lack them.
- `GetComponent` Editor-only samples are leads, not target-player proof.
- Separately report managed allocation, native allocation, retained memory, and
  CPU. Moving bytes out of the managed heap does not erase cost.
- Measure before and after with the same warm-up, capacities, workload, build,
  hardware, thread coverage, and sample window.
