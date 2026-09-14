# XR-110 — Python `recipients[]` does not apply the `phone` → `phones` alias

## Finding

Both SDKs advertise a singular `phone` alias. TypeScript applies it to **every** recipient object. Python applies it only to the singular `recipient=` kwarg. A list item `{ "phone": "+1..." }` is forwarded as-is. OpenAPI `CallTaskRecipientRequest` requires `phones` and sets `additionalProperties: false`, so the extra `phone` key is illegal.

TypeScript also **drops** unknown recipient keys. Python **keeps** them. Same input, two wire bodies.

## Surface / version / commit or URL

- Python `calle-ai==0.7.0` `f7a4b82` `src/calle/calls.py`
- TypeScript `@call-e/calle@0.7.0` `36ee6f1` `src/calls.ts` `toApiRecipient`
- OpenAPI `CallTaskRecipientRequest`

This is not gauntlet-006 (aliases exist and are client-only). It is Python vs TS drift on the **plural** path.

## Expected

`recipients=[{"phone": "<E164>"}]` would normalize the same way as `recipient={"phone": "<E164>"}` and the same way as TS `recipients: [{ phone: "..." }]`. Extra keys would be stripped or rejected in both languages.

## Actual

Python create:

```31:38:src/calle/calls.py
body = {
    "task": task,
    "recipients": [_normalize_recipient(recipient)] if recipient is not None else recipients,
    ...
}
```

```91:97:src/calle/calls.py
def _normalize_recipient(recipient: JsonObject) -> JsonObject:
    if "phones" in recipient:
        return recipient
    phone = recipient.get("phone")
    normalized = {key: value for key, value in recipient.items() if key != "phone"}
    normalized["phones"] = [phone] if phone is not None else []
    return normalized
```

If `phones` is present, extras (including a leftover `phone`) are kept. The list path never calls `_normalize_recipient`.

TypeScript:

```94:103:src/calls.ts
function toApiRecipient(input: CallRecipientInput): ... {
  const phones = input.phones ?? (input.phone !== undefined ? [input.phone] : []);
  const recipient = { phones };
  if (input.locale !== undefined) recipient.locale = input.locale;
  if (input.region !== undefined) recipient.region = input.region;
  return recipient;
}
```

```116:118:src/calls.ts
if (input.recipients !== undefined) {
  body.recipients = input.recipients.map(toApiRecipient);
}
```

Python tests only cover singular `recipient={"phone": ...}`. No test for `recipients=[{"phone": ...}]`.

## Evidence

- `server-sdk-python/src/calle/calls.py:31-38`, `91-97`
- `server-sdk-typescript/src/calls.ts:94-118`
- `server-sdk-python/tests/test_calls.py` (singular `recipient` only)
- OpenAPI `CallTaskRecipientRequest`: `required: [phones]`, `additionalProperties: false`

Offline contract read. No POST /v1/calls this session.

## Impact if an operator or agent trusted the current contract

A TS snippet ported to Python (`recipients=[{"phone": "..."}]`) 400s (`invalid_request` / `invalid_recipient`) or, if the server is lenient, drops the number. `recipient={"phone": "...", "name": "Alex"}` becomes `{phones, name}` in Python (400) and `{phones}` in TS (silent drop of `name`). Batch jobs are the ones that use the plural path.

## Ask

Map `recipients` through `_normalize_recipient` and copy only `phones` / `locale` / `region`, matching `toApiRecipient`. Add a unit test: `recipients=[{"phone": "+14155550100"}]` → wire `[{"phones": ["+14155550100"]}]`.

## Do not claim

- Refile of gauntlet-006 (the alias itself).
- A live 400 we provoked.
- Refile of 109 / 123 / 126 / 127.
