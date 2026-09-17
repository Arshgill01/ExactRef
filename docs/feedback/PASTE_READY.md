# Paste-ready CALL-E Feedback Survey

**Status: draft for you to review. Not submitted.** Form: [CALL-E Feedback Survey](https://docs.google.com/forms/d/e/1FAIpQLSfGWkt2F_ED6aLatQjtjBX8YEpBVQ47A39yeDd1KQRKX488Lg/viewform). You fill: [USER_OWNED.md](USER_OWNED.md) (Q-01–04, Q-08, Q-09, Q-12, Q-14–17).

Google Forms strips formatting, so every answer below is plain text. Paste the body only. The one repo link goes at the very end of Q-10, where it belongs — the judges read these answers; the repo is there if they want the raw envelopes.

---

## Q-05 — Did you start a project for this hackathon after July 23, 2026? *

Yes.

---

## Q-06 — If you didn't finish and submit your project, why not?

Leave blank. ExactRef was finished and submitted: https://devpost.com/software/exactref

---

## Q-07 — Which CALL-E interfaces did you use? *

Check SDK, API, MCP, and CLI.

I used the Calls API and the Python server SDK for the live calls, both Python and TypeScript SDK 0.7.0 plus the CLI 0.5.1 for offline error-injection, and the live MCP endpoint for planning and read-only lookups. Where a finding is offline I say so. I did not tick SKILL: reading a skill's source is not invoking it.

---

## Q-10 — What bugs or issues did you run into while using CALL-E, if any?

I built ExactRef around one question: when can a value someone reads out on the phone safely become a record? Chasing that turned into a lot of testing across the API, SDKs, CLI and MCP. The items below are the ones that survived being re-checked against the shipped 0.7.0 SDKs, CLI 0.5.1, the live MCP endpoint and current docs on 17 Sep. A few things I reported earlier turned out to be my mistake and I've dropped them (see the honesty note at the end). Where someone else already filed a defect I say so and don't claim the discovery.

Every item that could be verified was verified against real output; I've kept the raw envelopes. What's live vs offline is marked on each.

--- It places or proposes a second call ---

1. run_call is annotated idempotent but told never to repeat. (live) tools/list marks run_call destructiveHint true AND idempotentHint true, while its own description says "Do not call run_call more than once for the same plan_id." A host that trusts the hint retries the dial after a timeout. Ask: idempotentHint false on any tool that can place a call, or document and test a real dedup guarantee.
2. A timed-out submit points you back at a second submit. (offline) A 15 s transport abort on run_call comes back with no call_started and no retry_safe; the dedicated CLI wraps it correctly (retry_safe false) but then suggests "call recover", which re-sends the same plan_id + confirm_token to run_call. I observed the resubmission on a mock; I did not prove a duplicate dial. Ask: every failed run_call reports call_started "unknown", retry_safe false; make recover a lookup, not a second run.
3. A plan that can't run still hands you a run trigger. (live) At zero balance, plan_call returned ok/isError false and minted a plan_id + confirm_token; run_call on them was accepted, minted a run_id, and stored a FAILED run. So an unrunnable plan still produces the exact pair an agent needs to "just try running it." Ask: no plan_id/confirm_token for a plan that can't run; run_call should refuse a not-ready plan.

--- It writes or returns the wrong value ---

4. A call that never rang came back completed, with a schema-valid empty result. (live, this is the one that worries me most) I placed a consented test call to my own phone; it never rang. 36 minutes later GET showed status completed, failure_code null, task_completed false, attempts[0].started_at null, provider_call_id null, transcript_turns []. But structured_result was a full object of "" and "unknown" that passed the schema, and the docs say a null result means "no schema-valid result from the evidence." An operator following that rule writes six empty fields as if they were answers. Ask: return structured_result null when no transcript exists, and expose a connected:false / no-answer signal at the attempt level (the attempt status enum already exists).
5. One wrong character survived a full readback. (live, 5 Sep) After the recipient dictated an identifier and confirmed a character-by-character readback with "yes", the structured value was 07198SECTIST for an intended 07198FECTIST, and it passed schema validation. The extract matches the last spoken S-form, so this is transcript agreement, not a second channel — which is exactly the point: "schema-valid + yes" is not proof. Ask: treat an in-band yes as agreement with the last spoken form; if a later typed value disagrees, return mismatch or null. (This is why ExactRef exists.)
6. The result validation failure never shows up on the read path. (offline) Docs describe call.result_validation_failed, but it's webhook-only; GET and waitForResult show completed + structured_result null — identical to a plain extract miss. A polling operator can't tell "the model refused the write" from "nothing to extract." Ask: put failure_code result_validation_failed on the CallTask.

--- A client can't tell success from failure ---

7. An unknown run_id reads as a call that FAILED. (live, read-only, reproduced on two ids) get_call_run on a made-up id returns isError false, status "FAILED", message "run_id not found."; the CLI exits 0 with ok true. A typo, or an id past its TTL, reads as "your call failed." Ask: isError true with a not_found code, distinct from a real failed dial.
8. call status swears the call started when it never did. (offline) On a fresh machine with no token, call status returns call_started true, retry_safe true — the CLI hardcodes callStarted:true on both status paths, while call start uses a correct tri-state with "unknown." Anything logging call_started records a dial that never happened. Ask: "unknown" or omit on call status. Fix opened: https://github.com/CALLE-AI/call-e-integrations/pull/138
9. The two ways to call a tool disagree on success. (offline) With the same isError:true response, generic "mcp call" exits 0 with ok:true while the dedicated "call" command exits 1. Fix opened: https://github.com/CALLE-AI/call-e-integrations/pull/128
10. Out of money looks like a content-guardrail block. (live) At zero balance, the MCP activity feed labels the rejection guardrails_reject ("run_call rejected by guardrails."). An operator concludes their goal tripped a safety filter and rewrites a perfectly fine task. Meanwhile no surface — auth status, CLI, MCP — reports remaining balance at all; I only found the account was empty by failing three times. Ask: reserve guardrails_reject for guardrails; expose balance/remaining calls somewhere.
11. create-and-wait loses the call_id on every post-create error. (offline, both SDKs) POST succeeds, the follow-up GET fails (network, 502, deadline), and the thrown error has no call_id (TS TypeError with empty keys; Python CalleTimeoutError with none); neither SDK adds an Idempotency-Key when you omit one. The Quickstart teaches exactly this helper. A paid call exists and the process has no handle to it — so the natural next move is a second dial. Ask: put call_id on every error after create; Quickstart should be create → persist id → wait, with an Idempotency-Key. Fix opened: https://github.com/CALLE-AI/server-sdk-typescript/pull/26

--- The docs and the wire disagree ---

12. "No answer" is spelled two ways and every skill only knows one. (live schema + source) The live status vocabulary includes "NO ANSWER" (with a space); the MCP guide says treat it as NO_ANSWER; all five shipped skills list only NO_ANSWER and poll every ~10 s until terminal; the CLI passes the string straight through. An agent can poll forever after nobody picks up. Ask: make status an enum, or put the guide's one-line mapping into every skill from a single source.
13. The server ships a typed next_step that nothing reads. (live + source) run_call/get_call_run return a structured next_step (poll_after_seconds, ask_user_for_retry_confirmation, report_blocked, and more), and plan_call accepts retry_confirmation_action. A grep across the CLI and all skills finds zero consumers — everyone hardcodes a 10 s loop instead. The richest part of the contract is unused. Ask: one next_step consumer in @call-e/core that the CLI and skills import.
14. The tool descriptions are written for one host. (live) run_call says "the server will notify on completion… wait for the activity card updates"; the next tool says poll every 1–3 s. Cursor, Claude Code, Codex and the CLI have no activity card, so an MCP-native agent ends its turn waiting for a push that never arrives. Ask: host-neutral descriptions, one cadence, ChatGPT-specific prose behind _meta.
15. The Python SDK doesn't turn a non-JSON error into a CalleError. (offline; the Python half is already server-sdk-python #39) A plain-text 405/404 from the API becomes a raw json.JSONDecodeError in Python and an internal_error (documented retryable) in TS, so a wrong path retries on a schedule. Ask: non-JSON bodies map to a non-retryable error in both SDKs, raw body preserved.
16. Smaller, confirmed: the Python waiter raises on call_not_ready instead of continuing (server-sdk-python #30, confirmed; fix opened PR 40); Python recipients=[{"phone":...}] silently drops the phone→phones alias that TS applies (fix opened PR 41); confirm_token is printed in call plan stdout with no redaction flag (fix opened PR 139); "calls create --wait" exits 0 on a failed/canceled call so && scripts treat failure as success.

One more, from the credential cache (live, worth a serious look): the CLI's OAuth access token on disk is an HS256 JWT valid for ~1000 days (issued 19 Aug 2026, expires 15 May 2029), with no refresh token and no revoke — "auth logout" only deletes the local file; the token stays valid server-side. Its kid is "iams-jwt-dev-…", and the payload leaks tenant internals to a public sign-up account (role names including BotLab_Admin and a partner role, isAdmin, clientId, companyId). File permissions are correct (0600), but a backup or a copied home directory is a three-year dialling credential. Ask: short-lived access + refresh token, a real server-side revoke on logout, and strip role/tenant claims from the client token.

Prior art I'm not claiming as mine: server-sdk-python #39/#30, server-sdk-typescript #17/#23, calle-docs #40/#41/#42 and the closed #43/#44. Fixes I opened, all linked above and still open except docs PR 60 (merged).

Honesty note: I withdrew two earlier claims after re-checking. My "MCP rejects the SSE Accept header / GET hangs" report was wrong — a compliant dual-Accept POST works and GET returns a normal SSE stream; my old probe waited on an open stream body. And I narrowed the "recover places a second call" and "idempotent = duplicate dial" claims to what I actually observed (a resubmitted request on a mock), not a proven double dial. n=1 lives calls are diagnostics, not rates.

Full commands and raw (redacted) envelopes for everything above: https://github.com/Arshgill01/ExactRef/tree/main/docs/feedback/lab

---

## Q-11 — What would have given you a better experience with our CALL-E documentation?

The docs are careful and mostly honest — the fixes I want are small and specific:

1. One runnable recovery example: create with an Idempotency-Key, persist the call_id, poll that id, reconcile without creating a replacement. The Quickstart currently teaches create-and-wait, which is the one helper that loses the id on error.
2. Separate three different clocks explicitly: the HTTP request timeout, the local polling deadline, and the actual call lifetime. State plainly that a local timeout does not hang up the call and there is no client cancel after accept.
3. Say that queued is not idle. On my live call, top-level status stayed queued for ~12 polls while the attempt was already in_progress; the Calls table still defines queued as only "the call task is queued."
4. Name the four words that all mean "done" and none of which mean business success: Calls "completed" (lifecycle), MCP "COMPLETED" (run finished), task_completed (a post-hoc judgment), and the new Success-fee "business success criteria." No API field records the last one.
5. Label the three different objects called result: JSON-RPC response.result, the CLI's result.structuredContent, and get_call_run's nested result{} where summary/transcript live. Shipped skills still read summary at the top level.
6. Add an interface map (to the docs and to llms.txt): REST Calls/Goals, the two packages that expose a "calle" binary, MCP, and the skills — and which of them accept a custom result_schema (MCP can't). Today llms.txt lists no MCP, CLI or skills line at all, so an agent starting from the site never finds the MCP contract.
7. Document what GET will never show you: result_validation_failed is webhook-only, canceled arrives as webhook call.failed (branch on data.status), event type can be call.in_progress while event status is queued, and CallEvent.status is the current status joined at read time (my two event pulls of the same call, minutes apart, showed every row flipping from queued to completed).
8. Retention and install: ttl_seconds 0 means keep the number and transcript forever, the default is unpublished, and there's no delete; the hosted install guide still teaches "npm install -g" and bare "calle" while the skill it installs forbids exactly that.

Small, cheap, embarrassing ones (fixes opened for the first three): the onboarding README lists POST /calle/webhook as if it were a CALL-E endpoint (PR 136); the regions table gives the US "English, Indonesian" (PR 137); the Devpost "API Reference" link lands on the Quickstart (calle-docs PR 60, merged); a couple of webhook code samples don't compile as published; the live OpenAPI's own phone examples fail its own E.164 pattern.

---

## Q-13 — Is there any other feedback you'd like to provide?

My honest read after living in this for two weeks: the Calls API is already enough to build a real bounded workflow — durable create, poll, a small result schema, transcript turns. What I still can't trust on my own is an exact-character identifier. Schema-valid plus a confirmed readback gave me 07198SECTIST for 07198FECTIST on a live call, and a call that never connected still returned a schema-valid result. So I had to build a write-gate (ExactRef), because no official surface names the state "spoken, not verified." A valid JSON result, a completed conversation, business success, and an independently verified fact are four different things, and right now they share one word.

The pattern under most of my findings is the same: the server already speaks a better contract than its clients read. tools/list carries a typed next_step, a confirm_expires_at, a retry_confirmation_action, and a status vocabulary that includes "NO ANSWER" — and not one shipped client (CLI, five skills, the Cursor plugin) reads any of it. They hardcode a 10 s loop, a terminal list spelled NO_ANSWER, forward the confirm_token they're told not to print, and report call_started before login. Meanwhile the descriptions those clients receive were written for ChatGPT's activity card. So the biggest single improvement isn't a new feature — it's a small @call-e/core module that consumes next_step (honour poll_after_seconds, stop on report_result/report_blocked, surface ask_user_for_retry_confirmation as a question and never as an auto-retry), owns the terminal-status set including "NO ANSWER", checks confirm_expires_at, and redacts confirm_token — then the CLI and every skill import it instead of paraphrasing the guide.

So the negatives read as a sample and not a verdict, here's what I tested and found genuinely solid: telemetry is default-on but documented with three working opt-outs and an anonymous payload; publint is clean on both packages; neither tarball ships tests, .env or source maps; python has py.typed; the live OpenAPI 0.7.0 has no path, status, or nullability drift against the SDK repos and tsc --strict on the generated types is clean; query-string API keys are rejected with the same 401 as a missing header; the MCP OAuth bearer is not accepted as a REST key; TLS is valid; the 402/401 error envelopes match the docs exactly; and file permissions on the token cache are correct (0600). I also caught and withdrew two of my own wrong claims (see Q-10). I'm not trying to inflate a bug count — I'm trying to hand you the few reproducible things that would make an agent trust the phone.
