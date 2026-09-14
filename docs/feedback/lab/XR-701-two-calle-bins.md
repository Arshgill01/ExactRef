# XR-701 — Two npm packages install the same `calle` binary

## Finding

`@call-e/cli@0.5.1` (MCP/agent workflow) and `@call-e/calle@0.7.0` (REST Calls/Goals SDK) both publish `bin.calle`. A mixed install, a global `calle` on PATH, or `npx calle` can invoke the SDK CLI when the skill/docs meant the MCP CLI, or the reverse. The two CLIs do not share a command tree, flag names, or ID space.

## Surface / version / commit or URL

- npm `@call-e/cli@0.5.1` tarball `package.json` `bin: { calle: ./bin/calle.js }`, `engines.node: >=22`
- npm `@call-e/calle@0.7.0` tarball `package.json` `bin: { calle: ./dist/cli.js }`, no `engines`
- Git SDK `2808e21` still ships the same bin name
- Skills already warn (`skills/calle/references/commands.md`); the packages still collide

## Expected

One `calle` on a machine means one product. If two packages must exist, they use different bin names (`calle` vs `calle-sdk`) so `npx` / PATH cannot swap them.

## Actual

Observed (2026-09-14):

```text
npx -y @call-e/cli --help
Usage: calle <command> [options]
Commands:
  auth login / mcp tools / call plan / call start / …

npx -y @call-e/calle --help
Usage:
  calle calls create --task <text> [--phone <E164>] [--wait]
  calle calls get <call_id>
  calle goals run --goal-id … --phone … --idempotency-key …
```

Both tarballs declare `"bin": { "calle": … }`.

## Evidence

Commands above, exit 0. npm pack of both packages. CLI reference itself: “Older SDK releases, including `@call-e/calle@0.7.0`, export the same `calle` command as `@call-e/cli`. Even `npx` can select the SDK binary.”

## Impact if an operator or agent trusted the current contract

An agent that follows the SDK README (`npx @call-e/calle@latest calls create --phone … --wait`) while a skill said `calle call start --to-phone` either fails with `Unknown command` or, if PATH already has the other binary, **places a real REST call** with `--phone` semantics (one recipient per flag; XR-108) instead of planning via MCP. The reverse path never logs in and never lists MCP tools.

## Ask

Publish the SDK CLI as `calle-sdk` (or drop the SDK bin). Keep `calle` exclusively on `@call-e/cli`. Until then, `npx` examples must use the full package name and a one-line “wrong binary” detector.

## Do not claim

That a specific host’s PATH is already corrupted. That `npx -y @call-e/cli` itself picked the SDK (it did not, when the package name was explicit). A second live call. Refile of XR-108 / XR-109 (SDK `--phone` / `--wait` behavior).
