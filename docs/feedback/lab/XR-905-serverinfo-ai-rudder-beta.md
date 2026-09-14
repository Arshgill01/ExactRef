# XR-905 — `initialize.serverInfo` is `AI Rudder MCP` `3.0.0b1`

## Finding

Every MCP client that implements `initialize` sees `serverInfo.name: "AI Rudder MCP"` and `version: "3.0.0b1"`. CALL-E docs, npm, and the CLI present this endpoint as the CALL-E OpenAgent MCP server. `prompts` is advertised (`listChanged: true`) but `prompts/list` is `{ "prompts": [] }`. Protocol `2025-11-25` is returned when offered; offering `2024-11-05` is also accepted and echoed.

## Surface / version / commit or URL

- Live initialize 2026-09-14
- CLI default server `https://seleven-mcp-sg.airudder.com/mcp/openagent_oauth`
- Docs/skills: “CALL-E MCP”, never “AI Rudder” or `3.0.0b1`

## Expected

`serverInfo.name` is `calle` (or `CALL-E`). Version is a released CALL-E identifier (`2025-11-25` protocol ≠ server semver). `capabilities.prompts` is absent until a prompt exists.

## Actual

**Observed** (both protocol offers):

```json
"serverInfo": { "name": "AI Rudder MCP", "version": "3.0.0b1" }
```

`prompts/list` → `{ "prompts": [] }`. `logging` capability omitted; `logging/setLevel` → `-32601` (correct).

## Evidence

`mcp-probe2.mjs` `initialize` / `initialize 2024-11-05` / `prompts/list`.

## Impact if an operator or agent trusted the current contract

Install health checks that assert `serverInfo.name === "calle"` fail. Agents logging server version to support tickets report a vendor-internal beta string. Empty `prompts` capability makes hosts show a Prompts UI with nothing in it. **Inferred:** a security review that allowlists “CALL-E” by name will not match.

## Ask

Set `serverInfo` to `{ "name": "calle", "version": "<published MCP build>" }`. Remove `capabilities.prompts` until `prompts/list` is non-empty.

## Do not claim

That `3.0.0b1` is unsafe. A second live call.
