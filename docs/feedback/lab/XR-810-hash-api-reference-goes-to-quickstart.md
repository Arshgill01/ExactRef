# XR-810 — Devpost “API Reference” hash `#api-reference` is rewritten to `/quickstart`

## Finding

The docs homepage ships a legacy hash redirect. `#/sdks` maps to `/sdks`. `#/api-reference` maps to `/api-reference`. **`#api-reference` (no slash)** matches neither rule and falls through to `window.location.replace("/quickstart")`.

The official Devpost resources list uses the no-slash form for “API Reference.” A contestant who clicks it, with JS on, lands on Quickstart (which’s first action is `create_and_wait` — a real call). A fetch/agent that does not run JS gets the homepage HTML and never sees the OpenAPI.

`#/sdks` on the same bullet works.

## Surface / version / commit or URL

- https://call-e.devpost.com/resources (200, 2026-09-14):  
  `SDKs` → `https://docs.heycall-e.com/#/sdks`  
  `API Reference` → `https://docs.heycall-e.com/#api-reference`
- Live homepage script (same text in `calle-docs/zudoku.config.tsx` `legacyHashRedirect`)
- Python SDK README uses the slashed forms (`#/sdks`, `#/api-reference`) — those work in a browser

## Expected

Both resources links would open the named page. The fallback for an unknown hash would be 404 or stay, not Quickstart.

## Actual

```31:42:calle-docs/zudoku.config.tsx
if (
  route === "/api-reference" ||
  route.startsWith("/api-1/") ||
  ...
) {
  window.location.replace("/api-reference");
  return;
}

window.location.replace("/quickstart");
```

`hash.slice(1)` for `#api-reference` is `api-reference`, which is not `"/api-reference"`.

`GET https://docs.heycall-e.com/#api-reference` and `GET .../#/sdks` are both HTTP 200 homepage HTML (hash is not sent to the server). The script only runs in a browser.

## Evidence

- Resources HTML quote: “SDKs and API Reference” with the two hrefs above
- `zudoku.config.tsx:6-43` and the inlined script on `https://docs.heycall-e.com/`
- `curl` of `/api-reference` (path, no hash) is 200 — the real page exists
- Crawl: `#/sdks` body includes the redirector; it does not include the SDKs markdown

## Impact if an operator or agent trusted the current contract

Contestants looking up the REST contract from Devpost are dropped on Quickstart. The Quickstart’s Python/TS samples call `create_and_wait`. That is a real outbound call if they paste-and-run. Agents that fetch the hash URL never see OpenAPI field names and invent `structuredResult` / `cursor` from the SDK page they did reach.

## Ask

Change the resources href to `https://docs.heycall-e.com/api-reference`. In the redirector, treat `api-reference` and `/api-reference` the same; do not default unknown hashes to `/quickstart`.

## Do not claim

- That we executed the redirect in a real browser this turn (script read + URL parse).
- A call placed from Quickstart this session (none).
- Refile of XR-204 (`/mcp` 404) except to note `/mcp` is still 404.
- Refile of 109 / 123 / 126 / 127.
