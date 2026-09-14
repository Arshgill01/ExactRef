# ROLLUP — lead pass (XR-601..610) + fold-in of Grok XR-7xx / XR-8xx

2026-09-14. No `run_call`, no `call run|start|recover` against the live server, no `calls.create`, no form, no GitHub writes. `plan_call` used once live, planning only (no phone → `confirm_token: null`). `get_call_run` used live only with a fictitious id. Everything else: `tools/list`, read-only REST probes, offline harnesses against the published packages (`@call-e/cli@0.5.1`, `@call-e/calle@0.7.0`, `calle-ai==0.7.0`), and clones at `/tmp/calle-lab/` (`call-e-integrations` `1ce9d77`, `server-sdk-typescript` `1e1a2c1`, `server-sdk-python` `9f69e4a`, `calle-docs` `main`). Token cache never printed; no real subscriber numbers.

## New this pass, ranked by impact × viability

| # | ID | Harm class | One line | Ask (one line) |
|---|----|-----------|----------|----------------|
| 1 | [XR-601](XR-601-no-answer-space-never-terminal.md) | infinite poll / re-dial | Live schema and guide say `NO ANSWER` (space); all five skills' terminal lists say only `NO_ANSWER`; CLI passes the string through | Enum `status` in `outputSchema`, or add the guide's `NO ANSWER` sentence to every skill from one source |
| 2 | [XR-605](XR-605-create-and-wait-loses-call-id.md) | duplicate dial | `createAndWait` / `create_and_wait` drop `call_id` on every post-create error (TS also throws raw `TypeError`); Quickstart promotes it with no idempotency key | Attach `call_id` to every error after create; Quickstart = create → persist → wait |
| 3 | [XR-609](XR-609-call-status-hardcodes-call-started-true.md) | false “call exists” (medium after audit) | `call status` error envelope hardcodes `call_started: true` — even `auth_required` on a fresh machine; CLI reference defines `true` as “stable `run_id` received” | Pass `"unknown"`/omit from `call status`; unit test |
| 4 | [XR-602](XR-602-next-step-object-has-no-consumer.md) | retry-without-guidance | Server emits typed `next_step` (8 actions, `poll_after_seconds`, `retry_confirmation_action`); zero clients read it; `plan_call_same_plan_id` collides with “never twice” | One `next_step` consumer in `@call-e/core`; state whether `plan_call_same_plan_id` is the sanctioned second run |
| 5 | [XR-604](XR-604-confirm-token-printed-to-stdout.md) | credential in logs | `call plan` prints the execution credential twice to stdout; skills say “never display it” | Redact by default; `has_confirm_token`; opt-in reveal |
| 6 | [XR-610](XR-610-run-call-says-do-not-poll.md) | silent agent / no dial | `run_call` description: “do not perform extra operations; server will notify … wait for the activity card” — ChatGPT-only prose served to every host; `get_call_run` says poll | Host-neutral descriptions; ChatGPT text into `_meta` |
| 7 | [XR-603](XR-603-ttl-zero-is-forever.md) | privacy | `ttl_seconds: 0` = keep transcript + number permanently (schema text); guide never says so; no delete op | Document default + zero semantics; use `null`, not `0`, for forever |
| 8 | [XR-608](XR-608-rest-plaintext-errors-break-sdk-mapping.md) | wrong retry class | Live API returns `text/plain` 404/405; TS maps to retryable `internal_error` (Python half = XR-805) | JSON envelope from the router; non-JSON → non-retryable `unknown` |
| 9 | [XR-606](XR-606-hosted-install-guide-is-stale.md) | first-10-minutes | Hosted install guide still teaches bare `calle` + `npm i -g`; repo copy says never do that; footer links 404 | Redirect hosted URL to repo file; release checklist |
| 10 | [XR-607](XR-607-changelog-only-concurrency-and-success-fee.md) | ops / billing | 1 concurrent call and a “Success fee” exist only in the Sep 14 changelog; no guide, no API field, no definition of success | Concurrency + Billing sections; `success_fee_applied` on Call |

