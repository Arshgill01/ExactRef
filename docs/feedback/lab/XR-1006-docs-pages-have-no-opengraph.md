# XR-1006 — Docs pages have `<title>` but no OpenGraph tags

## Finding

Live docs HTML sets `<title>` (`Quickstart | CALL-E Developer Docs`, `CALL-E Developer API | CALL-E Developer Docs`, homepage `CALL-E Developer Docs`) and a canonical URL. There is no `og:title`, `og:description`, or `og:image`. Slack, Discord, Devpost, and many agents that unfurl the URL get an empty card.

`zudoku.config.tsx` `metadata.description` is “Guides and API reference…” — it does not show up as `og:description` on the prerendered pages we fetched.

## Surface / version / commit or URL

- Live `/`, `/quickstart`, `/goal-runs`, `/sdks`, `/api-reference` (2026-09-14)
- `calle-docs/zudoku.config.tsx` `metadata.title` / `defaultTitle` / `description`

## Expected

Each guide would emit `og:title` / `og:description` matching the MDX frontmatter (`title` + `description`) so a pasted docs link previews the page, not a blank unfurl.

## Actual

Python parse of the live HTML (same result on five routes):

```
title: Quickstart | CALL-E Developer Docs
og:title:
og:desc:
canonical: https://docs.heycall-e.com/quickstart
```

Homepage: title `CALL-E Developer Docs`, og fields empty.

Observed: HTML. Inferred: crawlers that only read OG miss the guide descriptions that `llms.txt` already has.

## Evidence

```
curl -sS https://docs.heycall-e.com/quickstart | rg 'og:title|og:description|<title>'
```

No `property="og:title"` / `og:description` in the five pages.

## Impact if an operator or agent trusted the current contract

Contest resource links and Slack pastes look untitled. Weak for a wrong write; strong for “agents/humans skip the docs because the unfurl is empty” and for search snippets.

## Ask

Emit `og:title` / `og:description` from Zudoku metadata / MDX frontmatter on every prerendered guide and the API Reference info page.

## Do not claim

- A specific Slack or Discord unfurl screenshot (HTML parse only).
- Refile of 109 / 123 / 126 / 127.
