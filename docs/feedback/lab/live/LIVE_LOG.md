# Live lab — 2026-09-17

Live CALL-E calls placed with the account owner's explicit authorisation, to the account owner's own phone, with the owner beside the phone. This supersedes the earlier lab rule of "no live calls"; the product board's own rule (fixture replay only) is unchanged.

Raw objects, numbers and transcripts live in `.data/live-2026-09-17/` (not committed). Everything in this file is redacted. Runner: `live.py` (REST), `@call-e/cli` 0.5.1 (MCP path). Webhook sink: `webhook_sink.py` behind an ngrok tunnel; every REST create in this lab carries `webhook_url`.

Account: API key from the OffHire `.env.local`; CLI OAuth login usable (expires 2029-05-15). Region: India (`IN`, supported, International). Pool: shared numbers, 1 simultaneous call (14 Sep changelog), so calls are sequential.

## Ground rules

- One create per case. No automatic redial. A local timeout is not a hangup: keep polling the existing id.
- The recipient is told the protocol before each call and reports what happened on the phone (rang / did not ring / answered).
- The recipient types the intended identifiers into this file before the call (second channel). The extract is compared character by character afterwards.
- Every claim promoted to the form must point at a raw file in `.data/` by name and at a redacted excerpt here.

## Case index

| Case | Path | Question | Status |
| --- | --- | --- | --- |
| C-01 (Codex live-01, 07:12Z) | REST | Does dictation + clarification produce an exact reference? | done — completed, 204 s accept→terminal, 12 polls `queued` with `in_progress` attempt |
| C-02 (Codex live-02, 07:21Z) | REST | Same prompt, recipient-only card with a correction | done — phone never rang; see finding LV-01 |
| L-01 | MCP/CLI | What does a no-answer look like on `get_call_run` and in `calle call status`? | planned |
| L-02 | MCP/CLI | Does `run_call` twice on one `plan_id` + `confirm_token` dial twice? | planned |
| L-03 | REST | Three dictated identifiers with F/S, 0/O, B/D, I/L/1 traps; `Idempotency-Key` replay after terminal; webhook capture | planned |
| L-04 | REST | Schema the answer cannot satisfy (`integer`, max 3, participant says seven): what do GET and the webhook show? | planned |

## Findings

### LV-01 — A call that never rang came back `completed`, `failure_code: null`, with a schema-valid result, 36 minutes later

Source: Codex case live-02, `call_t2SxwVonYPtacjRhntODcw`, created 2026-09-17T07:21:52Z. Recipient report at the time: "only received the first call" (the C-01 call). Codex polled 50 times over 619 s and stopped with top-level `queued`, one attempt `in_progress`, zero transcript turns. Re-read at 09:20Z:

```
status: completed          completed_at: 07:58:16Z   (36 min 24 s after create)
failure_code: null         failure_message: null
task_completed: false      completion_confidence: {score 0.58, label medium}
recipients[0].status: completed
attempts[0]: status completed, started_at null, completed_at null, provider_call_id null, transcript_turns []
structured_result: {reference "", pickup_status "unknown", pickup_timing "", reference_quote "", timing_resolved "unknown", readback_confirmed "unknown"}
summary: "The first call did not connect or complete; the recipient may be busy or unavailable, so you can confirm retrying in about 45 minutes, provide a different retry time, or ask to retry immediately."
evidence: ["No recipient response or transcript was captured.", "The required fictional pickup reference and pickup details were not obtained.", "The call record does not show usable call timing or duration."]
```

Events (`GET /v1/calls/{id}/events`, 10 rows, `next_cursor` null):

```
07:22:09 call.started      "run_call started."
07:22:11 call.in_progress  "botlab create bot."
07:22:29 call.in_progress  "calling resolve robot id."
07:22:32 call.in_progress  "calling create task."
07:22:33 call.completed    "calling task created."               <- first call.completed, 35 min before the real one
07:22:33 call.updated      "calling task status=pending"
07:57:46 call.updated      warning "calling task finished but intention is pending; waiting for detail sync."
07:57:57 call.updated      warning "calling detail sync wait timed out with pending intention."
07:57:57 call.updated      "calling task status=finished"
07:58:13 call.completed    "calling task completed with status=finished"
```

Every event row now carries `status: completed`. In Codex's 07:32Z snapshot the same rows carried `status: queued` — `CallEvent.status` is the call's current status joined at read time, not the status when the event happened.

What this means, against the published contract:

