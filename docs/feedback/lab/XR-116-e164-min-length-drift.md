# XR-116 — Calls vs Goals E.164 min-length patterns disagree

## Finding

The same OpenAPI file accepts a shorter E.164 on Calls `recipients[].phones` than on Goal Run `phone`. A number that creates a Call can 422 a Goal Run without a region or product change.

## Surface / version / commit or URL

OpenAPI 0.7.0 in both SDK trees (`36ee6f1` / `f7a4b82`), schemas:

- `CallTaskRecipientRequest.phones.items.pattern`: `^\\+[1-9]\\d{6,14}$` → 7–15 digits after `+`
- `CreateGoalRunRequest.phone.pattern`: `^\\+[1-9]\\d{7,14}$` → 8–15 digits after `+`

https://docs.heycall-e.com/calls — “A valid E.164 number does not establish that its destination is supported.” That sentence does not mention the two regexes.

## Expected

One E.164 rule for both surfaces, or a documented reason Goals reject the extra one-digit-shorter class.

## Actual

Calls: first digit 1–9, then 6–14 more digits.  
Goals: first digit 1–9, then 7–14 more digits.

NANP (`+1` + 10 digits) matches both. The gap is the 7-digit-total class (country code + short national number) that Calls’ schema allows and Goals’ schema rejects (`422 invalid_phone`).

SDKs do not pre-validate; they forward the string. The drift is the contract the SDKs generate from.

## Evidence

- `openapi/calle.openapi.yaml` `CallTaskRecipientRequest.phones.items.pattern`
- `openapi/calle.openapi.yaml` `CreateGoalRunRequest.phone.pattern`
- Files are byte-identical across the two SDK repos (`diff -q` 2026-09-14)

No live create. Pattern read only.

## Impact if an operator or agent trusted the current contract

A working Calls integration ported to Goals fails on the same stored number. The error looks like a bad phone, not a schema mismatch. Operators “fix” it by adding a digit or skipping the destination.

## Ask

Align the two patterns (prefer E.164: `+` and 8–15 digits total, or ITU min/max you actually route). Add one sentence on Goal Runs: Goal `phone` is stricter than Calls `phones`.

## Do not claim

- That a specific country is blocked (we did not probe routing).
- Refile of region issues 90 / 116 / 118 / 121.
- A live 422.
- Refile of 109 / 123 / 126 / 127.
