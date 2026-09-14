# XR-112 — Canceled Calls are delivered as webhook type `call.failed`

## Finding

`CallStatus` includes `canceled`. Terminal webhook types do not. Public webhook docs say failed **and canceled** tasks use `call.failed`. An operator who branches only on `event.type` treats cancel as a telephony failure. The discriminator is `data.status`.

## Surface / version / commit or URL

- https://docs.heycall-e.com/webhooks (fetched 2026-09-14): “Failed or canceled terminal call tasks use `call.failed`.”
- OpenAPI `WebhookEventType`: `call.completed | call.failed | call.result_validation_failed` (no `call.canceled`)
- OpenAPI `CallStatus`: includes `canceled`
- Official docs and SDK webhook examples: `if (event.type === "call.completed")` only

No public Calls cancel operation (gauntlet-004). `canceled` still exists as a resource status (dashboard / support / future).

## Expected

Either a `call.canceled` type, or every receiver example would switch on `data.status` after checking `type`.

## Actual

Docs overload `call.failed`. OpenAPI enum has no canceled type. Examples:

```
if (event.type === "call.completed") {
  console.log(event.data.id, event.data.recipients);
}
```

`examples/webhook-server.ts` applies `structured_result` on `call.completed` and logs other types without reading `data.status`.

`waitForResult` returns `canceled` as a successful Call object (see XR-109 for CLI exit 0).

## Evidence

- https://docs.heycall-e.com/webhooks — “Failed or canceled terminal call tasks use `call.failed`.”
- `openapi/calle.openapi.yaml` `WebhookEventType` / `CallStatus`
- `server-sdk-typescript/examples/webhook-server.ts:41-58`
- `server-sdk-python/examples/webhook_server.py:85-105`

Contract / docs only. No canceled live call this session.

## Impact if an operator or agent trusted the current contract

Pager / retry logic keyed on `call.failed` fires for a canceled task. CRM “call failed, try again” plus a new idempotency key creates a second call. Webhook-only apps that ignore non-completed types never learn the task ended.

## Ask

Add `call.canceled` **or** change the webhook guide example to:

```
if (event.type === "call.failed" && event.data.status === "canceled") { ... }
```

Do not say “failed means no-answer.”

## Do not claim

- That we observed a canceled delivery.
- Unsigned webhooks as an exploit (awesome#209 / FB-DOC-001 — CONFIRM only).
- Timeout-is-cancel (XR-504 / gauntlet-004).
- Refile of 109 / 123 / 126 / 127.
