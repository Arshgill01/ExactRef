# XR-204 — Developer docs site has no MCP page; repo URL is the only contract

## Finding

`https://docs.heycall-e.com/llms.txt` lists Quickstart, Calls, Goal Runs, SDKs, webhooks, errors — no MCP, no CLI, no `openagent_oauth`. `https://docs.heycall-e.com/mcp/openagent-oauth` returns HTTP 404. Agents that start from the published developer site never see the tool contract, the “do not auto-run `run_call`” rules, or the production MCP URL.

The repo guide and the Cursor plugin still name one URL: `https://seleven-mcp-sg.airudder.com/mcp/openagent_oauth`. That host is not `heycall-e.com`. An agent grepping docs.heycall-e.com for “MCP” will invent a path or copy the Calls API (`POST /v1/calls`) instead.

## Surface / version / commit

- Live `https://docs.heycall-e.com/` and `/llms.txt` (fetched 2026-09-14)
- Live `https://docs.heycall-e.com/mcp/openagent-oauth` → 404
- Repo canonical: `CALLE-AI/call-e-integrations` `main` `4a53b01` `docs/mcp/openagent-oauth.md`
- Plugin `packages/cursor-plugin/plugin/mcp.json` same airudder URL
- CLI default `DEFAULT_BASE_URL` = `https://seleven-mcp-sg.airudder.com`, channel `openagent_oauth`

## Expected

The developer docs index used by agents (`llms.txt`) includes the MCP endpoint, the three-tool workflow, and a non-404 permalink. Hostnames in plugin, CLI, and docs match or are explicitly aliased.

## Actual

`llms.txt` documentation list (complete): Webhooks, SDKs, Regions, Quickstart, Goal Runs, Errors, Changelog, Calls, Authentication, API Reference, OpenAPI. No MCP.

Minimal config in the repo guide:

```text
https://seleven-mcp-sg.airudder.com/mcp/openagent_oauth
```

Cursor `mcp.json` uses that URL. `calle mcp config` derives `<base-url>/mcp/<channel>`. There is no `docs.heycall-e.com` MCP URL that resolves.

## Evidence (local / read-only remote)

- GET `/mcp/openagent-oauth` on the docs host: 404
- GET `/llms.txt`: no MCP link
- Repo file and plugin JSON: airudder host only

No live `tools/list` recorded this resume. Do not treat this card as a fourth-tool finding.

## Impact if an operator or agent trusted the current contract

**Wrong write / wrong API.** Agent follows Quickstart `POST /v1/calls` (or Goal Runs) while the user asked for CALL-E MCP. Different envelope, different wait predicates, no `confirm_token`. Or the agent fabricates `https://docs.heycall-e.com/mcp/...` and fails auth, then retries with a new plan.

Secondary: hostname drift (`heycall-e.com` vs `airudder.com`) looks like a phishing tell to a cautious agent; the cautious path is “stop,” the incautious path is “use the REST Calls API instead.”

## Ask

Add an MCP page to docs.heycall-e.com, link it from `llms.txt`, and state the production Streamable HTTP URL plus “do not use `/v1/calls` for MCP-started runs.” Keep the airudder URL as the wire address; do not silently change it.

## Do not claim

OAuth metadata mismatch on the wire (not fetched). That the airudder URL is wrong. Token or region outage. XR-001 fourth tool.
