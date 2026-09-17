# Live lab — 2026-09-17

Live CALL-E calls placed with the account owner's explicit authorisation, to the account owner's own phone, with the owner beside the phone. This supersedes the earlier lab rule of "no live calls"; the product board's own rule (fixture replay only) is unchanged. No live CALL-E request (create, plan, run, or GET) was made after the owner's stop instruction; the corrections below were made from already-saved bytes.

Raw objects, numbers and transcripts live in `.data/live-2026-09-17/` (not committed). Redacted excerpts and the two committed artefacts are under `evidence/`. Runner: `live.py` (REST), `@call-e/cli` 0.5.1 (MCP path).

Account: API key from the OffHire `.env.local`; CLI OAuth login usable. Region: India (`IN`, supported, International). Pool: shared numbers, 1 simultaneous call (14 Sep changelog), so calls are sequential.

## Ground rules

- One create per case. No automatic redial. A local timeout is not a hangup: keep polling the existing id.
- The recipient is told the protocol before each call and reports what happened on the phone (rang / did not ring / answered).
- Every claim promoted to the form points at a saved file by name; anything not backed by saved bytes is marked "not claimed."

## Case index

| Case | Path | Question | Status |
| --- | --- | --- | --- |
| C-01 (Codex live-01, 07:12Z) | REST | Does dictation + clarification produce an exact reference? | done — completed, 204 s accept→terminal, 12 polls `queued` with `in_progress` attempt |
| C-02 (Codex live-02, 07:21Z) | REST | Same prompt, recipient-only card with a correction | done — phone never rang; see LV-01 |
| L-01..L-04 | — | no-answer shape, run_call twice, dictation traps, impossible schema | not run — account out of balance, owner declined top-up |

## Findings

### LV-01 — A call that never rang finished `completed`, `failure_code: null`, with no transcript and no connection metadata; the read path can't say "never connected"

Corrected 17 Sep after an independent review flagged over-reach. Kept only what two saved artefacts show; dropped the "premature `call.completed`" and "wrong write" claims.

Source: Codex case live-02, `call_t2SxwVonYPtacjRhntODcw`, created 2026-09-17T07:21:52Z. Recipient report: only the C-01 call rang; this one never did. Codex polled 50 times over 619 s and stopped with top-level `queued`, one attempt `in_progress`, zero transcript turns.

Saved artefacts (redacted, committed):
- `evidence/live02-events-early-0732Z.json` — events page pulled ~07:32Z (6 rows).
- `evidence/live02-terminal-0920Z.json` — full call object pulled ~09:20Z (terminal).

Terminal object (09:20Z):

```
status: completed          completed_at: 07:58:16Z   (≈36 min after create)
failure_code: null         failure_message: null
task_completed: false      completion_confidence: {score 0.58, label medium}
recipients[0].status: completed
attempts[0]: status completed, started_at null, completed_at null, provider_call_id null, transcript_turns []
structured_result: {reference "", pickup_status "unknown", pickup_timing "", reference_quote "", timing_resolved "unknown", readback_confirmed "unknown"}
summary: "The first call did not connect or complete; the recipient may be busy or unavailable, so you can confirm retrying in about 45 minutes, provide a different retry time, or ask to retry immediately."
evidence: ["No recipient response or transcript was captured.", "The required fictional pickup reference and pickup details were not obtained.", "The call record does not show usable call timing or duration."]
```

Early events (07:32Z, 6 rows, all `status: queued`):

```
07:22:09 call.started      status queued  "run_call started."
07:22:11 call.in_progress  status queued  "botlab create bot."
07:22:29 call.in_progress  status queued  "calling resolve robot id."
07:22:32 call.in_progress  status queued  "calling create task."
07:22:33 call.updated      status queued  "calling task created."
07:22:33 call.updated      status queued  "calling task status=pending"
```

What the saved bytes support:

