# XR-702 — Global flags before the command are parsed as the command name

## Finding

Top-level help advertises “Global options (accepted by every command)” including `--json` and `--no-telemetry`. The parser takes `argv[0]`/`argv[1]` as `group`/`command` **before** options. Putting a documented global flag first yields `Unknown command: --json auth` (exit 2). Agents that write `calle --json …` the way they write `git --no-pager …` never reach the subcommand.

## Surface / version / commit or URL

- `@call-e/cli@0.5.1` (`npx -y @call-e/cli --version` → `0.5.1`)
- `packages/cli/lib/cli.js` `runCliCommand`: `const [group, command, ...rest] = argv` then `parseOptions(rest)` (integrations `1ce9d77`)
- Help text on every leaf: “Global options (accepted by every command)”

## Expected

Flags listed as global are stripped regardless of position, or help says they must follow `group subcommand`. `calle --json auth status` equals `calle auth status --json`.

## Actual

Observed:

```text
npx -y @call-e/cli --json auth status --no-telemetry
# Unknown command: --json auth   EXIT:2

npx -y @call-e/cli --no-telemetry auth status --json
# Unknown command: --no-telemetry auth   EXIT:2

npx -y @call-e/cli --json
# Unknown command: --json   EXIT:2

npx -y @call-e/cli notacommand --json
# Unknown command: notacommand --json   EXIT:2
```

`--json` after a valid command works (`calle auth status --json` exit 0). `--json` is also documented as a no-op (“Accepted for compatibility. Successful command stdout is already JSON”).

## Evidence

Commands above. Parser:

```javascript
const [group, command, ...rest] = argv;
const { options, positional, optionNames } = parseOptions(rest);
// …
throw new InvalidArgumentsError(`Unknown command: ${[group, command].filter(Boolean).join(" ")}`);
```

`--help` / `-h` are special-cased **anywhere** in argv (`argv.includes("--help")`) and therefore work in any position. Other globals do not.

## Impact if an operator or agent trusted the current contract

A script or agent that prefixes `--json` or `--no-telemetry` (or copies Unix-style `tool --flag command`) gets a usage error. Combined with XR-701, `npx @call-e/cli --json call status --run-id …` never queries the run. `--json` on an unknown command is swallowed into the command name, so the error message is wrong.

## Ask

Parse known global flags from the full argv before resolving `group`/`command`, matching `--help`. Or delete “accepted by every command” and print “place globals after the subcommand.”

## Do not claim

That `--json` changes success payloads (docs already say it does not). A live call. XR-003 (`ok: true` on `isError`).
