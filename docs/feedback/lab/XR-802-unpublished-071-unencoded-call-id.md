# XR-802 — Git advertises Python SDK 0.7.1; PyPI is 0.7.0 and interpolates raw `call_id`

## Finding

`CALLE-AI/server-sdk-python` `main` is `calle-ai` 0.7.1 (`CHANGELOG.md` dated 2026-09-04, commit `9f69e4a` 2026-09-08). There is no `v0.7.1` tag, no GitHub Release (`[]`), and `https://pypi.org/pypi/calle-ai/0.7.1/json` is 404. `pip install calle-ai` still yields 0.7.0 (uploaded 2026-08-19).

The unpublished patch percent-encodes call IDs, including `.`. PyPI 0.7.0 does `GET /v1/calls/{call_id}` with the raw string. httpx then normalizes `..` so `calls.get("../goals")` becomes `GET /v1/goals`. 0.7.1 stays on `/v1/calls/%2E%2E%2Fgoals`.

Live docs OpenAPI is still `info.version: 0.7.0`. Git OpenAPI is `0.7.1` (mostly description edits, including dropping the “do not branch on `failure_code`” warning). Docs `/sdks` still pin `calle-ai==0.7.0`.

## Surface / version / commit or URL

- PyPI `calle-ai==0.7.0` — `site-packages/calle/calls.py` `get` / `list_events`
- Git `9f69e4a` — `src/calle/calls.py` `_call_path`; `CHANGELOG.md` `## [0.7.1] - 2026-09-04`; `RELEASE.md` (publish only via `vX.Y.Z` GitHub Release)
- GitHub tags API: `v0.7.0`, `v0.6.0` only. Releases: empty array.
- Live https://docs.heycall-e.com/openapi/calle.openapi.yaml `version: 0.7.0`
- https://docs.heycall-e.com/sdks.md still “Python: `calle-ai==0.7.0`”

## Expected

A changelog section dated and titled 0.7.1 would be installable (`pip install calle-ai==0.7.1`) or marked Unreleased. Pip users would have the path-encoding fix the repo tests for.

## Actual

```
pip index: 0.7.0, 0.6.0, 0.2.0, 0.1.0
GET https://pypi.org/pypi/calle-ai/0.7.1/json → 404
GET https://api.github.com/repos/CALLE-AI/server-sdk-python/releases → []
```

PyPI 0.7.0 (MockTransport, observed):

```
calls.get("../goals") → request raw_path /v1/goals
```

Git 0.7.1 (same input):

```
_call_path("../goals") == "/v1/calls/%2E%2E%2Fgoals"
raw_path b'/v1/calls/%2E%2E%2Fgoals'
```

0.7.1’s own test uses `call_id = "../goals?admin=1#fragment%2F"`.

## Evidence

- `/tmp/calle-lab-py/prove_sdk_bugs.py` `test_pypi_get_does_not_encode_dot_segments` (PyPI): printed `RAW_PATH /v1/goals`
- `PYTHONPATH=.../python-sdk/src` `_call_path` print above
- `site-packages/calle/calls.py:43` `return self._request("GET", f"/v1/calls/{call_id}")`
- `python-sdk/src/calle/calls.py:100-102` `quote(..., safe="").replace(".", "%2E")`
- `python-sdk/tests/test_calls.py:166-184` (0.7.1 path-segment test)
- `CHANGELOG.md:10-27`; `pyproject.toml` `version = "0.7.1"`
- `README.md:241-243` still licenses only `0.6.0` and `0.7.0`

No live GET of a real call. The `../goals` string is the repo’s own fixture, not a production id.

## Impact if an operator or agent trusted the current contract

`pip install calle-ai==0.7.1` fails; agents “upgrade” from the changelog and stop. Pip users keep unencoded IDs. If `call_id` is taken from an unsigned webhook `data.id` (current deliveries are unsigned — cite FB-DOC-001, not a new incident) a `../` value leaves `/v1/calls/` and hits another route with the same bearer token. Operators who clone `main` and pin “0.7.1” in docs that still say 0.7.0 disagree with production.

## Ask

Either publish `v0.7.1` (tag + GitHub Release + PyPI) or move the changelog block back to `[Unreleased]`. Keep the path encoder. Until publish, docs should say “pip latest is 0.7.0; `main` is unpublished.”

## Do not claim

- That we sent `../` to the live API.
- A rate of webhook-injected IDs.
- Refile of XR-111 / gauntlet-004 / 109 / 123 / 126 / 127.
