# XR-203 — Missing `ready_to_run` is treated as ready

## Finding

Official MCP: call `run_call` only after `plan_call` returns `ready_to_run=true`. `calle call start` only stops when the flag is **exactly** `false`. Absent, `undefined`, or a non-boolean value plus a non-empty `confirm_token` proceeds to `run_call`.

## Surface / version / commit

- `packages/cli/lib/cli.js` `handleCallCommand` `start` — `f0c9cf5` and `4a53b01`
- Official MCP `docs/mcp/openagent-oauth.md` “If `ready_to_run=true`, preserve…”

## Expected

No `run_call` unless structured `ready_to_run === true` and `confirm_token` is a non-empty string. Missing flag is not consent.

## Actual

```javascript
if (structuredPlan.ready_to_run === false) {
  throw new CallStageError(..., { code: "plan_not_ready", retrySafe: true });
}
planId = extractRequiredStructuredString(planResult, "plan_id", "plan_call");
confirmToken = extractRequiredStructuredString(planResult, "confirm_token", "plan_call");
await runPlannedCall({ planId, confirmToken, ... });
```

`confirm_token: null` is rejected (`plan_call_invalid_response`). `ready_to_run` omitted is not.

## Evidence (local / offline)

Existing test `call start returns an accepted run_id when get_call_run times out` already ships this fixture:

```json
{
  "structuredContent": {
    "plan_id": "plan-secret",
    "confirm_token": "confirm-secret"
  }
}
```

No `ready_to_run`. The test expects `run_call` to be invoked and the command to exit `0`.

Null-token fixture in `call start rejects a null structured confirm token` proves the opposite check exists only for `confirm_token`, not for `ready_to_run`.

## Impact if an operator or agent trusted the current contract

**Duplicate / unintended real call.** A content-only or partial plan (clarifying questions in text, structured object with ids only) is executed. `call start` is the skills.sh happy path: plan and run inside one command, no second confirmation.

## Ask

Require `ready_to_run === true` before `runPlannedCall`. Treat missing or non-boolean as `plan_not_ready`. Add a unit test that is the inverse of the current timeout fixture.

## Do not claim

Live planner omits the flag. Refile of 126/127. That `call plan` (plan-only) auto-runs — it does not.
