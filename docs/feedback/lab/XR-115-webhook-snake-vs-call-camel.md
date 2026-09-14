# XR-115 — Webhook `data` is raw CallTask; `calls.get` is a camelCase `Call`

## Finding

TypeScript `CalleClient.calls.get` maps the resource through `fromApiCall` (`taskCompleted`, `structuredResult`, `createdAt`). `WebhookEvent.data` is the generated OpenAPI `CallTask` (`task_completed`, `structured_result`, `created_at`). The same terminal snapshot has two field names in one package. Copying `call.taskCompleted` accessors onto `event.data` yields `undefined`.

This is not gauntlet-007 (transcript **turns** stay `offset_seconds` on an otherwise mapped `Call`). Here the **entire** webhook body is unmapped.

Python returns snake_case everywhere; no dual shape.

## Surface / version / commit or URL

- TypeScript `@call-e/calle@0.7.0` `36ee6f1`
- `src/calls.ts` `fromApiCall`
- `src/webhooks.ts` `export type WebhookEvent = components["schemas"]["WebhookEvent"]`
- `examples/webhook-server.ts` (correctly uses `event.data.task_completed`)
- OpenAPI: `WebhookCallData` `allOf: [CallTask]`

## Expected

`parseWebhookEvent(raw)` would run `fromApiCall` on `data`, or `WebhookEvent.data` would be typed as `Call`. Docs would say “webhook `data` is wire-case; `Call` is mapped.”

## Actual

`fromApiCall` is not exported (`src/index.ts`). Webhook helpers `verify` / `unwrap` are deprecated legacy HMAC (unsigned deliveries — CONFIRM, not a new incident). Current examples `JSON.parse` and read snake_case.

Official example (correct, but easy to “upgrade”):

```
taskCompleted: event.data.task_completed,
structuredResult: event.data.structured_result,
```

An operator who writes `event.data.taskCompleted` after using `waitForResult` will skip the completion check and still apply `structured_result` if they also used the wire name inconsistently — or skip the result entirely.

## Evidence

- `server-sdk-typescript/src/calls.ts:162-179` (`fromApiCall`)
- `server-sdk-typescript/src/webhooks.ts:5`
- `server-sdk-typescript/src/index.ts` (no `fromApiCall` export)
- `server-sdk-typescript/examples/webhook-server.ts:41-51`
- OpenAPI `WebhookCallData`

gauntlet-007 remains: mapped `Call.recipients[].attempts[].transcriptTurns[]` still use `offset_seconds`. Do not rebrand that.

## Impact if an operator or agent trusted the current contract

Automation that gates on `taskCompleted === true` never fires (`undefined`). Side effects that read `structuredResult` write `undefined` into storage. Silent miss, not a second live extract error.

## Ask

Export `fromApiCall` / `parseWebhookEvent` that maps `data` to `Call`. Type `WebhookEvent.data` as `Call`. Keep gauntlet-007’s turn mapping in the same pass if you touch the mapper.

## Do not claim

- Refile of gauntlet-007.
- Unsigned webhooks as a new exploit.
- A live webhook received this session.
- Refile of 109 / 123 / 126 / 127.
