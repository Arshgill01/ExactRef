# XR-912 — `calle call plan` hard-requires `--to-phone`; MCP `plan_call` does not

## Finding

Live `plan_call` accepts a planning-only request with no `to_phones` (`ready_to_run: false`, `confirm_token: null`). The CLI help says `--to-phone` is **Required** and `handleCallCommand` throws `Missing required --to-phone` when the list is empty. Agents that follow `calle call plan --help` cannot dry-run a plan. They must either invent a number (XR-707) or switch to `mcp call plan_call` (which the same help page does not mention).

## Surface / version / commit or URL

- `@call-e/cli@0.5.1` `lib/cli.js` usage string + `if (toPhones.length === 0) throw ... "Missing required --to-phone"`
- Live `plan_call` 2026-09-14, arguments `{ "goal": "XR-9xx packaging lab planning-only; do not dial." }` only

## Expected

`calle call plan --goal "..."` without `--to-phone` is a supported planning-only path, matching the MCP tool (`to_phones` default null). Help says “optional until ready to run.”

## Actual

**Observed** CLI:

```text
Usage: calle call plan --to-phone <phone> --goal <text> [options]
  --to-phone <phone>            Required; repeat once per destination phone number
```

```text
calle call plan --goal "planning only"
→ exit 2
{"ok":false,"error":{"code":"invalid_arguments","message":"Missing required --to-phone"}}
```

**Observed** MCP (no phone, 14969 ms, HTTP 200): `ready_to_run: false`, `confirm_token: null`, `next_step` string directing the user to the plan card (plan id redacted). No dial.

## Evidence

`calle call plan --help`; live JSON-RPC `tools/call` `plan_call` without `to_phones`. Token not printed.

## Impact if an operator or agent trusted the current contract

The CLI-shaped path always sends a destination into `plan_call`. Combined with XR-707 (national numbers accepted) this is how a “just plan it” agent still asserts a recipient. The safe planning-only contract exists only on the raw tool.

## Ask

Make `--to-phone` optional on `call plan` (keep it required on `call start`). Add a help example: `calle call plan --goal "…"`.

## Do not claim

Refile of XR-201 (`user_input` omitted by the CLI mapper) or XR-707 (national number guess). That `call start` should allow a missing phone.
