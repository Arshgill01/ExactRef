# XR-807 — Official onboarding API table lists `POST /calle/webhook` as a CALL-E endpoint

## Finding

The integrations README is the official onboarding path. Its Developer API table puts three CALL-E routes next to `POST /calle/webhook` (“Receive terminal call result webhooks”). That path is the **customer** receiver shown in `examples/webhook_server.py` (`HTTPServer` on `/calle/webhook`). It is not a method on `https://api.heycall-e.com`.

An agent that “follows the table” POSTs to `$CALLE_BASE_URL/calle/webhook` with the project API key, or expects CALL-E to expose webhook management there.

## Surface / version / commit or URL

- https://github.com/CALLE-AI/call-e-integrations `1ce9d77` README “API” / Endpoints table
- Python SDK `examples/webhook_server.py` listens on `POST /calle/webhook`
- Live https://docs.heycall-e.com/webhooks.md — you host the URL; set `webhook_url` on create
- OpenAPI paths: `/v1/calls`, `/v1/calls/{call_id}`, `/v1/calls/{call_id}/events`, `/v1/goals`, … — no `/calle/webhook` server path (the spec has a `receiveWebhookEvent` example for **your** receiver)

## Expected

The API table would list only `api.heycall-e.com` methods. Webhooks would be “your HTTPS URL, passed as `webhook_url`,” pointing at `/webhooks`.

## Actual

```267:272:integrations/README.md
| Method | Path | Description |
| `POST` | `/v1/calls` | Create a one-recipient or batch call task. |
| `GET` | `/v1/calls/{call_id}` | Read status, summaries, structured results, and transcripts. |
| `GET` | `/v1/calls/{call_id}/events` | List developer-facing call events. |
| `POST` | `/calle/webhook` | Receive terminal call result webhooks. |
```

Same section’s curl examples correctly use `$CALLE_BASE_URL/v1/calls`. The table does not.

## Evidence

- Integrations README fetched via local clone `1ce9d77` (2026-09-14)
- `python-sdk/examples/webhook_server.py:24-26` `if self.path != "/calle/webhook"`
- Live OpenAPI `paths` keys (downloaded `docs.heycall-e.com/openapi/calle.openapi.yaml`) have no `/calle/webhook`
- No POST to any CALL-E write endpoint this session

## Impact if an operator or agent trusted the current contract

A new-user agent copies the table into a “probe all endpoints” script and POSTs `/calle/webhook` at the API host (wrong), or omits `webhook_url` and waits on a CALL-E path that does not exist. Time lost; possible confused retry of `/v1/calls`.

## Ask

Delete the `/calle/webhook` row. One sentence: “Webhook URL is yours; pass `webhook_url` on create. See /webhooks.”

## Do not claim

- That we POSTed `/calle/webhook` to the live API.
- A new unsigned-webhook incident (FB-DOC-001).
- Refile of XR-204 / 109 / 123 / 126 / 127.

## Prior art (added 2026-09-14 22:30 IST)

Re-verified 2026-09-14 22:20 IST (lead): README.md:269–272 on `1ce9d77` unchanged. Nuance: the live OpenAPI does model `POST /calle/webhook` as a path (`operationId: receiveWebhookEvent`, line ~641) but with `servers: [{ url: https://{yourserver} }]` and `security: []` — i.e. the customer's receiver. The README table drops that server override and lists it beside `/v1/calls`. Card stands; paste wording adjusted to say the spec gets it right and the table does not.
