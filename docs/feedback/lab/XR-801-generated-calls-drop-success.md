# XR-801 — Generated Calls client treats 200/201 as undocumented and returns `None`

## Finding

The shipped `calle.generated` client cannot represent a Call. There is no `CallTask` or `WebhookEvent` model. `get_call.sync` / `create_call.sync` parse only error statuses. A successful `GET /v1/calls/{id}` (200) or `POST /v1/calls` (201) returns `None` by default, or raises `UnexpectedStatus` if `raise_on_unexpected_status=True`. Goal generate paths parse 200/201 correctly. The handwritten `CalleClient.calls` wrapper papers this over.

Observed on both PyPI `calle-ai==0.7.0` and git `9f69e4a` (`calle-ai` 0.7.1).

## Surface / version / commit or URL

- PyPI `calle-ai==0.7.0` (installed 2026-09-14)
- Git `CALLE-AI/server-sdk-python` `9f69e4a` (pyproject 0.7.1)
- `src/calle/generated/api/calls/get_call.py`, `create_call.py`
- `src/calle/generated/models/__init__.py` (no `CallTask`, no `WebhookEvent`)
- OpenAPI `CallTask` / `WebhookEvent` / `WebhookCallData` exist in `openapi/calle.openapi.yaml`
- Contrast: `generated/api/goal_runs/create_goal_run.py` parses `201` → `GoalRun`

## Expected

An OpenAPI-generated Calls client would parse 200/201 as `CallTask`. `WebhookEvent.data` would be the same object. `verify_openapi_contract.py` would fail CI if those models are missing.

## Actual

`get_call._parse_response` handles 401/403/404/429/500 only. 200 falls through to `return None` (default `raise_on_unexpected_status=False`).

`create_call._parse_response` handles 400/401/403/409/422/429/500 only. 201 → `None`. Return type is `ErrorEnvelope | None`.

`calle.generated.models.__all__` exports `CallTaskRecipient` and `CallTaskAttempt` but not `CallTask`. `WebhookCallData` is `allOf: [CallTask]`; `WebhookEvent` is also absent.

`scripts/verify_openapi_contract.py` asserts `CallTask` and `WebhookEvent` exist in the YAML, not in the generated package.

## Evidence

Offline mocks, `/tmp/calle-lab-py/prove_sdk_bugs.py`, PyPI 0.7.0:

- `test_generated_get_call_returns_none_on_200` — `sync("call_123")` is `None` after HTTP 200 with a complete CallTask body.
- `test_generated_get_call_raises_on_200_when_strict` — `UnexpectedStatus.status_code == 200`.
- `test_generated_create_call_returns_none_on_201` — `sync(...)` is `None` after HTTP 201.
- `test_no_calltask_or_webhookevent_model` — `import calle.generated.models.call_task` raises `ImportError`.
- Wrapper `CalleClient.calls.get` on the same 200 body returns the dict (control).

```37:78:src/calle/generated/api/calls/create_call.py
def _parse_response(...) -> ErrorEnvelope | None:
    if response.status_code == 400:
        ...
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(...)
    else:
        return None
```

No live `POST /v1/calls`. No phone call.

## Impact if an operator or agent trusted the current contract

An agent that imports the generated client (the package docstring: “A client library for accessing CALL-E Developer API”) treats a successful create/get as “no call.” It may POST again with a new idempotency key. That is a duplicate-call path. Webhook typing is impossible through generated models because `WebhookEvent` was never emitted.

## Ask

Regenerate so `CallTask` and `WebhookEvent` exist and 200/201 parse as `CallTask`. Add a CI assert: `from calle.generated.models import CallTask, WebhookEvent` and a respx test that `get_call.sync` is not `None` on 200.

## Do not claim

- That the handwritten `CalleClient.calls` wrapper drops 200 (it does not).
- A live create we provoked.
- Refile of XR-107 / XR-115 / 109 / 123 / 126 / 127.
