# UI, context menus, and timed actions

## ISUI and menus

Find a current vanilla ISUI class with the closest lifecycle. Follow creation,
initialization, controls, render/update, and cleanup; JavaDocs are not constructor
authority for Lua-defined classes. Keep UI client-side. Check scaling, translated
text width, and intended controller/split-screen support.

Look up `OnFillInventoryObjectContextMenu` or `OnFillWorldObjectContextMenu` in
[PZEventDoc](https://github.com/demiurgeQuantified/PZEventDoc/blob/develop/docs/Events.md)
and the matching vanilla menu. Confirm selection wrappers/stacks versus actual
items and any test/probe invocation. Building a menu must not consume items,
change world state, or send gameplay commands. Revalidate on click.

Use the event's player context rather than assuming player zero. Avoid duplicate
options for selections representing one operation. Visual eligibility does not
replace authoritative validation when the operation executes.

## Timed actions

Inspect installed `ISBaseTimedAction` and a nearby concrete action. Trace queue
insertion, validity, start/update, interruption, and completion. B42 lifecycle and
MP behavior can differ from B41: inspect any `perform`, `complete`, and duration
methods in that target instead of copying old mutation code into `perform`.

Identify presentation, authoritative mutation, and cancellation ownership.
Recheck item/world validity at commit. Preserve required base-class calls and
ordering from the verified pattern so the queue progresses and cleanup runs.

Do not combine a custom command mutation with engine-authoritative completion
that already performs it. One successful action should have one state-changing
commit. Prefer existing target synchronization when sufficient.

Test interruption, disappearing targets, repeated enqueue, and completion. For
MP, check remote observation/reconnect where relevant. Static inheritance checks
do not establish lifecycle correctness.

Use [source discovery](source-discovery.md) for vanilla and stubs and
[multiplayer and persistence](multiplayer-persistence.md) for shared changes.
