# XR-202 — Generic `mcp call` transport timeout has no `retry_safe` / `call_started`

## Finding

PR 128 (`f0c9cf5`) treats tool `isError` as a failed `mcp call`. A client-side timeout or HTTP abort on the same command is still a bare `McpHttpError`. The JSON has no `stage`, no `call_started`, no `retry_safe`, no `recovery_id`. Dedicated `call run` / `call start` wrap the same abort as `run_call_timeout` with `retry_safe: false` and a recover command.

This is not issue 127 (`ok: true` on `isError`). That card is still true on `4a53b01` and is being patched. The leftover on the PR branch is the timeout / transport path.

## Surface / version / commit

- PR branch `fix/mcp-call-tool-error` `f0c9cf5` — `handleMcpCommand` checks `result?.isError`, then `writeCommandError`
- `callCallStage` (dedicated `calle call *`) maps AbortError → `CallStageError` with `${stage}_timeout`
- `origin/main` `4a53b01` — generic `mcp call` also lacks timeout side-effect flags (and still has 127)

## Expected

Any failed `mcp call run_call` — tool error **or** timeout — reports the same conservative flags the dedicated workflow already uses: `call_started: "unknown"`, `retry_safe: false`, and does not invite a blind retry.

## Actual

`requestJsonRpc` on abort:

```text
MCP request timed out for tools/call
code: http_error
```

`errorPayload` only adds `retry_safe` / `call_started` when `error instanceof CallStageError`. Generic `mcp call` does not wrap timeouts that way.

Default `--timeout-seconds` for `run_call` via `mcp call` is **15**. `plan_call` is 150 only when the flag is omitted. An explicit `--timeout-seconds 15` also collapses planning.

`--poll-timeout-seconds` (default 300) applies only to `auth login`. It does not bound `get_call_run`. Agents that set it thinking they are limiting call-status waits get a no-op.

## Evidence (local / offline)

Timeout fixture (same AbortError shape as `call start labels a plan_call timeout as safe to retry`, pointed at `mcp call run_call`):

```javascript
// fetchImpl: initialize + initialized OK; tools/call throws
throw new DOMException("The operation was aborted", "AbortError");

// generic mcp call run_call — expected payload after f0c9cf5
{
  "ok": false,
  "server_url": "https://mcp.example/mcp/openagent_oauth",
  "error": {
    "code": "http_error",
    "message": "MCP request timed out for tools/call",
    "status_code": null
  }
}
// missing: stage, call_started, retry_safe, recovery_id, next_argv
```

Dedicated `call run` on the same abort (existing test `call recover reuses the original confirmation after a run_call timeout`):

```json
{
  "ok": false,
  "stage": "run_call",
  "call_started": "unknown",
  "retry_safe": false,
  "error": { "code": "run_call_timeout" }
}
```

PR 128 still trusts a remote boolean on `isError`:

```javascript
retrySafe: remoteError.retry_safe ?? defaults.retrySafe
```

`@call-e/core` `normalizeMcpToolResult` promotes the first JSON text block to `structuredContent`. A content-only `isError` body `{"retry_safe":true}` therefore overrides the conservative `run_call` default.

## Impact if an operator or agent trusted the current contract

**Duplicate real call.** Cursor skill prefers MCP tools. A 15s `run_call` timeout looks like “nothing happened.” No `retry_safe: false`. The agent retries `run_call` with the same `plan_id` / `confirm_token`. Direct MCP has no recovery record.

## Ask

Wrap generic `mcp call` failures (timeout, HTTP, JSON-RPC error) with the same `mcpCallSideEffectDefaults(toolName)` already used for `isError`. Do not let untrusted / content-promoted JSON flip `retry_safe` to true on `run_call`. Document that `--poll-timeout-seconds` is login-only.

## Do not claim

That a live `run_call` exceeded 15s (not measured). Issue 127 as a new bug. Remote server default for `retry_safe`.
