# XR-1009 — SDK README hash URLs fetch as the homepage for non-JS agents

## Finding

Both shipped SDK READMEs (npm `@call-e/calle@0.7.0`, PyPI `calle-ai==0.7.0`, and the git clones) document:

- `https://docs.heycall-e.com/#/sdks`
- `https://docs.heycall-e.com/#/api-reference`
- `https://docs.heycall-e.com/#/webhooks`
- `https://docs.heycall-e.com/#/changelog`

Those hashes are not sent to the server. `curl` / any agent HTTP client receives the homepage HTML (`CALL-E Developer Docs`, 3.5 KB index). Clean paths `/sdks`, `/api-reference`, `/webhooks`, `/changelog` exist and return the guides. The slashed hash form *does* redirect in a browser (unlike Devpost’s `#api-reference` — XR-810).

Package pages are the onboarding path for SDK users. Their agents never execute the homepage redirector.

## Surface / version / commit or URL

- `/tmp/calle-lab/tslab/node_modules/@call-e/calle/README.md` Documentation list
- `/tmp/calle-lab/server-sdk-python/README.md` (same hashes)
- npm registry `homepage`: GitHub `#readme` (not docs)
- PyPI `project_urls.Homepage`: GitHub; **no Documentation URL**
- Live `GET https://docs.heycall-e.com/#/sdks` → 200 homepage body (hash ignored)

## Expected

README links would be `https://docs.heycall-e.com/sdks` (and `/api-reference`, …). PyPI would list a Documentation URL.

## Actual

```
curl -sS -o /dev/null -w '%{http_code} %{size_download}' https://docs.heycall-e.com/#/sdks
# 200 3579   (homepage)
curl -sS -o /dev/null -w '%{http_code} %{size_download}' https://docs.heycall-e.com/sdks
# 200 ~57k   (SDKs guide)
```

Observed: README text + curl sizes. Inferred: an agent that “opens the SDK guide from the package README” conditions on homepage copy.

## Evidence

README Documentation sections quoted above. Homepage vs `/sdks` byte counts.

## Impact if an operator or agent trusted the current contract

The agent never sees `phones` vs `phone`, `timeoutMs` vs `timeout_seconds`, or “Python source not currently public,” and invents a client from the five-line integrations `createAndWait` hero instead. Wrong method names → failed create or a retry.

## Ask

Replace hash URLs with clean paths in both SDK READMEs. Add PyPI `Documentation: https://docs.heycall-e.com/sdks`.

## Do not claim

- That `#/sdks` fails in a browser (the redirector handles the slashed form).
- A refile of XR-810 (Devpost `#api-reference` without the slash → Quickstart).
- Refile of 109 / 123 / 126 / 127.
