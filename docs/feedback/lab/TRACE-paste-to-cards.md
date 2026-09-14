# TRACE — PASTE_READY claim → card → evidence

2026-09-14 22:10 IST. Every numbered Q-10 item and every factual sentence in Q-11 / Q-13 of `PASTE_READY.md` mapped to its card and the evidence line inside it. Anything that failed this pass was cut or corrected (see “Cuts and corrections” at the end).

Pinned versions used throughout: `@call-e/cli` 0.5.1 · `@call-e/calle` 0.7.0 · `calle-ai` 0.7.0 · `call-e-integrations` `1ce9d77` (2026-09-14 16:54 +0800) · `calle-docs` `88f37ff` · `server-sdk-python` `9f69e4a` · `server-sdk-typescript` `1e1a2c1` · live OpenAPI 0.7.0 · Cursor plugin 0.1.2 · skills.sh skill 0.1.0.

## Q-10 top-ten table

| Row | Card(s) | Evidence line |
|---|---|---|
| 1 XR-705 | `XR-705-run-call-idempotent-hint.md` | live `tools/list` annotations; re-read 2026-09-14 16:xx UTC: `run_call {destructiveHint: true, idempotentHint: true}` (`/tmp/calle-lab/mcp-tools-pretty.json`) |
| 2 XR-202/206 | `XR-202-mcp-call-timeout-no-side-effects.md` §Actual (`code: http_error`, “missing: stage, call_started, retry_safe”), `XR-206-recover-resubmits-run-call.md` §Impact | CLI unit fixtures on `f0c9cf5`/`4a53b01` |
| 3 XR-601 | `XR-601-no-answer-space-never-terminal.md` §Actual | live schema text; skill grep with line numbers; `cli_probe.mjs [call status NO ANSWER]` |
| 4 XR-605 | `XR-605-create-and-wait-loses-call-id.md` §Actual | `ts_probe.mjs` cases 3–5, `py_probe.py` cases 3–4 + header check (verbatim output) |
| 5 FB-001/XR-403 | `docs/PACKAGE.md:19`, `skills/exact-ref/references/call-fs01.json:6`, `XR-403-inband-confirm-not-second-channel.md` | OffHire `OH-01` live call 2026-09-05 |
| 6 XR-107 | `XR-107-validation-invisible-on-get.md` §Finding, line 13 (`verify_openapi_contract.py:266`) | docs `/webhooks`, OpenAPI `CallTask` |
| 7 XR-108 | `XR-108-cli-phone-is-recipient.md` line 28 (`input.recipients = flags.phones.map((phone) => ({ phones: [phone] }))`) | TS SDK `src/cli.ts` |
| 8 XR-704 | `XR-704-missing-run-is-failed.md` + Addendum (lead re-run, full envelope) | `/tmp/calle-lab/live2/get_call_run_unknown.json`, `call_status_unknown.json` |
| 9 XR-602 | `XR-602-next-step-object-has-no-consumer.md` §Finding/§Actual | live `get_call_run.outputSchema.next_step.action` enum (8 values); `rg next_step packages/ skills/` → 0 hits |
| 10 XR-604 | `XR-604-confirm-token-printed-to-stdout.md` §Finding (skill quotes with line numbers) | `cli_probe.mjs [call plan]`; `skills/calle/SKILL.md:37–38`, `references/commands.md:165–166` |

## Q-10 detailed items

