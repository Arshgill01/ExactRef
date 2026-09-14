# XR-301 — Playwright locks the false “Not currently public” Python cell

New. 2026-09-14. Companion to CONFIRM-XR-005, not a refile of it.

## Finding

`calle-docs` CI asserts the live SDKs table still shows a cell named “Not currently public” and asserts there is **zero** link to `CALLE-AI/server-sdk-python`. A correct docs edit would fail the suite until the test is changed. That is a lock on a false contract.

## Surface / version / commit or URL

- Live page the test protects: https://docs.heycall-e.com/sdks
- Test on GitHub `main` (fetched 2026-09-14): https://github.com/CALLE-AI/calle-docs/blob/main/tests/docs-site.spec.ts
- Local clone of the same assertion: `/Users/arshdeepsingh/Developer/CallE/repos/calle-docs/tests/docs-site.spec.ts`

## Expected

Docs tests assert true public facts: package pins, TypeScript repo link, and a Python repo link once the source is public.

## Actual

`tests/docs-site.spec.ts` (GitHub `main`, 2026-09-14):

```ts
await expect(
  page.getByRole("cell", { name: "Not currently public" }),
).toBeVisible();
await expect(
  page.getByRole("link", { name: "CALLE-AI/server-sdk-python" }),
).toHaveCount(0);
```

The sentence those assertions freeze, on the live SDKs page:

> The Python package is available from PyPI, but its source repository is not currently public.

Contradicting source: `gh repo view CALLE-AI/server-sdk-python` → `visibility: PUBLIC`, `isPrivate: false`, pushed 2026-09-14.

## Evidence

- Raw test file from `CALLE-AI/calle-docs` on 2026-09-14 contains the two expects above.
- Live `/sdks` still renders the cell the test names.
- CONFIRM-XR-005 is the page-level lie. This file is the CI lock.

## Impact if an operator or agent trusted the current contract

Same wrong-source path as XR-005, plus a maintainer who tries to tell the truth will watch CI fail and revert. The false contract is self-healing.

## Ask (docs PR outline — do not open unless parent decides)

In `tests/docs-site.spec.ts`, replace the two expects with:

- `getByRole("link", { name: "CALLE-AI/server-sdk-python" })` is visible and `href` is `https://github.com/CALLE-AI/server-sdk-python`.
- `getByRole("cell", { name: "Not currently public" })` has count 0.

Ship in the same PR as the `sdks.mdx` sentence change in CONFIRM-XR-005. Do not land the prose fix alone.

## Do not claim

- Not a new “Python is public” discovery. That remains XR-005.
- No second live call. Do not open the PR from this lab.
