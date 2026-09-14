# XR-114 — Docs reserve SDK `context`; 0.7.0 clients have no such field

## Finding

Calls and SDK guides say the server SDKs reserve a `context` input for future workflow data and do not send it to the API. `CreateCallInput` / `calls.create` in 0.7.0 have no `context` key. OpenAPI `CreateCallRequest` is closed (`additionalProperties: false`) and has no `context` either. The reserved field is documentation-only.

## Surface / version / commit or URL

- https://docs.heycall-e.com/calls — “The server SDKs also reserve a `context` input for future SDK-side workflow data. It is not sent to the API yet.”
- https://docs.heycall-e.com/sdks — same sentence
- TypeScript `@call-e/calle@0.7.0` `36ee6f1` `src/calls.ts` `CreateCallInput`
- Python `calle-ai==0.7.0` `f7a4b82` `src/calle/calls.py` `create`
- OpenAPI `CreateCallRequest` properties: `task`, `recipients`, `result_schema`, `recipient_result_schema`, `metadata`, `webhook_url`

## Expected

If docs say the SDKs expose `context`, the type / kwargs would accept it and drop it before POST. Or the sentence would be removed until the field exists.

## Actual

`CreateCallInput` fields: `task`, `recipient`, `recipients`, `resultSchema`, `recipientResultSchema`, `metadata`, `webhookUrl`. Grep of `src/` for a reserved `context` input: none (only Goal `variables` prose).

Python `create(...)` is an explicit signature. `context=` is a `TypeError`. Raw HTTP `{ "task": "...", "context": {} }` is `400` under `additionalProperties: false`.

`metadata` is the documented correlation bag. Docs now imply a second bag that is not implemented.

## Evidence

- https://docs.heycall-e.com/calls and `/sdks` (fetched 2026-09-14)
- `server-sdk-typescript/src/calls.ts:46-54`
- `server-sdk-python/src/calle/calls.py:17-28`
- `openapi/calle.openapi.yaml` `CreateCallRequest`

## Impact if an operator or agent trusted the current contract

An agent or human copies the docs and passes `context`. TS typecheck fails or the property is ignored by `toApiCreateCall` (it never reads `context`). Python raises. HTTP 400. Time lost looking for a dropped field. Operators who stash secrets in `context` thinking it is SDK-local may instead put them in `metadata`, which **is** echoed on webhooks (unsigned — CONFIRM FB-DOC-001, not a new incident).

## Ask

Delete the `context` sentence from Calls + SDK pages until `CreateCallInput.context` exists and is stripped. One line: use `metadata` for correlation; it is echoed.

## Do not claim

- That `metadata` leaked a secret on a live webhook we received (we did not).
- A new unsigned-webhook incident.
- Refile of 109 / 123 / 126 / 127.
