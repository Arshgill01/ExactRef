# ROLLUP — Python SDK / REST / webhooks / docs (Grok lab)

2026-09-14. No `POST /v1/calls`. No Goal Run create. No form. No GitHub issues. No Discord post. No tokens or live phone numbers in these files.

Workdir `/tmp/calle-lab-py/`. PyPI `calle-ai==0.7.0` in a 3.12 venv. Git clones: `server-sdk-python` `9f69e4a`, `calle-docs` `88f37ff`, `call-e-integrations` `1ce9d77`. Proofs: `prove_sdk_bugs.py` (20 passed, 1 path-encoding assert that *is* the 0.7.0 bug), `crawl_docs.py`.

## New files this pass

| File | One line |
|---|---|
| [XR-801-generated-calls-drop-success.md](XR-801-generated-calls-drop-success.md) | Generated Calls get/create return `None` on 200/201; no `CallTask`/`WebhookEvent` models |
| [XR-802-unpublished-071-unencoded-call-id.md](XR-802-unpublished-071-unencoded-call-id.md) | Git 0.7.1 unpublished; PyPI 0.7.0 `get("../goals")` becomes `GET /v1/goals` |
| [XR-803-calls-wait-lacks-goal-guards.md](XR-803-calls-wait-lacks-goal-guards.md) | Calls wait accepts 0/NaN interval, sleeps past deadline, ignores remaining HTTP budget |
| [XR-804-forbidden-is-authentication-error.md](XR-804-forbidden-is-authentication-error.md) | HTTP 403 → `CalleAuthenticationError`; exception has no `.message` |
| [XR-805-nonjson-error-not-calle-api.md](XR-805-nonjson-error-not-calle-api.md) | HTML/empty 4xx/5xx → `json.JSONDecodeError`, not `CalleAPIError` |
| [XR-806-call-not-ready-aborts-wait.md](XR-806-call-not-ready-aborts-wait.md) | Docs: `call_not_ready` = not terminal; waiter throws after one GET |
| [XR-807-post-calle-webhook-listed-as-api.md](XR-807-post-calle-webhook-listed-as-api.md) | Onboarding API table lists `POST /calle/webhook` as a CALL-E route |
| [XR-808-us-languages-include-indonesian.md](XR-808-us-languages-include-indonesian.md) | Official regions table: US languages = English, Indonesian |
| [XR-809-devpost-discord-is-devpost-guild.md](XR-809-devpost-discord-is-devpost-guild.md) | Homepage Discord invite is the Devpost guild, not CALL-E |
| [XR-810-hash-api-reference-goes-to-quickstart.md](XR-810-hash-api-reference-goes-to-quickstart.md) | Devpost `#api-reference` hash falls through to `/quickstart` |
| [XR-811-goalrun-datetime-vs-wrapper-str.md](XR-811-goalrun-datetime-vs-wrapper-str.md) | Generated `GoalRun.created_at` is `datetime`; wrapper returns ISO `str` |
| [XR-812-docs-example-e164-is-goals-strict.md](XR-812-docs-example-e164-is-goals-strict.md) | Quickstart `examples/calls.py` uses the Goal E.164 minimum on Calls create |

## Ranked by operator / agent harm

1. **XR-801** — Generated client success is `None`. Agent POSTs again. Duplicate call.
2. **XR-810** — Contest “API Reference” opens Quickstart (`create_and_wait`). Duplicate/unintended call if they run the sample.
3. **XR-802** — Pip users miss the path encoder; changelog 0.7.1 is not installable. Malformed `call_id` leaves `/v1/calls/`.
4. **XR-806** — Documented “not terminal” HTTP code aborts the official waiter (if the server ever emits it).
5. **XR-803** — Calls wait can oversleep or busy-loop; timeout then create-again (with XR-504).
6. **XR-805** — Non-JSON 502 during wait is an untyped exception; create-again path.
7. **XR-804** — 403 handled as “bad API key”; retries / key rotation during an in-flight call.
8. **XR-809** — Wrong Discord server for the official homepage button.
9. **XR-807** — Agents POST a customer webhook path at the API host.
10. **XR-808** — US/Indonesian locale lie on the 2026-09-14 regions snapshot.
11. **XR-812** — Third E.164 regex on the official Calls example (not a refile of XR-116).
12. **XR-811** — Goal timestamp type split; weaker unless someone compares model vs wrapper.

