# Elite feedback draft (not submitted)

Deadline: 18 Sep 2026 23:45 SGT. One form per person. Judged on completeness, viability, impact.

Paste file: [PASTE_READY.md](PASTE_READY.md). Labs: [lab/](lab/). You fill: [USER_OWNED.md](USER_OWNED.md).

## Prize sentence

Four words for done and three objects named `result` teach an agent to write a schema-valid substitution as a fact and to dial again while GET still says `queued`. A 15-second MCP timeout plus a recover command will place that second call; GET will still look like a clean extract-miss when validation failed. The server already emits the contract that would stop this — a typed `next_step`, `confirm_expires_at`, a `NO ANSWER` status — and not one shipped client reads it; the same `tools/list` marks `run_call` idempotent and tells every host to “wait for the activity card.”

## What moved today (2026-09-14)

New, cited, paste-ready:

- XR-401 stitched “verbatim” evidence (same live call). Now Q-10 A.4.
- XR-402 events page = 100 rows, cursor, `queued` on `call.in_progress`. Now Q-10 A.5.
- XR-501 four nouns for “done.” Now Q-11 / Q-13.
- XR-502 / XR-503 / XR-504 (`result_schema`, three `result` objects, timeout ≠ hangup). Already in Q-11 / Q-13.
- XR-403 reframes A.1: extract equals last confirmed spoken form. Do not say CALL-E dropped an F.
- Surface matrix in `lab/ROLLUP-surfaces.md` (SDK, API, CLI, MCP, Cursor, skills.sh, ExactRef).

Docs lab (2026-09-14, live pages): XR-301 Playwright locks the Python-private cell; XR-302 live `queued` = “The call task is queued.”; XR-303 `timeoutMs: 120_000` ≠ hangup; XR-304 schema-valid overclaim; XR-305 extra-calls noon vs Rules 23:45 SGT; XR-306 changelog #158 ≠ issue 126. Folded into Q-11.

CLI/MCP lab (`lab/ROLLUP-cli-mcp.md`): XR-202 + XR-206 timeout/`recover` = second `run_call` → Q-10 D.9. XR-203 missing `ready_to_run` → Q-10 D.10. XR-204 docs MCP 404, XR-207 Time `start`/`end` vs `started_at` → Q-11. XR-201 / XR-205 stay in the lab (plan args / offset TTL); not pasted as new Q-10 bugs.

SDK/API lab (`lab/ROLLUP-sdk-api.md`): XR-107 validation invisible on GET → Q-10 E.11. XR-108 `--phone` × N recipients → Q-10 E.12. XR-109 Calls `--wait` exit 0 → Q-10 E.13. XR-110 Python `recipients[]` skip, XR-111 `cursor` vs `after`, XR-112 canceled=`call.failed`, XR-114 docs `context` absent → Q-11. XR-113 / XR-115 / XR-116 stay in the lab (Retry-After, webhook casing, E.164 min-length).

Lead pass, 2026-09-14 evening (`lab/ROLLUP-fable-lead.md`), all in Q-10 F unless noted: XR-601 `NO ANSWER` vs `NO_ANSWER` (F.15). XR-605 `createAndWait` loses `call_id`, TS raw `TypeError`, no auto `Idempotency-Key`, Quickstart promotes it (F.16). XR-609 `call status` hardcodes `call_started: true` (F.17). XR-602 typed `next_step` unread; `plan_call_same_plan_id` vs “never twice” (F.19). XR-604 `confirm_token` printed to stdout (F.20). XR-610 `run_call` “server will notify” + XR-712 cadences (F.21). XR-608 live `text/plain` 404/405 → TS retryable, Python `JSONDecodeError` (F.22, with XR-805). XR-603 `ttl_seconds: 0` = permanent, XR-607 changelog-only concurrency / Success fee, XR-606 hosted install guide stale → Q-11. CONFIRM-XR-001 (`noauth`, app-only `_meta`), CONFIRM-XR-205 (`confirm_expires_at` never read), CONFIRM-XR-802 (repo contract check fails on live spec).

Grok passes folded (`lab/ROLLUP-grok-ts.md`, `lab/ROLLUP-grok-py.md`): XR-705 `idempotentHint` (F.14). XR-704 unknown run = `FAILED` (F.18). XR-801 / XR-802 / XR-806 Python trio (F.23). XR-707 national number planned (F.24). XR-711 Cursor never names `ready_to_run` (one sentence in D.10). XR-807 / XR-808 / XR-810 / XR-809 → Q-11 “small, cheap, embarrassing.” XR-701 (two `calle` bins) **not pasted**: issue 109 family. XR-702 / XR-703 / XR-709 / XR-710 / XR-803 / XR-804 / XR-811 / XR-812 stay in the lab.

Q-13 gained one paragraph: the server's contract is better than its clients; the fix is one `@call-e/core` module (`next_step` consumer, terminal set, token redaction) that every skill imports.

## Late pass (2026-09-14 ~22:00 IST) — audit, restructure, fold-in 2

- **Pre-submit checks closed.** XR-704 and XR-707 re-run read-only; full live envelopes appended to both cards (XR-707 is non-deterministic: Grok saw “recipient …0100, English”; the lead saw the region error inside `questions[]`; both `ok: true`, `isError: false`). XR-609's skill quote did not exist — the skills branch on `call_started: "unknown"`; the card now cites `cli-reference.md:194–201` and drops to medium. XR-607 changelog re-fetched; text unchanged; card now quotes the full entry and the Calls guide's `task_completed` reservation example.
- **Audit.** Every Q-10 item and Q-11/Q-13 sentence mapped in `lab/TRACE-paste-to-cards.md`. Cuts: two fabricated skill sentences (XR-604, XR-609), fabricated install-guide excerpts (XR-606), non-existent evidence file names (XR-605, XR-608), `auth token --show`. Corrections: guide line numbers (XR-602), sibling IDs (XR-605/608), footer status (XR-606).
- **Restructure.** PASTE_READY answer bodies are plain text (no pipes, no bold, no backticks). Q-10 opens with a lab link and a 10-row ranked list, then buckets A–G with ≤4 sentences per item. Q-11 opens with “the six sentences the docs owe.” Q-13 is three paragraphs ending on the `@call-e/core` ask.
- **Fold-in 2** (`lab/ROLLUP-fable-lead.md` §Fold-in 2): Q-10 G.25–29 = XR-902, XR-1007, XR-908, XR-909, XR-911; XR-901 → B.6; XR-912 → F.24; Q-11 gained XR-1001/1002 (discovery), XR-1005/1008/907/1004 (samples), XR-1003/1009 (small list). `ROLLUP-grok-pkg.md` had not landed at fold time; XR-9xx may still grow.

CONFIRMED only, not refiled: 126/127, gauntlet-001..007, XR-001..006, XR-401/402, XR-501..504, unsigned webhooks.

## OffHire

Desk is not the product. Exception `OH-01` is. Conversation-quality (interruption, “AI-like”) stays out of Q-10 unless it changes a write. FB-002 stays out. Stage of F/S is not isolated; do not say CALL-E dropped an F.

## Do not submit from an agent turn
