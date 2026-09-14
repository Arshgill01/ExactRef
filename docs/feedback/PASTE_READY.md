# Paste-ready CALL-E Feedback Survey

**Status: draft for you to review. Not submitted.** Form: [CALL-E Feedback Survey](https://docs.google.com/forms/d/e/1FAIpQLSfGWkt2F_ED6aLatQjtjBX8YEpBVQ47A39yeDd1KQRKX488Lg/viewform). Living file: [FORM_QUESTIONS_AND_LIVING_ANSWERS.md](FORM_QUESTIONS_AND_LIVING_ANSWERS.md). New evidence: [NEW_FINDINGS_2026-09-13.md](NEW_FINDINGS_2026-09-13.md). You fill: [USER_OWNED.md](USER_OWNED.md).

Do not submit until Q-01–Q-04, Q-08, Q-09, Q-12, Q-16 are yours. Post Discord first if you will check Q-14.

---

## Q-05 — Did you start a project for this hackathon after July 23, 2026? *

**Yes**

Public work on this hackathon in my tree starts 2026-09-05 (platform research and one diagnostic call), with product repos on 2026-09-08 and 2026-09-10, and the ExactRef package on 2026-09-13. All after 23 July 2026.

---

## Q-06 — If you didn't finish and submit your project, why not?

Leave blank while the 14 September deadline is still ahead.

---

## Q-07 — Which CALL-E interfaces did you use? *

Check **SDK**, **API**, **MCP**, and **CLI**.

- **SDK:** one authorized 2026-09-05 call, Python server SDK 0.7.0. TypeScript `@call-e/calle` 0.7.0 wait predicates re-read from source on 2026-09-13.
- **API:** that live call used POST `/v1/calls` + GET until a terminal result.
- **CLI:** 2026-09-13 `npx @call-e/cli auth status` (usable) and `npx @call-e/cli mcp tools`.
- **MCP:** same `mcp tools` call against `https://seleven-mcp-sg.airudder.com/mcp/openagent_oauth`.

Do **not** check SKILL until the ExactRef / official `calle` skill has actually been invoked in an agent turn. Do not check “None - documentation review only.” Reading `dist/` is not CLI use. Do not treat issue 109 as “we used CLI.”

---

## Q-10 — What bugs or issues did you run into while using CALL-E, if any?

Three buckets. No private numbers or transcripts attached.

**A. One live English call, 2026-09-05, Python SDK 0.7.0, Calls API, one create, one attempt. Not a rate.**

1. **Exact identifier (high).** After a full readback and “yes,” structured reference was `07198SECTIST`; the intended value was `07198FECTIST`. Schema checks passed. The extract matches the last in-band S-form the recipient confirmed. That is transcript consistency, not a second channel, and not proof that CALL-E independently “dropped an F.” Stage (ASR vs conversation vs extraction) not isolated. Impact: one character is enough to write the wrong operational id. Ask: treat in-band yes as agreement with the last spoken form; if a later typed value disagrees, return mismatch or null.
2. **Contradiction vs summary (high).** Recipient said “Sunday morning” and “5:00 PM.” Structured field kept the conflict; summary became Sunday 5 PM. Ask: one clarification, then null; summary must not pick a clock time the structured field left open.
3. **Top-level status (medium, DX).** GET call `status` stayed `queued` while attempt/events showed activity. Poll-until-terminal worked (~4m39s accept→result). Ask: top-level `in_progress` when an attempt is live, or document that `queued` can include an active attempt.
4. **Stitched “verbatim” evidence (medium, write trust).** Schema asked for a short verbatim recipient quote on the reference. The returned field joined later fragments with `USER:` and ellipses. A sibling evidence field on the same object matched one turn exactly. Ask: if the schema says verbatim and no single span exists, return empty or label the stitch. Do not treat a concatenation as proof of the identifier.
5. **Events page one is not the log (medium, DX).** GET `/v1/calls/{id}/events` returned 100 rows, a nonempty `next_cursor`, and `status: queued` on every event, including `type: call.in_progress`. That page ended about two minutes before attempt hangup. Ask: document default page size, that `next_cursor` means “not done,” and that event `type` and event `status` can disagree.

**B. MCP / CLI / Cursor skill, 2026-09-13, no second phone call.**

6. **Fourth MCP tool (docs/contract).** `calle mcp tools` returned `plan_call`, `run_call`, `get_call_run`, and `track_ui_events`. Official MCP guide and the Cursor skill describe three tools. `track_ui_events` is not documented in the integrations docs I cloned. Workaround: ignore the fourth tool. Ask: document or hide it for agent clients.
7. **Cursor skill 0.1.2 vs live `get_call_run` shape.** The official Cursor plugin still reads `summary` / `transcript` at the top level and does not mark them untrusted. skills.sh does. Same envelope as issue 126. The 0.1.2 launcher forbids bare `npx`; do not report that contrast. Fix opened as [PR 129](https://github.com/CALLE-AI/call-e-integrations/pull/129). Not a second filing of 126.
8. **Generic `calle mcp call` exit code.** Dedicated `calle call status` treats `result.isError === true` as failure. Generic `calle mcp call` always printed `ok: true` and exited 0. Confirmed in `packages/cli/lib/cli.js`. This is issue 127. Fix opened as [PR 128](https://github.com/CALLE-AI/call-e-integrations/pull/128); I am not opening a second issue.

**C. SDK source, offline.** Calls `waitForResult` returns on top-level terminal `status`. Goal `waitForResult` waits until `result` or `error` is non-null. A local timeout does not hang up the call. Shipped CLI `--timeout-seconds` is an HTTP timeout (15s default), not a hangup.

**D. CLI / MCP leftovers after PRs 128/129, 2026-09-14, no second phone call. Source + CLI fixtures. Not a refile of 126/127.**

9. **Timeout and recover place a second call (high).** PR 128 makes generic `mcp call` treat tool `isError` as failure. A 15-second transport abort on `run_call` is still `{ ok:false, error.code:"http_error" }` with no `call_started` / `retry_safe`. Dedicated `call run` wraps the same abort as `run_call_timeout` + `retry_safe: false`, then `next_argv` is `call recover`, which re-sends `plan_id` + `confirm_token`. Official MCP: do not retry an uncertain submit. Cursor prefers raw `mcp call`. Ask: every failed `mcp call run_call` (tool error or timeout) returns `call_started: "unknown"` and `retry_safe: false`; recover is a lookup, not a second `run_call`.
10. **Missing `ready_to_run` is treated as ready (medium).** `calle call start` only stops when the flag is exactly `false`. The shipped CLI unit fixture omits the flag and still invokes `run_call`. Official MCP requires `ready_to_run=true`. Ask: no `run_call` unless the flag is boolean true.

**E. SDK / API / TS CLI 0.7.0, offline. No live create.**

11. **Validation failure is webhook-only (high).** Docs send `call.result_validation_failed`. GET / `waitForResult` see `completed` + `structured_result: null` — the same shape as extract-miss. The Python OpenAPI contract test forbids `result_validation` on CallTask. Ask: put `failure_code: result_validation_failed` on the CallTask so a polling operator can refuse the write.
12. **CLI `--phone` × N starts N conversations (high).** OpenAPI `phones` is alternate numbers on one recipient. The TypeScript CLI maps each `--phone` to its own `recipients[]` row. Usage only says “Repeatable.” No public cancel after accept. Ask: one recipient with `phones: [...]`, or say each flag is a new conversation.
13. **`calle calls create --wait` exits 0 on `failed`/`canceled` (medium).** Goal CLI `--wait` exits 1 on a domain error. `&&` scripts treat a failed Call as success.

Keep from the live call: schema-valid object; pickup-state matched the recipient; one attempt / no auto-redial; destination reached a terminal result.

Do not refile: CLI binary collision (109), mid-call tools (123), region `call_not_ready` (90/116/118/121), unsigned webhooks as a live incident.

---

## Q-11 — What would have given you a better experience with our CALL-E documentation?

One page that uses the same nouns the wire uses.

Next to OpenAPI `CallStatus`, say that `queued` is not idle. The live Calls table still defines it as “The call task is queued.” A 2026-09-05 GET stayed `queued` while an attempt was live. MCP never says `queued`; it says every non-terminal is progress and that a client deadline does not cancel the phone call. Put those sentences next to Calls `waitForResult` (returns on `completed` / `failed` / `canceled`, not on `structuredResult`) and Goal `waitForResult` (returns when `result` or `error` is non-null). Budget several minutes from accept to materialized result (~4m39s on the one live call). Docs examples use `timeoutMs: 120_000`; the SDK default is 600s; a local timeout does not hang up.

Name four “done” words so they cannot be substituted: Calls `completed` is a lifecycle terminal; MCP `COMPLETED` is run-finished, not task success; Calls `task_completed` is a post-summary boolean; none of them is an independently verified identifier. The live Calls page says CALL-E “validates the structured result against it before returning the terminal call task state” and offers `confirmation_code` as a required extracted string. Schema-valid plus a confirmed readback is not a write-gate.

Label the three objects named `result`: JSON-RPC `response.result` is the `CallToolResult`; CLI `result.structuredContent` is that payload; `get_call_run` summary/transcript sit under a nested `result{}` (issue 126). Shipped Cursor 0.1.2 still prints `<post_summary or summary or message>` at the top level. skills.sh `SKILL.md` uses that template while its own `references/commands.md` reads `result.summary`.

State that `result_schema` and `webhook_url` exist on `POST /v1/calls` and do not exist on `plan_call` / `run_call` or `calle call plan`. State that `--timeout-seconds` is an HTTP timeout (15s default), not a hangup, and that the Calls API has no client cancel after accept.

Events: default page size 100, follow `next_cursor`, and event `type` can be `call.in_progress` while event `status` stays `queued`. Both list resources return `next_cursor`; the follow-up query name is `cursor` on events and `after` on goals. The wrong name replays page one forever.

`docs.heycall-e.com` has no MCP page (`/mcp/openagent-oauth` is 404; `llms.txt` lists Calls, SDKs, webhooks and omits MCP). Agents that start from the published site fall through to `POST /v1/calls`. The repo guide is the only contract. Put `call.result_validation_failed` on the CallTask, not only as a webhook type — GET / `waitForResult` otherwise look like extract-miss. Canceled tasks arrive as webhook `call.failed`; branch on `data.status`. Docs mention an SDK `context` field; 0.7.0 types do not have one. Delete the sentence or ship the field. Python `recipients=[{"phone": ...}]` skips the `phone`→`phones` alias TypeScript applies on every row.

PR 129 Time slot still reads `result.extracted.calling.start` / `.end`; the CLI prints `started_at` / `ended_at`. Same envelope, two field names.

Keep the stale-page fixes, re-fetched 2026-09-14: Python SDK source is public (`CALLE-AI/server-sdk-python`) while `/sdks` still says it is not, and `calle-docs` Playwright asserts the “Not currently public” cell and zero Python repo links. A truthful docs edit fails CI until that test changes. Changelog 10 Sep #158 (“fields directly”) is `structuredContent` vs text blocks, not the nested `result{}` in issue 126. Devpost dates table still omits the Feedback Period (Rules: through 18 Sep 23:45 SGT; judging starts 10:00 SGT, not 09:00). Extra-calls form says “by September 14th at 12pm SGT” while Rules close submissions at 11:45 pm SGT and extra allocations take 1–5 business days. CLI: shipped `calle mcp call` reports transport success, not tool success (issue 127). Document or hide `track_ui_events`.

---

## Q-13 — Is there any other feedback you'd like to provide?

The Calls API is already enough to build a bounded exception workflow: durable create, poll, small schema, transcript turns. What I still cannot trust for a record write is an exact-character identifier. Schema-valid plus readback-yes produced `07198SECTIST` for intended `07198FECTIST` on the one live English call. I had to add a write-gate (ExactRef) because no official surface names that state.

The agent path is a different product, and it does not tell the same story as the SDK path. MCP cannot take `result_schema`. Shipped Cursor 0.1.2 and the skills.sh `SKILL.md` template still read summary at the top level while the MCP handoff and the skills.sh reference file put it under `result{}`. CLI live verification treats `COMPLETED` as a pass; the MCP guide says `COMPLETED` is not task success; ExactRef says neither `COMPLETED` nor `task_completed` is writable. Shipped `calle mcp call` exits 0 on `isError`; `calle call status` does not.

If those surfaces keep using four words for “done” and three objects named `result`, an agent that follows the Cursor template and the OpenAPI `queued` enum will write the wrong identifier and may place a second call. A 15-second `mcp call run_call` timeout has no `retry_safe`; `call recover` then re-submits the confirm pair. GET will not show `call.result_validation_failed`. `calle calls create --wait` will exit 0 on `failed`. I am not asking for mid-call application tools in v1 (issue 123). I am asking for one contract: what a completed result is allowed to mean, where the summary lives, that `queued` is not idle, that a local timeout is not hangup, and that an uncertain submit is not a retry.

Offline programmed envelopes are not telephony observations. No second live call was placed after 2026-09-05.
