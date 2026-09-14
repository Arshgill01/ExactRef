# XR-1003 — Live Goal Runs guide still branded “API 0.6”

## Finding

The published Goal Runs page opens with **`API 0.6` · Server-side · Asynchronous**. The live OpenAPI `info.version`, the same page’s SDK section, and the shipped packages are **0.7.0**. The July 22 changelog entry that introduced “API 0.6” is historical; the eyebrow on today’s guide is not.

An integrator who pins `calle-ai==0.6.0` / `@call-e/calle@0.6.0` following the live badge will not get the Goal Runs client the rest of the page documents.

## Surface / version / commit or URL

- Live https://docs.heycall-e.com/goal-runs.md and `calle-docs/content/guides/goal-runs.mdx` line 8
- Same file line 343: “stable TypeScript and Python `0.7.0` packages”
- Live OpenAPI `info.version: 0.7.0` (`/tmp/calle-lab/live-openapi.yaml`)
- PyPI `calle-ai` 0.7.0; npm `@call-e/calle` 0.7.0
- Changelog July 22, 2026: “Phone-only Goal Run requests in API 0.6” and “SDK source candidates … 0.6.0 … until the 0.6.0 release is published”

## Expected

The current guide would say API / SDK 0.7.0 (or drop the API-minor badge). Historical 0.6 notes would stay in the changelog only.

## Actual

```
**API 0.6** · **Server-side** · **Asynchronous**
```

Later on the same page:

```
The following methods are available in the stable TypeScript and Python `0.7.0`
packages.
```

Observed: both strings on the live markdown. Inferred: 0.6.0 packages on npm/PyPI either do not exist or lack `client.goals` (not re-downloaded this turn; 0.7.0 is what the page tells you to call).

## Evidence

`curl -sS https://docs.heycall-e.com/goal-runs.md | head` and the MDX source. OpenAPI header `version: 0.7.0`.

## Impact if an operator or agent trusted the current contract

Pin the wrong minor, miss `client.goals.run` / `run_and_wait`, then fall back to Calls `create_and_wait` with a Goal-shaped payload (`phone` + `variables` without `task`) — `invalid_request` or a one-shot call that ignores the published Goal.

## Ask

Change the Goal Runs eyebrow to 0.7.0 (or remove it). Keep “API 0.6” only in the dated changelog entry.

## Do not claim

- That we installed `calle-ai==0.6.0`.
- A refile of XR-802 (git 0.7.1 unpublished).
- Refile of 109 / 123 / 126 / 127.
