# XR-712 — Four poll cadences for the same `get_call_run`

## Finding

The same status tool is documented with four incompatible timers. The live tool description says poll every 1–3 seconds. The official MCP guide says wait ~60s then 5–10s (or follow `next_step`). Shipped Cursor skill: wait 60s, then 5–10s. skills.sh skill: poll every 10 seconds from the first status. None of these is a hangup (XR-504); they are **how hard an agent hits the API** and **when it first speaks**.

## Surface / version / commit or URL

- Live `get_call_run.description` (`mcp tools --json` 2026-09-14)
- https://github.com/CALLE-AI/call-e-integrations/blob/main/docs/mcp/openagent-oauth.md “Reliable terminal-state workflow”
- Cursor skill 0.1.2 steps 6–7 (`1ce9d77`)
- skills.sh / `skills/calle/SKILL.md` call flow step 7 (poll every 10 seconds)

## Expected

One cadence, and `next_step.poll_after_seconds` wins when present. Tool description matches the guide.

## Actual

| Surface | First `get_call_run` | Then |
| --- | --- | --- |
| Live tool description | “After `run_call`, poll … every 1-3 seconds while activity is changing, then slow down” | 1–3s |
| Official MCP guide | “after about 60 seconds” | 5–10s or `next_step` |
| Cursor 0.1.2 | “wait 60 seconds before the first `get_call_run`” | 5–10s |
| skills.sh 0.1.0 | immediately, then every 10s | 10s |

`get_call_run` outputSchema includes `next_step.poll_after_seconds` (integer, optional). The tool description never mentions it.

## Evidence

Quotes above from the 2026-09-14 fetches/clone. `next_step` on a missing run had `poll_after_seconds: null`.

## Impact if an operator or agent trusted the current contract

An MCP-native agent that reads only `tools/list` will poll 20–60 times per minute from t=0 (rate limits; XR-113 is Goal `Retry-After` ignored — this is MCP hammering). A Cursor agent stays silent for 60s after `run_call`, which users read as a hang. A skills.sh agent talks every 10s. Support cannot say which contract is correct.

## Ask

Put the guide’s 60s / 5–10s (and `poll_after_seconds`) into the live `get_call_run` description. Change Cursor and skills.sh to the same paragraph.

## Do not claim

That 1–3s caused a 429 in this session (not measured). XR-504 (timeout ≠ hangup). XR-113 (Goal waiter ignores `Retry-After`).
