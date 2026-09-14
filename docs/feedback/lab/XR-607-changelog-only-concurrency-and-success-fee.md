# XR-607 — Concurrency limits and the “Success fee” exist only in the Sep 14 changelog; the thing that is billed has no API field

New. 2026-09-14 (changelog re-fetched 21:55 IST; text unchanged since the morning fetch; `calle-docs` `88f37ff` is the same entry). Not XR-306 (changelog claims structured MCP not result envelope). This is the operational/billing entry.

## Finding

The docs changelog entry dated September 14, 2026 (live `https://docs.heycall-e.com/changelog.md`, lines 3–19) reads, verbatim:

```text
**Updated concurrent call limits:** The shared number pool supports 1 simultaneous
call, purchased numbers support 10 simultaneous calls, and SIP integrations have
no CALL-E-imposed concurrent call limit. These limits refer to calls active at the
same time, not call initiation rate (calls per second, or CPS).

**Updated billing model:** Calls are now billed in 10-second increments, with total
cost consisting of a Call fee and a Success fee. The Call fee covers actual carrier
charges and model resource usage, including a small preparation and pre-connection
model cost even when a call is not connected.

The Success fee applies only when the task's defined business success criteria are
met. A connected call, an answered call, or a completed conversation alone does not
qualify as success. For example, a reservation task succeeds only when the requested
booking is confirmed—not simply when someone answers or discusses availability.
Call fees may still apply when those success criteria are not met.
```

Neither fact appears anywhere else on the docs site or in the integrations repo:

- The live Calls guide's batch/wave section (`calls.md` “dispatch calls in controlled waves instead of starting every call at once … Choose a wave size that balances response speed against the number of calls that may still be in flight”) never mentions that the default pool allows **one** call in flight. No status (`queued` is “The call task is queued.”) and no error code says “behind the pool limit.”
- No field on `CallTask`, `CallEvent`, or the webhook payload records a Success fee, a Call fee, or billed seconds (`rg -i "fee|charge|cost|billing|concurren|pool|simultaneous"` over live `openapi.yaml` 0.7.0 → zero hits).
- The Calls guide's own “Task completion” section (`calls.md` ~470–516) says `task_completed` is “CALL-E's post-call judgment of whether the task reached a clear end state,” that “`completed` alone does not establish task or business success,” and walks through a reservation example where the task completes with “No table available.” The changelog says a reservation “succeeds only when the requested booking is confirmed.” So: the API exposes `status`, `task_completed`, `completion_confidence`, `evidence`, and the customer's `result_schema` — and the fee is charged on a fifth thing, “business success criteria,” whose definition and evaluator are not exposed on any surface.

## Surface / version / commit or URL

- `https://docs.heycall-e.com/changelog.md` (fetched 2026-09-14 13:xx UTC and 16:25 UTC, identical); `calle-docs` `88f37ff` `content/guides/changelog.mdx`
- `https://docs.heycall-e.com/calls.md` — wave section, `queued` row, “Task completion” section
- Live `openapi.yaml` `info.version: 0.7.0` — grep above
- `call-e-integrations` `1ce9d77` — `rg -i "success fee|simultaneous|number pool"` → zero hits

## Expected

Guide sections: “Concurrency” (limit per number type, and what happens to call N+1: rejected with code X, or queued with status Y, or serialized) and “Billing” (who defines “business success criteria” — the customer's `result_schema`? CALL-E's judgment? — which response field records that it was met, and how it maps to `task_completed` and `call.result_validation_failed`). Batch example acknowledges the limit.

## Actual

Changelog only. Grep results as above. Wave paragraph unchanged. `CallTask` has no queued-behind-pool status and no billing fields. Live read-only probes did not exercise concurrency (would require creating calls; not done).

## Evidence

- `/tmp/calle-lab/live2/changelog.md` lines 3–19
- `/tmp/calle-lab/doc-calls.md` lines 413, 433–438, 468–516
- `/tmp/calle-lab/openapi.yaml` grep
- `/tmp/calle-lab/call-e-integrations` grep

## Impact if an operator or agent trusted the current contract

An agent that fans out three calls (as the guide's wave pattern allows) on the shared pool either gets two failures with no distinguishing code, or two silently delayed dials that fire after the user has re-planned — a duplicate-dial path (inferred; not observed). On billing, integrators cannot reconcile an invoice: nothing in the API says which calls incurred the Success fee, and the guide's own example (`task_completed: true`, “No table available”) is ambiguous under the changelog's definition. A hackathon judge's first operational question — how many calls at once — is answered only on the last page of the docs.

## Ask

Add “Concurrency” and “Billing” sections to the Calls guide; define “business success criteria” in terms of an API field (or state that it is the customer's `result_schema` evaluated by CALL-E); add `billing: { call_fee, success_fee_applied: bool, billed_seconds }` (or equivalent) to `CallTask` and `call.completed`; add an explicit status/error code for pool-limit rejection; update the wave example.

## Do not claim

Observed concurrency behaviour or an invoice. That the Success fee is charged on `task_completed` (undefined — that is the point). XR-306 as this card. Refile of 109/123/126/127.
