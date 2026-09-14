# XR-1001 — API Reference has no markdown variant

## Finding

Every guide that `llms.txt` lists as `*.md` returns `text/markdown`. The API Reference does not. `/api-reference.md` and every `/api-reference/<tag>.md` are **404** (`NoSuchKey`). `?format=md` on those URLs returns the HTML app (`text/html`), not the contract.

Agents that follow `llms.txt` → “API Reference” therefore get a JS page or a 404, never OpenAPI field names in markdown.

## Surface / version / commit or URL

- Live https://docs.heycall-e.com/llms.txt (200, 2026-09-14): `[API Reference](/api-reference)`
- Live https://docs.heycall-e.com/api-reference.md → **404**
- Live https://docs.heycall-e.com/api-reference/calls.md → **404** `NoSuchKey`
- Live `?format=md` on `/quickstart` and `/api-reference` → 200 `text/html`
- Contrast: `/quickstart.md`, `/calls.md`, `/sdks.md` → 200 `text/markdown`
- `calle-docs/zudoku.config.tsx` `publishMarkdown: true` applies to `content/guides/**`, not the OpenAPI plugin
- Playwright `tests/docs-site.spec.ts` asserts `/quickstart.md` is markdown and that `llms.txt` contains `[API Reference](/api-reference)` — it locks the HTML-only link

## Expected

The machine-readable entry for the contract would be a `.md` page or a clear pointer only to `/openapi/calle.openapi.yaml`. `?format=md` would not silently return HTML.

## Actual

Observed (`curl -sS -L -w '%{http_code} %{content_type}'`):

```
404  /api-reference.md
404  /api-reference/calls.md
200  text/html  /api-reference?format=md
200  text/markdown  /quickstart.md
```

`llms.txt` lists OpenAPI as a second bullet. Agents that only expand the “API Reference” line never see YAML.

## Evidence

Commands in `docs/feedback/lab/tools/crawl_links.py` and the 2026-09-14 curl log. Sitemap includes `/api-reference`, `/api-reference/calls`, `/goals`, `/goal-runs`, `/webhooks`, `/~schemas` — none have `.md` mirrors.

Observed: HTTP statuses and content-types. Inferred: an LLM client that appends `.md` to every `llms.txt` path (common) 404s on the contract.

## Impact if an operator or agent trusted the current contract

The agent invents field names (`cursor` vs `after`, `phone` vs `phones`, camelCase vs snake_case) or pastes Quickstart `create_and_wait` instead of reading OpenAPI. That is a wrong write or a duplicate call, not a missing pretty-print.

## Ask

Publish `/api-reference.md` (or per-tag markdown) that inlines or links the live OpenAPI, and point `llms.txt` at that `.md` (or only at `/openapi/calle.openapi.yaml`). Reject `?format=md` with 404 or serve markdown.

## Do not claim

- That we opened the Try-it playground (disabled).
- A refile of XR-810 (Devpost `#api-reference` → Quickstart) or XR-204 (`/mcp` 404).
- Refile of 109 / 123 / 126 / 127.
