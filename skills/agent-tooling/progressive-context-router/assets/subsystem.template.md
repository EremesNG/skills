# <Subsystem name>

## Responsibility

<One paragraph describing the behavior this subsystem owns and what it explicitly does not own.>

## Route signals

- User vocabulary: `<terms>`
- Explicit paths: `<paths>`
- Typical task shapes: `<bug/feature/refactor types>`

## Entry points and code roots

- `<path>:<symbol>` — <role>
- `<path>/` — <role>

## Flow

1. <Input and entrypoint>
2. <Important domain decision>
3. <Dependency or persistence>
4. <Output, event, or public contract>

## Dependencies and overlays

- Depends on `<domain>` for <reason>.
- Load `<overlay>` when <condition>.
- Do not load `<other domain>` unless <condition>.

## Invariants and hazards

- <Non-obvious invariant with evidence path.>
- <Ordering, retry, authorization, compatibility, or lifecycle hazard.>

## Tests and verification

- Tests: `<path>/`
- Narrow command: `<verified command>`
- Broader checks when: <condition>

## Common mistakes

- <Mistake> causes <impact>; inspect <path or test>.

## Escalate context when

- <A concrete unresolved question requires another document or domain.>

## Evidence and uncertainty

- Verified from: `<paths and symbols>`
- Needs confirmation: `<uncertain fact>`
