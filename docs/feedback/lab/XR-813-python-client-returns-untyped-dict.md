# XR-813 — Python high-level client returns `dict[str, Any]`; `mypy --strict` passes vacuously

2026-09-14. Offline. `calle-ai==0.7.0` from PyPI in `/tmp/calle-lab/venv`. Observed unless marked inferred.

## Finding

`CalleClient.calls.create` / `get` / `wait_for_result` / `create_and_wait` and the Goals equivalents are annotated `-> JsonObject` where `JsonObject = dict[str, Any]`. The package ships `py.typed`, so type checkers trust it — and then accept any key and reject every attribute. The TypeScript SDK returns a typed `Call`. A Python operator gets no compile-time protection on `structured_result`, `recipients`, `status`, or `failure_code`, and the "mypy strict passes" result on a usage file is true only because every value is `Any`.

## Surface / version

- `calle/calls.py:9` — `JsonObject = dict[str, Any]`; `:27`, `:42`, `:55`, `:64` return `JsonObject`. Same in `calle/goals.py:11`.
- `calle/py.typed` present.
- TypeScript `server-sdk-typescript` `src/calls.ts:214` `create(...): Promise<Call>`, `:268` `waitForResult(...): Promise<Call>`.
- Docs (`/calls` "Call identifiers") already teach the asymmetry: "use the top-level `id` … in HTTP and Python, or `call.id` in TypeScript"; Python samples use `call["id"]`, `call["recipients"][i]["structured_result"]`.
- Docs `/sdks` lists "Pydantic result schema helpers" for Python.

## Expected

A typed return (TypedDict at minimum; ideally the generated Pydantic model that `calle.generated` already carries for requests) so that `call.id`, `call.recipients[0].structured_result` type-check, and a misspelled key is an error.

## Actual

```
$ cat u.py
from calle import CalleClient
client = CalleClient(api_key="key_test", base_url="http://127.0.0.1:9")
def main() -> None:
    call = client.calls.create(task="Confirm the appointment.", recipients=[{"phones": ["+15555550100"]}])
    result = client.calls.wait_for_result(call.id, timeout_seconds=1)
    print(result.status)
$ python -m mypy --strict u.py
u.py:5: error: "dict[str, Any]" has no attribute "id"  [attr-defined]
u.py:6: error: "dict[str, Any]" has no attribute "status"  [attr-defined]
Found 2 errors in 1 file (checked 1 source file)
```

Rewriting to `call["id"]` / `result["structured_reuslt"]` (typo intended) passes `mypy --strict` with zero errors — the checker cannot see the key.

## Impact if trusted

An operator who reads "Python SDK, `py.typed`, mypy clean" assumes field names are checked. They are not. `structured_result` vs `structuredResult`, `recipients[0]["attempts"]` vs `["attempt"]`, or a `failure_code` branch on a misspelled key all pass CI and fail at runtime — after the call has been placed and billed. The 2026-09-05 write-gate work (ExactRef) had to add its own field lookup precisely because nothing in the Python return type names `structured_result`.

## Ask

Return a typed `Call` (and `GoalRun`) from the high-level Python client — `TypedDict` is a zero-runtime-cost first step; the generated Pydantic models are the end state. Until then, say on `/sdks` that Python returns plain dicts and that TypeScript is the typed SDK.

## Prior art

None found in `server-sdk-python` issues (#30, #39 are about waiter semantics and error mapping). Sibling: XR-801 (generated Calls client has no `CallTask` model and returns `None` on 200/201) — the same gap from the generated side.

## Do not claim

Not a runtime bug; every documented dict-access sample works. Not a second live call. Does not refile 109/123/126/127.