1. Missing connection outcome (the real finding). The phone never rang, yet the terminal object is `completed`, `failure_code: null`, with `attempts[0].started_at: null`, `provider_call_id: null`, `transcript_turns: []`. No documented field names "did not connect." A polling operator cannot distinguish "connected, said nothing" from "never rang." The attempt-status enum already exists; an attempt-level `connected: false` / `no_answer` would resolve it. Ask: expose a connection outcome and per-stage timestamps.
2. Prolonged, opaque progress. Top-level `queued` through 619 s of polling and (per `completed_at`) ~36 min total, while C-01 on the same account 10 min earlier took 204 s end to end. Nothing on GET explained the stall. Ask: meaningful queue/dispatch/connect/finalise stages.
3. Empty result vs the null rule (design ask, not a wrong write). Our schema permits `""` and `"unknown"`, so the object is schema-valid and represents *missing answers*, not invented ones. But the docs say `structured_result` is `null` when "CALL-E did not produce a schema-valid whole-task result from the available evidence," and here the evidence list says nothing was captured yet a non-null object came back — the two behaviours are in tension. Ask: return `null` (or a typed no-evidence marker) when no transcript exists. Not claimed: that anyone wrote these as facts, or that `null` is the only correct representation.
4. Channel-specific summary. `summary` is written for a chat client with a retry widget ("confirm retrying in about 45 minutes … or ask to retry immediately"); REST has no such control. Ask: host-neutral summaries.
5. Event `status` doesn't track the event's own moment. In the 07:32Z snapshot every row — including `call.updated` "calling task created" — carries `status: queued`, i.e. the call's status at read time. Ask: document that `CallEvent.status` is the current call status, or snapshot it per event.

Corrected / withdrawn:
- I earlier wrote "two `call.completed` events, the first 35 min early." The saved early snapshot has **no** `call.completed` row; the 07:22:33 row is `call.updated` "calling task created." A later, unsaved read rendered a `call.completed` at that timestamp (type may be reclassified between reads), but I did not persist it, so I do not claim it.
- I earlier called the empty result a "wrong write." It is schema-permitted missing data; reframed as the null-rule tension above.

Not claimed: why the call did not ring (carrier, pool, provider, or the balance that later ran out) — not isolated. Whether the 36-min latency is typical — n=1.

### LV-02 — Out of balance: REST returns a typed `402`; MCP returns `ok` with the billing message as a clarifying question, and `run_call` still mints a FAILED run labelled `guardrails_reject`

