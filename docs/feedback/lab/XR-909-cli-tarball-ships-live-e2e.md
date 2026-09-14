# XR-909 — `@call-e/cli@0.5.1` tarball ships `scripts/live-e2e.mjs --call`; published README links off-package

## Finding

`npm pack @call-e/cli@0.5.1` includes `scripts/` because `files` is `README, bin, docs, lib, scripts`. That directory contains `live-e2e.mjs`, which places a real call when invoked with `--call` and `CALLE_CLI_LIVE_TO_PHONE`. The published README’s first install link is `../../docs/install/cli.md` — that path does not exist inside the tarball (it only works in the monorepo). No `postinstall`. Telemetry defaults on, documented, opt-out `DO_NOT_TRACK=1` / `CALLE_TELEMETRY=0` / `--no-telemetry` (clean; not this card). attw: “This package does not contain types.” publint: clean. Git tag `@call-e/cli@0.5.1` matches `--version 0.5.1`.

## Surface / version / commit or URL

- npm `@call-e/cli@0.5.1` (15 files)
- `package/scripts/live-e2e.mjs` lines 27–31, 452
- `package/README.md` line 11

## Expected

Published `files` is `bin` + `lib` + `docs` (reference). Live e2e stays in the git repo. README links are in-tarball (`docs/cli-reference.md`) or absolute https URLs.

## Actual

**Observed** tarball contents include:

```text
package/scripts/live-e2e.mjs
package/scripts/run-agent-command.mjs
```

**Observed** `live-e2e.mjs`:

```javascript
const shouldRunCall = process.argv.includes("--call");
const toPhone = env.CALLE_CLI_LIVE_TO_PHONE;
// ...
throw new Error("CALLE_CLI_LIVE_TO_PHONE is required");
```

`package.json` scripts: `"verify:live:call": "node ./scripts/live-e2e.mjs --call"`.

**Observed** README: `[docs/install/cli.md](../../docs/install/cli.md)` — `../../` walks out of `node_modules/@call-e/cli`.

No `postinstall` / `preinstall` in the published `package.json`.

## Evidence

`npm pack @call-e/cli@0.5.1` under `/tmp/calle-lab/pkg/cli/`. `--version` → `0.5.1` exit 0. Telemetry destination is `<base-url>/api/ui-telemetry/track` (documented).

## Impact if an operator or agent trusted the current contract

An agent exploring `node_modules/@call-e/cli/scripts` can run the packaged e2e with `--call` against a cached login. The broken README link sends a fresh install to a 404, so they skip the “never use bare `calle`” page (XR-606 / XR-701).

## Ask

Remove `scripts` from `files` (keep `run-agent-command.mjs` only if skills require it, and document that). Rewrite the README install href to `https://github.com/CALLE-AI/call-e-integrations/blob/main/docs/install/cli.md`.

## Do not claim

That `live-e2e --call` was executed. Telemetry as a new leak (payload is documented; opt-out works). Refile of XR-701.
