---
name: project-zomboid-modding
description: Develop, debug, and migrate Project Zomboid mods using version-matched vanilla code and verified Lua/Java APIs. Use for PZ Lua, events, script definitions, crafting, UI, timed actions, multiplayer, and persistence, with Build 42 as the default target.
license: MIT
metadata:
  author: EremesNG
  version: "1.0.0"
  repository: https://github.com/EremesNG/skills
---

# Project Zomboid Modding

Build mods from evidence for the target game version. Prefer a small verified
implementation over a plausible API assembled from memory. Respond in the user's
language; preserve the project's naming and formatting conventions.

## Establish the target

Inspect the existing mod, dependencies, and available game installation. Record
the exact game version/branch, game path, and intended single-player, hosted MP,
or dedicated-server support. Default to Build 42 Stable for a new project; an
explicit version or existing compatibility contract wins. Do not silently migrate
B41 or freeze the current stable patch into a permanent requirement.

Use the running game's version/log and installation evidence. A Steam build ID,
folder called `42`, or documentation version alone does not prove the installed
patch. If unavailable, say **target version unverified**, continue independent
work, and request only missing evidence that blocks implementation.

## Resolve the API before implementing

Read [source discovery](references/source-discovery.md) when finding a source,
investigating an unknown symbol, or resolving conflicting versions.

- Start with the closest equivalent in installed `media/lua` or `media/scripts`.
  Follow helpers and the owning client/server/shared context.
- Use matching Umbrella stubs for types/inheritance, PZEventDoc for events, and
  pz-scripts-data/PZ API Docs for script fields. Check their target versions.
- JavaDocs include internal members. Require evidence of Lua exposure for Lua
  calls; inspect the matching engine when material behavior remains unclear.
- Context7 is optional. Missing tools, stale indexes, and absent installations
  are limitations, not reasons to invent signatures or claim runtime validation.
- Record non-obvious symbols, signatures, execution sides, source paths/URLs, and
  source versions/revisions. A negative search does not prove absence. Resolve
  meaningful source conflicts before relying on a contract.

## Load only the relevant guidance

| Task | Reference |
| --- | --- |
| Locate vanilla, stubs, docs, version evidence, or engine implementation | [Source discovery](references/source-discovery.md) |
| Lua/Java calls, collections, events, callback contracts | [Lua bridge and events](references/lua-bridge-events.md) |
| New mod, B41 migration, loading, sandbox options, distribution | [Mod structure](references/mod-structure.md) |
| Items, craftRecipe, translations, inventory or ISO world interaction | [Scripts, items, and world](references/scripts-items-world.md) |
| ISUI, context menus, timed actions | [UI and timed actions](references/ui-timed-actions.md) |
| Commands, authority, ModData, saves, multiplayer | [Multiplayer and persistence](references/multiplayer-persistence.md) |
| Reproduction, logs, regression checks, runtime limitations | [Debugging and testing](references/debugging-testing.md) |

## Implement proportionally

Preserve the requested feature and compatibility scope. For MP gameplay changes,
choose authoritative ownership before client UI. Do not add networking to purely
local visuals or a deliberately single-player-only mod. Namespace identifiers;
prefer verified extension points over broad vanilla overrides.

Derive examples from target sources, retaining attribution when reusing code.
Do not ship Umbrella stubs as runtime code or vendor game/decompiled sources.
Avoid importing an example mod's library dependency accidentally.

## Verify and report

Use [debugging and testing](references/debugging-testing.md). Separate source
inspection, static checks, and actual in-game results. Single-player loading
does not establish MP compatibility.

Return implemented behavior, affected files, target version, decisive API/event
evidence, checks performed, and runtime gaps. For an unknown contract, identify
what must be inspected instead of presenting guessed code as ready to run.
