# XR-709 — MCP CLI rejects `--phone`; SDK CLI only has `--phone`

## Finding

The two `calle` binaries (XR-701) use different recipient flags. `@call-e/cli` `call plan` / `call start` require `--to-phone` and treat `--phone` as an unknown option (exit 2). `@call-e/calle` documents only `--phone`. An agent that reads the SDK README or the Calls guide and then runs the MCP CLI never plans. Distinct from XR-108 (what `--phone` means on the SDK CLI).

## Surface / version / commit or URL

- `@call-e/cli@0.5.1` `call plan --help`: `--to-phone` required, repeatable
- `@call-e/calle@0.7.0` `calle --help`: `--phone <number>  E.164. Repeatable.`
- MCP tool field: `to_phones`

## Expected

One flag name on both CLIs, or `--phone` accepted as an alias of `--to-phone` on the MCP CLI.

## Actual

```text
npx -y @call-e/cli call plan --phone +15551234567 --goal "x"
# Unknown option: --phone
# help_argv: ["call","plan","--help"]
# EXIT:2
```

SDK help (same machine, same `calle` name):

```text
calle calls create --task <text> [--phone <E164>] [--wait]
  --phone <number>            E.164 phone number. Repeatable.
```

## Evidence

Commands above, 2026-09-14. No network call was made for the MCP `--phone` attempt (server_url null).

## Impact if an operator or agent trusted the current contract

Docs.heycall-e.com / SDK README examples use `--phone`. Skills and MCP CLI use `--to-phone`. After XR-701 picks the wrong binary, the surviving binary still rejects the other flag. The agent “repairs” by inventing `--to` or by switching to `calls create` (a real REST create).

## Ask

Accept `--phone` as an alias of `--to-phone` on `@call-e/cli`, and mention `--to-phone` on the SDK CLI help as the MCP name. One sentence on the SDKs page: these are different CLIs.

## Do not claim

XR-108 (repeatable `--phone` starts N conversations). XR-201 (CLI plan omits `user_input`). A live create.
