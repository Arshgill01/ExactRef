# Feedback lab

Agents write one finding file each under this directory. Do not submit the Google Form from here.

## File name

`XR-1xx-<short-slug>.md` or `XR-2xx-<short-slug>.md` for new discoveries. `CONFIRM-<known-id>.md` if you only re-verified a known card. CLI/MCP rollup: `ROLLUP-cli-mcp.md`.

## Required sections

- Finding
- Surface / version / commit or URL
- Expected
- Actual
- Evidence (paths, commands, quotes). No tokens, no phone numbers, no Discord post.
- Impact if an operator or agent trusted the current contract
- Ask (one concrete docs or product change)
- Do not claim (rate, second live call, refile of 109/123/126/127)

## Already owned. Mark CONFIRMED, do not rebrand as new.

FB-001 F/S after readback. FB-002 interruption. FB-003 time vs summary. FB-004 top-level queued. FB-005 synthesized evidence. gauntlet-001..007. XR-001 `track_ui_events`. XR-002 Cursor `result{}`. XR-003 `mcp call` `isError`. XR-004 wait predicates. XR-005 Python repo public. XR-006 Devpost dates table. XR-401 stitch. XR-402 events page one. XR-501..504. XR-107..116 (SDK/API, see ROLLUP-sdk-api.md). XR-201 `user_input` omitted. XR-202 `mcp call` timeout flags. XR-203 `ready_to_run` optional. XR-204 docs MCP 404. XR-205 offset/TTL/status. XR-206 recover resubmits. XR-207 checker vs `started_at`.

Added 2026-09-14 (see `ROLLUP-fable-lead.md`, `ROLLUP-grok-ts.md`, `ROLLUP-grok-py.md`): XR-601 `NO ANSWER` vs `NO_ANSWER`. XR-602 `next_step` object unread. XR-603 `ttl_seconds: 0` = forever. XR-604 `confirm_token` on stdout. XR-605 `createAndWait` loses `call_id`. XR-606 hosted install guide stale. XR-607 changelog-only concurrency / Success fee. XR-608 live `text/plain` errors → TS retryable. XR-609 `call status` hardcodes `call_started: true`. XR-610 `run_call` “server will notify.” XR-701..712 (TS/CLI/MCP, Grok). XR-801..812 (Python/REST/docs, Grok).

Added 2026-09-14 docs lab (`ROLLUP-grok-docs.md`): XR-1001 API Reference has no `.md`. XR-1002 `llms.txt`/search omit MCP. XR-1003 Goal Runs “API 0.6”. XR-1004 scheduled calling advertised. XR-1005 webhook samples do not compile. XR-1006 no OpenGraph. XR-1007 complete example ignores `CALLE_BASE_URL`. XR-1008 three wait timeouts. XR-1009 SDK README hash URLs. XR-1010 Playwright pins 0.7.0 + `/calle/webhook`. XR-1011 markdown mirrors drop heading ids. XR-1012 `cdn.zudoku.dev` preconnect 404.
