# Debugging and testing

## Reproduce

Record game version/branch, mod revision, dependencies, mode, save origin, and
steps. Inspect the first relevant error/stack trace in the actual client or server
log; later nil errors can result from an earlier load failure. Locate logs from
the active configuration rather than assuming a fixed path.

Distinguish package discovery, script parsing, Lua load order, wrong-side execution,
API mismatch, and gameplay logic. Confirm expected files loaded once before broad
instrumentation. Remove noisy per-tick logging after diagnosis.

## Verify at the available level

| Level | Useful checks | Does not prove |
| --- | --- | --- |
| Package | Content root, IDs, dependencies, asset case, duplicate copies | Correct execution |
| Static | Matching Umbrella diagnostics, supported syntax, script references | Kahlua exposure or MP correctness |
| Source | Vanilla call, event contract, callback side, engine behavior | Actual execution of the mod |
| In-game | Activate, trigger, inspect logs/resulting state | Other modes or versions |
| Multiplayer | Dedicated server and two clients as relevant, rejection, remote state | Save/reconnect correctness unless exercised |
| Persistence | Reload, restart, reconnect, copied-save migration | Untested legacy saves |

Reuse existing harnesses for pure Lua logic when useful. Mocked PZ APIs do not
validate real signatures, serialization, replication, or timing. A standard Lua
parser is not a PZ runtime. Do not install a game/IDE just for a documentation check.

For crafting, test consumption, retained tools, outputs, cancellation, and batches.
For actions, test interruption and one commit. For commands, test nil/malformed
arguments, invalid targets, and repeated requests. Select cases for the change,
not a universal checklist for every cosmetic edit.

Use a disposable world with minimal mods to isolate conflicts, then the intended
dependency set. Do not overwrite real saves. Follow task authorization before
deployment or starting external services.

## Report precisely

Include a compact verification record in the delivery or existing project notes:

```text
Target: exact build/mode and source of version evidence
Contract: symbol/event, signature, execution side
Evidence: actual path + line or URL + revision/version
Checks: performed source/static/runtime checks and results
Pending: missing runtime/mode, unresolved API, next verification step
```

Without the game, deliver source-grounded work where possible and concrete manual
test steps. Mark runtime verification pending. Never fabricate vanilla paths,
successful launches, or verification claims for sources only suggested in research.
