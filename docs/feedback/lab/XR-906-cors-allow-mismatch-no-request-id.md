# XR-906 — CORS allows GET/PATCH/DELETE on `/v1/calls`; `Allow` is OPTIONS,POST; no `x-request-id`; `/v1/openapi.json` is 404

## Finding

`OPTIONS /v1/calls` returns `200` `OK` with `access-control-allow-origin: *` and `access-control-allow-methods: GET, POST, PATCH, DELETE, OPTIONS`. The resource’s `Allow` on `GET`/`HEAD` is only `OPTIONS, POST` (405, `text/plain` — XR-608). Browser clients will believe GET/PATCH/DELETE are legal. No response carried `x-request-id` or rate-limit headers. `GET /v1/openapi.json` and `/v1/openapi.yaml` are `404` `Not Found` (`text/plain`). The live spec’s `servers[0].description` is “Placeholder developer API base URL.”

## Surface / version / commit or URL

- `https://api.heycall-e.com` 2026-09-14
- Live spec `/tmp/calle-lab/live-openapi.yaml` `info.version: 0.7.0`
- Errors doc: JSON envelope on every error (XR-608)

## Expected

CORS `Allow-Methods` matches `Allow`. Every API response includes a request id. Machine-readable OpenAPI is served at a documented path (or the spec says it is docs-only). `servers[].description` is “Production”.

## Actual

**Observed** `curl -sS -D- -X OPTIONS https://api.heycall-e.com/v1/calls -H 'Origin: https://example.com' -H 'Access-Control-Request-Method: POST'`:

```text
HTTP/1.1 200 OK
access-control-allow-origin: *
access-control-allow-methods: GET, POST, PATCH, DELETE, OPTIONS
access-control-allow-headers: Accept, Accept-Language, Authorization, Content-Language, Content-Type, Idempotency-Key, X-Call-E-Integration, X-Client, X-OpenAgent-Session-Secret, mcp-protocol-version, mcp-session-id
access-control-max-age: 600
AppName: internal.ai.seleven-mcp
```

**Observed** `HEAD`/`GET /v1/calls`: `405`, `allow: OPTIONS, POST`, body `Method Not Allowed`.

**Observed** `GET /v1/openapi.json`: `404`, body `Not Found`, `content-type: text/plain`.

**Observed** authenticated-route errors (invalid bearer): JSON envelope, `cache-control: no-store`, still no `x-request-id`. Query-string `?api_key=` / `?access_token=` → same 401 (keys in the query are **not** accepted — clean).

**Observed** `curl --http2` still negotiated HTTP/1.1. TLS: RapidSSL `CN=*.heycall-e.com`, valid 2026-06-03 .. 2026-12-18.

`Idempotency-Key` **is** in the spec (`required: false` on Calls create; `required: true` on Goal runs). `Retry-After` is only on Goal Run responses.

## Evidence

`/tmp/calle-lab/pkg/rest-probe.sh` dumps under `/tmp/calle-lab/pkg/rest/`. No `CALLE_API_KEY` in the environment; POST `{}` therefore 401’d before 400 validation (cannot claim a create occurred — 401 body has no `id`). MCP OAuth bearer on `GET /v1/calls/not-a-real-id` is also 401 (MCP token ≠ API key — clean).

## Impact if an operator or agent trusted the current contract

A browser agent that CORS-preflights will `GET`/`PATCH` `/v1/calls` and hit XR-608’s retryable plaintext 405. Support cannot correlate “the 401 I saw” without a request id. Codegen that fetches `/v1/openapi.json` from the API host fails and falls back to a stale git spec.

## Ask

Set CORS methods to `POST, OPTIONS` on `/v1/calls`. Add `x-request-id` on every response. Serve the live spec at `/v1/openapi.json` (or document the canonical URL). Change `servers[0].description` from “Placeholder”.

## Do not claim

Rate-limit behaviour (no 429 observed). That POST `{}` was validated (auth ran first). Refile of XR-608 except as the 405 body format.
