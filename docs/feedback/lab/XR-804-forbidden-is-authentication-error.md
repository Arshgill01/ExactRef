# XR-804 — HTTP 403 is `CalleAuthenticationError`; the exception has no `.message`

## Finding

Docs split 401 and 403: missing/invalid key vs valid key without capability. The Python SDK maps **both** to `CalleAuthenticationError`. Operators who `except CalleAuthenticationError: rotate_or_reload_key()` treat a policy 403 as a bad secret.

`CalleAPIError` never stores `message` as an attribute (`super().__init__(message)` only). `error.message` is `AttributeError`. Official README prints `error.status_code, error.code, error.details`. TypeScript-style `error.message` does not port.

## Surface / version / commit or URL

- PyPI `calle-ai==0.7.0` / git `9f69e4a` `src/calle/errors.py` `api_error_from_response`
- Live https://docs.heycall-e.com/errors.md — “`forbidden` means the key is valid but not allowed…”
- Live https://docs.heycall-e.com/authentication.md — `401 unauthorized` vs `403 forbidden`
- Recovery table (errors.md): “`unauthorized` or `forbidden` | Check the key and its access…”

## Expected

401 → `CalleAuthenticationError`. 403 → `CalleAPIError` (or `CalleForbiddenError`) with `code == "forbidden"`. `error.message` would match the envelope `error.message` string.

## Actual

```51:54:src/calle/errors.py
if status_code in {401, 403}:
    return CalleAuthenticationError(...)
```

```4:16:src/calle/errors.py
class CalleAPIError(Exception):
    def __init__(self, *, code, message, status_code, details=None):
        super().__init__(message)
        self.code = code
        self.status_code = status_code
        self.details = details or {}
        # no self.message
```

## Evidence

`prove_sdk_bugs.py` `test_forbidden_is_authentication_error` (mocked GET 403 `code: forbidden`):

- raises `CalleAuthenticationError`
- `status_code == 403`, `code == "forbidden"`
- `isinstance(..., CalleAPIError)` is True
- `hasattr(exc.value, "message")` is False
- `str(exc.value) == "Key cannot use this project."`

`test_api_error_has_no_message_attr` on a 400 envelope: same missing attribute.

Unauthenticated live GET (read-only, bogus bearer) returned the documented envelope and 401, not 403. We did not provoke a live 403.

## Impact if an operator or agent trusted the current contract

A 403 on a billed destination or unpublished Goal is handled as “reload `CALLE_API_KEY`.” The key is valid. The agent retries with the same key, or an operator rotates keys during an in-flight wait. `error.message` in a logger/formatter crashes the except block and can skip the “do not create again” path.

## Ask

Map 403 to a non-auth class (or document that `CalleAuthenticationError` includes forbidden). Set `self.message = message` on `CalleAPIError`. Recovery table: 403 = capability/project, do not rotate the key.

## Do not claim

- A live 403 we received.
- That 401 mapping is wrong.
- Refile of XR-113 / 109 / 123 / 126 / 127.
