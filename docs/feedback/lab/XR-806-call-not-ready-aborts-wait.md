# XR-806 — Docs: `call_not_ready` means “not terminal yet”; Python wait treats it as a hard HTTP failure

## Finding

Live Errors page defines `call_not_ready` as: the call task has not reached a terminal state. That is a poll-again signal. `CalleCalls.wait_for_result` has no special case. Any 4xx from `GET /v1/calls/{id}` becomes `CalleAPIError` and the loop ends after one request.

The recovery table on the same page never mentions `call_not_ready`. OpenAPI lists the code on `APIError.code` but no operation documents a 409/425 with that code. The waiter is still one `if status in {completed, failed, canceled}` plus “HTTP error ⇒ throw.”

## Surface / version / commit or URL

- Live https://docs.heycall-e.com/errors.md (fetched 2026-09-14): “`call_not_ready` means the call task has not reached a terminal state.”
- OpenAPI `APIError.code` enum includes `call_not_ready` (live 0.7.0 and git 0.7.1). Grep of `paths` returns no operation that names it.
- PyPI / git `src/calle/calls.py` `wait_for_result` + `_request`

## Expected

If the code means “not terminal,” `wait_for_result` would keep polling (same as `queued` / `in_progress`). If the code is unused, Errors would say so or drop it. The recovery table would include the row.

## Actual

Errors.md one sentence, not in the “Choose the next action” table.

Waiter (status-only, then throw on HTTP):

```58:61:src/calle/calls.py
call = self.get(call_id)
if call.get("status") in {"completed", "failed", "canceled"}:
    return call
```

`get` → `_request` → `api_error_from_response` on any `>= 400`.

## Evidence

`prove_sdk_bugs.py` `test_call_not_ready_aborts_wait`: mocked GET 409 `{error:{code:"call_not_ready", message:"The call task has not reached a terminal state."}}`.

- `wait_for_result(..., interval_seconds=0.001, timeout_seconds=0.5)` raises `CalleAPIError` with `code == "call_not_ready"`
- `route.call_count == 1` (no second poll)

Observed: docs sentence + waiter behavior + mock. Inferred: that production GET ever returns this code (OpenAPI does not attach it to getCall). Distinguish: we did not see a live `call_not_ready`.

## Impact if an operator or agent trusted the current contract

If the server emits the documented code during post-call finalization, the official waiter throws while the phone/result is still in flight. The agent may `create` again (duplicate) or write “failed” from an HTTP error that the Errors page defined as “not done yet.” If the code is never returned, the page still teaches agents to expect a retryable “not terminal” HTTP error that the SDK cannot retry.

## Ask

Either (1) document `call_not_ready` as unused and remove it from the public enum, or (2) attach it to `GET /v1/calls/{id}` and make `wait_for_result` continue polling on that code (and add the recovery-table row). Do not leave “not terminal” next to a waiter that throws.

## Do not claim

- That live GET returned `call_not_ready` this session.
- Refile of XR-004 (Calls vs Goal wait predicates) or XR-113.
- Refile of 109 / 123 / 126 / 127.