| Item | Claim | Card | Evidence line |
|---|---|---|---|
| A.1 | `07198SECTIST` vs `07198FECTIST`; schema-valid; last confirmed S-form | FB-001 (`docs/PACKAGE.md:19`, `call-fs01.json:6`), `XR-403` | live call `OH-01` |
| A.2 | “Sunday morning” + “5:00 PM” → summary Sunday 5 PM | FB-003 (`call-fs01.json:9,11`) | live call `OH-01` |
| A.3 | top-level `queued` during attempt; ~4m39s | FB-004; `XR-302-queued-means-idle.md:36` | live call `OH-01` |
| A.4 | stitched “verbatim” with `USER:` and ellipses; sibling field exact | `XR-401-stitched-evidence.md` | live call `OH-01` |
| A.5 | 100 rows, `next_cursor`, `queued` on `call.in_progress`, ends ~2 min before hangup | `XR-402-event-page-cursor.md` §Actual table | live events snapshot |
| B.6 | four tools; `_meta` `noauth` / `ui.visibility [app]` / `openai/visibility private` | `NEW_FINDINGS_2026-09-13.md` XR-001; `CONFIRM-XR-001.md` | live `tools/list` |
| B.7 | Cursor 0.1.2 top-level summary / no untrusted boundary; PR 129; 126 | `NEW_FINDINGS_2026-09-13.md` XR-002; `RESEARCH_2026-09-13-evening.md` “Changed” | GitHub `main` |
| B.8 | generic `mcp call` `ok: true` on `isError`; issue 127; PR 128 | `NEW_FINDINGS_2026-09-13.md` XR-003 | `packages/cli/lib/cli.js` |
| C | Calls vs Goal wait predicates; timeout ≠ hangup; `--timeout-seconds` 15 / 150 | XR-004 (`NEW_FINDINGS`), `XR-504-timeout-is-not-hangup.md`, `cli-reference.md:238` | SDK source; CLI reference |
| D.9 | `http_error` without flags; `run_call_timeout` + `retry_safe: false`; recover re-sends pair; Cursor prefers MCP | `XR-202` §Actual lines 25–52, 77; `XR-206` line 47, 68 | CLI fixtures |
| D.10 | `call start` stops only on `false`; fixture omits flag; Cursor never names `ready_to_run` | `XR-203-ready-to-run-optional.md`; `XR-711-cursor-skill-skips-ready-to-run.md` | CLI unit fixture; Cursor SKILL.md |
| E.11 | validation failure webhook-only; contract test forbids `result_validation` | `XR-107` line 13 | `verify_openapi_contract.py:266` |
| E.12 | `--phone` × N → N recipients; “Repeatable”; no cancel | `XR-108` line 28; `XR-303-timeout-is-not-cancel.md` | TS `src/cli.ts` |
| E.13 | Calls `--wait` exit 0 on failed/canceled; Goal exits 1 | `XR-109-cli-wait-exit-zero-on-failed-call.md` lines 5, 9 | TS `src/cli.ts` |
| F.14 | `idempotentHint: true` + `destructiveHint: true`; “Do not call … more than once” | `XR-705` | live `tools/list` (re-read 16:xx UTC) |
| F.15 | `NO ANSWER` in schema; guide 246–248; skills lines 189/86/170/158/180; CLI passthrough; `live-e2e.mjs:17–18` | `XR-601` | grep 2026-09-14 21:5x IST (this pass) |
| F.16 | no `call_id` on thrown objects; `TypeError ownKeys []`; `CalleTimeoutError ownKeys ["name"]`; Python same class for ReadTimeout and deadline; no auto `Idempotency-Key`; Quickstart vs `examples/calls.py` | `XR-605` §Actual | `ts_probe.mjs`, `py_probe.py` verbatim |
| F.17 | `auth_required` envelope with `call_started: true`; cli-reference 194–201; two literal sites; skills key on `"unknown"` | `XR-609` (rewritten this pass) | live run 16:2x UTC; `sed -n 174,203p cli-reference.md`; `rg "callStarted: true" cli.js` |
| F.18 | `isError: false`, `FAILED`, “run_id not found.”, `report_blocked`; two agents, two ids | `XR-704` + Addendum | `live2/get_call_run_unknown.json` |
| F.19 | 8-value enum; `retry_confirmation_action`; guide 234–235, 252–253; 0 grep hits; string on `plan_call` | `XR-602` | `mcp-tools-pretty.json`; `rg next_step packages/ skills/` |
| F.20 | token twice in stdout; SKILL.md 37–38; commands.md 165–166; `auth status` omits token; cli-reference 188–189 | `XR-604` (rewritten this pass) | `cli_probe.mjs`; greps |
| F.21 | `run_call` / `get_call_run` descriptions verbatim; guide 234–235; Cursor 79/82; skills.sh 144 | `XR-610`, `XR-712-poll-cadence-four-stories.md` | `mcp-tools-pretty.json` |
| F.22 | 405/404 `text/plain`; 401 JSON; TS `internal_error`; Python `JSONDecodeError` | `XR-608`, `XR-805-nonjson-error-not-calle-api.md` | live curl 13:xx and 16:2x UTC; `ts_probe.mjs` 1, `py_probe.py` 1 |
| F.23 | generated client `None`; 0.7.1 unpublished; raw `call_id`; `verify_openapi_contract.py` fails; `call_not_ready` | `XR-801`, `XR-802` + `CONFIRM-XR-802.md`, `XR-806` | Grok `prove_sdk_bugs.py`; lead run of verify script (exit 1) |
| F.24 | two branches (recipient asserted / region error in `questions[]`); both `ok: true`, `isError: false` | `XR-707` + Addendum | `/tmp/calle-lab-ts/mcp/plan-edges/local-digits.out`; `/tmp/calle-lab/live2/plan_call_national.json` |

