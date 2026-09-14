# XR-1010 — Playwright pins SDK 0.7.0 and OpenAPI `/calle/webhook`

## Finding

`calle-docs/tests/docs-site.spec.ts` asserts facts that will rot or that lock a known docs lie:

1. Visible text `@call-e/calle@0.7.0` and `calle-ai==0.7.0` on `/sdks`.
2. OpenAPI body contains the path `/calle/webhook` (the customer-receiver path listed as if it were a CALL-E route — XR-807).
3. Already owned: the Python “Not currently public” cell (XR-301). Not refiled here.

A docs PR that publishes 0.7.1 or that removes `/calle/webhook` from the spec (correct: it is not an API the client calls) fails CI until the test is edited. That is how the Python-private cell survived.

No Playwright assertion pins region lists, pricing, or MCP tool counts except indirectly via `llms.txt` membership (XR-1002).

## Surface / version / commit or URL

- `/tmp/calle-lab/calle-docs/tests/docs-site.spec.ts` lines 362, 527–531
- Live packages today: npm 0.7.0 / PyPI 0.7.0 / CLI 0.5.1 — the version pin is currently true, the lock is the finding

## Expected

Tests would assert “a version cell exists” or read the version from the package, and would not require a customer webhook path inside the developer OpenAPI.

## Actual

```
expect(openApiText).toContain("/calle/webhook");
await expect(page.getByText("@call-e/calle@0.7.0").first()).toBeVisible();
await expect(page.getByText("calle-ai==0.7.0").first()).toBeVisible();
```

Observed: test source. Inferred: the next SDK bump or a spec cleanup of `/calle/webhook` dies in this file the same way XR-005 died in XR-301.

## Evidence

`rg` of `docs-site.spec.ts`. Live OpenAPI still contains `/calle/webhook` (customer server, `servers.url: https://{yourserver}`).

## Impact if an operator or agent trusted the current contract

Version pins: stale install lines after 0.7.1 (XR-802’s unpublished git minor is the next candidate). `/calle/webhook` pin: agents keep POSTing a receiver path at `api.heycall-e.com` (XR-807).

## Ask

Assert a version pattern or fixture, not a literal `0.7.0`. Drop the `/calle/webhook` substring require (or assert it only under `servers: https://{yourserver}`). Keep XR-301’s Python-public fix separate.

## Do not claim

- That 0.7.0 is already wrong on npm/PyPI today (it matches).
- A refile of XR-301 (Python-private expect) or XR-807 (onboarding table) except as the test lock.
- Refile of 109 / 123 / 126 / 127.
