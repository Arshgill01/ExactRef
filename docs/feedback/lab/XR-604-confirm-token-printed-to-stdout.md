# XR-604 — `call plan` prints the execution credential to stdout; the skill says “do not display … execution confirmation data that appears in planning-only output”

New. 2026-09-14 (quotes re-verified 21:50 IST against `1ce9d77`). Complements XR-403 (in-band confirm is not a second channel) with a concrete handling defect. Not XR-403 refiled.

## Finding

`confirm_token` is the value that turns a plan into a dial: `run_call` requires it and the guide calls the pair “the execution handshake.” The CLI's `call plan` returns the raw token in `result.structuredContent.confirm_token` and again inside `result.content[0].text`, printed to stdout with no redaction flag.

The skills.sh skill acknowledges the leak and asks the model to look away:

```text
skills/calle/SKILL.md:37-38
- Do not print, request, or expose access tokens or execution confirmation data.

skills/calle/references/commands.md:165-166
Do not display or reuse any execution confirmation data that appears in planning-only output.
```

“Execution confirmation data that appears in planning-only output” is `confirm_token` in `call plan` stdout. The model is the only reader of that stdout; the token is already in the agent context, the terminal scrollback, and any tool-call log before the rule can apply. The Cursor plugin's safety rule (`packages/cursor-plugin/plugin/rules/call-e-safety.mdc:14`) lists OAuth/bearer/refresh/access tokens as never-print; `confirm_token` is not in that list — it is only “preserve exactly.”

The vendor already ships the right pattern one command over: `auth status` reports `cache_path`, `usable`, `expires_at` and never the bearer token (observed 2026-09-14), and the recovery record keeps `plan_id` + `confirm_token` in a `0600` file — “they are not printed” (`cli-reference.md:188–189`). `call plan` is the one path that prints it.

## Surface / version / commit or URL

- `@call-e/cli@0.5.1` offline harness (`runCli` + fake Streamable-HTTP MCP server): `call plan --json` output
- Live `plan_call` 2026-09-14 (planning only, `ready_to_run: false`): `confirm_token: null` emitted at the top level of `structuredContent`; live schema says a ready plan fills it (“Include it in `run_call`”)
- `call-e-integrations` `1ce9d77`: `skills/calle/SKILL.md:37–38`, `skills/calle/references/commands.md:165–166`, `packages/cursor-plugin/plugin/rules/call-e-safety.mdc:12–14`, `packages/cli/docs/cli-reference.md:188–189`, `packages/cli/lib/cli.js` `call plan` → `emitJson(result)` unfiltered
- Guide `docs/mcp/openagent-oauth.md:84` (“places or schedules a real call and the returned `plan_id` and `confirm_token`…”), `:282` (“Treat `plan_id`, `confirm_token`, and `run_id` as opaque values”)

## Expected

`call plan` behaves like `auth status`: returns `plan_id`, `ready_to_run`, `questions`, `display_goal`, `confirm_expires_at`, `has_confirm_token: true`; hides the token by default; `call plan --show-confirm-token` (or `call run --plan-id <id>` reading the private record) for the manual path. The skill rule becomes unnecessary.

## Actual

Offline probe, shipped 0.5.1, fake server returns `confirm_token: "confirm-SECRET-1"`:

```text
[call plan] exit 0  stdout contains confirm_token value: true
```

Present in `structuredContent.confirm_token` and in `content[0].text`. No flag on `call plan` suppresses either.

## Evidence

- `/tmp/calle-lab/tslab/cli_probe.mjs` `[call plan]` case (run 2026-09-14)
- `/tmp/calle-lab/mcp-tools-pretty.json` (`plan_call.outputSchema.confirm_token`)
- `/tmp/calle-lab/live2/plan_call_national.json` (`confirm_token: null` on a non-ready plan)
- Line-cited greps on `1ce9d77`

No live `run_call`. No live token value was produced or stored (planning calls were not ready).

## Impact if an operator or agent trusted the current contract

The credential that authorizes a phone call to a third party is logged wherever tool output is logged. Anyone with `plan_id` + `confirm_token` + a valid session can `run_call` before `confirm_expires_at`. The skill's wording confirms the vendor knows the value appears in planning output and chose a behavioural rule over redaction.

## Ask

Redact `confirm_token` from `call plan` stdout by default; add `has_confirm_token`; opt-in reveal flag; add `confirm_token` to the Cursor safety rule's never-print list until then.

## Do not claim

A live `confirm_token` value. That the token is reusable after `run_call` (not tested). XR-403 as this card. Refile of 109/123/126/127.
