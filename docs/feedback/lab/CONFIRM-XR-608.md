# CONFIRM-XR-608 — HEAD `/v1/calls` and `/v1/openapi.json` are also `text/plain`

New evidence only. Original card: live GET 405/404 plaintext; TS maps to retryable `internal_error`.

## Finding (added 2026-09-14, packaging pass)

`HEAD /v1/calls` is `405 Method Not Allowed`, `content-type: text/plain`, `allow: OPTIONS, POST`, `Content-Length: 18` (same body as GET). `GET /v1/openapi.json` and `/v1/openapi.yaml` are `404 Not Found`, body `Not Found`, `text/plain`. No `x-request-id`. CORS OPTIONS is JSON-less `200` `OK` (`text/plain`, 2 bytes) — not an error, but another non-JSON router response.

Invalid-key `GET /v1/calls/not-a-real-id` remains the documented JSON 401 envelope (unchanged).

## Evidence

```text
curl -sS -m 20 -I https://api.heycall-e.com/v1/calls
# HTTP/1.1 405  content-type: text/plain; charset=utf-8  allow: OPTIONS, POST

curl -sS -m 20 -D- https://api.heycall-e.com/v1/openapi.json
# HTTP/1.1 404  content-type: text/plain  body: Not Found
```

Dumps: `/tmp/calle-lab/pkg/rest/head-calls.*`, `openapi-json.*`.

## Do not claim

A new card for plaintext 405 (this is XR-608). That `/v1/openapi.json` 404 is the same harm class as 405-retry (it is adjacent; filed as XR-906 for the missing spec URL).
