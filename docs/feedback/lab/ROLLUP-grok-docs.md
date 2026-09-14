# ROLLUP — docs samples, links, llms.txt (Grok XR-1001..1012)

2026-09-14. No `run_call`, no `calls.create` against a recipient, no form, no Discord post, no GitHub issues/PRs, no tokens or subscriber numbers in these files.

Workdir `/tmp/calle-lab/`. Live `docs.heycall-e.com`. Packages `@call-e/calle@0.7.0`, `@call-e/cli@0.5.1`, `calle-ai==0.7.0`. Scripts: `docs/feedback/lab/tools/` (`run_lab.sh`). Reports: `/tmp/calle-lab/lab-out/`.

## New this pass, ranked by operator / agent harm

| # | ID | Harm | One line | Ask |
|---|----|------|----------|-----|
| 1 | [XR-1002](XR-1002-llms-omits-mcp-cli-skills.md) | wrong product / live create | `llms.txt` + sitemap + Pagefind omit MCP/CLI/skills; contest path is invisible | Add `/mcp` to nav, `llms.txt`, Playwright |
| 2 | [XR-1001](XR-1001-api-reference-has-no-markdown.md) | invented fields | `/api-reference.md` 404; `?format=md` is HTML | Publish API markdown or point `llms.txt` at OpenAPI only |
| 3 | [XR-1007](XR-1007-complete-example-ignores-base-url.md) | unintended live call | Auth says examples read `CALLE_BASE_URL`; `examples/calls.py` does not | Pass `base_url` from env |
| 4 | [XR-1004](XR-1004-scheduled-calling-advertised-as-shipped.md) | invented schedule / burst create | README “Scheduled and Batch Calling” vs SDKs “not included” | Split batch vs schedule |
| 5 | [XR-1005](XR-1005-webhook-samples-do-not-compile.md) | skip event-id check | Webhook Python `return` outside function; TS `event` undefined | Wrap handlers; compile in CI |
| 6 | [XR-1008](XR-1008-three-published-wait-timeouts.md) | duplicate create | Wait budgets 120 / 300 / 600 on official docs | One number (+ XR-303’s “does not cancel”) |
| 7 | [XR-1003](XR-1003-goal-runs-still-says-api-06.md) | wrong pin | Live Goal Runs eyebrow **API 0.6**; packages/spec 0.7.0 | Eyebrow 0.7.0 |
| 8 | [XR-1009](XR-1009-sdk-readme-hash-urls-are-homepage.md) | agent misses SDK guide | npm/PyPI README `#/sdks` curls as homepage | Clean `/sdks` paths |
| 9 | [XR-1011](XR-1011-markdown-mirrors-drop-heading-ids.md) | miss recovery section | `.md` mirrors lack heading ids (`#task-completion`, `#sdk-examples`) | Emit ids in `publishMarkdown` |
| 10 | [XR-1010](XR-1010-playwright-pins-versions-and-webhook-path.md) | lock stale facts | Playwright requires `0.7.0` text and `/calle/webhook` | Stop pinning literals |
| 11 | [XR-1006](XR-1006-docs-pages-have-no-opengraph.md) | skipped docs | No `og:title` / `og:description` | Emit OG from frontmatter |
| 12 | [XR-1012](XR-1012-zudoku-cdn-preconnect-404.md) | crawl noise | `preconnect` `cdn.zudoku.dev` → 404 | Remove or fix origin |

Confirmations with new evidence: [CONFIRM-XR-204](CONFIRM-XR-204.md) (`/mcp` still 404; still absent from `llms.txt` + Pagefind), [CONFIRM-XR-606](CONFIRM-XR-606.md) (hosted install guide still `npm install -g @call-e/cli` + bare `calle`).

## Sample pass/fail (calle-docs source; fetched `doc-*.md` mirrors match)

**Counts:** TypeScript **17/18** pass · Python **9/11** pass · curl vs live OpenAPI **7/7** pass · CLI flags vs `@call-e/cli@0.5.1` **126/126** pass · `examples/calls.py` `py_compile` **pass** (env bug is XR-1007, not syntax).

Including fetched mirrors: TS 34/36, Python 18/22 (same two webhook fences twice).

