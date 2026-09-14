# XR-805 — Non-JSON 4xx/5xx raise `json.JSONDecodeError`, not `CalleAPIError`

## Finding

Both `CalleCalls._request` and `CalleGoals._request` do `response.json()` on every `status >= 400` with no try/except. An HTML 401, an empty 502, or a proxy page is not mapped through `api_error_from_response`. Callers who only catch `CalleAPIError` / `CalleAuthenticationError` / `CalleTimeoutError` see a raw decode error.

The official complete example (`calle-docs/examples/calls.py`) groups `json.JSONDecodeError` with connection/timeout — so the docs authors already tripped this. The SDK README error snippet does not.

## Surface / version / commit or URL

- PyPI `calle-ai==0.7.0` / git `9f69e4a` `src/calle/calls.py:83` and `src/calle/goals.py:134`
- https://docs.heycall-e.com/errors.md envelope (always JSON `{error:{code,message,details}}`)
- `calle-docs/examples/calls.py:91` `except (CalleConnectionError, CalleTimeoutError, json.JSONDecodeError)`

## Expected

A non-JSON error body would still become `CalleAPIError` (or `CalleConnectionError`) with `status_code` set and `code` defaulting to `internal_error`. JSON envelopes stay as today.

## Actual

```83:84:src/calle/calls.py
if response.status_code >= 400:
    raise api_error_from_response(response.status_code, response.json())
```

`httpx.Response.json()` on `text/html` or empty body raises `json.JSONDecodeError`. That exception is not a `CalleAPIError`.

## Evidence

`prove_sdk_bugs.py` against PyPI 0.7.0:

- `test_non_json_401_is_not_calle_error` — GET 401 body `<html>unauthorized</html>` → `json.JSONDecodeError`
- `test_empty_502_is_not_calle_error` — GET 502 `content=b""` → `json.JSONDecodeError`

Control: live `GET https://api.heycall-e.com/v1/goals?limit=1` with bearer `bogus_key_not_a_secret` returned JSON `{"error":{"code":"unauthorized","message":"Invalid or missing API key.","details":{}}}` (401). The happy-path envelope matches the docs. The SDK still cannot survive a non-JSON edge in front of that API.

## Impact if an operator or agent trusted the current contract

A WAF/HTML 401 or empty 502 during `wait_for_result` is not `CalleTimeoutError` and not `CalleAPIError`. The wait aborts. An agent that interprets “unknown exception” as “create never accepted” POSTs again. The official example only survives because it special-cases `JSONDecodeError`.

## Ask

Wrap `response.json()` in `_request`. On decode failure raise `CalleAPIError(code="internal_error", message="Non-JSON error body.", status_code=..., details={"content_type": ...})`. Document that typed errors are raised even when the body is not the envelope.

## Do not claim

- That the live API returned HTML today (it returned the JSON envelope for our bogus key).
- A rate of proxy failures.
- Refile of 109 / 123 / 126 / 127.
