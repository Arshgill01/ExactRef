# XR-604 — `call plan` prints the execution credential to stdout; skills say “never surface it,” but every skill routes stdout to the model

New. 2026-09-14. Complements XR-403 (in-band confirm is not a second channel) with a concrete handling defect. Not XR-403 refiled.

## Finding

`confirm_token` is the value that turns a plan into a dial: `run_call` requires it and the guide calls it “the execution handshake.” The CLI's `call plan` returns the raw token in `result.structuredContent.confirm_token` and again in the `result.content[0].text` JSON blob, printed to stdout with no `--redact` option. The Cursor/Codex/Claude/OpenClaw/skills.sh skills tell the agent to run `call plan`, read the JSON, and then: “Do not display the confirm_token or any raw token to the user.” The same skills also say “Never run `call start` … without asking the user” — while the token that lets `call start` run is already sitting in the agent's context, in the terminal scrollback, in any chat/tool log that captures shell output, and in the Cursor agent transcript.

The sanctioned safe path (`call start` does plan → confirm → run internally) never needs the token in stdout. The token leak exists only for the “plan first, then confirm” path the skills recommend.

## Surface / version / commit or URL

- `@call-e/cli@0.5.1`, offline harness against a fake MCP server: `call plan --json` output keys
- Live `plan_call` (no phone, planning only): `confirm_token: null` — the field is emitted at the top level of `structuredContent`; a ready plan fills it (schema: `confirm_token` string, “Include it in `run_call`”)
- `call-e-integrations` `1ce9d77`:
  - `skills/calle/SKILL.md` (“Do not display the confirm_token or any raw token”; same sentence in `packages/cursor-plugin/plugin/skills/calle/SKILL.md`, codex, claude, openclaw)
  - `packages/cli/lib/cli.js` `call plan` → `emitJson(result)` unfiltered
  - `docs/mcp/openagent-oauth.md` 156–158 (`confirm_token` semantics)
- Prior art the vendor already shipped: `auth status` deliberately omits the bearer token; `auth token --show` is the opt-in reveal

## Expected

`call plan` behaves like `auth status`: return `plan_id`, `ready_to_run`, `missing_fields`, `display_goal`, `confirm_expires_at`, `has_confirm_token: true`; hide the token by default; `call plan --show-confirm-token` (or `call start --plan-id`) for the rare manual path. Skills stop asking the model to hold a credential it is told not to show.

## Actual

Offline probe: shipped `@call-e/cli@0.5.1` `runCli` against a fake Streamable-HTTP MCP server whose `plan_call` returns `confirm_token: "confirm-SECRET-1"`:

```text
[call plan] exit 0  stdout contains confirm_token value: true
```

The value is present in `result.structuredContent.confirm_token` and again inside `result.content[0].text`. No flag on `call plan` suppresses either.

Skill text (all five):

```text
Do not display the confirm_token or any raw token to the user.
```

The agent is the one entity that reads stdout. “Do not display” is enforceable only by the agent's discretion.

## Evidence

- `/tmp/calle-lab/tslab/cli_probe.mjs` `[call plan]` case (token present twice in stdout; run 2026-09-14)
- `/tmp/calle-lab/mcp-tools-pretty.json` (`plan_call.outputSchema.confirm_token`)
- Grep on `1ce9d77` for “Do not display the confirm_token”

No live `run_call`. No live token stored or printed in this lab (planning call had `confirm_token: null`).

## Impact if an operator or agent trusted the current contract

The credential that authorizes a phone call to a third party is routinely logged wherever tool output is logged. Anyone with the plan_id + token + a valid session can `run_call` before `confirm_expires_at`. Also a design contradiction that judges will notice: the skill asks the model to hide something the CLI hands it in plain text.

## Ask

Redact `confirm_token` from `call plan` stdout by default; add a `has_confirm_token` boolean and an opt-in reveal flag; have `call start --plan-id <id>` fetch confirmation server-side. Update the skills to say the token is not printed.

## Do not claim

A live `confirm_token` value. That the token is reusable after `run_call` (not tested). XR-403 as this card. Refile of 109/123/126/127.
