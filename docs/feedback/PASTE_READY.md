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

1. **Exact identifier (high).** After a full readback and “yes,” structured reference was `07198SECTIST`; the intended value was `07198FECTIST`. Schema checks passed. Stage (ASR vs conversation vs extraction) not isolated. Impact: one character is enough to write the wrong operational id. Ask: identifier-capture mode, or null + mismatch instead of a silent substitution.
2. **Contradiction vs summary (high).** Recipient said “Sunday morning” and “5:00 PM.” Structured field kept the conflict; summary became Sunday 5 PM. Ask: one clarification, then null; summary must not pick a clock time the structured field left open.
3. **Top-level status (medium, DX).** GET call `status` stayed `queued` while attempt/events showed activity. Poll-until-terminal worked (~4m39s accept→result). Ask: top-level `in_progress` when an attempt is live, or document that `queued` can include an active attempt.

**B. MCP / CLI / Cursor skill, 2026-09-13, no second phone call.**

4. **Fourth MCP tool (docs/contract).** `calle mcp tools` returned `plan_call`, `run_call`, `get_call_run`, and `track_ui_events`. Official MCP guide and the Cursor skill describe three tools. `track_ui_events` is not documented in the integrations docs I cloned. Workaround: ignore the fourth tool. Ask: document or hide it for agent clients.
5. **Cursor skill vs live `get_call_run` shape.** The official Cursor plugin terminal template reads `summary` / `transcript` at the top level and does not mark them untrusted. skills.sh does. This is the same envelope described in issue 126; the Cursor skill still teaches the empty-field path. Ask: read `result.summary` / `result.transcript`; copy the untrusted-output boundary into the Cursor skill. Not a second filing of 126.
6. **Generic `calle mcp call` exit code.** Dedicated `calle call status` treats `result.isError === true` as failure. Generic `calle mcp call` always prints `ok: true` and exits 0. Confirmed in current `packages/cli/lib/cli.js`. This confirms issue 127; I am not opening a second issue.

**C. SDK source, offline.** Calls `waitForResult` returns on top-level terminal `status`. Goal `waitForResult` waits until `result` or `error` is non-null. A local timeout does not hang up the call.

Keep from the live call: schema-valid object; pickup-state matched the recipient; one attempt / no auto-redial; destination reached a terminal result.

Do not refile: CLI binary collision (109), mid-call tools (123), region `call_not_ready` (90/116/118/121), unsigned webhooks as a live incident.

---

## Q-11 — What would have given you a better experience with our CALL-E documentation?

- Next to `CallStatus`: say whether `queued` can include an active attempt, and that a local wait timeout does not cancel the call. Budget several minutes from accept to materialized result (~4m39s on the one live call).
- Document Calls vs Goal wait predicates side by side.
- Structured results: schema-valid + confirmed readback ≠ independently verified identifier (F/S is the example).
- MCP: document the `result{}` envelope on `get_call_run` (issue 126). Document or omit `track_ui_events`. Update the Cursor skill readiness list from “three tools” to whatever `tools/list` actually returns.
- SDKs table: Python source is public (`CALLE-AI/server-sdk-python`) while the page still says it is not.
- Devpost dates table: add the Feedback Period (through 18 Sep 23:45 SGT) and align judging start with Official Rules (10:00 SGT). Extra-calls form noon SGT vs Rules 23:45 SGT should be printed together.
- CLI: one sentence that `calle mcp call` currently reports transport success, not tool success (issue 127).
- Cursor vs skills.sh: one page that the Cursor plugin is MCP-first and must treat transcripts as untrusted.

---

## Q-13 — Is there any other feedback you'd like to provide?

The Calls API is already enough to build a bounded exception workflow: durable create, poll, small schema, transcript turns. What I still cannot trust for record writes is exact-character identifiers and honest unknowns.

The agent path is a different product from the SDK path. MCP cannot take `result_schema` or `webhook_url`. The official Cursor skill is behind the skills.sh skill on untrusted output and result-field paths, and `tools/list` already exposes a fourth undocumented tool. If Cursor is a first-class host, that plugin is the integration I would fix first.

I am not asking for mid-call application tools in v1 (issue 123 already covers that). I am asking for the three surfaces to tell the same story about what a “completed” result is allowed to mean.

Offline programmed envelopes are not telephony observations. No second live call was placed after 2026-09-05.
