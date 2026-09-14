# XR-1004 — Integrations README lists scheduled calling as a current capability

## Finding

The CALL-E integrations README capabilities table ships **Scheduled and Batch Calling**: “Schedule individual calls or send a batch task to multiple recipients.” The official SDKs page, in the same product, lists **Recurring or scheduled calls** under “This release does not include.” Live OpenAPI `CreateCallRequest` has no schedule / start-at field. The Calls guide’s batch story is `recipients[]` now, not a scheduler.

“Batch” is half-true (multi-recipient create exists). “Schedule” is not on the Developer API.

## Surface / version / commit or URL

- `call-e-integrations/README.md` Capabilities row (clone `/tmp/calle-lab/call-e-integrations`, also the Regions source repo)
- Live https://docs.heycall-e.com/sdks.md “Supported scope” / “This release does not include”
- `live-openapi.yaml` `CreateCallRequest` properties: `task`, `recipients`, `result_schema`, `recipient_result_schema`, `metadata`, `webhook_url`

## Expected

Capabilities would match the shipped API: batch recipients yes; scheduled / recurring no (or marked In Development next to “Goal-Driven Long Tasks”).

## Actual

README:

```
| **Scheduled and Batch Calling** | Schedule individual calls or send a batch task to multiple recipients |
```

SDKs guide:

```
This release does not include:
- ...
- Recurring or scheduled calls
```

Observed: both texts. Inferred: the server has no public schedule endpoint we did not see in the live spec.

## Evidence

Grep of the two files plus OpenAPI `CreateCallRequest`. No `schedule`, `start_at`, or `not_before` on create.

## Impact if an operator or agent trusted the current contract

An agent builds a “cron of `createAndWait`” or invents a `scheduled_at` field (`additionalProperties: false` → `invalid_request`) or busy-waits until a wall clock then POSTs — a burst of real calls at the scheduled instant with no server-side hold.

## Ask

Split the row: keep batch recipients; move schedule to **In Development** (or link a dashboard-only scheduler if that is the only path). Add a CI grep that the README does not claim APIs absent from OpenAPI.

## Do not claim

- That we found a hidden schedule endpoint.
- A refile of XR-607 (changelog-only concurrency / Success fee).
- Refile of 109 / 123 / 126 / 127.
