# ROLLUP — CLI / MCP / Cursor skill (2026-09-14)

No live `plan_call`, `run_call`, `track_ui_events`, or `POST /v1/calls`. No tokens in this tree. `tools/list` was not re-fetched this resume.

Surfaces read: `call-e-integrations` `origin/main` `4a53b01` and `fix/mcp-call-tool-error` `f0c9cf5`; `call-e-integrations-plugin` `fix/cursor-skill-result-envelope` `560d61c`; official MCP guide on `main`; `docs.heycall-e.com` / `llms.txt`; published Cursor skill 0.1.2 vs PR 129; CLI `packages/cli/lib/cli.js` + unit fixtures.

## File index

| File | Harm class | One line |
| --- | --- | --- |
| [XR-201-plan-args-omit-user-input.md](XR-201-plan-args-omit-user-input.md) | wrong write / wrong script | `call plan`/`start` send `goal`+`to_phones`, never `user_input` |
| [XR-202-mcp-call-timeout-no-side-effects.md](XR-202-mcp-call-timeout-no-side-effects.md) | **duplicate real call** | Generic `mcp call` timeout has no `retry_safe`; 15s `run_call` default |
| [XR-203-ready-to-run-optional.md](XR-203-ready-to-run-optional.md) | **duplicate / unintended call** | `call start` runs unless `ready_to_run === false` |
| [XR-204-docs-site-missing-mcp.md](XR-204-docs-site-missing-mcp.md) | wrong API | `docs.heycall-e.com` has no MCP page; `llms.txt` omits it |
| [XR-205-offset-ttl-token-lifetime.md](XR-205-offset-ttl-token-lifetime.md) | wrong time / stale reuse | `_meta` offset −480; no `ttl_seconds`; status is local-only |
| [XR-206-recover-resubmits-run-call.md](XR-206-recover-resubmits-run-call.md) | **duplicate real call** | `next_argv` recover = second `run_call` |
| [XR-207-checker-vs-calling-fields.md](XR-207-checker-vs-calling-fields.md) | **wrong write** (clock) | PR 129 Time slot uses `.start`/`.end`; CLI prints `started_at` |

## Top discoveries by agent-harm

1. **Duplicate real call** — [XR-202](XR-202-mcp-call-timeout-no-side-effects.md) + [XR-206](XR-206-recover-resubmits-run-call.md). Cursor prefers raw MCP tools. A 15-second `run_call` timeout returns `{ ok:false, error.code:"http_error" }` with no side-effect flags, so the agent retries. Dedicated CLI instead returns `retry_safe:false` and a `next_argv` that **re-invokes** `run_call`. Official MCP says do not retry an uncertain submit. Same confirm pair, second outbound call if the first was accepted.
2. **Trusted remote / optional ready flag** — [XR-203](XR-203-ready-to-run-optional.md). `call start` (skills.sh happy path) auto-executes when `ready_to_run` is missing. Existing CLI unit fixture already does this. [XR-202](XR-202-mcp-call-timeout-no-side-effects.md) also: content-promoted JSON can set `retry_safe: true` on `run_call` `isError` after PR 128.
3. **Wrong write** — [XR-207](XR-207-checker-vs-calling-fields.md) (Time = `Not available` or invented); [XR-201](XR-201-plan-args-omit-user-input.md) (user constraints never reach the planner); [XR-205](XR-205-offset-ttl-token-lifetime.md) (planner may apply −480 as UTC offset). [XR-204](XR-204-docs-site-missing-mcp.md) steers agents from MCP into `POST /v1/calls`.

## Confirmed, not refiled

| Id | Status this pass |
| --- | --- |
| 126 / XR-002 | Still true on published Cursor 0.1.2 (top-level summary/transcript). PR 129 addresses the envelope; leftover is XR-207 field names. |
| 127 / XR-003 | Still true on `4a53b01`. PR 128 fixes `isError` for `mcp call`; leftover is XR-202 timeout. |
| XR-001 | Fourth tool `track_ui_events`. Not invoked. Not rebranded. |
| XR-502 / XR-503 / XR-504 | OffHire / result-noun / timeout-is-not-hangup cards. Not restated. |

## Path contrast (main vs PR 128)

| Event | `4a53b01` `mcp call` | `f0c9cf5` `mcp call` | `calle call run` (both) |
| --- | --- | --- | --- |
| Tool `isError` | `ok: true` (127) | `ok: false`, `mcp_tool_error`, defaults by tool name | `ok: false`, stage flags, recover if no `run_id` |
| Transport timeout | `ok: false`, `http_error`, **no flags** | same leftover | `run_call_timeout`, `retry_safe: false`, `next_argv` recover |
| Success + slow status | raw tool result | raw tool result | `ok: true`, `status_query_succeeded: false`, `next_argv` = status |

## Skill / docs contrast

| Contract | Official MCP | Cursor 0.1.2 | PR 129 Cursor | skills.sh |
| --- | --- | --- | --- | --- |
| `user_input` | required verbatim | yes on MCP path | yes on MCP path | CLI `call start` uses `--goal` only |
| `ready_to_run` | must be true | “immediately `run_call`” + no second confirm | same tension | CLI decides inside `call start` (XR-203) |
| Untrusted / `result{}` | inspect summary; not named untrusted | missing (126) | present | present |
| Time fields | unspecified | `<start/end time>` | `.start` / `.end` | `started_at` / `ended_at` |
| Recover | do not retry; CLI recover mentioned | `next_argv` recover | same | same |
| Docs site | repo markdown only | plugin URL airudder | same | CLI |

## Do not claim

Live tool schemas, live TTL, live idempotency of `confirm_token`, a second OffHire call, or new GitHub issues. Do not submit the form or Discord from this lab.
