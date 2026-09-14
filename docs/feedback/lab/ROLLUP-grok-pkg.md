# ROLLUP — packaging / OpenAPI / MCP protocol / REST (Grok pkg, XR-901..913)

2026-09-14. No `run_call`. No `calls.create` with a recipient. `plan_call` once, planning only (no phone → `ready_to_run: false`, `confirm_token: null`; plan id not copied here). `get_call_run` only with `not-a-real-id` / wrong types / extras / an 8000-char string. Token cache read programmatically; never printed. No form, Discord, or GitHub writes.

Pinned:

| Surface | Version / HEAD |
|---|---|
| npm `@call-e/calle` | **0.7.0** (git `2808e21` is unpublished 0.7.1) |
| npm `@call-e/cli` | **0.5.1** (git tag `@call-e/cli@0.5.1`) |
| PyPI `calle-ai` | **0.7.0** (git `9f69e4a` is unpublished 0.7.1) |
| Live OpenAPI | `info.version: 0.7.0` (`/tmp/calle-lab/live-openapi.yaml`) |
| Live MCP | `https://seleven-mcp-sg.airudder.com/mcp/openagent_oauth` · `serverInfo` `AI Rudder MCP` `3.0.0b1` |
| REST | `https://api.heycall-e.com` |
| integrations / SDKs | `1ce9d77` / `2808e21` / `9f69e4a` |

## Ranked by impact × viability

| # | ID | Harm class | One line | Ask |
|---|----|-----------|----------|-----|
| 1 | [XR-901](XR-901-mcp-undocumented-resources.md) | host loads undocumented UI | `initialize` advertises resources; `resources/list` returns 3 Skybridge plan-card widgets pointed at `dashboard.heycall-e.com` | Gate or document resources; drop empty `prompts` capability |
| 2 | [XR-902](XR-902-sse-only-accept-406.md) | MCP client cannot connect | `Accept: text/event-stream` → 406; GET hangs 20s | Accept SSE or document JSON-POST only; 405 on GET |
| 3 | [XR-912](XR-912-cli-plan-requires-to-phone.md) | invented destination | CLI `call plan` requires `--to-phone`; live `plan_call` does not | Make `--to-phone` optional on `call plan` |
| 4 | [XR-904](XR-904-inputschema-additionalproperties-omitted.md) | schema vs runtime | `get_call_run` schema is open; extras are pydantic-rejected; 8k `run_id` is FAILED | `additionalProperties: false` + maxLength |
| 5 | [XR-911](XR-911-cli-json-noop-exit-codes-undocumented.md) | false auth failure | `--json` no-op; `auth status` has no `ok`; 0/1/2 undocumented | Add `ok: true`; document exits |
| 6 | [XR-906](XR-906-cors-allow-mismatch-no-request-id.md) | browser + support | CORS allows GET/PATCH/DELETE; `Allow` is OPTIONS,POST; no `x-request-id`; `/v1/openapi.json` 404 | Align CORS; request id; serve spec |
| 7 | [XR-908](XR-908-calle-esm-only-license-maps.md) | CJS cannot load SDK | `require('@call-e/calle')` → `ERR_PACKAGE_PATH_NOT_EXPORTED`; no LICENSE; maps → missing `src/` | ESM-only note + LICENSE; drop maps or ship `src` |
| 8 | [XR-903](XR-903-unknown-method-wrong-jsonrpc-code.md) | bad retry class | Slash-shaped unknown method is `-32602`; batch is HTTP 400 pydantic | Always `-32601` for unknown methods |
| 9 | [XR-907](XR-907-openapi-examples-violate-e164.md) | copy-paste 400 | Spectral **2 errors**: example phones fail E.164; `openapi-typescript`+`tsc` clean | Reserved `+15555550100` examples |
| 10 | [XR-910](XR-910-python-no-version-generated-public.md) | generated client used as API | No `__version__`; empty License; `calle.generated` importable | Set `__version__`; mark generated private |
| 11 | [XR-905](XR-905-serverinfo-ai-rudder-beta.md) | wrong product identity | `serverInfo` is `AI Rudder MCP` `3.0.0b1`; empty prompts | Rename to `calle` + shipped version |
| 12 | [XR-909](XR-909-cli-tarball-ships-live-e2e.md) | packaged live-call script | npm `files` includes `scripts/live-e2e.mjs --call`; README `../../docs/install/cli.md` 404s | Drop `scripts` from pack; absolute docs URL |
| 13 | [XR-913](XR-913-sdk-cli-rejects-version.md) | install check fails | SDK `calle --version` → exit 1 `Unknown option` | Add `--version` or drop SDK `bin.calle` |