### Fold-in 2 (bucket G and inserts)

| Item | Claim | Card | Evidence line |
|---|---|---|---|
| B.6 insert | `resources` (3 skybridge widgets, `dashboard.heycall-e.com`), `prompts/list` empty | `XR-901-mcp-undocumented-resources.md` §Actual | `/tmp/calle-lab/pkg/mcp-results/mcp-probe.json` (Grok) |
| F.24 insert | `call plan` “Missing required --to-phone”; raw `plan_call` plans without | `XR-912-cli-plan-requires-to-phone.md`; lead's `plan-smoke.json` (no phone, `ready_to_run: false`) | CLI help + `handleCallCommand` |
| G.25 | 406 `-32600` “Not Acceptable: Client must accept application/json”; GET no response 20 s; forged `Mcp-Session-Id` accepted | `XR-902-sse-only-accept-406.md` §Actual | `/tmp/calle-lab/pkg/mcp-probe2.mjs` (Grok; not re-run by lead) |
| G.26 | `authentication.md:64` sentence; `examples/calls.py:83` `CalleClient(api_key=api_key)`; TS examples pass env | `XR-1007-complete-example-ignores-base-url.md` | lead re-grep ✓ (`rg CALLE_BASE_URL examples/calls.py` → none) |
| G.27 | `ERR_PACKAGE_PATH_NOT_EXPORTED`; `exports {types, import}`; no `license` / `engines`; no LICENSE file; `.d.ts.map` → `src/` | `XR-908-calle-esm-only-license-maps.md` §Actual | lead re-run ✓ (`node --input-type=commonjs -e "require('@call-e/calle')"`; `ls node_modules/@call-e/calle` → `dist package.json README.md`) |
| G.28 | tarball `scripts/live-e2e.mjs`; `--call` + `CALLE_CLI_LIVE_TO_PHONE`; `verify:live:call`; README `../../docs/install/cli.md` | `XR-909-cli-tarball-ships-live-e2e.md` §Actual | `npm pack` under `/tmp/calle-lab/pkg/cli/` (Grok); `live-e2e.mjs` lines 14–22 also read by lead for XR-601 |
| G.29 | `--json` unread (`rg options.json lib/cli.js` → none); `auth status` no `ok`; exit 2 unknown command; exit 0 on XR-704 | `XR-911-cli-json-noop-exit-codes-undocumented.md` §Actual; lead's unauthenticated `auth status` run (no `ok`, exit 0) | CLI runs 2026-09-14 |

## Q-11 sentences

