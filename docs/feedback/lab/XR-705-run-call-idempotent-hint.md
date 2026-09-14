# XR-705 — `run_call` advertises `idempotentHint: true` while forbidding a second call

## Finding

Live `tools/list` marks `run_call` with `destructiveHint: true` **and** `idempotentHint: true`. The tool description says “Do not call `run_call` more than once for the same `plan_id`.” MCP hosts that honor `idempotentHint` may retry the same `tools/call` after a timeout or transport error. That retry is a second outbound call. Distinct from XR-202 (CLI timeout envelope has no `retry_safe`): this is the **schema annotation** telling the host retries are safe.

## Surface / version / commit or URL

- Live `calle mcp tools --json` 2026-09-14 (`@call-e/cli@0.5.1`)
- Tool `run_call` `annotations` + description
- MCP spec: `idempotentHint` means repeating the call with the same arguments has no additional effect

## Expected

`idempotentHint: false` (or omitted) on any tool that can place a phone call. Description and annotation agree: one `plan_id` → at most one `run_call`.

## Actual

From `tools/list` (annotations sit on `run_call`; `_meta.openai/toolInvocation/invoking` is `"Starting call run..."`):

```json
"annotations": {
  "readOnlyHint": false,
  "destructiveHint": true,
  "idempotentHint": true,
  "openWorldHint": true
}
```

Description (same object): “Do not call `run_call` more than once for the same `plan_id`. Once started, wait for the activity card updates.”

`plan_call` is the opposite lie in the other direction: `openWorldHint: false` while it creates a durable remote plan.

## Evidence

`npx -y @call-e/cli mcp tools --json` dump at `/tmp/calle-lab-ts/mcp/tools-json.txt` (not committed; quoted above). No `run_call` was invoked.

## Impact if an operator or agent trusted the current contract

A host that retries “idempotent” tools after a 15s HTTP timeout (XR-202) will send `run_call` again with the same `plan_id` / `confirm_token`. If the first request was accepted, the second is a duplicate real call. The description tells the model not to retry; the annotation tells the **runtime** that retry is fine. Runtimes win.

## Ask

Set `run_call.annotations.idempotentHint` to `false`. Add `retry_safe: false` to any uncertain `run_call` error. Set `plan_call.openWorldHint` to `true`.

## Do not claim

That a host was observed auto-retrying in this session (inferred from the annotation + spec). A second live call. XR-202 / XR-206 (timeout / recover argv) as this card.
