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
