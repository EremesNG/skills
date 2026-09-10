# Multiplayer authority and persistence

## Choose ownership

Classify client presentation, authoritative gameplay, and persisted data. For
shared gameplay, validate and commit on the server through a supported target
path. UI expresses intent. Prefer existing engine replication/actions when they
cover the operation; local display settings do not need networking.

For custom commands, verify overloads in matching vanilla/stubs and
[GlobalObject](https://projectzomboid.com/modding/zombie/Lua/LuaManager.GlobalObject.html):

```text
client intent -> sendClientCommand -> server OnClientCommand
             -> validate sender/request -> commit once
             -> engine replication and/or sendServerCommand
             -> client OnServerCommand -> refresh presentation
```

This is an architecture sketch. `sendServerCommand` can notify without replicating
inventory/world mutations. Confirm the concrete API's synchronization requirements.

## Validate the server boundary

Use the authenticated sender supplied to the callback. Allowlist module/command
names. Arguments can be nil or malformed: validate types, finite numeric ranges,
lengths, supported IDs, and payload size where relevant. Resolve authoritative
targets and check ownership, permissions, distance, resources, and eligibility.

Do not accept arbitrary item types/counts, player identities, method names, or
Lua source as authoritative instructions. Reject invalid requests without partial
changes. Prevent duplicate reward/consumption commits through operation state
and, where needed, a bounded replay policy. Rate-limit expensive operations
proportionally.

Keep rendering optional on dedicated servers. Single player and listen servers
may follow different paths from remote MP; verify target `isClient()`/`isServer()`
patterns rather than guessing which covers every case. Shared Lua is not shared
process memory.

## ModData and saves

Choose storage whose lifecycle matches the data: item, player, object, or world.
Confirm actual persistence and transmission APIs in matching stubs and vanilla;
there is no assumed universal `syncModData` operation.

Namespace payloads and version evolving schemas. Persist supported serializable
values/stable IDs, not assumed-to-survive functions or live Java references.
Initialize without overwriting existing data. Make migrations repeat-safe and
preserve data they do not understand.

Persistence and replication are separate contracts. Establish save timing,
writers, transmission, and initial/late-join synchronization. Avoid sending large
payloads every tick.

Verify reload, server restart, reconnect, late join, and multiple clients as the
feature requires, including rejected/repeated requests and resulting inventory
or world effects. Use copied saves for migrations.

Source contracts: [PZEventDoc](https://github.com/demiurgeQuantified/PZEventDoc/blob/develop/docs/Events.md)
and [Umbrella/vanilla discovery](source-discovery.md). These validation criteria
are design guidance; concrete signatures must come from the target.
