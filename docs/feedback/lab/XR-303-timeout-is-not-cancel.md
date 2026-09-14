# XR-303 — Calls examples treat a 120s wait timeout as the end of the call

New docs-example lie. Distinct from XR-004 (predicate difference). No client cancel. A local timeout does not hang up.

## Finding

The live Calls and SDKs guides show `waitForResult` / `createAndWait` with `timeoutMs: 120_000` / `timeout_seconds=120`. They never say that exception is local polling only. The same Calls page says clients cannot cancel. SDK default wait is 600s. One live Calls create needed ~4m39s from accept to materialized result.

## Surface / version / commit or URL

- Live: https://docs.heycall-e.com/calls.md Polling and events
- Live: https://docs.heycall-e.com/sdks.md `createAndWait` / `create_and_wait` examples
- TypeScript 0.7.0: `server-sdk-typescript/src/calls.ts` `waitForResult`
- Python 0.7.0: `server-sdk-python/src/calle/calls.py` `wait_for_result`
- Contrast (honest): GitHub `call-e-integrations` `docs/mcp/openagent-oauth.md` terminal workflow

## Expected

Every wait example that uses a short timeout says: timeout raises a client error; the call continues; do not create again; resume GET / wait with the saved id.

## Actual

Live Calls example:

```ts
const completed = await client.calls.waitForResult(call.id, {
  timeoutMs: 120_000,
  intervalMs: 2_000,
});
```

Live SDKs example uses the same 120s window on `createAndWait` / `create_and_wait`.

Live Calls also says:

> The Calls API does not expose an operation for clients to cancel a call after it has been created. A call that is already in flight may therefore continue to completion even when your application no longer needs its result.

SDK source (0.7.0), Calls `waitForResult`: default `timeoutMs` / `timeout_seconds` is **600**. On expiry it throws `CalleTimeoutError`. It does not send a cancel. Supported scope on `/sdks` lists “Client-initiated cancellation of in-flight calls” as **not included**.

MCP guide (honest, not copied onto Calls):

> Reaching a client-side monitoring deadline or stopping the polling process does not fail or cancel the phone call.

Contradicting operational source: one authorized Calls API call, 2026-09-05, accept→result ~4m39s (> 120s).

## Evidence

- Live `/calls.md` and `/sdks.md` fetched 2026-09-14.
- `calls.ts` lines: `timeoutMs = options.timeoutMs ?? 600000`; throw `CalleTimeoutError` after the loop.
- `calls.py`: `timeout_seconds: float = 600.0`; raise `CalleTimeoutError`.
- No second live call this lab.

## Impact if an operator or agent trusted the current contract

**Duplicate call.** Agent copies the 120s example, hits `CalleTimeoutError`, treats the call as dead or canceled, creates again. The first call is still in flight.

## Ask (docs PR outline — do not open unless parent decides)

In `content/guides/calls.mdx` and `content/guides/sdks.mdx`:

- After each `timeoutMs: 120_000` / `timeout_seconds=120` example, add: “This limit is local polling. It does not cancel the call. On timeout, GET the saved id; do not POST a replacement.”
- Change the printed example to `600_000` / `600` to match the SDK default, or keep 120 only if the warning is adjacent.
- Cross-link the no-cancel paragraph to `waitForResult`.

## Do not claim

- Not a new service cancel API. Not XR-004 (that is Calls-status vs Goal-result predicates).
- No second live call. Do not refile 109.
