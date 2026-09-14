# XR-812 — Official `examples/calls.py` E.164 regex is Goals-strict, not Calls-strict

## Finding

The complete Python example linked from live Quickstart rejects phones with `re.fullmatch(r"\+[1-9][0-9]{7,14}", phone)` — 8–15 digits after `+`. OpenAPI Calls `recipients[].phones` is `^\+[1-9]\d{6,14}$` (7–15 after `+`). Goal Run `phone` is `^\+[1-9]\d{7,14}$` (8–15 after `+`).

The official Calls example therefore applies the **Goal** minimum to a Calls `create`. A number the Calls API schema accepts is `ValueError` locally and never sent.

This is not XR-116 (the two OpenAPI patterns disagree). It is a third pattern on the documented Calls happy path.

## Surface / version / commit or URL

- https://docs.heycall-e.com/quickstart.md “Run a complete example” → `calle-docs/examples/calls.py`
- `calle-docs` `88f37ff` `examples/calls.py:25-26`
- Live OpenAPI 0.7.0 `CallTaskRecipientRequest.phones.items.pattern` vs `CreateGoalRunRequest.phone.pattern`
- Git OpenAPI 0.7.1: same two patterns (unchanged in the 0.7.0↔0.7.1 diff we read)

## Expected

The Calls example would use the Calls pattern, or one documented E.164 for all surfaces.

## Actual

```25:27:calle-docs/examples/calls.py
if not re.fullmatch(r"\+[1-9][0-9]{7,14}", phone):
    raise ValueError("Use an authorized E.164 phone number.")
```

Calls OpenAPI: first digit 1–9, then **6–14** more digits.  
Goals OpenAPI / this regex: then **7–14** more digits.

NANP `+1` + 10 digits matches all three. The gap is the 7-digit-total class XR-116 already named for Goals vs Calls.

## Evidence

- `examples/calls.py` as cloned 2026-09-14
- Live `openapi/calle.openapi.yaml` patterns (same as XR-116 evidence)
- Quickstart still: `python examples/calls.py start ... --phone "$CALLE_TEST_PHONE"`

No live create. Pattern read + regex only.

## Impact if an operator or agent trusted the current contract

A short national number that Calls would accept never leaves the example script. The user “fixes” the number or skips the destination. Porting the example regex onto a Calls batch job silently drops XR-116’s extra class.

## Ask

Use one function shared with the OpenAPI Calls pattern (or ITU 8–15 total digits) and name it. Do not copy the Goal regex into the Calls example.

## Do not claim

- A live 422.
- Refile of XR-116 (OpenAPI vs OpenAPI). This card is example vs Calls OpenAPI.
- Refile of 109 / 123 / 126 / 127.
