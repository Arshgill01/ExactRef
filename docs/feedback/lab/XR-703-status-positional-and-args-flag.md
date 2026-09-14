# XR-703 — `call status <id>` and `mcp call --args` are the flags agents actually type

## Finding

The natural CLI shapes `calle call status <run_id>` and `calle mcp call <tool> --args '<json>'` are rejected. Status requires `--run-id`. MCP invoke requires `--args-json`. The user-facing task prompt and many agent templates still use the rejected spellings. Exit 2, no MCP round-trip.

## Surface / version / commit or URL

- `@call-e/cli@0.5.1`
- Leaf help: `calle call status --run-id <id>`; `calle mcp call <tool-name> --args-json <json>`
- This lab’s own experiment brief used `--args` (the flag the CLI does not accept)

## Expected

Either accept a single positional run id and `--args` as an alias, or have every public prompt/skill/README use only `--run-id` / `--args-json`.

## Actual

Observed:

```text
npx -y @call-e/cli call status not-a-real-id
# invalid_arguments  Unexpected arguments: not-a-real-id
# help_argv: ["call","status","--help"]  EXIT:2

npx -y @call-e/cli call status
# Missing required --run-id  EXIT:2

npx -y @call-e/cli mcp call plan_call --args '{"user_input":"x"}'
# Unknown option: --args  EXIT:2

npx -y @call-e/cli mcp call
# Usage: calle mcp call <tool-name> --args-json '<json>'  EXIT:2
```

JSON is written to stdout and a human line to stderr on each of these. `--json` does not change the shape.

## Evidence

Commands above. `assertNoUnexpectedPositional` in `cli.js`. MCP option set is exactly `args-json` and `timezone` (`"mcp call": new Set(["args-json", "timezone"])`).

## Impact if an operator or agent trusted the current contract

A fresh agent that copies `calle call status $RUN_ID` or `mcp call plan_call --args '…'` never reaches the server. It then “fixes” the command by guessing `--phone` (also rejected; see XR-709) or by calling `run_call` again. The `--args` spelling is the one this lab was told to use.

## Ask

Accept one positional as `--run-id` on `call status`, and accept `--args` as an alias of `--args-json`. Mirror both in `--help`.

## Do not claim

That `--args-json` is undocumented (help and `cli-reference.md` name it). A live status of a real run. XR-003.
