# CONFIRM-XR-001 — `track_ui_events` is an app-only, unauthenticated widget endpoint served to every model

2026-09-14. New evidence for XR-001 (fourth undocumented tool). Tool listed, never invoked. No call. No form.

## What was re-verified

Live `tools/list` (`npx -y @call-e/cli@0.5.1 mcp tools --json`) still returns four tools. The fourth carries `_meta` that the earlier card did not quote:

```json
"track_ui_events": {
  "_meta": {
    "ui": { "visibility": ["app"] },
    "securitySchemes": [{ "type": "noauth" }],
    "openai/widgetAccessible": true,
    "openai/visibility": "private"
  },
  "annotations": { "readOnlyHint": false, "destructiveHint": false, "idempotentHint": true, "openWorldHint": false }
}
```

Read together: the server declares the tool as **not for the model** (`ui.visibility: [app]`, `openai/visibility: private`) and **requiring no auth**, yet it is returned to any MCP client on the `openagent_oauth` channel, including the CLI, Cursor, Claude Code and Codex. Only the ChatGPT host honours the `openai/*` keys. Every other host shows a writable, unauthenticated telemetry tool to the model.

Companion facts from the same list:

- `plan_call` and `get_call_run` are `ui.visibility: ["model","app"]`; `run_call` has no `ui` key.
- `run_call` is the only tool with `destructiveHint: true` and also `idempotentHint: true` (XR-705).

## Why it adds to XR-001

XR-001 said “fourth tool, undocumented.” This shows the vendor *intended* it to be hidden and unauthenticated, and that the hiding is host-specific metadata rather than server-side filtering. The ask sharpens: filter by channel server-side, or require auth on the tool.

## Do not claim

What `track_ui_events` accepts or stores (not invoked). Refile of XR-001. Second live call.
