# Mod structure, loading, and migration

Inspect a working mod and the target loader before scaffolding. Distinguish the
repository root, loadable mod root, and Workshop upload root. B42 uses versioned
mod layouts: verify `common` and version directories, `mod.info` placement, and
selection/merge rules for the patch. A folder called `42` does not establish
compatibility with every B42 patch. Do not nest an already-versioned mod again.

Within the selected content root, route `media/lua/client`, `server`, and `shared`
by runtime responsibility. Shared code can execute in more than one context;
putting a mutation there does not give it one authoritative owner. Shared
definitions should not assume UI availability. Use the appropriate
`media/scripts` root for definitions and preserve asset path case across hosts.

Verify mod ID, dependencies, metadata syntax, content root, and in-game activation
before debugging gameplay. Workshop IDs and mod IDs are distinct. Namespace script
modules and Lua names. Umbrella is editor tooling, not a runtime dependency.

For B41 migration, inventory loading, events, items, crafting callbacks, timed
actions, networking, and save data. Migrate the requested surface using B42
equivalents. Do not rename every `recipe` to `craftRecipe` without checking
semantics and remaining legacy support. Preserve explicit B41 compatibility
through verified version-specific code where requested.

For sandbox settings/options, find the target's definition, translation,
initialization, and access patterns. Distinguish built-in sandbox configuration
from third-party options libraries. Verify server/world settings versus local
preferences; do not invent an options API.

Inspect existing deployment scripts before use. Assemble and inspect a staged
package first. Follow task authorization for installation/publication; invoking
this skill does not authorize Workshop publication, overwriting an installed mod,
or replacing saves.

Use [source discovery](source-discovery.md) for matching evidence. The
[toolkit's layout notes](https://github.com/drandarov-io/project-zomboid-mod-toolkit/blob/master/MODDING.md)
are an operational lead to check against the installed loader; its deployment
script is not required.
