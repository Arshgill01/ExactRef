# XR-605 — `createAndWait` / `create_and_wait` throw away the `call_id` on any post-create failure; the Quickstart promotes them

New. 2026-09-14. Distinct from XR-803 (Python Calls wait lacks Goal's deadline guards), XR-806 (`call_not_ready` aborts the waiter) and XR-504 (timeout ≠ hangup): those are about *waiting*. This card is about the *create* half of the combined helper — the id is gone on every error path, in both languages — and the Quickstart that steers new users onto it. XR-810 (Grok) notes the Devpost link lands on this Quickstart.

## Finding

Both SDKs ship a one-liner that POSTs a call and then polls. In both, the POST succeeds and the resulting `call_id` lives only in a local variable. If anything in the wait phase throws — network error, non-JSON body, 5xx, deadline — the caller gets an exception that does not carry the id as a field. TypeScript embeds it in the message string on timeout only; Python does the same. Any other failure (connection error, `TypeError`, `JSONDecodeError`) loses it entirely.

The Quickstart's “Create and wait” section shows exactly this helper with no idempotency key and no id persistence. The same repo's `examples/calls.py` does the right thing (uuid idempotency key, writes `call-id.json` before waiting) — but the Quickstart does not link it.

Additional TS defect proven offline: a `fetch` rejection surfaces as a raw `TypeError`, not `CalleConnectionError`, so even a well-written `catch (e instanceof CalleError)` misses it.

## Surface / version / commit or URL

- `server-sdk-typescript` `1e1a2c1` (`@call-e/calle`): `src/resources/calls.ts` `createAndWait()`; `src/http.ts` (no try/catch around `fetch`)
- `server-sdk-python` (`calle-ai`): `calle/resources/calls.py` `create_and_wait()`; `calle/_client.py` `_request()`
- `calle-docs` `main` `doc-quickstart.md`, section “Create and wait” (TS + Python samples) vs `examples/calls.py`
- Docs `/calls.md` “Recovering from a lost response” (persist `idempotency_key` + `call_id`)

## Expected

A helper that dials a phone and then waits either (a) returns/throws an object carrying `call_id` on every path, or (b) is documented as “for scripts only; production must persist the id before waiting.” Network failures map to `CalleConnectionError` as the errors doc promises.

## Actual

Offline probes against the published packages (custom `fetch` / `httpx.MockTransport`; no network; no real call). Output verbatim:

TypeScript `@call-e/calle` 0.7.0:

```text
[createAndWait: POST ok, GET rejects]  threw TypeError: fetch failed   code=undefined status=undefined ownKeys=[]
[createAndWait: POST ok, GET 502]      threw CalleAPIError code=internal_error status=502 ownKeys=["code","status","details","name"]
[createAndWait: deadline]              threw CalleTimeoutError: Timed out waiting for CALL-E call call_fixture. ownKeys=["name"]
[fetch rejects on POST create]         threw TypeError: fetch failed   (create itself: not CalleConnectionError)
```

No thrown object carries a `callId` property; the id appears once, inside the timeout message string.

Python `calle-ai` 0.7.0:

```text
[create_and_wait: POST ok, GET ReadTimeout]  raised CalleTimeoutError: CALL-E API request timed out.        attrs={}
[create_and_wait: wait deadline]             CalleTimeoutError attrs=[] msg=Timed out waiting for CALL-E call call_fixture.
[create without idempotency_key]             request headers contain Idempotency-Key? False
```

Two different situations — one GET timed out vs the overall deadline passed — raise the same class with no attribute to tell them apart or to recover the id. The SDK does not generate an `Idempotency-Key` when the caller omits one.

Quickstart “Create and wait” (both languages): `client.calls.createAndWait({...})` / `client.calls.create_and_wait(...)` — no `idempotency_key`, no id persistence, no `try`.

## Evidence

- `/tmp/calle-lab/tslab/ts_probe.mjs` (cases 3–5; run 2026-09-14)
- `/tmp/calle-lab/py_probe.py` (cases 3–4 and the header check; run 2026-09-14)
- `/tmp/calle-lab/doc-quickstart.md` “Create and wait”; `/tmp/calle-lab/calle-docs/examples/calls.py` (writes `call-id.json` before waiting)

No live call was created; all POSTs went to mocks.

## Impact if an operator or agent trusted the current contract

A real call has been placed and paid for; the process has no handle to it. The natural recovery is “try again” → second dial to the same person. Calls' `Idempotency-Key` is optional (Goals require it), and the Quickstart omits it, so the retry is not deduplicated. This is the exact failure the docs' own recovery section warns about, reproduced by the docs' own first-page sample.

## Ask

Attach `callId` / `call_id` to every error thrown after create in both SDKs (or return `{ call, error }`). Wrap `fetch` in `CalleConnectionError`. In the Quickstart, replace the combined helper with create → persist id → `waitForResult(id)`, and generate an `Idempotency-Key`. Link `examples/calls.py`.

## Do not claim

XR-803 / XR-806 / XR-504 as this card. A live duplicate dial. Server-side behaviour on retry without a key (not tested). Refile of 109/123/126/127.
