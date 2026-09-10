# Architecture context

Document only stable boundaries and flows that an agent is likely to misunderstand from local code alone.

## System shape

<Brief description of applications, services, packages, runtimes, and their responsibilities.>

## Entry flows

### <Flow name>

1. `<entrypoint or registration>` receives <request/event/input>.
2. `<symbol or module>` applies <important decision or invariant>.
3. `<dependency>` performs <persistence/external call/dispatch>.
4. `<tests>` verify <contract>.

## Boundaries and ownership

| Boundary | Owner | Public contract | Verification |
|---|---|---|---|
| `<domain/service>` | `<path or team metadata>` | `<API/event/package>` | `<tests or command>` |

## Dependency direction

- `<module>` may depend on `<module>` because <reason>.
- `<module>` must not depend on `<module>` because <invariant>.

## Non-obvious invariants

- <Stable rule with evidence path.>

## Escalation conditions

Read additional domain documentation when:

- <condition that changes data ownership, public contracts, or runtime boundaries>;
- <condition that makes a local change cross-domain>.

## Evidence and uncertainty

- Verified from: `<paths, manifests, tests>`
- Needs confirmation: `<uncertain fact>`
