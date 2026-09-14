# XR-704 — Unknown `run_id` is a successful `FAILED` call, not a tool error

## Finding

`get_call_run` and `calle call status --run-id` for a nonexistent id return HTTP/CLI success: `ok: true`, `isError: false`, process exit 0, `status: "FAILED"`, `message: "run_id not found."`. An agent that branches on `status === "FAILED"` or on `ok` reports that a phone call failed. Nothing was dialed. Distinct from XR-003 (`mcp call` wrapping `isError` as `ok: true`): here the **tool itself** sets `isError: false`.

## Surface / version / commit or URL

- Live MCP `get_call_run` via `@call-e/cli@0.5.1` (2026-09-14)
- Dedicated `calle call status --run-id` (throws on `isError`, but `isError` is false)
- `outputSchema` requires only `run_id` and `status` (a fabricated FAILED object satisfies it)

## Expected

Missing/unknown `run_id` is a tool error (`isError: true`) or a 4xx-class envelope (`ok: false`, exit ≠ 0) with a code such as `not_found`. `FAILED` is reserved for a run that existed and reached a telephony/system terminal.

## Actual

`calle mcp call get_call_run --args-json '{"run_id":"not-a-real-id"}'` and `calle call status --run-id not-a-real-id` both (exit 0):

```json
{
  "ok": true,
  "result": {
    "isError": false,
    "structuredContent": {
      "run_id": "not-a-real-id",
      "status": "FAILED",
      "message": "run_id not found.",
      "next_step": {
        "action": "report_blocked",
        "instruction": "Report the current terminal run status. Do not start another call."
      }
    }
  }
}
```

By contrast, omitting `run_id` entirely is `isError: true` (Pydantic `missing_argument`) but still `ok: true` / exit 0 on generic `mcp call` (XR-003). The dedicated `call status` path would throw on that `isError`; it does **not** throw on not-found.

## Evidence

Commands above, 2026-09-14, logged-in CLI. No `run_call` was issued.

## Impact if an operator or agent trusted the current contract

Cursor/skills list `FAILED` as a terminal status and print `[Status] FAILED` plus an empty summary. The user is told the call failed. `next_step` says “Do not start another call,” which is correct for a real failure and **also** correct for a typo — so a mistyped id looks identical to a hung-up attempt. Operators file support tickets against a run that never existed.

## Ask

Return `isError: true` (or `ok: false` / exit 2 on the dedicated command) with `code: not_found` when the run record is missing. Do not emit `status: FAILED` for an id the server never assigned.

## Do not claim

XR-003 (`ok: true` when `isError: true`). That a real call failed. A second live dial. Rate of mistyped ids.

## Addendum — independent re-run 2026-09-14 ~16:20 UTC (lead pass)

Both `npx -y @call-e/cli@0.5.1 mcp call get_call_run --args-json '{"run_id":"run_does_not_exist_xr704"}' --json` and `call status --run-id run_does_not_exist_xr704 --json` exited 0 with the identical envelope (`/tmp/calle-lab/live2/get_call_run_unknown.json`, `call_status_unknown.json`):

```json
{
  "ok": true,
  "tool_name": "get_call_run",
  "result": {
    "structuredContent": {
      "run_id": "run_does_not_exist_xr704",
      "requested_run_id": null, "parent_run_id": null, "root_run_id": null,
      "status": "FAILED",
      "message": "run_id not found.",
      "display_goal": null, "schedule_mode": "immediate", "scheduled_at": null, "schedule_timezone": null,
      "result": { "summary": null, "post_summary": null, "outcome": null, "extracted": {}, "transcript": null, "call_id": null, "call_ids": [], "batch": null },
      "expires_at": null, "activity": [], "next_cursor": null,
      "next_step": {
        "action": "report_blocked", "tool_name": null, "run_id": "run_does_not_exist_xr704", "plan_id": null, "parent_run_id": null,
        "poll_after_seconds": null, "scheduled_at": null, "schedule_timezone": null, "required_user_input": [],
        "instruction": "Report the current terminal run status. Do not start another call."
      }
    },
    "isError": false
  }
}
```

(`server_url` and the duplicated `content[0].text` omitted.) Reproduced by a second agent on a second id: not a one-off.