Observed 2026-09-17 09:35Z after the two Codex calls exhausted the balance (no surface reports balance, so the owner didn't know).

REST, `POST /v1/calls` (`.data/live-2026-09-17/L01R/created-*.json`):

```
HTTP 402  {"error": {"code": "insufficient_balance", "message": "Insufficient CALL-E balance. Please top up at .../account/billing and try again.", "details": {"reason_code": "iams_balance_insufficient"}}}
```

Exactly what errors.md promises: stable code, documented recovery, no call id. Correct. Both SDKs map it correctly (TS `CalleAPIError` code `insufficient_balance` status 402; Python same, `status_code` 402); `create_and_wait` / `createAndWait` throw before any call exists.

MCP, `calle call plan` → `plan_call` (`.data/live-2026-09-17/L01/plan.json`, raw):

```
ok true, isError false
plan_id "p86YC19F1", ready_to_run false, confirm_token null      <- null, NOT a credential
next_step: "Please try again later."   (a string on plan_call; an object on run_call/get_call_run)
clarifying_questions / questions[].question / confirm_summary: all = "Insufficient CALL-E balance. Please top up ..."
```

MCP, `mcp call run_call` on that plan (`.data/live-2026-09-17/L01/run_call_not_ready.json`, raw):

```
ok true, isError false, exit 0
status "FAILED", run_id "fYdWmS2Fhj3lI9Fxi8DG1A", message "Insufficient CALL-E balance. ..."
activity: [{kind "guardrails_reject", level warning, message "run_call rejected by guardrails."}]
next_step: {action "report_blocked", instruction "Report the current terminal run status. Do not start another call."}
```

`calle call status --run-id fYdWmS2Fhj3lI9Fxi8DG1A` → `ok true`, `isError false`, `status FAILED`, exit 0.

What the saved bytes support:

1. The same billing condition is a typed, documented error on REST and a *clarifying question* on MCP: `plan_call` puts the message in `clarifying_questions[]`, `questions[].question`, and `confirm_summary` (the field skills read aloud before asking to dial). A question-rendering host asks the operator "Insufficient CALL-E balance…?" as if it were missing task info.
2. `run_call` on a not-ready plan (`ready_to_run: false`, `confirm_token: null`) is still accepted (`isError false`) and mints a `run_id` with `status FAILED`. That FAILED run is shape-identical to a dial that failed and to a typo'd `run_id` (XR-704: "run_id not found." is also `status FAILED`, `isError false`). One word, three conditions, `isError false` on all.
3. The block is labelled `guardrails_reject` ("run_call rejected by guardrails.") though the message is billing — an operator concludes a content filter tripped and rewrites a fine goal.
4. `next_step` on `plan_call` is the string "Please try again later." — wrong action (a retry does nothing without top-up) and wrong type (documented as an object).
5. No `auth status`, CLI or MCP surface I tested reports remaining balance; three surfaces discovered it by failing.

Corrected: my first note read `confirm_token <4 chars>` — a redaction bug (`len(str(None))==4`). The token is `null`; there is no minted credential and no "exact pair to just run." The valid part is #2 (a run is minted for a not-ready plan). `live.py` redaction fixed.

Asks: MCP `plan_call` returns a typed error (`isError true`, code `insufficient_balance`) and no plan; `run_call` refuses a not-ready plan; a specific billing reason code instead of `guardrails_reject`; a documented remaining-balance field or a header on the 402.

Addendum: `calle call start` at zero balance stops correctly (`ok false`, `call_started false`, exit 1) but reports `error.code "plan_not_ready"`, "needs more information before it can run," and `retry_safe true` — retrying does nothing and the plan doesn't need info. The balance check also runs before every other `plan_call` validation (`+1234`, a national number, `+91112`, `+85012345678` all return the identical balance question with `ready_to_run false`), so an agent iterating on a plan at zero balance gets no field-level feedback. (`.data/live-2026-09-17/probes/plan_*.json`)

### LV-03 — The cached CLI access token advertises a ~1000-day lifetime, carries no refresh token, and `logout` makes no revoke request (observed); plus long-lived identity claims (worth questioning)

Corrected 17 Sep to observed facts only; exploitation verdicts removed.

Source: `~/.calle-mcp/cli/<hash>/token.json` (mode 0600, dir 0700 — permissions correct). Decoded locally; nothing sent. Personal values redacted.

Observed (saved):
- `token.expires_in` ≈ 86,399,930 s and the JWT's `exp − nbf` are both ≈ 1000 days (issued ~2026-08-19, expiry ~2029-05).
- No `refresh_token` and no `scope` in the cached response.
- JWT header `{"alg":"HS256","kid":"iams-jwt-dev-20260727-01"}`; payload carries `userId`, `loginAccount`, `username`, `isAdmin`, `clientId`, `companyId`, `roleInfo` (role labels incl. `BotLab_Admin`, a partner role), `timeZone "UTC-04:00"`, `iss "iams_management"`, `nbf`, `exp`. (`nbf`, not `iat` — not treated as issue time.)
- In an isolated fake cache, `auth logout` deleted the local files and issued **no** network request; `rg -i "revoke|refresh_token"` over `cli/lib` and `core/lib` (1ce9d77) is empty.

Not established (so not claimed): whether a copied token is still accepted after logout (no server-side revocation test run); whether the role labels grant elevated access (labels ≠ authorization); whether a `dev` key id or HS256 is used unsafely; that decodable JWT claims constitute a breach (they're expected). Removed the words "leaks," "genuine security item," and "stays valid server-side."

Asks (operational): document the access-token lifetime in the OAuth guide and `auth status`; offer a shorter lifetime and/or a documented rotation/revocation mechanism; make `logout` semantics explicit (local-only vs server-side); minimise client-visible identity claims. Refs: RFC 7519 (JWT), RFC 7009 (OAuth revocation).
