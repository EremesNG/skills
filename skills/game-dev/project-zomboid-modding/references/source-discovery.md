# Source discovery and version evidence

## Select evidence by question

| Question | Preferred evidence | Limit |
| --- | --- | --- |
| What does this installation do? | Its vanilla Lua/scripts and matching engine classes | Mirrors and other installations can differ |
| Can Lua call this, with which types? | Matching Umbrella, vanilla call, bridge registration as needed | Stubs can lag; Java visibility is not Lua exposure |
| Where/when does an event run? | Matching PZEventDoc and trigger site | Generated analysis needs review |
| Which script fields/callback shape? | Matching vanilla, pz-scripts-data, PZ API Docs | Defaults and syntax vary by version |
| How might a feature be organized? | Vanilla patterns, then licensed example mods | Mods may depend on private libraries or older APIs |

The exact running installation wins a conflict about runtime behavior. An
observed call does not establish every overload or execution context. Retain
the origin/version of decompiled input; bytecode or runtime evidence resolves
material ambiguity caused by decompiler reconstruction.

## Local discovery

Prefer an explicit game path. Otherwise inspect project configuration and known
Steam libraries, including `steamapps/libraryfolders.vdf` if present. Do not assume
the first library or a Windows path. Locate `media/lua`, `media/scripts`, and actual
JAR/class locations; not every installation must use one `projectzomboid.jar`.
Do not scan an entire disk by default.

These PowerShell examples are read-only; set paths to existing local checkouts:

```powershell
$pzGame = 'D:\SteamLibrary\steamapps\common\ProjectZomboid'
$pzUmbrella = 'D:\modding-tools\Umbrella'
rg -n -F 'sendClientCommand' "$pzGame/media/lua"
rg --files "$pzGame/media/lua" -g '*TimedAction*' -g '*ContextMenu*'
rg -n 'IsoPlayer|IsoGameCharacter' "$pzUmbrella/library" -g '*.lua'
rg -n -F 'craftRecipe' "$pzGame/media/scripts" -g '*.txt'
```

Inspect bounded surrounding code, then follow helper definitions. Use an available
equivalent if `rg` is absent. Correlate a recent startup log or displayed version
with the intended installation/session. Steam build IDs are not PZ semantic versions.

## Source directory

Consulted on 2026-09-10. These locations do not guarantee version alignment.
Pin the revision used when implementing a mod.

- [Official release information](https://projectzomboid.com/blog/news/2026/07/project-zomboid-build-42-20-released/): announced B42 Stable; the header reported 42.20.4 when checked. Recheck when choosing a target.
- [Umbrella](https://github.com/PZ-Umbrella/Umbrella): EmmyLua API stubs; its README covers EmmyLua and LuaLS setup. Match release/branch and keep stubs out of deployed Lua.
- [PZEventDoc](https://github.com/demiurgeQuantified/PZEventDoc) and [event contracts](https://github.com/demiurgeQuantified/PZEventDoc/blob/develop/docs/Events.md): arguments and contexts. Optional `--game_path` analysis inspects installed code but explicitly needs human review. Read current requirements and CLI help first.
- [PZ API Docs](https://pz-wiki-modding.github.io/PZ-API-Docs/) and [pz-scripts-data](https://github.com/PZ-Wiki-Modding/pz-scripts-data): generated docs and structured script data. The docs identified 42.20.2 when checked; “B42” alone is insufficient version evidence.
- [pz-translation-data](https://github.com/PZ-Wiki-Modding/pz-translation-data): translations are now maintained separately; scripts-data marks its old translation data deprecated.
- [Official JavaDocs](https://projectzomboid.com/modding/) and [LuaManager.GlobalObject](https://projectzomboid.com/modding/zombie/Lua/LuaManager.GlobalObject.html): Java signatures and candidate Lua globals; still check exposure/version.
- [Vanilla Lua mirror](https://github.com/Project-Zomboid-Community-Modding/ProjectZomboid-Vanilla-Lua): fallback without local sources. Verify branch/revision and label mirror evidence.
- [ZomboidDecompiler](https://github.com/demiurgeQuantified/ZomboidDecompiler): inspect its compatibility table and CLI help for the installed build. Use isolated output, record input origin, and inspect needed classes. Do not redistribute game code.

## Optional indexed discovery

If Context7 tools are exposed, resolve the library dynamically and inspect its
metadata before querying. Candidate IDs from prior research:

```text
/websites/pzwiki_net_wiki
/demiurgequantified/projectzomboidjavadocs
/websites/demiurgequantified_github_io_projectzomboidluadocs
/demiurgequantified/pzeventdoc
```

These IDs were not independently validated when creating this skill. Do not
assume availability or stable snippet counts. Query the exact symbol/version,
follow the underlying source, and compare with local evidence. If unavailable,
use direct sources or local checkouts; no MCP installation is required.

For architecture examples, prior research identifies
[StarlitLibrary](https://github.com/demiurgeQuantified/StarlitLibrary),
[HorseMod](https://github.com/PZ-HorseTeam/HorseMod),
[ChaosMod](https://github.com/clixff/ChaosMod-ProjectZomboid), and
[project-zomboid-mod-toolkit](https://github.com/drandarov-io/project-zomboid-mod-toolkit).
Inspect revision, license, and dependencies before reuse. These are discovery
leads, not API authority. Never execute a deployment helper just to read its layout.
