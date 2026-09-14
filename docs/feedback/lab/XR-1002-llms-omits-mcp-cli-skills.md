# XR-1002 — `llms.txt`, sitemap, and site search omit MCP / CLI / skills

## Finding

The official agent-discovery file on the docs host lists nine guides plus API Reference and OpenAPI. It does not mention MCP, the CLI, or skills. The sitemap matches that set (16 HTML URLs). Pagefind reports `page_count: 17`. There is no docs page for the MCP guide, so search cannot index `plan_call` / `run_call` / `get_call_run`.

Contest onboarding (hosted install prompt, integrations README) starts at MCP + skills. An agent that begins at `https://docs.heycall-e.com/llms.txt` never sees that contract.

## Surface / version / commit or URL

- Live https://docs.heycall-e.com/llms.txt and `/tmp/calle-lab/doc-llms.txt` (same 9 guides)
- Live https://docs.heycall-e.com/sitemap.xml (16 `<loc>`s, no `/mcp`)
- Live https://docs.heycall-e.com/pagefind/pagefind-entry.json `page_count: 17`
- Live `/mcp` and `/mcp.md` still 404 (owned XR-204)
- Official MCP guide lives at `call-e-integrations/docs/mcp/openagent-oauth.md` (GitHub), not on the docs host
- Playwright `publishes non-empty Markdown and LLM discovery files` asserts the current `llms.txt` membership and **does not** require an MCP line — it will fail a PR that adds one unless updated

## Expected

`llms.txt` (and search) would list the MCP guide, or a stub page that points at the GitHub/hosted install URL, so an agent using the docs host learns the three-tool order.

## Actual

`llms.txt` body (complete Documentation + API sections) has no `mcp`, `cli`, `skill`, or `plan_call`.

Pagefind entry has no document list in the JSON (hash only). A missing `/mcp` page cannot be indexed. Site search on `docs.heycall-e.com` therefore cannot return the MCP guide.

Observed: file contents and 404s. Inferred: Pagefind’s 17 pages are the sitemap set plus chrome, still without MCP.

## Evidence

```
curl -sS https://docs.heycall-e.com/llms.txt
curl -sS https://docs.heycall-e.com/sitemap.xml
curl -sS https://docs.heycall-e.com/pagefind/pagefind-entry.json
# {"version":"1.5.2","languages":{"en":{"hash":"en_2bb557e9fd","wasm":"en","page_count":17}},...}
curl -sS -o /dev/null -w '%{http_code}' https://docs.heycall-e.com/mcp
# 404
```

`robots.txt` allows `/` and points at the sitemap — crawlers are not the blocker.

## Impact if an operator or agent trusted the current contract

Hackathon agents that “read the docs” via `llms.txt` implement Calls `createAndWait` (Quickstart) and never learn `plan_call` → `run_call` → `get_call_run`. That is a different product surface and a real outbound call if they paste Quickstart.

## Ask

Add a `/mcp` guide (or a stub that links the integrations MCP doc) to the docs nav, `llms.txt`, sitemap, and Pagefind. Update the Playwright `llms.txt` assertions to require that entry.

## Do not claim

- That we queried the live Pagefind WASM index for the string `plan_call` (entry JSON + missing page are the evidence).
- A refile of XR-204 except as the 404 that makes search empty — this card is the discovery file, not the missing route alone.
- Refile of 109 / 123 / 126 / 127.
