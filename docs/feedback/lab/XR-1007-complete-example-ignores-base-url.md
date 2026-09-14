# XR-1007 — Official complete example ignores documented `CALLE_BASE_URL`

## Finding

Authentication tells operators that “the example SDK servers and call scripts read `CALLE_BASE_URL` when you provide it” so staging jobs do not send live calls. The official complete example linked from Quickstart — `calle-docs/examples/calls.py` — constructs `CalleClient(api_key=api_key)` only. The Python 0.7.0 client does not read the environment itself. A staging `export CALLE_BASE_URL=…` is silently ignored; the script still targets `https://api.heycall-e.com`.

TypeScript SDK examples in `server-sdk-typescript` *do* pass `process.env.CALLE_BASE_URL`. The docs sentence is written as if both languages’ examples do.

## Surface / version / commit or URL

- Live https://docs.heycall-e.com/authentication.md “Environments”
- Live https://docs.heycall-e.com/quickstart.md “Run a complete example” → `examples/calls.py`
- `calle-docs/examples/calls.py` `main()` (`CalleClient(api_key=api_key)`)
- PyPI `calle-ai==0.7.0` `calle/client.py` `base_url: str = "https://api.heycall-e.com"` — no `os.environ` read
- Contrast: `server-sdk-typescript/examples/create-and-wait.ts` `baseUrl: process.env.CALLE_BASE_URL ?? "https://api.heycall-e.com"`

## Expected

The script the Quickstart tells people to run would honor `CALLE_BASE_URL`, or the Authentication sentence would say only the TypeScript examples do.

## Actual

Authentication:

```
The example SDK servers and call scripts read CALLE_BASE_URL when you provide it.
```

`examples/calls.py`:

```
with CalleClient(api_key=api_key) as client:
    return run(client, args.directory, args.phone)
```

No `os.environ.get("CALLE_BASE_URL")`. `python -m py_compile examples/calls.py` succeeds — the bug is env handling, not syntax.

Observed: source + SDK constructor. Inferred: a mis-set staging URL still places a production call when `start --phone` is used (we did not run `start`).

## Evidence

Grep of `examples/calls.py` and `calle/client.py`. Quickstart install block exports `CALLE_API_KEY` and `CALLE_TEST_PHONE` only.

## Impact if an operator or agent trusted the current contract

The operator believes they pointed the complete example at a sandbox. The script still creates a real call on the default host. That is a duplicate/unintended live call, the thing Authentication claims to prevent.

## Ask

Pass `base_url=os.environ.get("CALLE_BASE_URL", "https://api.heycall-e.com")` in `examples/calls.py`, or delete the Authentication sentence. Add a unit test that a stub transport sees the env URL.

## Do not claim

- That we ran `examples/calls.py start` or placed a call.
- A refile of XR-605 (`createAndWait` drops `call_id`).
- Refile of 109 / 123 / 126 / 127.
