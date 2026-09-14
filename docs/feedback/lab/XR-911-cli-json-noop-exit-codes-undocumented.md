# XR-911 — Every `--help` lists `--json`; it is a no-op; exit codes 0/1/2 are undocumented; `auth status` has no `ok`

## Finding

Leaf `--help` prints `Global options` including `--json` with no explanation. `docs/cli-reference.md` says `--json` is “Accepted for compatibility. Successful command stdout is already JSON.” The parser never reads `options.json`. Skills tell agents to “check `ok`”. Successful `auth status` (usable token) and `mcp config` / `regions list` emit JSON **without** an `ok` key. Invalid usage is exit **2** + `ok: false`; `--help` / `--version` are exit **0**. The reference never defines 0/1/2. `calle help` is unknown (exit 2) — noted in ROLLUP-grok-ts, not refiled.

## Surface / version / commit or URL

- `@call-e/cli@0.5.1` `lib/cli.js` (`COMMON_HELP` lists `--json`; no `options.json` read)
- `docs/cli-reference.md` JSON / `--json` row; **zero** “exit code” hits
- Skills: check `ok` on CLI JSON (lead rollup noted the no-token case; this adds the **usable-token** case)

## Expected

`--help` either omits `--json` or says “no-op; stdout is already JSON.” Every success envelope includes `ok: true`. A short “Exit codes: 0 success, 1 runtime/MCP, 2 usage” table in the reference and in root help.

## Actual

**Observed** `calle auth status --json` (usable cache, exit 0):

```json
{
  "server_url": "https://seleven-mcp-sg.airudder.com/mcp/openagent_oauth",
  "cache_exists": true,
  "usable": true,
  "expires_at": "2029-05-15T16:40:46.011723Z"
}
```

No `ok`. Same shape without `--json`.

**Observed** exits (MCP CLI):

| argv | exit | `ok` |
|---|---|---|
| `--help` / `--version` | 0 | n/a (text) |
| `auth status` (usable) | 0 | **absent** |
| `notacommand` / missing `--run-id` | 2 | false |
| `call status --run-id not-a-real-id` | 0 | true (XR-704) |

SDK `@call-e/calle` CLI: `--version` is `Unknown option` exit **1** (XR-913). `--json` there actually dumps JSON.

## Evidence

`node /tmp/calle-lab/pkg/cli/package/bin/calle.js` with `CALLE_TELEMETRY=0`. `rg options.json lib/cli.js` → no matches.

## Impact if an operator or agent trusted the current contract

A skill that gates on `ok` will treat a healthy login as failure and start `auth login` again (or refuse to plan). Scripts that assume `--json` changes output, or that any JSON on stdout is exit 0 meaning “call succeeded,” already collide with XR-109 / XR-704.

## Ask

Add `ok: true` to `auth status`, `mcp config`, `mcp tools`, and `regions list`. Document 0/1/2 in root `--help` and `cli-reference.md`. Change the `--json` help line to “no-op (stdout is JSON)”.

## Do not claim

Refile of XR-702 (globals **before** the command). XR-109 (create --wait exit 0 on failed **call**). That `--json` after a valid command errors (it does not).