1. The Calls guide says a `completed` state "does not establish that a person answered", and the errors page says the Calls API "does not guarantee a distinct no-answer" value. Both are honest. But the guide also says `structured_result` is `null` when "CALL-E did not produce a schema-valid whole-task result from the available evidence". Here the evidence list says no response and no transcript were captured, and the result is a non-null object of empty strings and `"unknown"` enums that passes the schema. An operator following the documented rule (`null` = no result) writes six empty fields.
2. No documented field says "this call never connected". The signals are `attempts[0].started_at: null`, `provider_call_id: null`, `transcript_turns: []`, which no guide names as the no-connect signature.
3. The summary is addressed to a chat user with a retry widget ("you can confirm retrying in about 45 minutes ... or ask to retry immediately"). Through the REST Calls API there is no retry confirmation to give; an agent that pastes the summary to the operator is now proposing a redial.
4. Two `call.completed` events for one call; the first fires when the provider task is created, 35 minutes before anything terminal. Anyone consuming the events feed (not the webhook) on type `call.completed` acts 35 minutes early.
5. Event messages are internal pipeline strings ("botlab create bot", "resolve robot id", "intention is pending", "detail sync"), and `call.started` says "run_call started." on a REST-created call.
6. Top-level `queued` for 36 minutes while the provider task existed. The C-01 call, same account, same number, 10 minutes earlier, took 204 s end to end. Whatever stalled ("intention pending" for 35 min) was invisible on GET.

Asks: a recipient/attempt-level `connected: false` (or `attempt.status: no_answer` — the attempt enum already exists) and `structured_result: null` when no transcript exists; one `call.completed` per call; summaries without channel-specific retry prose; document that `CallEvent.status` is the current status, or snapshot it.

Not claimed: why the call did not ring (carrier, pool, provider) — not isolated. Whether the 36-minute stall is typical — n=1.

### LV-02 — Out of balance: REST says `402 insufficient_balance`; MCP says `ok`, mints a plan and a run, and calls it a guardrails rejection

Observed 2026-09-17 09:35Z when the account balance ran out after the two Codex calls (billing not visible through any API; the operator did not know).

REST, `POST /v1/calls` (live.py case L01R, `.data/live-2026-09-17/L01R/created-*.json`):

```
HTTP 402  {"error": {"code": "insufficient_balance", "message": "Insufficient CALL-E balance. Please top up at https://dashboard.heycall-e.com/account/billing and try again.", "details": {"reason_code": "iams_balance_insufficient"}}}
```

Exactly what errors.md promises: stable code, documented recovery ("resolve the account's billing condition"). No call id, nothing to poll. Correct.

MCP, `calle call plan` → `plan_call` (`.data/live-2026-09-17/L01/plan.json`):

```
ok true, isError false
plan_id "p86YC19F1", ready_to_run false, confirm_token <4 chars>, expires_at +24h
next_step: "Please try again later."            (a string on plan_call; an object on run_call/get_call_run)
clarifying_questions: ["Insufficient CALL-E balance. Please top up at ... and try again."]
questions: [{key "question_1", question "Insufficient CALL-E balance. ..."}]
confirm_summary: "Insufficient CALL-E balance. ..."
```

MCP, `mcp call run_call` with that plan_id + confirm_token (`.data/live-2026-09-17/L01/run_call_not_ready.json`):

```
ok true, isError false, exit 0
status "FAILED", run_id "fYdWmS2Fhj3lI9Fxi8DG1A", message "Insufficient CALL-E balance. ..."
activity: [{kind "guardrails_reject", level warning, message "run_call rejected by guardrails."}]
next_step: {action "report_blocked", instruction "Report the current terminal run status. Do not start another call."}
```

`calle call status --run-id fYdWmS2Fhj3lI9Fxi8DG1A` → `ok true`, `isError false`, `status FAILED`, exit 0.

What this means:

1. The same billing condition is a typed, documented error on REST and a *question for the user* on MCP. `plan_call` puts the account error in `clarifying_questions[]` and `questions[].question`, so a host that renders questions asks the operator "Insufficient CALL-E balance. Please top up…?" as if it were a clarification, and `confirm_summary` — the field the skills read aloud before asking permission to dial — is the billing message.
2. A `plan_id` and `confirm_token` are issued for a plan that cannot run; `run_call` on them is accepted (`isError false`), a `run_id` is minted and a FAILED run is stored. That FAILED run is indistinguishable in shape from a dial that failed, from a typo'd run_id (XR-704: `run_id not found.` is also `status FAILED`, `isError false`), and now from "you have no money". Three different conditions, one status word, and `isError false` on all three.
3. The activity feed labels the billing block `guardrails_reject` — "run_call rejected by guardrails." An operator reading activity concludes their task was blocked by a content guardrail and rewrites the goal.
4. `next_step` on `plan_call` is the string "Please try again later." — the wrong instruction (retrying does nothing without a top-up) and the wrong type (the guide documents `next_step` as an object with `action`).
5. Balance is invisible: no API, CLI or MCP surface reports it. Three surfaces discovered it by failing.