## Confirmed, not rebranded

| ID | This pass |
|---|---|
| XR-005 / XR-301 | Live `/sdks.md` still: Python source “Not currently public.” Repo is public. |
| XR-006 | Dates table still has no Feedback row. Not re-copied; see existing `CONFIRM-XR-006.md`. |
| XR-110 | `recipients=[{"phone": ...}]` still unaliased on 0.7.0 **and** git 0.7.1 (`test_plural_recipients_still_skip_phone_alias`). |
| XR-113 | 429 still one shot, no `retry_after` on `CalleRateLimitError`. |
| XR-114 | `/sdks` still reserves SDK `context`. |
| XR-116 | Live OpenAPI still has the two E.164 mins. XR-812 is the example regex, not this. |
| XR-204 | `https://docs.heycall-e.com/mcp` and `/mcp.md` still 404. |
| XR-303 / XR-504 | Docs still show Calls `timeout_seconds=120`; waiter does not cancel. |
| FB-DOC-001 | Webhooks remain unsigned; `verify`/`unwrap` deprecated. |

## Docs crawl (timeouts on every URL)

- Every `llms.txt` guide `.md` and HTML path: **200**.
- Live OpenAPI: **200**, `info.version: 0.7.0` (git spec is 0.7.1).
- Hash URLs (`#/sdks`, `#/api-reference`, …): HTTP 200 homepage HTML + JS redirector.
- `/mcp`, `/mcp.md`: **404** (XR-204).
- `https://call-e.devpost.com/details/resources`: **404**. Canonical resources URL is `/resources` (200).
- Install guide `open.heycall-e.com/document/mcp-archive/CALL-E-installation-guide.md`: **200**. MCP/CLI/skills only — no `pip install calle-ai`, no `CALLE_API_KEY`. “Confirm three tools” (XR-001, cite only).
- Unauth / bogus-bearer `GET /v1/goals?limit=1` and `GET /v1/calls/call_does_not_exist`: **401** `{"error":{"code":"unauthorized","message":"Invalid or missing API key.","details":{}}}` — matches the documented envelope.
- All 11 docs Python fences: `ast.parse` OK. Incomplete snippets (no imports) are display-only.

## Onboarding notes (clean dir, no create)

- `pip install calle-ai` → **0.7.0**. No `__version__` on `calle`.
- Env name is `CALLE_API_KEY` on docs/SDK/integrations; install guide never mentions it (CLI login instead).
- Integrations hero still uses a 5-line `createAndWait` (would place a call — not run).
- Python `>=3.11` in the SDK; install guide requires Node/npm only.

## Explicitly not new

Wait predicates (XR-004 / gauntlet-001). Timeout ≠ hangup (XR-504). `Retry-After` ignored (XR-113). Plural `phone` alias (XR-110). Unsigned webhooks (FB-DOC-001). Python-private cell (XR-005). MCP page 404 (XR-204). Canceled webhook type (XR-112). `context` missing (XR-114). Feedback dates (XR-006).

## Patch order if one engineer has a day

1. Generate `CallTask` + `WebhookEvent`; parse 200/201 (XR-801).
2. Publish or un-release 0.7.1; keep the path encoder (XR-802).
3. Share Goal wait guards with Calls wait; continue on `call_not_ready` or delete the code (XR-803, XR-806).
4. Safe `response.json()`; split 403; set `error.message` (XR-805, XR-804).
5. Devpost: slash the API Reference href; CALL-E Discord only (XR-810, XR-809).
6. README: drop `/calle/webhook` row; fix US/ID languages; align `examples/calls.py` regex (XR-807, XR-808, XR-812).
