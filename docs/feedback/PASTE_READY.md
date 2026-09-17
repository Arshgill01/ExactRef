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

I built ExactRef around one question: when can a value someone reads out on the phone safely become a record? Chasing that turned into a lot of testing across the API, SDKs, CLI and MCP. The items below survived being re-checked against the shipped 0.7.0 SDKs, CLI 0.5.1, the live MCP endpoint and current docs on 17 Sep — and then a second, adversarial review that made me withdraw or narrow several of my own claims (see the honesty note). Each item marks what's live vs offline, and I only claim what a saved response supports. Where someone else already filed a defect I say so and don't claim the discovery.

--- Recovery and duplicate-submission risk ---

1. run_call is annotated idempotent while its prose forbids repeating it. (live) tools/list marks run_call idempotentHint true and destructiveHint true, but its description says "Do not call run_call more than once for the same plan_id." A client that trusts the hint may resubmit after a timeout. I did not test server dedup or observe a duplicate dial. Ask: document and test the same-plan/token guarantee, then make the annotation, the retry instructions and the CLI recovery agree with it.
2. A timed-out submit points you back at a second submit. (offline mock) A 15 s transport abort on run_call comes back with no call_started and no retry_safe; the dedicated CLI wraps it correctly (retry_safe false) but then suggests "call recover", which re-sends the same plan_id + confirm_token to run_call. I saw the resubmitted request on a mock transport; whether the server deduplicates it I did not test. Ask: every failed run_call reports call_started "unknown", retry_safe false; make recover a lookup, not a second run.
3. A missing readiness flag runs the call anyway (fail-open). (offline, reproduced against CLI 0.5.1 + source) call start blocks only when ready_to_run is exactly false (cli.js: `if (structuredPlan.ready_to_run === false)`); a plan with the field absent falls straight through to run_call, and the raw mcp call run_call path doesn't check readiness at all. The live tool requires ready_to_run true. Ask: require boolean true before submission, in the CLI and in the skill text.

--- Getting the result wrong, or not being able to read it ---

4. A call that never rang finished "completed", with no way on the read path to tell. (live) I placed a consented test call to my own phone; it never rang. The terminal object was status completed, failure_code null, task_completed false, with attempts[0].started_at null, provider_call_id null, transcript_turns []. structured_result was a schema-valid object of "" and "unknown" — allowed by my own schema, so these are missing answers, not invented ones. But nothing on GET says "did not connect," and the docs say a null result means "no schema-valid result from the evidence" while here a non-null empty object came back with an evidence list stating nothing was captured. Ask: expose a connection outcome and per-stage timestamps at the attempt level (the attempt enum already exists), and return null when there's no transcript.
5. One wrong character survived a full readback. (live, 5 Sep) After the recipient dictated an identifier and confirmed a character-by-character readback with "yes", the structured value was 07198SECTIST for an intended 07198FECTIST, and it passed schema validation. The extract matches the last spoken S-form, so this is transcript agreement, not a second channel — which is the point: "schema-valid + yes" is not proof. Root cause (ASR vs conversation vs extraction) isn't isolated. Ask: treat an in-band yes as agreement with the last spoken form; if a later typed value disagrees, return mismatch or null. (This is why ExactRef exists.)
6. A polling client can't see an extraction/validation failure. (docs + source review) The webhook contract names call.result_validation_failed, but I couldn't find a documented read-path field that distinguishes it from any other reason for a null result on GET/waitForResult. I did not run the impossible-schema live test. Ask: document the read-path representation, or expose a typed validation outcome on CallTask.

--- A client can't tell success from failure ---

7. An unknown run_id reads as a call that FAILED. (live, read-only, two ids) get_call_run on a made-up id returns isError false, status "FAILED", message "run_id not found."; the CLI exits 0 with ok true. A typo reads as "your call failed" (a TTL-expired id would plausibly read the same, untested). Ask: isError true with a not_found code, distinct from a real failed dial.
8. call status reports call_started true when nothing started. (offline) On a fresh machine with no token, call status returns call_started true, retry_safe true — the CLI hardcodes callStarted:true on both status paths, while call start uses a correct tri-state with "unknown." Anything logging call_started records a dial that never happened. Ask: "unknown" or omit on call status. Fix opened: https://github.com/CALLE-AI/call-e-integrations/pull/138
9. The two ways to call a tool disagree on success. (offline) With the same isError:true response, generic "mcp call" exits 0 with ok:true while the dedicated "call" command exits 1. Fix opened: https://github.com/CALLE-AI/call-e-integrations/pull/128
10. Insufficient balance is encoded three different ways. (live, saved responses) REST returns a clean 402 insufficient_balance (correct, and both SDKs map it correctly). But MCP plan_call returns ok/isError false and puts the billing message into clarifying_questions[] and confirm_summary (ready_to_run false, confirm_token null), so a question-rendering host asks the operator to "clarify" their empty wallet; a subsequent run_call mints a FAILED run whose activity is labelled guardrails_reject, as if a content filter tripped. I also couldn't find a documented remaining-balance field in the CLI/MCP surfaces I tested. Ask: a typed billing reason and a top-up action across surfaces; don't label billing as guardrails or missing task info.
11. create-and-wait loses the call_id on the post-create errors I tested. (offline, both SDKs, seven cases) POST succeeds, the follow-up GET fails (network, 502, deadline, call_not_ready, JSON/non-JSON 4xx), and the thrown error carries no call_id (timeouts include it only in message text); neither SDK adds an Idempotency-Key when you omit one. The Quickstart teaches exactly this helper. A paid call may exist with no handle to it. Ask: put call_id on every error after create; Quickstart should be create → persist id → wait, with an Idempotency-Key. Fix opened: https://github.com/CALLE-AI/server-sdk-typescript/pull/26

