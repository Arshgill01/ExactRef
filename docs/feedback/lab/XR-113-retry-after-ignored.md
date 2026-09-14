# XR-113 — Goal wait ignores documented `Retry-After`

## Finding

Create Goal Run `201` and Get Goal Run `200` both document a `Retry-After` header: suggested seconds before the next poll. Public errors copy says honor `Retry-After` on `429`. Neither SDK reads the header. Wait loops sleep a fixed `intervalMs` / `interval_seconds`. A 429 becomes `CalleRateLimitError` with no retry.

Calls wait has no `Retry-After` in OpenAPI; this note is Goals.

## Surface / version / commit or URL

- OpenAPI 0.7.0 `POST /v1/goals/{goal_id}/runs` and `GET .../runs/{goal_run_id}` response header `Retry-After`
- https://docs.heycall-e.com/goal-runs — “`Retry-After` suggests when to begin polling”; 429 row: “Honor `Retry-After` when present”
- TypeScript `36ee6f1` `src/goals.ts` `waitForResult` / `runAndWait`
- Python `f7a4b82` `src/calle/goals.py` `wait_for_result` / `run_and_wait`

## Expected

`waitForResult` would sleep `max(interval, Retry-After seconds)` when the header is present, and 429 handling would do the same before throwing or retrying with the same idempotency key.

## Actual

TS Goal wait uses `AbortController` + `sleep(Math.min(intervalMs, remainingMs))`. The fetch result’s headers are discarded after `fromApiGoalRun(response.data)`.

Python Goal wait passes remaining time as the **HTTP** timeout, then `time.sleep(min(interval_seconds, remaining_seconds))`. No header read.

`CalleRateLimitError` stores `status` / `status_code` and `details` only (`src/errors.ts`, `src/calle/errors.py`). No `retryAfter` field.

## Evidence

- `openapi/calle.openapi.yaml` Goal create `201` headers `Retry-After`; Goal get `200` headers `Retry-After`
- `server-sdk-typescript/src/goals.ts:254-289`
- `server-sdk-python/src/calle/goals.py:70-96`
- `server-sdk-typescript/src/errors.ts:50-65`
- https://docs.heycall-e.com/goal-runs common errors `429`

No live Goal Run this session.

## Impact if an operator or agent trusted the current contract

`runAndWait` can poll faster than the server asked, then 429, then throw. An operator who generates a new idempotency key on that throw creates a second Run (docs: do not). Fixed 2s polls also ignore a larger suggested backoff after `201`.

## Ask

Parse `Retry-After` on Goal create/get (and on 429). Sleep that many seconds (capped by wait timeout) before the next GET. Attach `retryAfter` on `CalleRateLimitError`.

## Do not claim

- That we were rate-limited live.
- That Calls wait should read a header the Calls paths do not document.
- Timeout ≠ hangup (gauntlet-004 / XR-504).
- Refile of 109 / 123 / 126 / 127.
