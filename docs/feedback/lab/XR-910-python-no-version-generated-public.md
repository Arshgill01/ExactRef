# XR-910 — PyPI `calle-ai==0.7.0` has no `__version__`, empty License metadata, and `calle.generated` is importable

## Finding

`pip install calle-ai==0.7.0`: `calle.__version__` is missing; `__all__` is the wrapper only. `import calle.generated` succeeds and exports `AuthenticatedClient`, `Client` (the openapi-python-client that returns `None` on 200 — XR-801). Wheel `METADATA` has `License:` empty / no `License-File` (git 0.7.1 sets `license = "MIT"`). `Requires-Python: >=3.11`. `Requires-Dist: attrs>=22.2.0, httpx<1.0.0,>=0.27.0` (unpinned upper on attrs). `calle/py.typed` exists (0 bytes) and `Typing :: Typed` is set. `mypy --strict` on a 20-line `from calle import CalleClient` file: **Success**. Cold import ~47 ms. Tests/`.env` not in the wheel (clean).

## Surface / version / commit or URL

- PyPI `calle-ai==0.7.0` in a fresh 3.12 venv `/tmp/calle-lab/pkg/pyvenv`
- Git `server-sdk-python` `9f69e4a` is unpublished 0.7.1 (XR-802)

## Expected

`calle.__version__ == importlib.metadata.version("calle-ai")`. `calle.generated` is private (`# noqa`, not importable as a supported module) or documented as generated-only. Wheel METADATA includes MIT. Public `__all__` is the only supported import path.

## Actual

**Observed**

```text
pip show calle-ai  → Version: 0.7.0  License: (empty)
calle.__version__  → missing
calle.__all__      → CalleClient, CalleAPIError, CalleAuthenticationError,
                     CalleConnectionError, CalleRateLimitError, CalleTimeoutError,
                     CalleWebhookSignatureError
import calle.generated → OK  __all__ = ('AuthenticatedClient', 'Client')
generated.models has CallTask? False
mypy --strict usage.py → Success: no issues found
```

`pyright --verifytypes calle` could not resolve the installed package from this lab’s invocation (`No py.typed file found`, score 0%) even though `calle/py.typed` exists — treated as a tool/layout miss, not a second finding.

## Evidence

`/tmp/calle-lab/pkg/pyvenv` + `usage.py`. No live `calls.create`.

## Impact if an operator or agent trusted the current contract

Agents pin “whatever `calle.__version__` is” and get `AttributeError`, then reinstall or switch to `calle.generated` and hit XR-801 (`None` on 200 → create again). License scanners flag PyPI 0.7.0 as unlicensed.

## Ask

Add `__version__` (single source with `importlib.metadata`). Mark `calle.generated` as unsupported in the README (`from calle import CalleClient` only). Publish the MIT metadata with 0.7.1.

## Do not claim

Refile of XR-801 (generated Calls `None`) or XR-802 (unpublished 0.7.1 / path encoding). That pyright --verifytypes is broken in the product (our invocation failed to resolve the package).