Confirms with new evidence: [CONFIRM-XR-608](CONFIRM-XR-608.md) (`HEAD /v1/calls` + `/v1/openapi.json` plaintext), [CONFIRM-XR-704](CONFIRM-XR-704.md) (8k `run_id` still FAILED / `isError: false`).

## What we checked and found clean (also valuable)

- **Telemetry:** default on; destination `<base-url>/api/ui-telemetry/track`; opt-out `DO_NOT_TRACK=1`, `CALLE_TELEMETRY=0`, `--no-telemetry`; documented in README + `cli-reference.md`. Payload is anonymous id / hosts / error codes (already noted by the lead pass).
- **CLI `--version`:** MCP CLI prints `0.5.1` and matches npm + git tag `@call-e/cli@0.5.1`.
- **publint:** clean on both `@call-e/calle@0.7.0` and `@call-e/cli@0.5.1`.
- **Tarball hygiene (tests/secrets):** neither npm pack ships tests, `.env`, or JS sourcemaps of implementation (only `.d.ts.map` on the SDK). Python wheel ships no tests/`.env`.
- **`sideEffects: false`** on the TS SDK.
- **Python `python_requires >=3.11`**, `py.typed` present, `mypy --strict` on a 20-line `CalleClient` usage file **passes**. Cold import ~47 ms.
- **OpenAPI structure:** live 0.7.0 vs TS-git 0.7.0 vs Py-git 0.7.1 — **no** added/removed paths, **no** `CallStatus` / `WebhookEventType` / required-field / nullability drift. Description-only delta vs TS-git (`failure_code` “no published enum”). `openapi-typescript` + `tsc --strict` on the live spec: **0 errors**. Hand-written `structuredResult: JsonObject \| null` agrees with generated `structured_result`.
- **`Idempotency-Key`:** documented (optional on Calls create, required on Goal runs). `Retry-After:` only on Goal Run responses (XR-113 remains the waiter gap).
- **Query-string API keys:** `?api_key=` / `?access_token=` → same 401 as missing header. Not accepted.
- **MCP OAuth bearer is not a REST key:** `GET /v1/calls/not-a-real-id` with the CLI token → 401 JSON envelope.
- **TLS:** RapidSSL `*.heycall-e.com`, valid 2026-06-03 .. 2026-12-18.
- **`get_call_run` enforcement (the good half):** missing args, wrong types, and extra fields are `isError: true` pydantic errors (XR-904 is the schema lie, not missing enforcement).
- **`notifications/initialized` optional** in practice; forged/missing `Mcp-Session-Id` still serves tools (stateless — fine if documented).
- **CLI no `postinstall`.**
- **401 JSON envelope** matches the errors doc (`unauthorized` / `Invalid or missing API key.`). POST `{}` without a key never reached 400 (auth first); nothing was created.

## Do not claim

- A second OffHire / live outbound call. Any `run_call`. `calls.create` with a real recipient. Form submit, Discord, GitHub issues/PRs.
- Tokens or subscriber numbers (none in this tree).
- Refile of 109 / 123 / 126 / 127 / 90 / 116 / 118 / 121.
- Refile of XR-701 (two `calle` bins) — XR-913 is the `--version` mismatch only.
- Refile of XR-608 as a new id — plaintext 405/404 is CONFIRMed; CORS / missing spec URL is XR-906.
- Refile of XR-704 — 8k `run_id` is CONFIRM.
- Refile of XR-001 — resources are a different surface than `track_ui_events`.
- Refile of XR-802 / XR-801 — unpublished 0.7.1 and generated `None` on 200 stay those cards; XR-910 only adds `__version__` / license / public `generated`.
- Refile of XR-702 — globals-before-command.
- Refile of XR-706 / XR-610 — plan-card vs chat prose; XR-901 is that the **resource** exists.
- Rate limits, HTTP/2 production behaviour (`curl --http2` still saw HTTP/1.1), or gzip on large bodies (401s were too small).
- That `pyright --verifytypes calle` is a product defect (this lab could not make pyright resolve the installed package).
- POST `/v1/calls` 400/422 shape (no API key in env; auth returned 401 first).
