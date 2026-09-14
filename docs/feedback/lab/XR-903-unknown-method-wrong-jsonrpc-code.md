# XR-903 — Unknown MCP method `definitely/not/a/method` is `-32602`, not `-32601`

## Finding

JSON-RPC unknown-method is `-32601` Method not found. Live, `logging/setLevel` and `completion/complete` correctly return `-32601`. A nonsense method containing slashes (`definitely/not/a/method`) returns HTTP 200 with `-32602` Invalid request parameters and empty `data`. Clients that branch on `-32601` to disable optional features will treat a typo’d method as a parameter bug and retry with different params.

JSON-RPC **batch** arrays are rejected with HTTP **400** and `-32602` (pydantic `JSONRPCMessage` model_type), not `-32600`/`-32700`.

## Surface / version / commit or URL

- Live MCP 2026-09-14, protocolVersion `2025-11-25`
- JSON-RPC 2.0 error codes

## Expected

Any unimplemented method name → `-32601`. Batch (if unsupported) → a single documented error (`-32600` Invalid Request) with HTTP 200 or 400, named in the MCP guide.

## Actual

**Observed** unknown slash method:

```json
{"jsonrpc":"2.0","id":"unk-1","error":{"code":-32602,"message":"Invalid request parameters","data":""}}
```

**Observed** real optional methods:

```json
{"jsonrpc":"2.0","id":"lg1","error":{"code":-32601,"message":"Method not found"}}
{"jsonrpc":"2.0","id":"comp1","error":{"code":-32601,"message":"Method not found"}}
```

**Observed** batch (`[{tools/list},{resources/list}]`):

```text
HTTP 400
{"jsonrpc":"2.0","id":"server-error","error":{"code":-32602,"message":"Validation error: 4 validation errors for JSONRPCMessage\nJSONRPCRequest\n  Input should be a valid dictionary..."}}
```

`notifications/initialized` omitted: subsequent `tools/list` still 200 (notification is optional in practice).

## Evidence

`/tmp/calle-lab/pkg/mcp-probe2.mjs` + follow-up `logging/setLevel` / `completion/complete`. No tokens in files.

## Impact if an operator or agent trusted the current contract

A host probing `resources/subscribe` vs a typo’d method gets different codes. Retry logic on `-32602` resends the same unknown method. Batch-supporting clients get a 400 pydantic dump, not a spec error.

## Ask

Map every unmatched method name to `-32601`. If batch is unsupported, document it and return `-32600` with `id: null`. Hide pydantic traces from `error.data` / `message`.

## Do not claim

That `-32602` on slash names is a security issue. Refile of XR-003 (CLI `ok: true` on `isError`).