| Sentence (key phrase) | Card | Evidence |
|---|---|---|
| “The call task is queued.” | `XR-302` line 24 | live `/calls.md` row |
| four done words; `task_completed` with `completion_confidence`/`evidence` | `XR-501-completed-nouns.md`; `doc-calls.md` 468–480 | live guide |
| Success fee / “completed conversation alone does not qualify” / reservation example / pool 1 / 10 / SIP | `XR-607` (rewritten this pass) | `live2/changelog.md` 3–19; `doc-calls.md` 433–438, 505–516 |
| `timeoutMs: 120_000`, default 600, not a hangup; no cancel | `XR-303` lines 7, 38, 49–50; `XR-504` | SDK source |
| `--timeout-seconds` 15 s HTTP | `cli-reference.md:238` | CLI reference |
| three `result` objects; Cursor template; skills.sh SKILL vs commands.md | `XR-503-result-nouns.md`; `XR-002` | skill files |
| PR 129 `start`/`end` vs `started_at`/`ended_at` | `XR-207-checker-vs-calling-fields.md` lines 5–7 | PR 129 diff |
| `result_schema` / `webhook_url` absent on MCP | `XR-502-mcp-no-result-schema.md` line 5 | live `tools/list` |
| “validates the structured result … terminal call task state”; `confirmation_code` | `XR-304-identifier-schema-valid-overclaim.md` lines 7, 23, 27 | live guide |
| `ttl_seconds: 0` permanent; guide “optional retention TTL”; 24 h default; no delete; CLI cannot send | `XR-603`; `XR-205` | live schema; `plan-smoke.json`, `live2/plan_call_national.json` (`expires_at` = created + 24 h) |
| hosted install guide `npm install -g`, bare `calle`; repo launcher text; SKILL.md 43/47; footer → `404.html` | `XR-606` (rewritten this pass) | curl final-URL; diff |
| OpenAPI 0.7.0 vs 0.7.1; verify script fails | `XR-802`, `CONFIRM-XR-802` | script run exit 1 |
| events page 100 / `cursor` vs `after` | `XR-402`, `XR-111-cursor-vs-after.md` line 5 | OpenAPI |
| `call.result_validation_failed` on CallTask | `XR-107` | docs `/webhooks` |
| canceled → `call.failed`, branch on `data.status` | `XR-112-canceled-webhook-is-call-failed.md` line 9 | live `/webhooks` |
| SDK `context` absent | `XR-114` line 5 | SDK types |
| Python `recipients=[{"phone"}]` no alias | `XR-110` line 5; `py_probe.py` case 6 | mock transport body |
| `/mcp`, `/mcp.md` 404; `llms.txt` nine guides, no MCP/CLI/skills; sitemap 16 URLs; Playwright locks membership | `XR-204-docs-site-missing-mcp.md`; `XR-1002-llms-omits-mcp-cli-skills.md`; `CONFIRM-XR-204.md` | curl; `tests/docs-site.spec.ts` |
| `/api-reference.md` + `/api-reference/<tag>.md` 404 `NoSuchKey`; `?format=md` 200 HTML; guides `text/markdown` | `XR-1001-api-reference-has-no-markdown.md` §Actual | curl log |
| webhook fences: Python `'return' outside function`, `json` not imported; TS `TS2552 Cannot find name 'event'`; 17/18 TS, 9/11 Py pass | `XR-1005-webhook-samples-do-not-compile.md`; `ROLLUP-grok-docs.md` sample table | `docs/feedback/lab/tools/check_samples.py` |
| wait budgets 120 / 300 / 600; Quickstart “five-minute polling timeout” | `XR-1008-three-published-wait-timeouts.md` | `calls.mdx`, `examples/calls.py`, `calle/calls.py` |
| OpenAPI phone examples fail own pattern; Spectral 2 errors; Redocly 4 warnings | `XR-907-openapi-examples-violate-e164.md` | lint output (Grok) |
| README “Scheduled and Batch Calling” vs SDKs “Recurring or scheduled calls” not included; `CreateCallRequest` no schedule field; MCP `plan_call` has `schedule_mode` | `XR-1004-scheduled-calling-advertised-as-shipped.md`; lead's `mcp-tools-pretty.json` (`schedule_mode`, `scheduled_at` on `plan_call`) | grep |
| Goal Runs eyebrow “API 0.6” vs “0.7.0 packages” on the same page | `XR-1003-goal-runs-still-says-api-06.md` | live `/goal-runs.md` |
| SDK READMEs `#/sdks` → homepage (3.5 KB) for non-browser clients | `XR-1009-sdk-readme-hash-urls-are-homepage.md` | curl sizes |
| `POST /calle/webhook` in API table; US “English, Indonesian”; Devpost API Reference → Quickstart; Discord → Devpost guild | `XR-807`, `XR-808`, `XR-810`, `XR-809` | Grok crawl |
| `/sdks` “Not currently public”; Playwright locks it | `CONFIRM-XR-005.md`; `XR-301-playwright-locks-python-private.md` | live page; `calle-docs` test |
| changelog #158 ≠ 126 | `XR-306` | changelog |
| Devpost dates table; 10:00 SGT | XR-006 (`NEW_FINDINGS`) | Devpost + Rules |
| extra-calls noon vs 23:45 SGT; 1–5 business days | `XR-305-extra-calls-form-noon.md` | form text |
| `mcp call` transport success (127); `track_ui_events` | XR-003, XR-001 | — |