| ID | Lang | Kind | Result |
|---|---|---|---|
| authentication.mdx:3 | ts | complete | PASS |
| authentication.mdx:4 | py | complete | PASS |
| authentication.mdx:2 | curl | GET `/v1/goals?limit=1` | PASS |
| calls.mdx:3 | ts | continuation | PASS |
| calls.mdx:4 | py | continuation | PASS |
| calls.mdx:5–11 | ts | schema fragments | PASS (wrapped object) |
| calls.mdx:13–14 | ts/py | wait + events | PASS (`timeoutMs` / `timeout_seconds` names match SDK) |
| calls.mdx:1–2 | curl | POST/GET `/v1/calls` | PASS (headers + `task` required) |
| goal-runs.mdx:10–12 | ts/py | continuation | PASS (`publishedRunSpec`, `nextCursor`, `phone`) |
| goal-runs.mdx curl ×4 | curl | goals list/get/run/poll | PASS (`Idempotency-Key`, `phone`) |
| quickstart.mdx:3–4 | ts/py | complete | PASS |
| quickstart.mdx:6–7 | ts/py | createAndWait | PASS types (behavior = owned XR-605) |
| quickstart.mdx:8,10 | ts/py | read result | PASS |
| sdks.mdx:3,5–6 | ts/py | complete / continuation | PASS (`phones`, not `phone`) |
| webhooks.mdx:2 | ts | handler | PASS with harness stubs |
| **webhooks.mdx:3** | **py** | **handler** | **FAIL** `SyntaxError: return outside function` |
| **webhooks.mdx:4** | **ts** | **handler** | **FAIL** `TS2552: Cannot find name 'event'` |
| **webhooks.mdx:5** | **py** | **handler** | **FAIL** `return` outside function |

Skills / MCP guide / CLI reference: JSON `argv` arrays use `--to-phone` (not `--phone`), `--run-id`, `--json`, `--start-only`, `--no-browser-open`, `--args-json`. Offline `calle call plan --phone …` is rejected. **Clean.**

No sample used a wrong SDK method name, `timeoutMs` on Python, or `phones` vs `phone` on Goal Runs.

## Broken-link table

**New 404s:** 8 URL patterns (API Reference markdown family + Zudoku CDN). **Owned, not refiled:** `/mcp`, `/mcp.md`, Devpost `/details/resources`. **Not bugs:** npm HTML 403 (registry JSON 200), dashboard 403 (auth wall), crawler `pagefind/ptr,chunk` (JS source).

| URL | Status | Card |
|---|---|---|
| `/api-reference.md` | 404 `NoSuchKey` | XR-1001 |
| `/api-reference/calls.md` (and goals, goal-runs, webhooks, `~schemas.md`) | 404 | XR-1001 |
| `/api-reference?format=md` | 200 **HTML** | XR-1001 |
| `/mcp`, `/mcp.md` | 404 | CONFIRM-XR-204 |
| `https://cdn.zudoku.dev/` | 404 (preconnect) | XR-1012 |
| `https://call-e.devpost.com/details/resources` | 404 | owned (canonical `/resources` 200) |
| Devpost `#api-reference` | browser → Quickstart | owned XR-810 |
| HTML `#task-completion` etc. | **exist** | clean |
| `.md#task-completion`, `.md#sdk-examples` | hash missing | XR-1011 |

Devpost `/resources` example GitHub paths (batch-runner, n8n, three skills): **200**. `modelcontextprotocol.io/docs/tools/inspector`: **200** (redirects to dated spec URL). No **new** Devpost resource 404s.

## What was checked and clean

- **robots.txt:** `Allow: /`, sitemap URL correct.
- **Guide `.md` mirrors:** all nine guides 200 `text/markdown`.
- **OpenAPI** `/openapi/calle.openapi.yaml` 200, `info.version: 0.7.0`.
- **curl fences vs spec:** paths, `Authorization`, `Content-Type`, `Idempotency-Key`, required `task` / Goal `phone`; no extra fields. `CALL-E-Event-Id` matches the spec parameter name.
- **CLI vs skills/MCP guide:** `--to-phone` exists; `--phone` does not; `--json` accepted.
- **SDK method names** in docs: `createAndWait` / `create_and_wait`, `waitForResult` / `wait_for_result`, `publishedRunSpec` — typecheck on 0.7.0.
- **Status enum on Calls guide:** five values including `queued` (meaning already owned XR-302). No extra `NO ANSWER` on the docs host (XR-601 is skills/schema).
- **E.164 / US Indonesian / `context` / `createAndWait` Quickstart / onboarding `/calle/webhook` table / changelog concurrency:** owned, not refiled.
- **Placeholders:** `<E164_PHONE>`, `<YOUR_API_KEY>` only; no `TODO`/`TBD`/`<your-…>` in published guides. SDKs “does not include” list is explicit, not a leftover stub. Integrations “In Development” is labeled.
- **Versions:** docs and Playwright say 0.7.0 (true today). Goal Runs “API 0.6” is the live inconsistency (XR-1003). CLI 0.5.1 / Cursor skill 0.1.2 / skills.sh attribution 0.1.0 are different packages, not a single pin error.
- **Homepage hash `#/sdks`:** works in a browser (slashed form). Agent/curl issue is XR-1009.

## Do not claim

A second live call. Form submit. Discord or GitHub writes. Refile of 109 / 123 / 126 / 127 / 90 / 116 / 118 / 121. Refile of XR-005 / 204 / 301 / 302 / 303 / 601 / 605 / 606 / 607 / 712 / 807 / 808 / 809 / 810 / 114.
