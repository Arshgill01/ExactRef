# CONFIRM-XR-802 — The Python repo's own contract check rejects the live OpenAPI spec

2026-09-14. New evidence for XR-802 (git 0.7.1 unpublished; live/docs pin 0.7.0). No call. No form.

## What was re-verified

`server-sdk-python` ships `scripts/verify_openapi_contract.py`, which the repo's `validate.sh` runs in CI. Its first assertion is `spec.info.version == "0.7.1"`. Swapping the vendored `openapi/calle.openapi.yaml` for the live `https://docs.heycall-e.com/openapi/calle.openapi.yaml` (fetched 2026-09-14) and running the script:

```text
RuntimeError: OpenAPI contract check failed: unexpected API version
exit=1
```

Restored the vendored file afterwards; working tree clean.

## Why it matters beyond XR-802

The vendor's own guard says the SDK on `main` is contract-checked against a spec the public API does not serve. Either the live spec is behind (and the SDK's path-encoding fix is verified against a future contract), or `main` drifted ahead without a release. A hackathon builder who clones `main` to “see the source” gets a package whose contract check fails against production.

## Also seen this pass

- Live `run_call` / `get_call_run` `outputSchema.status` is a free string with `NO ANSWER` as an example (XR-601), which the git 0.7.1 spec also does not enumerate.
- Live `plan_call` `outputSchema.next_step` is `type: string`; `run_call`/`get_call_run` `next_step` is an object (XR-602).

## Do not claim

Which side (docs or repo) is authoritative. A second live call. Refile of 109/123/126/127.
