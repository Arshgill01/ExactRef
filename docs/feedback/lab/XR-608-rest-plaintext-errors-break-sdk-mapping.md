# XR-608 — The API itself returns plain-text `404`/`405`; the TS SDK relabels them as retryable `internal_error`

New. 2026-09-14. XR-805 (Grok) proves the **Python** half offline with hypothetical HTML/empty bodies. This card adds (a) live proof that the production API — not a WAF — emits non-JSON errors, and (b) the **TypeScript** mapping, which is a different failure (wrong retry class, not an untyped exception).

## Finding

The errors doc promises a stable JSON envelope for every error. Live, the API returns `text/plain` bodies for a wrong-method call (`GET /v1/calls` → `405 Method Not Allowed`) and for an unknown path (`GET /v1/nonexistent` → `404 Not Found`). Only authenticated-route errors (`401` on `POST /v1/calls` with a bad key) come back as the documented JSON.

The TypeScript SDK's `apiErrorFromResponse` assumes JSON on `status >= 400`; when parsing fails it falls back to `code: "internal_error"`, which the errors doc lists as **retryable**. A typo'd path, a wrong method, or a mis-set base URL therefore becomes a retry loop for any client that follows the doc's own retry table. (Python: raw `JSONDecodeError`, see XR-805 — now reproducible against the live host, not just a mock.)

## Surface / version / commit or URL

- Live 2026-09-14 (`curl -sS -m 15 -i`): `GET https://api.heycall-e.com/v1/calls` → `405`, body `Method Not Allowed`, `content-type: text/plain`; `GET .../v1/nonexistent` → `404`, body `Not Found`; `POST .../v1/calls` with invalid key → `401` JSON `{ "error": { "code": ... } }`
- `https://docs.heycall-e.com/errors.md` — “every error response uses the same envelope”; retry table marks `internal_error` retryable
- `server-sdk-typescript` `1e1a2c1` `src/http.ts` / `src/errors.ts` `apiErrorFromResponse`
- `server-sdk-python` `calle/_client.py` `_request()`; `calle-docs/examples/calls.py` (`except json.JSONDecodeError`)

## Expected

Every 4xx/5xx from the API host carries the JSON envelope (including router-level 404/405). SDKs map a non-JSON body to a non-retryable `CalleAPIError` with `code: "unknown"` (or `http_<status>`) and keep the raw body in `.body`.

## Actual

Offline probes replaying the live bodies through the published SDKs (verbatim output):

TypeScript `@call-e/calle` 0.7.0:

```text
[405 text/plain on GET]    threw CalleAPIError: CALL-E API request failed. code=internal_error status=405
[502 html on POST create]  threw CalleAPIError: CALL-E API request failed. code=internal_error status=502
[200 text/html on GET]     threw SyntaxError: Unexpected token '<' ... is not valid JSON   (untyped)
```

Python `calle-ai` 0.7.0 (same inputs):

```text
[405 text/plain on GET]    raised json.decoder.JSONDecodeError   (XR-805)
```

## Evidence

- Live `curl -sS -m 15 -i` runs 2026-09-14 (headers/bodies quoted above; bogus key used for the 401 control)
- `/tmp/calle-lab/tslab/ts_probe.mjs` cases 1, 2, 6
- `/tmp/calle-lab/py_probe.py` case 1

No call created. The 401 probe used a deliberately invalid key.

## Impact if an operator or agent trusted the current contract

TS: a permanent misconfiguration (wrong path/method/base URL) is classified as a transient server fault and retried on the doc's schedule — noisy at best; if the misconfigured request is a `POST` with a valid path behind a proxy that returns text on transient failure, the client retries a call-creating request without knowing what happened to the first one (inferred). Python: untyped exception crosses every `except CalleError` boundary and crashes agents that were written to the documented error hierarchy.

## Ask

Return the JSON envelope from the router (404/405). In TS map non-JSON → `code: "unknown_non_json"` non-retryable, preserve body. In Python wrap `response.json()` on the error path and raise `CalleAPIError(code="unknown", body=text)`. Add a test in both SDKs with a `text/plain` body.

## Do not claim

That production routes return text on 5xx (not observed). XR-805 as this card (Python half is Grok's). Refile of 109/123/126/127.
