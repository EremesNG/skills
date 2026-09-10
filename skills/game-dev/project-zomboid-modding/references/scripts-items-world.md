# Scripts, items, and world interaction

## Script definitions and B42 crafting

Find the nearest vanilla definition and its callbacks. Consult matching
[PZ API Docs](https://pz-wiki-modding.github.io/PZ-API-Docs/) and
[pz-scripts-data](https://github.com/PZ-Wiki-Modding/pz-scripts-data).
Check property casing, value types, separators, namespaces, defaults, and
references. Documentation YAML is not the game's script syntax.

For `craftRecipe`, verify input consumption/retention and quantities, outputs,
tools, learning/skill conditions, time, category, and callbacks from the target.
Derive field syntax from those sources rather than a guessed universal template.
Legacy `recipe` migration is a semantic change.

The [craftRecipe reference](https://github.com/PZ-Wiki-Modding/PZ-API-Docs/blob/main/docs/source/scripts/craftrecipe.rst)
documents `OnCreate`, `OnTest`, `OnFailed`, and `OnUpdate`; they do not necessarily
share arguments. Its documented `OnCreate` uses `CraftRecipeData` and a character,
unlike common older examples. Verify named callbacks are reachable when resolved,
including global namespace and load order. Local-only functions are insufficient
for string-resolved callbacks.

Avoid applying an effect both through outputs and a Lua callback. Test success,
invalid inputs, interruption, and batch/repeat behavior as relevant; verify
consumed quantities and retained tools, not just recipe visibility.

Translations now have a separate
[dataset](https://github.com/PZ-Wiki-Modding/pz-translation-data).
Verify target filenames, keys, encoding, and namespaces. Use translation keys
rather than embedding UI text in gameplay logic.

## Items and inventory

Distinguish script definitions, runtime `InventoryItem`, containing inventory,
and dropped world representations. Verify fully qualified types and creation,
consumption, transfer, and removal behavior. An inventory change and displayed
count are different observations.

For delayed actions, revalidate possession, quantity, condition, and destination
capacity at commit. Follow target vanilla replication for mutations; a custom
notification does not ensure remote inventory consistency.

## World and ISO objects

Resolve `IsoObject` and `IsoGridSquare` through verified selection/lookup APIs.
One square may hold several objects; coordinates alone may not identify the
target. Validate type, continued existence, distance/access, and square availability.
A client-supplied object index is not permanent identity across network delays.

Inspect vanilla creation/removal lifecycle and replication, including separate
sprite, collision, and persistence updates where applicable. A texture change
does not necessarily create a working gameplay object. Load
[MP guidance](multiplayer-persistence.md) for shared mutations.