Confirmations with new evidence: [CONFIRM-XR-001](CONFIRM-XR-001.md) (`track_ui_events` is `noauth` + app-only `_meta`, still served to every model), [CONFIRM-XR-205](CONFIRM-XR-205.md) (`call start` ignores `confirm_expires_at`; years-expired plan still sent to `run_call` offline), [CONFIRM-XR-802](CONFIRM-XR-802.md) (repo's own `verify_openapi_contract.py` fails on the live spec: `unexpected API version`).

Noted, not filed: `auth status` with no token exits 0 and has no `ok` key (skills say “check `ok`”); `--min-ttl-seconds` (token) vs `ttl_seconds` (records) share a word; token cache is `0700`/`0600` and telemetry sends `error_code`/`error_name` only (checked; not a finding).

## Grok cards folded into the drafts (strongest first)

| ID | Why it is in the paste | Dedup note |
|----|------------------------|------------|
| XR-705 | `run_call` `idempotentHint: true` + `destructiveHint: true` — an MCP host may retry the dial | Not XR-202 (CLI envelope) |
| XR-704 | Unknown `run_id` → `ok: true`, `isError: false`, `status: FAILED`, exit 0 | Not XR-003 (`isError` true case) |
| XR-801 | Generated Python Calls client returns `None` on 200/201 → “create again” | New |
| XR-802 (+CONFIRM) | 0.7.1 in git, unpublished; pip 0.7.0 leaks raw `call_id` into the path | New |
| XR-806 | Documented `call_not_ready` = not terminal; Python waiter aborts after one GET | Not XR-004 |
| XR-711 | Cursor 0.1.2 never names `ready_to_run`; “immediately `run_call`” | Sibling of XR-203 (CLI); Cursor text is new |
| XR-707 | `plan_call` accepts a national number and asserts a recipient | Not XR-116 (min-length) |
| XR-712 / XR-706 | Four poll cadences; `plan_call` prose forbids chat while guide requires it | Companions to XR-602 / XR-610 |
| XR-805 | Python non-JSON error → `JSONDecodeError` | Python half of XR-608 |
| XR-807 / XR-808 / XR-810 / XR-809 | Onboarding table lists a customer webhook path as an API route; US languages “English, Indonesian”; Devpost “API Reference” → Quickstart; Discord button → Devpost guild | Q-11 / Q-13 material |
| XR-701 | Two packages install `calle` | **Not pasted** — this is issue 109's family (do not refile) |

## Corrections in the 2026-09-14 late pass

Three cards in the table above were rewritten after a claim-by-claim audit (`TRACE-paste-to-cards.md` §Cuts): XR-604 (real skill sentences with line numbers; removed a paraphrase that did not exist), XR-609 (skills branch on `"unknown"`, not `true`; severity high → medium; contract text now from `cli-reference.md:194–201`), XR-606 (actual hosted/repo excerpts; footer is 200 at `/404.html`). XR-704 and XR-707 gained addenda with the full live envelopes from an independent re-run; XR-707's “asserts a recipient” is one of two observed branches. XR-607 now quotes the full changelog entry and the Calls guide's `task_completed` reservation example. Row 3 (XR-609) drops to medium in the paste.

## Fold-in 2 — Grok XR-9xx (MCP / packaging) and XR-10xx (docs samples / links)

State at fold time (2026-09-14 ~22:20 IST): `ROLLUP-grok-docs.md` landed; **`ROLLUP-grok-pkg.md` had not landed** and XR-9xx was still growing (901–913 present). Folded only cards marked observed with harm ≥ medium. Re-run independently by the lead where cheap (marked ✓).

| ID | Where in paste | Why | Dedup / note |
|----|----------------|-----|--------------|
| XR-902 | Q-10 G.25 | `Accept: text/event-stream` → 406; GET hangs; no session id | New; MCP transport, not XR-202 |
| XR-1007 ✓ | Q-10 G.26 | `examples/calls.py` ignores documented `CALLE_BASE_URL` | New; not XR-605 |
| XR-908 ✓ | Q-10 G.27 | `require('@call-e/calle')` → `ERR_PACKAGE_PATH_NOT_EXPORTED`; no LICENSE / engines | New |
| XR-909 | Q-10 G.28 | CLI tarball ships `live-e2e.mjs --call`; README link escapes tarball | New; safety |
| XR-911 ✓ (auth status half) | Q-10 G.29 | `--json` no-op; exit codes undocumented; `auth status` has no `ok` | New; lead had noted the `ok` gap |
| XR-901 | Q-10 B.6 (one sentence) | `resources` + empty `prompts` capabilities undocumented | Extends XR-001, not refiled |
| XR-912 | Q-10 F.24 (one clause) | `call plan` hard-requires `--to-phone`; `plan_call` does not | Pairs with XR-707 |
| XR-1001 | Q-11 discovery paragraph | `/api-reference.md` 404; `?format=md` is HTML | New |
| XR-1002 | Q-11 discovery paragraph | `llms.txt` / sitemap / Pagefind omit MCP; Playwright locks membership | Strengthens XR-204 |
| XR-1005 | Q-11 samples paragraph | webhook fences do not compile | New |
| XR-1008 | Q-11 samples paragraph | 120 / 300 / 600 wait budgets | Extends XR-303 |
| XR-907 | Q-11 samples paragraph | OpenAPI examples fail own E.164 pattern | Not XR-116 / XR-812 |
| XR-1004 | Q-11 samples paragraph | README “Scheduled” vs SDKs “not included” | Caveat added: MCP `plan_call` has `schedule_mode` |
| XR-1003, XR-1009 | Q-11 “small, cheap” list | “API 0.6” eyebrow; README hash URLs | Low-medium |
| **Not pasted** | — | XR-903 (JSON-RPC code), XR-904 (`additionalProperties`), XR-905 (`serverInfo`), XR-906 (CORS / request id), XR-910 (`__version__`), XR-913 (`--version`), XR-1006 (OG tags), XR-1010 (Playwright pins — XR-301 family), XR-1011 (heading ids), XR-1012 (CDN preconnect) | Below medium or inferred-heavy |

## Contradictions across surfaces (matrix)

Rows are the contract point; columns are where each surface stands. “—” = silent.

| Contract point | Live tool schema / description | Official MCP guide (`1ce9d77`) | Skills (skills.sh / Cursor / Codex / Claude / OpenClaw) | CLI `@call-e/cli` 0.5.1 | SDKs / REST / docs site |
|---|---|---|---|---|---|
| No-answer terminal spelling | `NO ANSWER` (example, free string) | `NO ANSWER` ≡ `NO_ANSWER` | `NO_ANSWER` only | passes string; no terminal flag; e2e script accepts both | — (XR-601) |
| After `run_call`, what next | `run_call`: “do not perform extra operations; server will notify” · `get_call_run`: poll 1–3 s | poll ~60 s then 5–10 s, follow `next_step` | 10 s loop, or 60 s + 5–10 s | one status GET then return `next_argv` | — (XR-610, XR-712) |
| Machine-readable next action | `next_step` object, 8 actions, `poll_after_seconds`; string on `plan_call` | “follow `next_step` when present” | never read | never read; own `next_argv` | — (XR-602) |
| Second `run_call` for same plan | description: never · `next_step.action: plan_call_same_plan_id` · `idempotentHint: true` | never | never | `call recover` re-sends confirm pair (XR-206) | — (XR-602, XR-705) |
| Is a call started after an error | — | — | “if `call_started` true, do not start again” | `call status` → always `true`; `call start` → tri-state | — (XR-609) |
| Where `confirm_token` may appear | returned in `structuredContent` | “execution handshake” | “never display it” | printed twice to stdout | — (XR-604) |
| `confirm_expires_at` | emitted | — | — | never read | — (CONFIRM-XR-205) |
| Record retention | `ttl_seconds`: omit = default, `0` = permanent | “optional retention TTL” | — | cannot send it | — (XR-603, XR-205) |
| Unknown `run_id` | `isError: false`, `status: FAILED`, `next_step.report_blocked` | — | treat `FAILED` as terminal | `ok: true`, exit 0 | — (XR-704) |
| Error body format | — | — | — | — | docs: always JSON · live: `text/plain` 404/405 · TS: retryable `internal_error` · Py: `JSONDecodeError` (XR-608, XR-805) |
| Lost response after create | — | — | — | recovery file (no expiry) | docs: persist key + id · Quickstart `createAndWait`: neither · SDKs: id only in message string (XR-605) |
| Concurrency / billing | — | — | — | — | changelog only: 1 call, Success fee; Calls guide batch loop unchanged (XR-607) |
| How to run the CLI | — | — | `run-agent-command.mjs` only | — | hosted install guide: bare `calle`, `npm i -g` (XR-606) |
| API version | — | — | — | — | live spec 0.7.0 · git spec 0.7.1 · repo check asserts 0.7.1 (XR-802) |
| Fourth tool | `track_ui_events`: `noauth`, `ui.visibility: [app]`, `openai/visibility: private` | three tools | three tools | lists four | — (XR-001) |

## Observed vs inferred

**Observed:** all schema/description quotes (live `tools/list`); live `plan_call` planning-only envelope; live `get_call_run` on a fictitious id; live unauthenticated `call status` / `auth status` envelopes; live REST 404/405/401 bodies; offline `runCli` harness outputs (`[call plan]`, `[call start expired token]`, `[call start]`, `[call status NO ANSWER]`); offline TS/Python SDK probe outputs; hosted vs repo install guide diff; footer 404s; `verify_openapi_contract.py` failure; grep results on the pinned clones.

**Inferred (labeled in cards):** an agent actually polling forever on `NO ANSWER`; server behaviour on a stale `confirm_token`; concurrency rejection/queueing behaviour; a scheduled run being polled for hours; `call status` `call_started: true` on network/5xx paths (source read only).

## Do not claim

A second OffHire/live call. Any `run_call`. Form submit, Discord, GitHub issues. Refile of 109 / 123 / 126 / 127 (XR-701 stays out for that reason). Tokens or real subscriber numbers.
