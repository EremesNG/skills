# Lua bridge and events

## Java is not automatically Lua

Establish receiver type, inherited declaring class, overload, argument order,
return type, nullability, and execution side. Follow `IsoPlayer` inheritance when
a method belongs to `IsoGameCharacter`. Compare matching Umbrella declarations
with actual vanilla invocations.

JavaDocs can include private members. Even a public Java method is insufficient
proof of Kahlua exposure. If needed, inspect installed LuaManager registration
and the specific class. A GlobalObject entry is a candidate Lua global: confirm
its exposed name rather than mechanically calling
`LuaManager.GlobalObject.someFunction(...)` from Lua.

Preserve observed `:` versus `.` calling conventions. Do not assume standard Lua
features, native modules, or LuaJIT support without checking the game's Kahlua
environment. Annotations do not change runtime availability.
Use [source discovery](source-discovery.md) for matching evidence.

## Collections and lifetime

Distinguish Lua tables, Java lists, arrays, iterators, and other collections.
A verified Java List-like value commonly uses `size()` and zero-based `get(index)`;
`#value` and `ipairs` are not substitutes. Do not generalize to maps/sets. Avoid
removing elements during forward iteration unless the concrete API permits it.

Players, items, containers, or world objects captured by delayed callbacks can
disappear or change ownership. Revalidate at use time and reacquire through
verified identifiers across context or save/load boundaries.

## Event contracts

Look up the exact event in
[PZEventDoc](https://github.com/demiurgeQuantified/PZEventDoc/blob/develop/docs/Events.md)
and a matching trigger site. Record argument order/types, nil cases, side,
frequency, and lifecycle. A player parameter may be an index rather than an
`IsoPlayer`; use the documented conversion.

Keep a named callback reference when removal is needed. Register once per
intended lifecycle and account for reloads. Namespace handlers, filter relevant
objects/commands early, and avoid full-world scans on frequent events.
Do not mask load errors with broad protected calls.

Events, Hooks, recipe callbacks, and overrides have different registration and
return contracts. Use the mechanism demonstrated by the target source.

For example, PZEventDoc documents `OnClientCommand(module, command, player, args)`
on the server and allows nil `args`. Revalidate for the target before implementing.
The callback's player is the sender; an ID inside supplied arguments is not a
replacement.
