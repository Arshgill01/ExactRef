# CONFIRM-XR-005 — Python SDK source is public; live SDKs page still says it is not

Fetched 2026-09-14. No live CALL-E call. No form submit.

## Finding

The live SDKs guide still tells operators the Python server SDK source “is not currently public.” `CALLE-AI/server-sdk-python` is a public GitHub repository today.

## Surface / version / commit or URL

- Live: https://docs.heycall-e.com/sdks and https://docs.heycall-e.com/sdks.md
- Source: https://github.com/CALLE-AI/calle-docs/blob/main/content/guides/sdks.mdx
- Changelog still implies the same split: https://docs.heycall-e.com/changelog (September 3, 2026 names only the TypeScript repo)
- Repo: `gh repo view CALLE-AI/server-sdk-python` on 2026-09-14

## Expected

The repository column matches GitHub visibility. A public MIT-style SDK repo is linked the same way TypeScript is.

## Actual

Live sentence:

> The TypeScript SDK is maintained in a public repository. The Python package is available from PyPI, but its source repository is not currently public.

Live table cell for Python: `Not currently public`. No `CALLE-AI/server-sdk-python` link.

`gh` on 2026-09-14:

- `visibility: PUBLIC`
- `isPrivate: false` / `private: false`
- `url: https://github.com/CALLE-AI/server-sdk-python`
- `pushed_at: 2026-09-14T02:10:32Z`

## Evidence

- Live HTML/Markdown fetched 2026-09-14 from `docs.heycall-e.com/sdks`.
- GitHub raw `calle-docs` `content/guides/sdks.mdx` still has `| Python | \`calle-ai\` | Not currently public |`.
- The CI lock that keeps this sentence from being fixed without a test change is documented separately as [XR-301-playwright-locks-python-private.md](XR-301-playwright-locks-python-private.md).

## Impact if an operator or agent trusted the current contract

An agent or integrator treats Python as closed-source, skips wait-predicate and timeout reading in the public repo, and copies only the docs examples (`timeout_seconds=120`). That is the path to a local timeout plus a second create. Security reviewers also miss the public Python surface the page denies exists.

## Ask (docs PR outline — do not open unless parent decides)

In `content/guides/sdks.mdx`:

- Replace “its source repository is not currently public” with “The Python SDK is maintained in a public repository.”
- Change the Python repository cell from `Not currently public` to a link: `[CALLE-AI/server-sdk-python](https://github.com/CALLE-AI/server-sdk-python)`.
- In `content/guides/changelog.mdx` September 3: name the Python repo next to TypeScript, or drop the one-sided “TypeScript SDK source is available” sentence.
- Pair with the test edit in XR-301 or CI will fail the docs fix.

## Do not claim

- Not a new discovery of XR-005. This is a 2026-09-14 re-fetch.
- No second live call. No rate. Do not treat PyPI `calle-ai==0.7.0` as unpublished.
