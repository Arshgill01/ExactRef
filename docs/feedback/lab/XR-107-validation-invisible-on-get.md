# XR-107 — `call.result_validation_failed` is invisible on GET / `waitForResult`

## Finding

Public webhooks treat structured-result validation failure as a first-class terminal type. The CallTask resource, the OpenAPI contract test, and both SDK waiters hide it. A polling operator sees `status: completed` plus `structured_result: null` — the same shape as “no schema” or “could not extract.”

## Surface / version / commit or URL

- Public docs: https://docs.heycall-e.com/webhooks (fetched 2026-09-14)
- OpenAPI 0.7.0 in both SDKs (`WebhookEventType`, `CallTask`, `CallStatus`)
- TypeScript `@call-e/calle@0.7.0` `36ee6f1` (`src/calls.ts` `waitForResult`)
- Python `calle-ai==0.7.0` `f7a4b82` (`src/calle/calls.py` `wait_for_result`)
- Python `scripts/verify_openapi_contract.py` line 266

## Expected

A completed call whose requested schema was rejected would be distinguishable on `GET /v1/calls/{call_id}`: a `failure_code`, a `result_validation` object, or a non-completed status. `waitForResult` would not look like a successful extract-miss.

## Actual

Docs: `call.result_validation_failed` is sent when a completed call had an internal structured-result validation failure. Invalid results are returned as `null`. The payload does not expose validation details.

OpenAPI `CallStatus` is only `queued | in_progress | completed | failed | canceled`. `WebhookEventType` is `call.completed | call.failed | call.result_validation_failed`. There is no matching CallTask field.

The Python contract test **forbids** the field:

```
assert_contract("result_validation" not in call_properties, "CallTask must not expose result_validation")
```

Both SDK tests assert the same (`"resultValidation" in call` is false / `"result_validation" not in call`).

`CalleCalls.waitForResult` / `wait_for_result` return when `status` is `completed|failed|canceled`. They never see webhook `type`. Official examples then log `structuredResult` / `structured_result`.

## Evidence

- `server-sdk-python/scripts/verify_openapi_contract.py:266`
- `server-sdk-typescript/src/calls.ts:268-279`
- `server-sdk-python/src/calle/calls.py:50-63`
- `server-sdk-typescript/tests/calls.test.ts` (`expect("resultValidation" in call).toBe(false)`)
- `server-sdk-python/tests/test_calls.py` (`assert "result_validation" not in call`)
- OpenAPI `WebhookEventType` vs `CallTask.properties` (no `result_validation`)
- https://docs.heycall-e.com/webhooks — validation-failed type; GET snapshot is the same `CallTask`

No live call this session. This is the published contract, not a telephony observation.

## Impact if an operator or agent trusted the current contract

`createAndWait` / `waitForResult` + write `structured_result` will treat a rejected extract as “nothing to write” or “recipient did not answer the question.” A webhook-only app that handles only `call.completed` never runs the failure path. Polling-only apps cannot branch at all. That is silent data loss of the validation-failure signal, not a second FB-001.

## Ask

Add `failure_code: result_validation_failed` (or restore `result_validation`) on CallTask when the webhook type would be `call.result_validation_failed`. Until then, one sentence on the Calls wait and structured-results pages: GET/`waitForResult` cannot distinguish validation failure from extract-miss; only the webhook `type` can.

## Do not claim

- A live `result_validation_failed` delivery (we did not receive one).
- That schema-valid output is true (FB-DOC-002 / FB-001).
- That the SDK should have revalidated extra keys (gauntlet-003).
- Refile of 109 / 123 / 126 / 127.
