# XR-201 — Dedicated `call plan` / `call start` omit `user_input`

## Finding

Official MCP and every skill that uses raw `plan_call` require the latest user message in `user_input`. The dedicated CLI path never sends that field. It sends only `--to-phone` → `to_phones` and `--goal` → `goal`.

## Surface / version / commit

- `call-e-integrations` `fix/mcp-call-tool-error` `f0c9cf5` and `origin/main` `4a53b01` (same `buildPlanArguments`)
- Official MCP guide: `docs/mcp/openagent-oauth.md` on `main`
- CLI help / reference: `calle mcp call` examples use `user_input`; `calle call plan` examples use `--goal`

## Expected

`plan_call` arguments from the CLI workflow include `user_input` verbatim, matching the published tool contract and the Cursor / Codex / Claude command templates.

## Actual

```javascript
// packages/cli/lib/cli.js — buildPlanArguments
const args = {
  to_phones: toPhones,
  goal: requireStringOption(options, "goal", "--goal"),
};
// language / region optional. No user_input. No ttl_seconds. No scheduled_at.
```

Existing unit test `call plan maps flags to plan_call arguments` asserts the wire object is `{ to_phones, goal, language, region }` plus `_meta`. No `user_input`.

Cursor fallback still tells the agent: if fields are incomplete, use `mcp call plan_call` with `user_input`. If fields look complete, use `call start` / `call plan` and drop the user message.

## Evidence (local / offline)

Fixture the existing test already uses (no network):

```json
{
  "name": "plan_call",
  "arguments": {
    "to_phones": ["<E164>"],
    "goal": "Confirm appointment"
  },
  "_meta": {
    "openai/userLocation": { "timezone": "Asia/Shanghai" },
    "timezone_offset_minutes": -480
  }
}
```

Contrast: official MCP “Important inputs” lists `user_input` first and says “Always preserve the user's latest message in `user_input`.” CLI reference example for `mcp call` is `--args-json '{"user_input":"Call Alex"}'`.

## Impact if an operator or agent trusted the current contract

Wrong call script, not a second dial by itself. Constraints that exist only in the user message (“do not leave a voicemail”, “ask for the off-hire reference, do not guess”) never reach the planner on the dedicated path. The planner can still return `ready_to_run` + `confirm_token`. `call start` then executes that thinner plan.

An agent that switches paths mid-flow (MCP `user_input` plan, then CLI `call run` with the returned token) also mixes two argument shapes for the same plan.

## Ask

Make `call plan` / `call start` send `user_input` (copy of `--goal` or a new flag). Document that `--goal` is not a substitute for `user_input`. Reject or warn when skills call `plan_call` without it.

## Do not claim

Schema required-ness of `user_input` on the live server (tools/list not captured this resume). Rate. Second live call. Refile of 126/127.
