# XR-302 — Live Calls status table defines `queued` as “queued,” which reads as idle

New published contract. FB-004 remains the one live-call observation; do not refile FB-004. This is the docs sentence that now locks the idle reading.

## Finding

The live Calls guide added a five-value status table. The `queued` row’s meaning is only “The call task is queued.” It does not say a top-level `queued` can coexist with attempt/event activity. An agent that treats `queued` as “not started” will create again.

## Surface / version / commit or URL

- Live: https://docs.heycall-e.com/calls and https://docs.heycall-e.com/calls.md (fetched 2026-09-14)
- GitHub `calle-docs` `content/guides/calls.mdx` on `main` (ahead of the stale local clone at `b387e01`)
- OpenAPI: `calle-docs/openapi/calle.openapi.yaml` `CallStatus` / `AttemptStatus`
- One-call observation: OffHire live call 2026-09-05, Python SDK 0.7.0 (FB-004). No second call this lab.

## Expected

The table says `queued` is non-terminal and may include an accepted task with a live or recently started attempt. “Do not create a second call because status is `queued`.”

## Actual

Live table sentence:

> `queued` | No | The call task is queued.

Same page, later:

> The Calls API does not expose an operation for clients to cancel a call after it has been created.

OpenAPI `CallStatus` elaborates only `in_progress`:

> `in_progress` includes post-call result finalization; terminal states are published only after the post-call outcome is available.

`AttemptStatus` separately includes `queued`, `dialing`, `in_progress`. The guide never maps “top-level `queued` + attempt activity” to “not idle.”

Contradicting source (owned FB-004, one call, 2026-09-05): GET call `status` stayed `queued` while attempt/events showed activity. Poll-until-terminal still worked (~4m39s accept→result).

## Evidence

- Live `/calls.md` “Call status” table fetched 2026-09-14.
- `openapi/calle.openapi.yaml` `CallStatus` description quoted above.
- Do not upgrade FB-004 provenance. One call.

## Impact if an operator or agent trusted the current contract

**Duplicate call.** Workflow sees `queued`, infers the first create did not start, posts again (new idempotency key or no key). The first call is already the operator’s live attempt.

## Ask (docs PR outline — do not open unless parent decides)

In `content/guides/calls.mdx` Call status table, change the `queued` meaning cell from “The call task is queued.” to:

> Non-terminal. May include an accepted task whose attempt/events already show dialing or conversation. Do not create another call.

Add one line under the table: top-level `queued` is not “idle.”

## Do not claim

- Not a second live call. Not a new FB-004.
- Do not file unsigned webhooks. awesome#209 is merged; live `/webhooks` already says there is no signature.
