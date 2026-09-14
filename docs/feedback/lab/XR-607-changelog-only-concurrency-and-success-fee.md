# XR-607 — Concurrency limit (1 call) and the “Success fee” exist only in the Sep 14 changelog; no guide, no API field, no definition of “success”

New. 2026-09-14. Not XR-306 (changelog claims structured MCP not result envelope). This is the operational/billing entry.

## Finding

The docs changelog entry dated 2026-09-14 adds two facts that change how every integration should behave:

1. “Updated concurrent call limits: shared number pool supports **1 simultaneous call**.”
2. “Updated billing model: total cost consisting of a **Call fee** and a **Success fee**. The Success fee applies only when the task's defined business success criteria are met.”

Neither appears anywhere else on the docs site or in the integrations repo. The Calls guide still shows batch / wave patterns that create several calls in a loop with no concurrency note, and no error code or status tells a caller “queued behind the pool limit.” No field on a call, event, or webhook says whether the Success fee was charged, and “business success criteria” is not tied to any existing field (`task_completed`, `result_validation_failed`, `GoalRunError.result_invalid`) — the closest candidates each mean something different.

## Surface / version / commit or URL

- `https://docs.heycall-e.com/changelog` (`doc-changelog.md`, entry 2026-09-14)
- `https://docs.heycall-e.com/calls.md` — batch / wave section (multiple `create` in a loop; no limit)
- `openapi.yaml` (live 0.7.0): Call, CallEvent, Webhook payload schemas — `rg -i "fee|charge|cost|billing|concurren|pool|queue"` → zero hits
- `call-e-integrations` `1ce9d77`: `rg -i "success fee|concurrent|simultaneous|number pool"` → zero hits outside the changelog mirror

## Expected

Guide sections: “Concurrency” (limit, what happens to call #2: rejected with code X / queued with status Y / silently serialized) and “Billing” (definition of success, the field that records it, how it maps to `task_completed` and validation failures). The batch example acknowledges the limit.

## Actual

Changelog only. Grep results as above. Calls guide batch pattern unchanged. `Call` schema has no `queued`/`pending_pool` status and no billing fields.

Live read-only probes did not exercise concurrency (would require creating calls; not done).

## Evidence

- `/tmp/calle-lab/calle-docs/doc-changelog.md` (entry text)
- `/tmp/calle-lab/calle-docs/doc-calls.md` batch section
- `/tmp/calle-lab/openapi.yaml` grep
- `/tmp/calle-lab/call-e-integrations` grep

## Impact if an operator or agent trusted the current contract

An agent that fans out three calls (as the guide shows) either gets two failures with no distinguishing code, or two silently delayed dials that fire after the user has given up and re-planned — a duplicate-dial path (inferred; not observed). On billing, integrators cannot reconcile invoices: nothing in the API says which calls incurred the Success fee, and “business success” may be charged for a call the integrator's own validator rejected (`call.result_validation_failed`). For a hackathon judge, the first fact they need before demoing (how many calls at once) is on the last page they read.

## Ask

Add “Concurrency” and “Billing” sections to the Calls guide; define success in terms of an API field; add `billing: { call_fee, success_fee_applied: bool }` (or equivalent) to `Call` and `call.completed`; add a specific error code / status for pool-limit rejection; update the batch example.

## Do not claim

Observed concurrency behaviour or an invoice. XR-306 as this card. Refile of 109/123/126/127.
