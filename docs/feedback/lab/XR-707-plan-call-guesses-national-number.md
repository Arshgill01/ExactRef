# XR-707 — `plan_call` accepts a non-E.164 national number and proceeds as if it has a recipient

## Finding

`to_phones` is described as “E.164” and “If the user provides a local/ambiguous phone number, leave this unset… instead of guessing the country code.” Sending a 10-digit national number (no `+`, no country code) is **accepted** (`ok: true`, `isError: false`). The planner claims it already has the recipient (“number ending in …0100”, English) and only asks for the goal. Distinct from XR-116 (SDK OpenAPI regex digit-count drift).

## Surface / version / commit or URL

- Live `plan_call` 2026-09-14 via `@call-e/cli@0.5.1`
- `tools/list` `plan_call.inputSchema.properties.to_phones` description
- Tool description: “Do not guess region/language or reformat ambiguous phone numbers.”

## Expected

Non-E.164 values are rejected (`isError: true`) or treated as unknown (leave unset; ask for country code). No implied region/language.

## Actual

Args (national digits only; not written here). Response excerpt:

```text
confirm_summary: I have the recipient number ending in ...0100 and can place
the call in English, but I need to know what the call should say or accomplish.
ready_to_run: false
questions[0].key: goal
```

A 10-digit NANP-looking value was enough for the planner to assume English and a usable recipient. `555-1234` (even less structure) came back as a “clarifying question” whose text was the error “Calls to this region are not supported right now.” — an error stuffed into `questions[].question`.

## Evidence

`mcp/plan-edges/local-digits.out` and `non-e164.out` in the local lab dir. Schema quote from `mcp tools --json`. Observed, not inferred: the confirm_summary names a last-four and a language without either being supplied as `language` / E.164.

## Impact if an operator or agent trusted the current contract

An agent that “helpfully” copies a local office number into `to_phones` (against the schema text) gets a plan that looks almost ready. Filling the goal then yields `ready_to_run: true` and a real call to whatever country the planner guessed. The same agent following the description would have left `to_phones` unset.

## Ask

Validate `to_phones` as E.164 before planning. If the value is national/ambiguous, ignore it and ask for country code; do not invent language/region. Do not put hard errors in `questions[].question`.

## Do not claim

The guessed country or that a call was placed. XR-116 (Calls vs Goal regex length). A specific live destination.
