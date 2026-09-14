# CONFIRM-XR-204 — `/mcp` and `/mcp.md` still 404; still absent from `llms.txt` and Pagefind

## Finding

Re-verified 2026-09-14. Not a new id.

## Surface / version / commit or URL

- https://docs.heycall-e.com/mcp → 404
- https://docs.heycall-e.com/mcp.md → 404
- https://docs.heycall-e.com/llms.txt — no MCP line
- https://docs.heycall-e.com/sitemap.xml — no `/mcp`
- https://docs.heycall-e.com/pagefind/pagefind-entry.json `page_count: 17`

## Expected

A docs MCP page, or at least an `llms.txt` pointer at the GitHub guide.

## Actual

Both paths 404. New evidence this pass: Pagefind cannot index a missing page; `llms.txt` still omits MCP (see XR-1002 for the discovery-file ask).

## Evidence

```
curl -sS -o /dev/null -w '%{http_code}' https://docs.heycall-e.com/mcp
# 404
curl -sS -o /dev/null -w '%{http_code}' https://docs.heycall-e.com/mcp.md
# 404
```

## Impact if an operator or agent trusted the current contract

Unchanged: agents never find `plan_call` on the docs host.

## Ask

Unchanged from XR-204 / XR-1002: publish `/mcp` and list it in `llms.txt`.

## Do not claim

- A new route id. This is confirmation only.
- Refile of 109 / 123 / 126 / 127.