Asks: MCP `plan_call` should return a typed error (`isError true`, code `insufficient_balance`) and no plan; `run_call` should not mint a run for a not-ready plan; `guardrails_reject` reserved for guardrails; a balance/remaining-calls read somewhere (`auth status`, `GET /v1/account`, or a header on 402).

Addenda (same session):

- `calle call start` at zero balance stops correctly (`ok false`, `call_started false`, exit 1) but reports `error.code "plan_not_ready"`, message "Call plan needs more information before it can run: Insufficient CALL-E balance…", and `retry_safe true`. Retrying does nothing; the plan does not need information. (`.data/live-2026-09-17/L01/call_start_zero_balance.json`)
- Both SDKs map the live 402 correctly: TS `CalleAPIError {code "insufficient_balance", status 402, details.reason_code "iams_balance_insufficient"}`; Python `CalleAPIError` with `code "insufficient_balance"`, `status_code 402`. `createAndWait` / `create_and_wait` throw the same before any call exists. Correct.
- The balance check runs before every other `plan_call` validation: `to_phones` of `+1234`, a 10-digit national number, `+91112` and `+85012345678` all return the identical balance question, `ready_to_run false`, `isError false`, and each mints a `plan_id`. An agent iterating on a plan at zero balance gets no validation feedback at all. (`.data/live-2026-09-17/probes/plan_*.json`)

Live tests L-01..L-04 are not being run: the owner declined to top up. Not claimed from them.

### LV-03 — The CLI's OAuth access token is a 1000-day HS256 JWT with a `dev` key id, internal tenant roles in the claims, and no revocation path

Source: `~/.calle-mcp/cli/<hash>/token.json` on this machine (mode 0600, directory 0700 — the file permissions are right). Claims decoded locally; nothing sent anywhere. Personal values redacted.

```
issued_at 2026-08-19T16:41:56Z   expires_at 2029-05-15T16:40:46Z   token.expires_in 86399930   (≈ 1000 days)
token: { access_token <833 chars>, expires_in, token_type }      no refresh_token, no scope
JWT header:  {"alg": "HS256", "kid": "iams-jwt-dev-20260727-01", "typ": "JWT"}
JWT payload: userId, loginAccount <email>, username, isAdmin 0, clientId, companyId, companyName/companyCode "third_user_<username>",
             roleInfo: [Administrator, Fujifilm_partner, BotLab_Admin_Approval, BotLab_Admin], timeZone "UTC-04:00", iss "iams_management",
             nbf 1787156645, exp 1873557645
```

`calle auth logout` "Remove local token, login, and call recovery cache" — `packages/cli/lib/cli.js` and `packages/core/lib/*.js` (1ce9d77) contain no revoke or refresh call; `rg -i "revoke|refresh_token"` over both is empty. The OAuth guide's only lifetime statement is "never expose … refresh tokens", and the CLI's `--min-ttl-seconds` default is 300 s against a token with 2.7 years left.

What this means:

1. A bearer that can place paid phone calls lives on disk for ~1000 days, cannot be rotated by the client (no refresh token) and cannot be revoked by the client (`logout` deletes the file; the token stays valid). A laptop backup, a copied home directory or a leaked `--cache-root` is a three-year dialling credential.
2. The signing key id says `dev` and the algorithm is symmetric (HS256): any service that verifies these tokens holds the key that mints them. That is the vendor's business, but the `kid` on a production token is a smell worth a look.
3. The payload leaks tenant internals to a hackathon user: role names `Fujifilm_partner`, `BotLab_Admin_Approval`, `BotLab_Admin` on an account created through the public sign-up, plus `isAdmin`, `clientId`, `companyId`, and a `timeZone` of UTC-04:00 for a user in UTC+05:30. None of these are needed by the MCP server to authorise `run_call`.
4. The OAuth guide tells agents not to expose refresh tokens; there are none. It says nothing about the access-token lifetime, which is the thing an operator would actually want to know.

Asks: short-lived access token + refresh token (or at most days, not years); a server-side revoke on `auth logout` and a "sign out everywhere" in the dashboard; strip role/tenant claims from the client-facing token or move to an opaque token; document the lifetime in the OAuth guide and in `auth status`.
