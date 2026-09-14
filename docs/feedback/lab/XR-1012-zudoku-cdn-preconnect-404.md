# XR-1012 — Docs HTML preconnects to `https://cdn.zudoku.dev/` which 404s

## Finding

Prerendered docs pages include `<link rel="preconnect" href="https://cdn.zudoku.dev/">`. `GET https://cdn.zudoku.dev/` returns **404**. Script and CSS for the app are local (`/assets/entry.client-….js`). The preconnect does not load a required asset today, but it is a live 404 from every docs page.

## Surface / version / commit or URL

- Live https://docs.heycall-e.com/quickstart and `/` (2026-09-14)
- Crawl external probe: `https://cdn.zudoku.dev/` status 404

## Expected

Preconnect only to origins that serve assets, or omit the tag if Zudoku is self-hosted.

## Actual

```
<link rel="preconnect" href="https://cdn.zudoku.dev/">
```

```
curl -sS -o /dev/null -w '%{http_code}' https://cdn.zudoku.dev/
# 404
```

Observed: tag + status. Inferred: leftover default from the Zudoku theme; not a broken guide body.

## Evidence

`rg cdn.zudoku` on the live Quickstart HTML. Crawl `broken` list.

## Impact if an operator or agent trusted the current contract

Browser extra DNS/TLS to a 404 origin (noise, CSP reports). An agent that crawls every `href` reports a site-wide broken link. Low for a wrong write.

## Ask

Remove the preconnect or point it at an origin that returns 200 (or 204).

## Do not claim

- That docs JS failed to load (it is same-origin).
- Refile of 109 / 123 / 126 / 127.