## Q-13 sentences

| Key phrase | Card |
|---|---|
| `07198SECTIST` / write-gate | FB-001, XR-403, XR-304 |
| MCP cannot take `result_schema` | XR-502 |
| Cursor / skills.sh top-level summary vs `result{}` | XR-002, XR-503 |
| CLI verification `COMPLETED` = pass; guide says not task success | `cli-verification.md:118`; guide 248–250; XR-501 |
| `mcp call` exit 0 on `isError` | XR-003 / 127 |
| typed `next_step`, `confirm_expires_at`, `retry_confirmation_action`, `NO ANSWER` | XR-602, CONFIRM-XR-205, XR-601 |
| 10-second loop; `NO_ANSWER` list | XR-601, XR-712 |
| years-expired plan forwarded (offline) | CONFIRM-XR-205 |
| `confirm_token` printed | XR-604 |
| `call_started: true` before login | XR-609 |
| ChatGPT prose; idempotent annotation | XR-610, XR-705 |
| 15 s timeout no `retry_safe`; recover re-submits | XR-202, XR-206 |
| GET hides validation failure; `--wait` exit 0 | XR-107, XR-109 |
| no dialable number on 2026-09-14 plans | `plan-smoke.json`, `live2/plan_call_national.json` (`confirm_token: null`) |

## Cuts and corrections made in this pass

