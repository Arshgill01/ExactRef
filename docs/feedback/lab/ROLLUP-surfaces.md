# Surface rollup — the same fact, seven tellings

**Date:** 2026-09-14. **No live call. No form submit. No new GitHub issue.**
**Job:** map how SDK, API, CLI, MCP, Cursor skill, skills.sh skill, and ExactRef tell the same operational facts. Find contradictions that would make an agent write a wrong identifier or place a duplicate call.

This is not a rewrite of [PASTE_READY.md](../PASTE_READY.md). That draft already owns the live F/S case and the 2026-09-13 CLI/MCP listing. This file cites what each surface *says now*, including shipped `main` versus unreleased local fix branches.

## Surfaces pinned this pass

| Surface | What was read | Version / commit |
|---|---|---|
| SDK | TypeScript `waitForResult` + `CallStatus`; Python `wait_for_result` + `CallStatus` | `@call-e/calle` 0.7.0 (`36ee6f1`); `calle-ai` 0.7.0 (`f7a4b82`) |
| API | OpenAPI `CallStatus` / `CallTask`; Calls guide; SDKs guide | `calle-docs` `b387e01`; no MCP page in that tree |
| CLI shipped | `handleMcpCommand` + live-verify docs on `origin/main` | `@call-e/cli` 0.5.1 at `4a53b01` |
| CLI local | same files on the isError branch | `f0c9cf5` `fix/mcp-call-tool-error` (unreleased) |
| MCP | Official guide (GitHub only; not on docs.heycall-e.com) | [openagent-oauth.md](https://github.com/CALLE-AI/call-e-integrations/blob/main/docs/mcp/openagent-oauth.md) + integrations README |
| Cursor shipped | `packages/cursor-plugin/plugin/skills/calle` on `origin/main` | plugin **0.1.2** at `4a53b01` |
| Cursor local | same path in `call-e-integrations-plugin` | still labeled **0.1.2** at `560d61c` `fix/cursor-skill-result-envelope` |
| skills.sh | `skills/calle/SKILL.md` + `references/commands.md` | skill **0.1.0** |
| ExactRef | `skills/exact-ref/SKILL.md` + `references/examples.md` + `safety.md` | this repo |

`docs.heycall-e.com` has Calls/SDK/webhook pages and no MCP guide. The official MCP contract lives on GitHub.

Unreleased local branches are cited only as “working copy.” An agent that installs `@call-e/cli@0.5.1` or the published Cursor plugin still sees shipped `4a53b01`.

## Compact matrix

Cells are the claim, not the essay. Citations sit under each fact.

| Fact | SDK 0.7.0 | API | CLI 0.5.1 shipped | MCP guide | Cursor 0.1.2 shipped | skills.sh 0.1.0 | ExactRef |
|---|---|---|---|---|---|---|---|
| What “completed” means | Calls wait returns on top-level `completed`/`failed`/`canceled`. Goal wait returns when `result` or `error` is non-null. | `completed` is a lifecycle terminal after post-call outcome. `task_completed` is a separate post-summary boolean. | Live verify: only `COMPLETED` is a passing terminal. | `COMPLETED` = run finished; **not** task success. | Terminal list includes `COMPLETED`. Template treats it as the moment to print the summary. | Same terminals. Forbids “The call succeeded.” Still no write-gate. | MCP `COMPLETED` and Calls `task_completed` are **not** permission to write. |
| Where summary lives | `Call.summary` (top-level). Also recipient/attempt `summary`. | `CallTask.summary` top-level. | CLI envelope: `result.structuredContent`. Live verify dumps “summary” as a debug field. | JSON-RPC `response.result`; handoff “result fields”; prose also says the tool “can include … summary”. | SKILL template: `<post_summary or summary or message>` (top-level). | **Split:** SKILL.md top-level; `commands.md` `result.summary`. | “MCP summaries live under `result{}`.” |
| Is `queued` idle? | Enum lists `queued` ≠ `in_progress`. Wait keeps polling. No “do not create again.” | Same split. `completed_at` is null “while queued or in progress.” Does not say `queued` can hide a live attempt. | Non-terminal → “in progress.” Uncertain start → recover, do not resubmit. No Calls `queued`. | Every non-terminal is progress (`PREPARING`, …). Never uses Calls `queued`. | Non-terminal → “Phone call is in progress!” | Same. Agent flow: never create again because status is queued (ExactRef examples, not this skill). | `queued` + attempt activity is **not** idle. Do not create again. |
| Is readback-yes verified? | Schema-valid `structuredResult` is the extraction contract. No provenance enum. | Same. `task_completed` is a post-summary judgment, not a second channel. | `COMPLETED` passes live verify. No identifier provenance. | “Apply your application's success criteria.” | Prints `[Call Summary]` as the result. No untrusted mark. | Marks summary/transcript untrusted. Still no `independently_verified`. | Readback-plus-yes = `conversational_confirmed`. Only typed + second channel is writable. |
| Can MCP take `result_schema`? | `create({ resultSchema })` / `result_schema=`. | `POST /v1/calls` field `result_schema`. | `call plan` flags: phone, goal, language, region, timezone. **No schema flag.** | `plan_call` / `run_call` input lists omit it. No `webhook_url` either. | No schema field. Goal text only. | Goal text only. | Compile emits a Calls `resultSchema`. Host-owned create. MCP cannot attach it. |
| Does timeout cancel? | `CalleTimeoutError`. Wait loop does not hang up. | **No client cancel** after create. In-flight calls continue. | `--timeout-seconds` is an **HTTP** timeout (default 15s; `plan_call` 150s). Not a hangup. | Client deadline / stop polling **does not** fail or cancel the call. | Poll until terminal or user asks to stop. No cancel sentence. | Stop if interrupted. No cancel sentence. | Local timeout is not hangup. API has no client cancel. |
| Does `isError` fail the process? | HTTP errors throw. No MCP `isError`. | HTTP status. | **`calle call *` throws on `isError`. Generic `calle mcp call` always `ok: true` / exit 0.** | Wire has `CallToolResult.isError`. Guide never says a client must fail closed. | Silent. | Silent. | Out of scope. |
| Fourth tool | N/A | N/A | `mcp tools` prints whatever the server returns. Verify text says “including” the three call tools. | Expected set is exactly three. Inspector step: confirm those three. | Readiness: confirm the three. No “extra is OK.” No `track_ui_events` ban. | Confirm the three. No fourth-tool sentence. | Do not call `track_ui_events` or any undocumented MCP tool. |

Local working copies flip two cells: CLI `f0c9cf5` makes `mcp call` fail on `isError`; Cursor `560d61c` reads `result.summary`, marks output untrusted, and forbids `track_ui_events`. Both still advertise the shipped version numbers (CLI 0.5.1 / plugin 0.1.2).

---

## Fact 1 — what “completed” means

| Surface | Says | Citation |
|---|---|---|
| SDK | Calls `waitForResult` returns when `status` is `completed`, `failed`, or `canceled`. It does not wait for `structuredResult`. Goal `waitForResult` returns when `run.result !== null \|\| run.error !== null`. | `server-sdk-typescript/src/calls.ts` 268–276; `src/goals.ts` 280–281; Python `calle/calls.py` 60–61; `calle/goals.py` 90 |
| API | `CallStatus`: “`in_progress` includes post-call result finalization; terminal states are published only after the post-call outcome is available.” `task_completed`: “Post-summary judgment for whether the task reached a clear end state for the user.” Goal: “A completed call can still have `result: null` and `error: null` briefly.” | `calle-docs/openapi/calle.openapi.yaml` `CallStatus` 1203–1205, `task_completed` 1440–1444, `GoalRunStatus` 1084–1087 |
| CLI shipped | Default live accept list is `COMPLETED` only. Other MCP terminals end polling but **fail** verification. “A successful status lookup also does not mean the telephone call succeeded” appears only after the local CLI docs patch. Shipped `origin/main` reference has no `isError` / task-success sentence in the envelope section. | `packages/cli/docs/cli-verification.md` 104, 118; shipped `cli-reference.md` on `4a53b01` |
| MCP | “`COMPLETED` means the run completed; it does not by itself confirm that the requested task succeeded. Inspect the summary, details, and transcript, then apply your application's success criteria.” | [openagent-oauth.md](https://raw.githubusercontent.com/CALLE-AI/call-e-integrations/main/docs/mcp/openagent-oauth.md) terminal-status paragraph |
| Cursor 0.1.2 shipped | Terminal set includes `COMPLETED`. On any terminal, print `[Status]` + `[Call Summary]`. No “not task success” sentence. | `call-e-integrations/packages/cursor-plugin/plugin/skills/calle/SKILL.md` 86–111 |
| Cursor local 0.1.2 | “`COMPLETED` is a terminal status, not task success, and does not authorize a record write.” | `call-e-integrations-plugin/.../calle/SKILL.md` 40–41 |
| skills.sh | Same MCP terminal list. “Never paraphrase … `The call succeeded.`” | `skills/calle/SKILL.md` 170–172, 189–190 |
| ExactRef | “Treating MCP `COMPLETED` or Calls `task_completed` as permission to write” is a listed misuse. | `skills/exact-ref/SKILL.md` 25 |

**Collision:** four nouns — Calls `completed`, MCP `COMPLETED`, Calls `task_completed`, ExactRef `independently_verified` — look like “done.” Only the last is a write-gate. See [XR-501-completed-nouns.md](XR-501-completed-nouns.md).

SDK-internal split (Calls status vs Goal `result`/`error`) remains [XR-004](../NEW_FINDINGS_2026-09-13.md); do not refile.

---

## Fact 2 — where summary lives

| Surface | Says | Citation |
|---|---|---|
| SDK | `Call.summary`, `CallRecipient.summary`, `CallAttempt.summary` — all first-class top-level fields on those objects. | `server-sdk-typescript/src/calls.ts` 22–28, 42, 77 |
| API | `CallTask.summary`: “Short human-readable summary of the call task outcome.” Independent of `structured_result`. Guide: `task_completed` / evidence “come from the post-call summary.” | OpenAPI 1435–1439; `calle-docs/content/guides/calls.mdx` 432 |
| CLI | Actionable object is `result.structuredContent` (the CLI wrapper around MCP `CallToolResult`). Live verify prints “summary” among debug fields. | `cli-reference.md` 88–90 (local and the same envelope on main); `cli-verification.md` 117 |
| MCP | Three `result` nouns: (1) JSON-RPC `response.result` is the `CallToolResult`; (2) handoff table says `get_call_run` exposes “result fields”; (3) prose: “The response can include status, activity, summary, details, transcript.” | openagent-oauth.md “Tool Result Envelope” + `get_call_run` + handoff table |
| Cursor 0.1.2 shipped | Terminal template: `<post_summary or summary or message>` and `<transcript>` with **no** `result.` prefix. `commands.md` later says “If `result.transcript` is absent.” | SKILL.md 110–120; `references/commands.md` 208–209 |
| Cursor local | “Read `result.summary` and `result.transcript` from the `get_call_run` payload. Those fields are nested under `result{}`; top-level `summary` and `transcript` can be empty on a `COMPLETED` run.” Template uses `result.post_summary`. | plugin SKILL.md 37–39, 140–150; `references/commands.md` 220–224 |
| skills.sh | **Self-split.** SKILL.md template: `<post_summary or summary or message>` and `<transcript>`. `references/commands.md` template: `<result.post_summary or result.summary or message>` and `<result.transcript>`. | `skills/calle/SKILL.md` 199–209; `skills/calle/references/commands.md` 280–291 |
| ExactRef | “MCP summaries live under `result{}`. Do not read them at the top level.” | `skills/exact-ref/SKILL.md` 55 |

**Collision:** an agent that follows shipped Cursor, or the skills.sh SKILL.md template, writes from a top-level `summary` that issue 126 and the local Cursor patch say is empty on `COMPLETED`. See [XR-503-result-nouns.md](XR-503-result-nouns.md). Cursor-vs-skills.sh untrusted gap remains XR-002; this file adds the skills.sh self-split and the three-`result` overload.

---

## Fact 3 — is `queued` idle?

| Surface | Says | Citation |
|---|---|---|
| SDK | `CallStatus = "queued" \| "in_progress" \| "completed" \| "failed" \| "canceled"`. Wait treats `queued` as non-terminal (keep polling). No create-guard. | `schema.ts` 433; `calls.ts` 274–276 |
| API | Same enum. `in_progress` “includes post-call result finalization.” `completed_at` null “while queued or in progress.” Attempt has its own `queued`/`dialing`/`in_progress`. **Does not say** a call-task `queued` can coexist with a live attempt. | OpenAPI 1203–1211, 1477; `AttemptStatus` in `schema.ts` 449 |
| CLI | MCP statuses only. Non-terminal → “Phone call is in progress.” Uncertain `run_call` → `call recover`, “Do not submit the call again.” | Cursor/skills `commands.md` recovery; `cli-reference.md` 195 |
| MCP | “Treat every non-terminal status as progress.” Example: `PREPARING`. “Do not … call `run_call` again” on deadline or missing `run_id`. | openagent-oauth.md workflow steps 3–4 and no-`run_id` paragraph |
| Cursor 0.1.2 | Non-terminal template is “Phone call is in progress!” Shipped copy does not mention Calls `queued`. | SKILL.md 89–101 |
| skills.sh | Same progress template. | SKILL.md 174–187 |
| ExactRef | “Top-level status is `queued` and you must not create a second call.” “`queued` plus attempt activity is not idle.” Examples step 5: “Never create a second call because status is queued.” | SKILL.md 17, 52; `references/examples.md` 34 |
| Live (owned) | One 2026-09-05 Calls GET stayed `queued` while attempt/events showed activity. | OffHire `LIVE_CALL_FINDINGS.md`; FB-004 |

**Collision:** API/SDK teach `queued` ≠ `in_progress`. MCP/Cursor never use `queued` and treat every non-terminal as live. An agent that maps “API `queued` = not started” after a Cursor/MCP timeout will `POST /v1/calls` again. That is a duplicate-call path. Observation is FB-004; the **surface split** is what this matrix adds.

---

## Fact 4 — is readback-yes verified?

| Surface | Says | Citation |
|---|---|---|
| SDK / API | Extraction contract is schema-valid JSON. `structured_result` is null only when invalid or schema omitted. `task_completed` is a post-summary judgment, “available independently of your custom result schema.” No second-channel field. | OpenAPI 1430–1433, 1440–1444; `calls.mdx` 157, 432 |
| CLI | `COMPLETED` = live verification pass. Transcript/summary are debug dump, not a provenance state. | `cli-verification.md` 118 |
| MCP | After `COMPLETED`, “inspect the summary, details, and transcript, then apply your application's success criteria.” | openagent-oauth.md |
| Cursor 0.1.2 shipped | `[Call Summary]` is presented as the final result. No untrusted boundary. No “unverified identifier” rule. | SKILL.md 103–126 |
| skills.sh | Untrusted boundary. Still no classify step. | SKILL.md 60–75, 199 |
| ExactRef | “Never write schema-valid plus readback-yes as a fact.” Readback-plus-yes → `conversational_confirmed`. Hero: intended `07198FECTIST`, extracted `07198SECTIST` after readback + yes, schema-valid. | SKILL.md frontmatter + classify; `references/examples.md` FS-01 |
| Live (owned) | Same hero. FB-001. | PASTE_READY Q-10 A.1 |

**Collision:** five surfaces treat schema-valid + terminal as enough to show or ship the string. ExactRef is the only surface that names readback-yes as non-writable. An agent that never loads ExactRef will write `07198SECTIST`.

---

## Fact 5 — can MCP take `result_schema`?

| Surface | Says | Citation |
|---|---|---|
| SDK | First-class create input (`resultSchema` / `result_schema`). Docs examples always send one. | `calls.ts` 50–51, 119–121; `sdks.mdx` 101–129, 148–171 |
| API | `CreateCallRequest.result_schema` and `recipient_result_schema`. Validated before terminal state. | OpenAPI 1142–1170; `calls.mdx` 21–23 |
| CLI | `call plan` / `call start` options: `--to-phone`, `--goal`, `--language`, `--region`, `--timezone`. No `--result-schema`. | `cli-reference.md` 273–279; Cursor `commands.md` 123–129 |
| MCP | `plan_call` inputs: `user_input`, `to_phones`, `region`, `language`, `goal`, `scheduled_at`, `plan_id`, `ttl_seconds`. `run_call`: `plan_id`, `confirm_token`, `ttl_seconds`. Guide also: no `webhook_url`. | openagent-oauth.md tool inputs; README 176–177 |
| Cursor / skills.sh | Goal string only. | both SKILL call-flow sections |
| ExactRef | `compileIdentifierTask` returns a Calls-shaped `resultSchema` (`identifier`, `readback_confirmed`, `identifier_evidence`, `unresolved_time`). “Live CALL-E create is host-owned.” If the host is MCP, that schema cannot be sent. | `src/lib/task.ts` 33–57; ExactRef SKILL.md 10 |

**Collision:** the only machine check for an identifier lives on the SDK/API path. The agent path cannot attach it. See [XR-502-mcp-no-result-schema.md](XR-502-mcp-no-result-schema.md).

---

## Fact 6 — does timeout cancel?

| Surface | Says | Citation |
|---|---|---|
| SDK | Wait throws `CalleTimeoutError`. No cancel request in the loop. | `calls.ts` 268–279; Python `calls.py` 50–63; `errors.py` `CalleTimeoutError` |
| API | “The Calls API does not expose an operation for clients to cancel a call after it has been created. A call that is already in flight may therefore continue to completion even when your application no longer needs its result.” | `calls.mdx` 404–408 |
| CLI | `--timeout-seconds`: “Request timeout in seconds.” Default **15**; `plan_call` **150**. `--poll-timeout-seconds` is **login** only. Live poll timeout (600s) expires the verifier, not the call. | `cli-reference.md` 251–252; `cli-verification.md` 103, 116 |
| MCP | “Reaching a client-side monitoring deadline or stopping the polling process does not fail or cancel the phone call.” Resume `get_call_run`. Do not `run_call` again. | openagent-oauth.md workflow 4 + cadence paragraph; README 174–177 |
| Cursor 0.1.2 | Poll until terminal **or the user asks you to stop**. No “timeout ≠ hangup.” | SKILL.md 81–83 |
| skills.sh | Stop when terminal, user asks, or “command execution is interrupted.” | `commands.md` 271–272 |
| ExactRef | “A local timeout is not hangup.” “CALL-E has no client cancel after accept.” | SKILL.md 53; `references/safety.md` 9 |

**Collision:** CLI 15s is easy to read as “the call failed.” API + MCP say the phone is still up. An agent that retries create/run after `get_call_run_timeout` places a duplicate. See [XR-504-timeout-is-not-hangup.md](XR-504-timeout-is-not-hangup.md).

---

## Fact 7 — does `isError` fail the process?

| Surface | Says | Citation |
|---|---|---|
| SDK / API | No MCP `isError`. Transport/API errors throw. | SDK client request helpers |
| CLI shipped `4a53b01` | `callCallStage` (dedicated `calle call *`) throws when `result?.isError === true`. Generic `handleMcpCommand` `mcp call` writes `mcpSuccessPayload` (`ok: true`) and returns 0. | `call-e-integrations-plugin/packages/cli/lib/cli.js` 1112–1123 vs 1343–1344; same on `origin/main` |
| CLI local `f0c9cf5` | `mcp call` throws `mcp_tool_error`, exits 1, `ok: false`. Docs: “A JSON-RPC HTTP 200 is not tool success.” | `call-e-integrations/packages/cli/lib/cli.js` 1427–1429; `cli-reference.md` 117–122 |
| MCP | Envelope is `CallToolResult` (has `isError` on the wire). Guide never mentions `isError` or process exit. | openagent-oauth.md Tool Result Envelope |
| Cursor / skills.sh | No `isError` handling. | both SKILL.md |
| ExactRef | Silent. | — |

Owned as XR-003 / issue 127. Local branch is a proposed fix, not the published CLI. Do not open a second issue.

---

## Fact 8 — fourth tool

| Surface | Says | Citation |
|---|---|---|
| MCP README | “run CALL-E with **three tools**.” Table lists only those three. | integrations README 134, 165–171 |
| MCP guide | “The expected tool set is `plan_call`, `run_call`, `get_call_run`.” Inspector: confirm those three. | openagent-oauth.md lifecycle + Inspector step 6 |
| CLI | `mcp tools` is a passthrough. Live verify: JSON includes those three (not “exactly three”). | `cli-verification.md` 113 |
| Cursor 0.1.2 shipped | Readiness: “Confirm that `plan_call`, `run_call`, and `get_call_run` are available.” | SKILL.md 58 |
| Cursor local | “Extra tools are not a readiness failure. Do not call `track_ui_events`.” | plugin SKILL.md 19–20, 80 |
| skills.sh | Confirm the three. No extra-tool rule. | SKILL.md 105 |
| ExactRef | “Calling `track_ui_events` or any undocumented MCP tool” is a listed misuse. | SKILL.md 24; `safety.md` 10 |
| Prior listing (owned) | 2026-09-13 `calle mcp tools` → four names including `track_ui_events`. | XR-001 / PASTE_READY Q-10 B.4 |

Owned as XR-001. Not re-listed as XR-5xx. Not re-invoked this pass.

---

## What would make an agent write the wrong identifier

1. Trust Calls `completed` + schema-valid `structured_result` + readback-yes (SDK/API), or MCP `COMPLETED` + printed summary (Cursor 0.1.2), or CLI live `COMPLETED` — and skip ExactRef. Hero: `07198SECTIST`.
2. Read `summary` / `transcript` at the top level (shipped Cursor; skills.sh SKILL.md) while the live envelope puts them under `result{}`. Empty top-level on `COMPLETED` → invent or scrape prose.
3. Put ExactRef’s compiled `resultSchema` into MCP `plan_call`. The field is dropped. Extraction falls back to unconstrained summary text.

## What would make an agent place a duplicate call

1. Treat API/SDK `queued` as “not started” after MCP/Cursor already have a `run_id` (or after Calls GET stayed `queued` during the live attempt).
2. Treat CLI `--timeout-seconds` (15s HTTP) or a local wait timeout as hangup, then `run_call` / `POST /v1/calls` again. MCP and the API forbid that; shipped Cursor never says so.
3. Treat generic `calle mcp call` `ok: true` as “tool succeeded,” miss `isError`, and retry `run_call` (shipped CLI).

## Already owned — CONFIRMED, not rebranded

XR-001 fourth tool. XR-002 Cursor `result{}` / untrusted vs skills.sh. XR-003 `mcp call` `isError` (shipped still true; local CLI branch is the proposed fix). XR-004 Calls vs Goal wait. FB-001 F/S. FB-003 summary time. FB-004 live `queued`. Do not refile 109, 123, 126, 127.

## New this pass

- [XR-501-completed-nouns.md](XR-501-completed-nouns.md)
- [XR-502-mcp-no-result-schema.md](XR-502-mcp-no-result-schema.md)
- [XR-503-result-nouns.md](XR-503-result-nouns.md)
- [XR-504-timeout-is-not-hangup.md](XR-504-timeout-is-not-hangup.md)

---

## Draft for parent

Paste-ready Q-11 / Q-13 upgrades. **Do not overwrite** [PASTE_READY.md](../PASTE_READY.md) until you review. Every sentence below is grounded in a cell cited above.

### Q-11 — What would have given you a better experience with our CALL-E documentation?

One page that uses the same nouns the wire uses.

Next to OpenAPI `CallStatus`, say that `queued` is not “idle”: a call-task can stay `queued` while an attempt is `dialing` / `in_progress` (2026-09-05 GET; ExactRef “do not create again”). MCP never says `queued`; it says every non-terminal status is progress and that a client deadline does not cancel the phone call. Put those three sentences on the same page as Calls `waitForResult` (returns on `completed`/`failed`/`canceled`, not on `structuredResult`) and Goal `waitForResult` (returns when `result` or `error` is non-null).

Name the four “done” words so they cannot be substituted: Calls `completed` is a lifecycle terminal; MCP `COMPLETED` is “run finished,” not task success; Calls `task_completed` is a post-summary boolean; none of them is an independently verified identifier. Schema-valid plus a confirmed readback is not a write-gate (F/S on 2026-09-05).

Say where the summary actually lives, with the three `result` objects labeled: JSON-RPC `response.result` is the `CallToolResult`; CLI `result.structuredContent` is that tool payload; `get_call_run`’s identifier/summary fields sit under a nested `result{}` (issue 126). Shipped Cursor 0.1.2 still prints `<post_summary or summary or message>` at the top level. skills.sh `SKILL.md` uses that same top-level template while its own `references/commands.md` reads `result.summary`. An agent cannot satisfy both files.

State that `result_schema` / `webhook_url` exist on `POST /v1/calls` and do not exist on `plan_call` / `run_call` or `calle call plan`. The compiled ExactRef schema cannot be attached on the MCP path.

State that `--timeout-seconds` is an HTTP request timeout (15s default), not a hangup, and that the Calls API has no client cancel after accept.

State that shipped `calle mcp call` reports transport success (`ok: true`) even when `isError: true`; dedicated `calle call status` does not (issue 127). Document or hide `track_ui_events`; `tools/list` is already four tools while the MCP guide’s expected set is three.

### Q-13 — Is there any other feedback you'd like to provide?

The Calls API is already enough to build a bounded exception workflow: durable create, poll, small schema, transcript turns. What I still cannot trust for a record write is an exact-character identifier. Schema-valid plus readback-yes produced `07198SECTIST` for intended `07198FECTIST` on the one live English call. ExactRef is the write-gate I had to add because no official surface names that state.

The agent path is a different product, and it does not tell the same story as the SDK path. MCP cannot take `result_schema`. Shipped Cursor 0.1.2 and the skills.sh `SKILL.md` template still read summary at the top level while the MCP handoff and the skills.sh reference file put it under `result{}`. CLI live verification treats `COMPLETED` as a pass; the MCP guide says `COMPLETED` is not task success; ExactRef says neither `COMPLETED` nor `task_completed` is writable. Shipped `calle mcp call` exits 0 on `isError`; `calle call status` does not.

If those seven surfaces keep using four words for “done” and three objects named `result`, an agent that follows the Cursor template and the OpenAPI `queued` enum will write the wrong identifier and may place a second call. I am not asking for mid-call application tools in v1 (issue 123). I am asking for one contract: what a completed result is allowed to mean, where the summary lives, that `queued` is not idle, and that a local timeout is not hangup.

Offline programmed envelopes are not telephony observations. No second live call was placed after 2026-09-05.

---

## Prize sentence

Four words for done and three objects named `result` teach an agent to write `07198SECTIST` as a fact and to dial again while GET still says `queued`.

Later same-day labs (not a rewrite of this matrix): [ROLLUP-cli-mcp.md](ROLLUP-cli-mcp.md) (XR-201–207) and [ROLLUP-sdk-api.md](ROLLUP-sdk-api.md) (XR-107–116). Highest-harm items are in [PASTE_READY.md](../PASTE_READY.md) Q-10 D/E.
