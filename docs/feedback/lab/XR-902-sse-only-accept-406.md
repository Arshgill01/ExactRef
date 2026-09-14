# XR-902 — Streamable-HTTP `Accept: text/event-stream` is 406; GET on the MCP URL hangs

## Finding

The live MCP endpoint requires `Accept` to include `application/json`. `Accept: text/event-stream` (the Streamable HTTP / SSE preference many MCP SDKs send) returns HTTP **406** with JSON-RPC `-32600` “Not Acceptable: Client must accept application/json”. The same 406 is returned for `Accept: text/html`. `Accept: application/json` and the CLI’s dual `application/json, text/event-stream` succeed as JSON (never SSE). A bare `GET` with the CLI’s Accept list did not return in 20s (client abort).

## Surface / version / commit or URL

- Live `https://seleven-mcp-sg.airudder.com/mcp/openagent_oauth` 2026-09-14
- `@call-e/core` `1ce9d77` `lib/mcp-client.js` sets `Accept: application/json, text/event-stream` (so the official CLI is fine)
- MCP Streamable HTTP: clients may send `Accept: text/event-stream` or `GET` to listen

## Expected

If the server is JSON-only, `initialize` / docs say so, and `Accept: text/event-stream` returns a finite 406 (or 405 on GET) with a `Retry-After`/`Allow` that names POST+JSON. GET is not left open.

## Actual

**Observed:**

```text
POST tools/list Accept: application/json          → 200 application/json
POST tools/list Accept: text/event-stream         → 406
  {"jsonrpc":"2.0","id":"server-error","error":{"code":-32600,"message":"Not Acceptable: Client must accept application/json"}}
POST tools/list Accept: text/html                 → 406 (same envelope)
POST tools/list Accept: application/json, text/event-stream → 200 application/json (no SSE)
GET  /mcp/openagent_oauth (same dual Accept)      → no response in 20005ms (TimeoutError)
```

No `mcp-session-id` on any response (stateless). A forged `Mcp-Session-Id: totally-not-a-session` still returned `tools/list` 200.

## Evidence

`/tmp/calle-lab/pkg/mcp-probe2.mjs` labels `Accept text/event-stream`, `Accept text/html`, `HTTP GET endpoint`. Token from CLI cache; never printed.

## Impact if an operator or agent trusted the current contract

Any host whose MCP HTTP transport prefers SSE-only (or opens GET for server messages) fails to list tools or hangs until its own timeout. The agent then “MCP is down” and falls back to inventing `run_call` arguments or using the REST SDK. **Inferred:** ChatGPT’s app path works because it sends JSON; Cursor/generic SDK clients are the ones that break.

## Ask

Accept `text/event-stream` as a JSON response (or implement SSE). Return 405 + `Allow: POST` on GET instead of a hang. State “JSON POST only; no Streamable HTTP GET” in the MCP guide.

## Do not claim

That a specific third-party host was observed hanging in this session. A live `run_call`.
