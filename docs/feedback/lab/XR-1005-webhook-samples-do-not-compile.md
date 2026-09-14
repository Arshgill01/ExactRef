# XR-1005 — Webhook handler samples do not compile as published

## Finding

The only docs samples that failed offline compile are the Webhooks “Receive events” / “Idempotent handling” fences. Python uses `return` at module scope (`SyntaxError: 'return' outside function`) and never imports `json`. The second TypeScript fence uses `event` without declaring it (`TS2552: Cannot find name 'event'`). Every other TS/Python/curl sample from `calle-docs` typechecks or matches OpenAPI.

## Surface / version / commit or URL

- Live https://docs.heycall-e.com/webhooks.md and `calle-docs/content/guides/webhooks.mdx`
- Fetched `/tmp/calle-lab/doc-webhooks.md` (same fences)
- `@call-e/calle@0.7.0` / `calle-ai==0.7.0` in `/tmp/calle-lab`
- Harness: `docs/feedback/lab/tools/check_samples.py`

## Expected

A published handler sample would be a complete function (or say “inside your route handler”) and would typecheck with the shipped SDK.

## Actual

Python as published (`python -m py_compile` on the raw fence):

```
SyntaxError: 'return' outside function
    return {"error": "invalid_event_id"}, 400
```

and

```
SyntaxError: 'return' outside function
    return {"ok": True, "duplicate": True}
```

TypeScript second fence (`tsc --strict --module NodeNext --target ES2022`):

```
error TS2552: Cannot find name 'event'. Did you mean 'Event'?
```

The first TS fence parses `event` from `rawBody` but never exports it; the next fence assumes it. `rawBody` / `request` / `eventStore` are also undeclared (wrapped for the first fence).

Observed: compiler output on the raw fences. Inferred: copy-paste into a worker file fails before any webhook is received.

## Evidence

`/tmp/calle-lab/lab-out/sample-report.json` — source-only: TS 17/18, Python 9/11, curl 7/7. The four Python fails are these two fences plus their `doc-webhooks.md` mirrors.

Header name `CALL-E-Event-Id` matches OpenAPI `WebhookEventId` — that part is clean.

## Impact if an operator or agent trusted the current contract

The agent “fixes” the sample by dropping event-id matching or by accepting any POST. Unsigned webhooks are already the contract; a broken sample makes it likelier they skip the only check the page asks for (`CALL-E-Event-Id` == `event.id`) and fire side effects twice.

## Ask

Wrap both languages in a named handler, import `json`, pass `event` into the idempotency snippet, and add a `py_compile` / `tsc` job on the fences.

## Do not claim

- That we received a live webhook.
- A refile of unsigned-webhook FB-DOC-001 — this is compile, not the missing signature.
- Refile of 109 / 123 / 126 / 127.