--- The docs and the wire disagree ---

12. "No answer" is spelled two ways and every skill only knows one. (live schema + source) The live status vocabulary includes "NO ANSWER" (with a space); the MCP guide says treat it as NO_ANSWER; all five shipped skills list only NO_ANSWER and poll on a fixed cadence until terminal; the CLI passes the string straight through. An agent risks polling forever after nobody picks up (a risk from the contract, not an observed loop). Ask: make status an enum, or put the guide's one-line mapping into every skill from a single source.
13. The server ships a typed next_step that no client interprets. (live + source) run_call/get_call_run return a structured next_step (poll_after_seconds, ask_user_for_retry_confirmation, report_blocked, and more), and plan_call accepts retry_confirmation_action. The CLI forwards the object, but a grep across the inspected CLI/core runtime and the skills finds no dedicated consumer — the polling cadence is hardcoded instead. Ask: one tested next_step consumer in @call-e/core that the CLI and skills import.
14. The tool descriptions are written for one host. (live) run_call says "the server will notify on completion… wait for the activity card updates"; the next tool says poll every 1–3 s. Cursor, Claude Code, Codex and the CLI have no activity card. I didn't observe an agent hang, but the guidance points a non-ChatGPT host at a push channel it doesn't have. Ask: host-neutral descriptions, one cadence, ChatGPT-specific prose behind _meta.
15. Non-JSON error bodies aren't wrapped in a typed error. (offline; the Python half is already server-sdk-python #39) A plain-text 404/405 becomes a raw json.JSONDecodeError in Python and a generic internal_error (documented retryable) in TS, so a wrong path can retry on a schedule. Ask: wrap non-JSON responses in a typed SDK error that keeps the HTTP status and a bounded body, and classify permanent 4xx vs transient gateway failures accordingly — not a blanket rule.
16. The "complete" Python example ignores the documented CALLE_BASE_URL. (current docs + offline stub) Authentication says the example scripts honor CALLE_BASE_URL; the actual complete example builds CalleClient(api_key=...) only, and the SDK defaults to the production host, so someone who exported a staging URL runs the sample against production. I proved the omission with a stub constructor; I did not send a request. Ask: pass base_url explicitly in the example and test the constructor args.
17. Smaller, confirmed: the Python waiter raises on call_not_ready instead of continuing (server-sdk-python #30, confirmed; fix opened PR 40); Python recipients=[{"phone":...}] leaves the phone→phones alias unnormalized that TS applies (fix opened PR 41); confirm_token is printed in call plan stdout with no redaction flag (fix opened PR 139); "calls create --wait" exits 0 on a failed/canceled call so && scripts treat failure as success.

On the credential cache (live, observed facts only): the cached CLI OAuth access token advertises a ~1000-day lifetime (expires_in and the JWT's exp−nbf both ≈1000 days), carries no refresh token, and in an isolated fake-cache test "auth logout" deleted the local files without making any network request (no revoke/refresh call exists in the inspected CLI/core source). File permissions are correct (0600). I did not test whether a copied token is still accepted after logout, and I'm not claiming the identity claims grant elevated access. Ask: document the token lifetime and logout/revocation semantics, offer a shorter lifetime and a rotation/revocation mechanism, and minimise client-visible identity claims.

Prior art I'm not claiming as mine: server-sdk-python #39/#30, server-sdk-typescript #17/#23, calle-docs #40/#41/#42 and the closed #43/#44. Fixes I opened are linked above, all still open except docs PR 60 (merged).

Honesty note: an adversarial re-review caught real over-reach in my own drafts, and I corrected it rather than shipping it. My "MCP rejects the SSE Accept header / GET hangs" report was wrong — a compliant dual-Accept POST works and GET returns a normal SSE stream; my old probe waited on an open stream body. I withdrew a "premature completion event" claim (the early event snapshot has no such event) and a "wrong write" framing (empty results are schema-permitted missing data), and I narrowed the duplicate-dial and token claims to what saved bytes actually show. These individual live tests are diagnostics, not reliability estimates.

Reproduction commands and redacted evidence excerpts: https://github.com/Arshgill01/ExactRef/tree/main/docs/feedback/lab

---

## Q-11 — What would have given you a better experience with our CALL-E documentation?

The docs are careful and mostly honest — the fixes I want are small and specific:

1. One runnable recovery example: create with an Idempotency-Key, persist the call_id, poll that id, reconcile without creating a replacement. The Quickstart currently teaches create-and-wait, which is the one helper that loses the id on error.
2. Separate three different clocks explicitly: the HTTP request timeout, the local polling deadline, and the actual call lifetime. State plainly that a local timeout does not hang up the call and there is no client cancel after accept.
3. Say that queued is not idle. On my live call, top-level status stayed queued for ~12 polls while the attempt was already in_progress; the Calls table still defines queued as only "the call task is queued."
4. Reconcile the words for "done" and, especially, billing: Calls "completed" (lifecycle), MCP "COMPLETED" (run finished), and task_completed (a post-hoc judgment) are three different things — say so in one place. Then explain how task_completed and evidence relate to the new Success-fee charge and where an operator can reconcile whether a given call was billed for "business success"; today no API field ties them together.
5. Label the three different objects called result: JSON-RPC response.result, the CLI's result.structuredContent, and get_call_run's nested result{} where summary/transcript live. Shipped skills still read summary at the top level.
6. Add an interface map (to the docs and to llms.txt): REST Calls/Goals, the two packages that expose a "calle" binary, MCP, and the skills — and which of them accept a custom result_schema (MCP can't). Today llms.txt lists no MCP, CLI or skills line at all, so an agent starting from the site never finds the MCP contract.
7. Document the read path's quirks: result_validation_failed is webhook-only, canceled arrives as webhook call.failed (branch on data.status), and CallEvent.status reflects the call's status at read time rather than the event's own moment (in one saved snapshot every row, including a "task created" update, carried status queued). Say which field a polling client should trust.
8. Retention and install: ttl_seconds 0 means keep the number and transcript indefinitely, the default is unpublished, and there's no documented delete; the hosted install guide still teaches "npm install -g" and bare "calle" while the skill it installs forbids exactly that. Frame this as missing documented retention/deletion controls.

A few smaller documentation fixes (PRs opened for the first three): the onboarding README lists POST /calle/webhook as if it were a CALL-E endpoint (PR 136); the regions table gives the US "English, Indonesian", which is at least worth confirming (PR 137); the Devpost "API Reference" link lands on the Quickstart (calle-docs PR 60, merged — deployment not re-verified); a couple of webhook samples don't compile standalone (they may need a handler wrapper); and the live OpenAPI's own placeholder phone examples don't match its own E.164 pattern.

---

## Q-13 — Is there any other feedback you'd like to provide?

My honest read after living in this for two weeks: the Calls API is already enough to build a real bounded workflow — durable create, poll, a small result schema, transcript turns. What I still can't trust on my own is an exact-character identifier. Schema-valid plus a confirmed readback gave me 07198SECTIST for 07198FECTIST on a live call, and a call that never connected still returned a schema-valid result. So I had to build a write-gate (ExactRef), because no official surface names the state "spoken, not verified." A valid JSON result, a completed conversation, business success, and an independently verified fact are four different things, and right now they share one word.

The pattern under most of my findings is the same: the server already speaks a better contract than its clients read. tools/list carries a typed next_step, a confirm_expires_at, a retry_confirmation_action, and a status vocabulary that includes "NO ANSWER" — and not one shipped client (CLI, five skills, the Cursor plugin) reads any of it. They hardcode a 10 s loop, a terminal list spelled NO_ANSWER, forward the confirm_token they're told not to print, and report call_started before login. Meanwhile the descriptions those clients receive were written for ChatGPT's activity card. So the biggest single improvement isn't a new feature — it's a small @call-e/core module that consumes next_step (honour poll_after_seconds, stop on report_result/report_blocked, surface ask_user_for_retry_confirmation as a question and never as an auto-retry), owns the terminal-status set including "NO ANSWER", checks confirm_expires_at, and redacts confirm_token — then the CLI and every skill import it instead of paraphrasing the guide.

So the negatives read as a sample and not a verdict, here's what I checked and found genuinely solid (scoped to what I actually ran): across 35 offline SDK/CLI cases repeated three times, successful calls returned normally, explicit Idempotency-Keys were preserved, and a literal ready_to_run false correctly blocked execution; telemetry is default-on but documented with three working opt-outs and an anonymous payload; publint is clean on both published packages; the installed SDK/CLI files match the published archives; the live 402 and 401 envelopes match the docs, query-string API keys are rejected with the same 401 as a missing header, and the MCP OAuth bearer is not accepted as a REST key; the live MCP transport accepts a compliant dual-Accept POST and returns SSE on GET (which is what made me withdraw my earlier streaming complaint). These make the findings above more specific; none of them establishes a phone-call reliability rate. And the review that produced this list also made me retract real over-reach of my own — I'd rather hand you a smaller set of things that are actually true.