1. **Cut** (XR-604 / F.20): the quoted skill sentence “Do not display the confirm_token or any raw token to the user” did not exist in any shipped skill. Replaced with the real sentences and line numbers: `skills/calle/SKILL.md:37–38` (“Do not print, request, or expose access tokens or execution confirmation data”) and `references/commands.md:165–166` (“Do not display or reuse any execution confirmation data that appears in planning-only output”). Also cut the claim that skills “recommend plan first, then confirm” — skills.sh says `call plan` is “only for a planning-only request.” Cut the non-existent `auth token --show`.
2. **Cut** (XR-609 / F.17): the quoted skill rule “If `call_started` is true, do not run `call start` again” did not exist; the skills branch on `call_started: "unknown"`. Replaced with the CLI reference's own definition of `true` (`cli-reference.md:194–201`). Severity lowered high → medium and the reason stated.
3. **Corrected** (XR-606): fabricated excerpts (“`calle call start --goal`”, “Do not run `calle` directly; always go through run-agent-command.mjs so the agent gets JSON envelopes”) replaced with the actual hosted and repo text; the contrast is now hosted `npm install -g` + `env … calle …` vs repo launcher + JSON `argv` vs skill “Do not run bare `calle` or use `npx`” (SKILL.md:47). Footer link status corrected from “302 → 404” to “200 at `/404.html`”. Wrong cross-reference to XR-709 removed.
4. **Corrected** (XR-707 / F.24): “asserts a recipient” is one of two observed branches (Grok's run); the lead re-run produced the region error inside `questions[]`. Paste now states both and calls the planner non-deterministic; the reproduced defect is “non-E.164 accepted with a success envelope, hard error as a question.”
5. **Corrected** (XR-602): guide line numbers 232–233 → 234–235.
6. **Corrected** (XR-607): changelog quote expanded to the full entry (purchased numbers 10, SIP unlimited, 10-second increments, pre-connection cost, reservation example); added the Calls guide's own `task_completed` reservation example as the ambiguity.
7. **Corrected** (XR-605, XR-608): evidence file names that did not exist (`wait_probe.mjs`, `error_probe.mjs`, `pylab/*`, `rest-probes.txt`) replaced with the real `ts_probe.mjs` / `py_probe.py` and verbatim outputs; wrong sibling references (XR-811/807/804) replaced with XR-803/806/805.
8. **Corrected** (B.6): now cites the `_meta` facts from `CONFIRM-XR-001` rather than the 2026-09-13 “not in repo” grep alone.
9. **Cut** (Q-06): “Leave blank while the 14 September deadline is still ahead” → ExactRef is submitted; leave blank.
10. **Not pasted**: XR-701 (issue 109 family), XR-702/703/709/710/803/804/811/812 (below medium or overlapping).

## Re-verification 2 (2026-09-14 ~22:00–22:40 IST, lead) — every Grok card cited in PASTE_READY

Method: re-ran the exact read-only command in the card, or re-opened the exact file:line in the 2026-09-14 clones (`/tmp/calle-lab/*`, integrations `1ce9d77`, py `9f69e4a`, ts `2808e21`), and compared the verbatim quote. No `run_call`, no create with a recipient, no `plan_call` this pass. MCP probes used the cached CLI token programmatically (`mcp_reverify.mjs`, token never printed).

| Card | Paste item | Check performed | Result |
|---|---|---|---|
| XR-704 | top-10 #9, F.18 | live `get_call_run` unknown id (last pass) + CONFIRM-XR-704 8k id | PASS |
| XR-705 | top-10 #1, F.14 | live `tools/list` annotations (last pass) | PASS |
| XR-707 | F.24 | live re-run (last pass; two branches recorded) | CORRECTED (last pass) |
| XR-711 | F.15 / Q-11 | `cursor-plugin/.../SKILL.md` steps 2–4 verbatim; `call-e-safety.mdc:15` "Do not configure CALL-E run_call for auto-run" | PASS |
| XR-712 | F.21 | Cursor SKILL.md steps 6–7 verbatim (60 s then 5–10 s); skills.sh step 7 | PASS |
| XR-801 | F.23(a) | `generated/api/calls/create_call.py:39–78` handles 400/401/403/409/422/429/500 → `return None`; `models/__init__.py` exports `CallTaskObject` (a `Literal["call_task"]`), no `CallTask` / `WebhookEvent` | PASS |
| XR-802 | F.23(b) | CONFIRM-XR-802 (last pass) | PASS |
| XR-805 | F.22 | `src/calle/calls.py:83–84` `response.json()` before mapping | PASS · prior art server-sdk-python #39 added |
| XR-806 | F.23(c) | `calls.py:58–61` status-only waiter; `errors.md:136` "call_not_ready means the call task has not reached a terminal state." | PASS · prior art TS #17/#23 added |
| XR-807 | Q-11 | `README.md:269–272` table verbatim | PASS with nuance: live OpenAPI has `/calle/webhook` path (`receiveWebhookEvent`) with `servers: https://{yourserver}`; paste reworded to "the OpenAPI gets this right; the table drops it" |
| XR-808 | Q-11 | `README.md:371,383` and live `regions.md` rows | PASS |
| XR-809 | Q-11 | Discord invite API: `HP4BhW3hnp` → guild Devpost (66,834); `6AbXUzUV8w` → CALL-E (724); homepage has only the Devpost href | PASS |
| XR-810 | Q-11 | Devpost resources page href `https://docs.heycall-e.com/#api-reference`; `zudoku.config.tsx` redirector only matches `route === "/api-reference"` (slash), else `/quickstart` | PASS |
| XR-901 | Q-11 | `initialize` → `resources.listChanged: true`, `prompts.listChanged: true`; `resources/list` → `plan_call_widget` `text/html+skybridge`, `openai/widgetDomain https://dashboard.heycall-e.com/`; `prompts/list` → `[]` | PASS |
| XR-902 | top-10 #8, G.25 | `Accept: text/event-stream` → 406 `-32600 "Not Acceptable: Client must accept application/json"`; JSON Accept → 200; GET aborted at 15 s | PASS |
| XR-907 | Q-11 | Spectral `spectral:oas` on live spec: 2 errors `oas3-valid-media-example` phone pattern, 9 warnings | PASS |
| XR-908 | G.27 | `require('@call-e/calle')` (last pass) | PASS |
| XR-909 | G.28 | `packages/cli/package.json` `files` includes `scripts`; `verify:live:call` = `live-e2e.mjs --call`; `live-e2e.mjs:27,31,452` `--call` / `CALLE_CLI_LIVE_TO_PHONE`; `README.md:11` `../../docs/install/cli.md` | PASS |
| XR-911 | G.29 | `cli-reference.md:241` "Accepted for compatibility"; `cli.js` never reads `options.json`; fresh-cache `auth status` (last pass) | PASS |
| XR-912 | F.24 | `cli.js:979` `throw new InvalidArgumentsError("Missing required --to-phone")` in `buildPlanArguments` | PASS |
| XR-1001 | Q-11 | `/api-reference.md` 404, `/api-reference/calls.md` 404, `?format=md` → HTML | PASS |
| XR-1002 | Q-11 | live `llms.txt` has no mcp/cli/skill line; `/mcp`, `/mcp.md` 404; sitemap 16 locs, Pagefind 17 pages | PASS |
| XR-1003 | Q-11 | live `goal-runs.md:5` "**API 0.6**" vs `:340` "0.7.0" | PASS |
| XR-1004 | Q-11 | `README.md:98` "Schedule individual calls or send a batch task" | PASS |
| XR-1005 | Q-11 | `py_compile` on live webhooks.md fences: two `SyntaxError: 'return' outside function`; TS fence uses `event` undeclared | PASS |
| XR-1007 | top-10 #7, G.26 | `examples/calls.py:83` + `authentication.md:64` (last pass) | PASS |
| XR-1008 | Q-11 | `examples/calls.py:62` 300; `quickstart.md:195` "five-minute"; `calls.md:532/544` 120; `calls.py:55` default 600 | PASS |
| XR-1009 | Q-11 | npm/PyPI README `#/sdks`, `#/api-reference`; curl of `/#/sdks` = homepage | PASS |

Totals: 28 cards checked · PASS 26 · CORRECTED 2 (XR-707 last pass; XR-807 nuance this pass) · CUT 0.

## Prior art recorded this pass (issues by others; cited in paste as "filed by others, confirmed here")

| Issue | State | Cards given a "Prior art" section | Paste location |
|---|---|---|---|
| server-sdk-python #39 (JSONDecodeError leak) | open | XR-805 | F.22 |
| server-sdk-python #30 (calls vs goals wait) | open | XR-803, XR-504 | C, F.23(c) |
| server-sdk-typescript #17 (waitForResult returns before result) | open | XR-806, XR-504 | C |
| server-sdk-typescript #23 (timeoutMs unbounded) | open | XR-806, XR-504 | C |
| calle-docs #40 (terminal before structured_result) | open | XR-304 | Q-11 |
| calle-docs #41 (structured_result without evidence) | open | XR-304, XR-401 | top-10 #5, Q-11 |
| calle-docs #42 (attempt timestamps lose timezone) | open | XR-205 | card only |
| calle-docs #43 (failure_code contradiction) | closed | XR-501, XR-107 | Q-11 |
| calle-docs #44 (task_completed naming) | closed | XR-501 | Q-11 |

Own upstream PRs cited: call-e-integrations #128 (`isError` → failed mcp call), #129 (Cursor reads `result{}`), both open. awesome-phone-call-agents #673 (listing, not a fix; not cited in paste). `ROLLUP-upstream-prs.md` landed (commit `ec903b5`) during this pass; "Fix proposed: <url>" appended in the paste to top-10 #4 and F.16 (TS #26), F.17 (integrations #138), F.20 (#139), F.23(c) (python #40), Q-11 small list (#136, #137, docs #60); python #41 (XR-110) is listed in the Q-10 prior-art line only, since XR-110 has no paste item.

## Re-rank (top-10, this pass)

In: XR-1007 (#7, official example dials production when a staging URL is set) and XR-902 (#8, MCP client cannot connect; re-verified live). Out: XR-108 (now detail item 12 only) and XR-604 (detail item 20 only). XR-901 and XR-1002 stay in Q-11 (docs/discovery harm, not a wrong action). List stays at exactly 10.
