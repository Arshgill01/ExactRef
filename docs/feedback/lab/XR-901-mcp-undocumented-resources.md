# XR-901 — Live MCP advertises and serves undocumented Skybridge plan-card resources

## Finding

`initialize` returns `capabilities.resources` and `capabilities.prompts`. `resources/list` then returns three HTML widgets (`plan_call_widget`, `plan_call_widget_stable`, `legacy_plan_call_widget`) plus `resources/templates/list` (`legacy_plan_call_widget_version`). `resources/read` on the stable URI returns `text/html+skybridge` with `_meta.openai/widgetDomain: https://dashboard.heycall-e.com/`. Official MCP guide and all five skills document **tools only** (three tools; XR-001 is the fourth tool). Hosts that honor the resources capability will load a ChatGPT-app widget against the live OAuth MCP server.

## Surface / version / commit or URL

- Live `POST https://seleven-mcp-sg.airudder.com/mcp/openagent_oauth` 2026-09-14
- `@call-e/cli@0.5.1` token cache (token never printed)
- Official MCP guide on integrations `1ce9d77` `docs/mcp/openagent-oauth.md` (tools only)
- `initialize.serverInfo`: `AI Rudder MCP` `3.0.0b1` (see XR-905)

## Expected

If resources are a ChatGPT-app implementation detail, `initialize.capabilities.resources` is omitted (or `_meta` marks them app-only, like `track_ui_events`). The hosted MCP guide lists every advertised capability. Non-ChatGPT hosts do not receive `ui://` widgets.

## Actual

**Observed** `initialize` result (verbatim minus headers):

```json
{
  "protocolVersion": "2025-11-25",
  "capabilities": {
    "experimental": {},
    "prompts": { "listChanged": true },
    "resources": { "subscribe": false, "listChanged": true },
    "tools": { "listChanged": true }
  },
  "serverInfo": { "name": "AI Rudder MCP", "version": "3.0.0b1" }
}
```

**Observed** `resources/list` (first item; two aliases omitted here):

```json
{
  "name": "plan_call_widget",
  "uri": "ui://one_shot_call/plan_call_widget_vsha256_73393bcf1c315332.html",
  "description": "Structured plan card widget for collecting missing call details before execution.",
  "mimeType": "text/html+skybridge",
  "_meta": {
    "openai/widgetDomain": "https://dashboard.heycall-e.com/",
    "openai/widgetCSP": {
      "connect_domains": ["https://dashboard.heycall-e.com", "https://seleven-mcp-sg.airudder.com"],
      "resource_domains": ["https://dashboard.heycall-e.com", "https://seleven-mcp-sg.airudder.com"]
    }
  }
}
```

`prompts/list` returned `{ "prompts": [] }` while `prompts.listChanged: true` was advertised.

## Evidence

Commands (token read from `~/.calle-mcp/cli/<hash>/token.json`, never echoed):

```bash
# JSON-RPC initialize / resources/list / resources/read / prompts/list
# Accept: application/json, text/event-stream
# Authorization: Bearer <redacted>
```

Envelopes saved sanitized at `/tmp/calle-lab/pkg/mcp-results/mcp-probe.json`. HTTP 200 on list/read. No `run_call`. `plan_call` used once with no phone (`ready_to_run: false`, `confirm_token: null`).

## Impact if an operator or agent trusted the current contract

A generic MCP host that lists resources will fetch HTML from the CALL-E dashboard origin and treat it as part of the call workflow. Cursor/Claude/Codex skills never mention `resources/*`, so agents either ignore the plan card (XR-706) or a host renders a ChatGPT widget the skill cannot drive. **Inferred:** a host following `openai/widgetCSP` will open network to `dashboard.heycall-e.com` from the agent session.

## Ask

Document the three resources (or hide them behind the same `ui.visibility: [app]` gate as `track_ui_events`). Drop `capabilities.prompts` until a prompt exists. Add a “Resources” section to the official MCP guide.

## Do not claim

That the widget HTML was executed or that it placed a call. Refile of XR-001 (fourth **tool**). XR-706 (plan-card vs chat) as this card — this is the missing **resources** surface, not the `next_step` prose.
