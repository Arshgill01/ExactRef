# XR-913 — `@call-e/calle` CLI has no `--version` (exit 1); `--help` documents `--json` as a real flag

## Finding

The SDK binary (`@call-e/calle@0.7.0` `dist/cli.js`, also named `calle`) rejects `--version` / `-V` as `Unknown option` (exit 1) and prints REST usage. Its `--json` **does** change output (full response object). The MCP CLI (`@call-e/cli@0.5.1`) implements `--version` → `0.5.1` and treats `--json` as a no-op (XR-911). An agent that “checks `calle --version` before calling” gets exit 1 when PATH resolved the SDK (XR-701), then proceeds as if the CLI is broken.

## Surface / version / commit or URL

- `npx --package=@call-e/calle@0.7.0 calle --version` 2026-09-14
- SDK `--help` text (no `--version` line)
- MCP CLI `--version` / `-V` → `0.5.1` exit 0

## Expected

Both bins that install as `calle` accept `--version` and print their package version, **or** the SDK bin is renamed (`calle-sdk`). `--json` means the same thing on both.

## Actual

**Observed**

```text
npx --package=@call-e/calle@0.7.0 calle --version
Unknown option: --version
# exit 1

npx --package=@call-e/calle@0.7.0 calle --help
Usage:
  calle calls create --task <text> [--phone <E164>] ...
  ...
  --json                      Print the full response object as JSON.
  --help                      Show this help.
```

MCP: `calle --version` → `0.5.1` exit 0. `calle --json` with no command is unknown-command exit 2 if `--json` is argv[0] (XR-702); `calle --help` exit 0.

## Evidence

Commands above. Distinct from “two packages install `calle`” (XR-701): this is the **flag surface** mismatch after the wrong binary is already selected.

## Impact if an operator or agent trusted the current contract

Version gates, `calle --version | awk` install checks, and “if --json then parse stdout” all disagree across the two bins. Exit 1 on `--version` looks like a crashed CLI.

## Ask

Add `--version` to the SDK CLI (print `0.7.0`). Or stop installing `bin.calle` from `@call-e/calle` (preferred; see XR-701). Align `--json` help text on both.

## Do not claim

Refile of XR-701 / issue 109 as this card. That the SDK `--json` is a no-op (it is not).
