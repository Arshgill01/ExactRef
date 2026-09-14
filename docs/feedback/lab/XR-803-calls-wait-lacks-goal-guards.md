# XR-803 — Calls `wait_for_result` lacks the deadline guards Goal wait already has

## Finding

In the same package, Goal `wait_for_result` rejects non-finite/non-positive poll knobs, caps sleep to the remaining budget, and sets the HTTP timeout to remaining time. Calls `wait_for_result` / `create_and_wait` do none of that. Goal unit tests encode the contract; Calls has no equivalent tests.

This is not XR-113 (neither waiter reads `Retry-After`). This is not XR-504 / gauntlet-004 (local timeout ≠ hangup). It is Calls vs Goals **inside Python wait**.

## Surface / version / commit or URL

- PyPI `calle-ai==0.7.0` and git `9f69e4a` — `src/calle/calls.py` `wait_for_result` / `create_and_wait`
- `src/calle/goals.py` `_validate_polling_seconds`, `wait_for_result`, `run_and_wait`
- Goal tests: `tests/test_goals.py` `test_wait_for_result_rejects_invalid_polling_seconds_without_request`, `test_wait_for_result_does_not_sleep_past_deadline`, `test_wait_for_result_limits_poll_request_to_remaining_timeout`
- Docs examples use `timeout_seconds=120` on Calls (`sdks.mdx`, `calls.mdx`)

## Expected

Calls wait would share Goal’s three guards: validate `interval_seconds` / `timeout_seconds`, `sleep(min(interval, remaining))`, pass remaining time as the GET timeout.

## Actual

```50:63:src/calle/calls.py
deadline = time.monotonic() + timeout_seconds
while time.monotonic() <= deadline:
    call = self.get(call_id)
    if call.get("status") in {"completed", "failed", "canceled"}:
        return call
    time.sleep(interval_seconds)
```

`create_and_wait` pops `interval_seconds` / `timeout_seconds` with `float(...)` and never validates.

Goal:

```141:143:src/calle/goals.py
if not math.isfinite(value) or value <= 0:
    raise ValueError(f"{name} must be a finite positive number.")
```

plus `timeout_seconds=remaining_seconds` on GET and `sleep(min(interval_seconds, remaining_seconds))`.

## Evidence

Offline mocks against PyPI 0.7.0 (`prove_sdk_bugs.py`):

- `test_calls_wait_accepts_zero_interval` — `interval_seconds=0.0` raises only `CalleTimeoutError` after polling (Goal would `ValueError` with zero requests).
- `test_calls_wait_sleeps_past_deadline` — `timeout_seconds=1`, `interval_seconds=10`, clock stub: `sleeps == [10.0]` (Goal test asserts `sleeps == [1.0]`).
- `test_calls_wait_does_not_cap_http_timeout` — wait budget 0.25s, client timeout 30s; the GET’s httpx timeout values include `30.0`. Goal test asserts every timeout value `<= 0.25`.

No live poll. No create.

## Impact if an operator or agent trusted the current contract

Docs Calls examples use a 120s wait (XR-303 already: timeout ≠ cancel). With default `interval_seconds=2` that is fine; with a copied `interval_seconds=10` and a short remaining budget the process sleeps past the advertised timeout. `interval_seconds=0` busy-loops. A hung GET uses the 30s client timeout and can blow a 120s wait by a full HTTP budget per poll. After `CalleTimeoutError` an agent that POSTs a replacement places a second call (cite XR-504, do not refile).

## Ask

Extract one `_poll_until` used by both waiters: validate finite positive seconds, cap sleep, pass remaining HTTP timeout. Port the three Goal tests onto `CalleCalls.wait_for_result`.

## Do not claim

- Refile of XR-113 (`Retry-After`).
- Refile of XR-504 / gauntlet-004 (timeout ≠ hangup).
- That we observed a live hung GET.
- Refile of 109 / 123 / 126 / 127.
