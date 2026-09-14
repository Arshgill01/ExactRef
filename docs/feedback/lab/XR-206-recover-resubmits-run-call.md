# XR-206 — `call recover` / `next_argv` is a second `run_call`, not a status lookup

## Finding

When `run_call` times out or returns no `run_id`, the CLI writes a private recovery record and tells the agent to run `next_argv` = `call recover --recovery-id …`. Recover **re-submits** `run_call` with the original `plan_id` and `confirm_token`. Official MCP says: uncertain `run_call` with no `run_id` → do not retry automatically; escalate.

Skills phrase this as “the call may already be in progress” and then instruct the agent to execute that recover command once. The metadata reads like continuation. The implementation is another execution.

## Surface / version / commit

- `packages/cli/lib/cli.js` `runPlannedCall`, `callRecoveryCommand` — `f0c9cf5` / `4a53b01`
- CLI reference: “Safely repeat an uncertain `run_call` with its original private confirmation data”
- Official MCP: “direct MCP has no documented general lookup or recovery operation. Do not create a new plan or retry automatically” then “CLI users should follow the returned `call recover` command”
- Cursor / skills.sh recovery sections: use `next_argv`, do not parse `next_command`, do not loop recover

## Expected

Recovery after an uncertain submit is a **lookup** (or a documented idempotent ack). `next_argv` that can place a call is labeled as an execution retry, not as “safe continuation.”

## Actual

```javascript
const runResult = await callCallStage({
  stage: "run_call",
  toolArguments: { plan_id: planId, confirm_token: confirmToken },
  callStarted: "unknown",
  retrySafe: false,
  recoveryId: activeRecoveryId,
  nextCommand: callRecoveryCommand(...), // ["call","recover","--recovery-id", ...]
});
```

`call recover` reads the cache and calls `runPlannedCall` again with the same pair.

`next_command` is a Bash-quoted string (`shellQuote` uses single quotes). Skills correctly say do not execute it. Windows agents that ignore that and paste `next_command` into cmd/PowerShell get a broken or dangerous line. `next_argv` is the structured form.

After a **successful** `run_id` but failed `get_call_run`, `next_argv` is `call status` (safe). After an **uncertain** `run_call`, `next_argv` is `call recover` (execution). Same field name, opposite side effect.

## Evidence (local / offline)

Existing e2e / unit: `call recover reuses the original confirmation after a run_call timeout`.

```json
{
  "ok": false,
  "call_started": "unknown",
  "retry_safe": false,
  "recovery_id": "<opaque 20-128>",
  "next_argv": [
    "call", "recover", "--recovery-id", "<opaque>",
    "--timezone", "Asia/Shanghai",
    "--server-url", "https://mcp.example/mcp/openagent_oauth",
    "--cache-root", "<cache>"
  ]
}
```

Second invocation with that `next_argv` sends:

```json
{ "name": "run_call", "arguments": { "plan_id": "plan-secret", "confirm_token": "confirm-secret" } }
```

If that second `run_call` also times out, `next_argv` is unchanged. Skill says do not loop; the payload still looks like a valid next step.

## Impact if an operator or agent trusted the current contract

**Duplicate real call.** First `run_call` was accepted; CLI timed out before `run_id`. Recover places a second outbound call to the same destination. Generic `mcp call run_call` (XR-202) has no recovery record at all, so the agent’s only move is a raw retry — same harm.

Agents that treat every `next_*` field as “the CLI said this is safe” will also try to shell-execute `next_command` (Unix quoting on Windows).

## Ask

Rename or split the envelope: `next_argv` for status vs `retry_run_argv` for a documented idempotent resubmit. State whether `confirm_token` is single-use. If it is not idempotent, recover must not call `run_call` again. Keep `next_command` display-only and Unix-quoted; say so on the error object (`next_command_shell: "bash"`).

## Do not claim

That the server is or is not idempotent on `confirm_token` (not observed live). That PR 128 changes recover. Issue 127.
