# XR-304 — Calls guide treats schema-valid extraction as a writable identifier

New docs overclaim. FB-001 remains the one live F/S substitution. Do not refile FB-001.

## Finding

The live Calls guide says CALL-E “validates the structured result against it before returning the terminal call task state” and offers `confirmation_code` as a required extracted string. Schema-valid plus a conversational yes is not independent verification. One live call returned a one-character substitution after readback and yes.

## Surface / version / commit or URL

- Live: https://docs.heycall-e.com/calls.md (Call inputs, Structured results, Appointment confirmation)
- Live: https://docs.heycall-e.com/quickstart.md “Read the result”
- One-call observation: OffHire, 2026-09-05, Python SDK 0.7.0 (FB-001). No second call.

## Expected

Docs say `structured_result` is an extraction: schema-valid, possibly confirmed in conversation, still `spoken_only` until a human types the value from a second channel.

## Actual

Live Calls:

> `result_schema` is a JSON Schema object for the whole call task. CALL-E validates the structured result against it before returning the terminal call task state.

> The schema is an extraction contract: the SDK sends the schema to CALL-E, CALL-E extracts a result from the completed call evidence, and the service validates the result before returning it.

Appointment pattern requires `confirmation_code`:

> The confirmation number or booking reference provided by the business, or an empty string if none was provided.

Live Quickstart:

> The terminal call task includes a stable status, a schema-valid structured result, and task-level outcome fields from the post-call summary.

The “Task completion” section (good) says `completed` is not business success. It does not say a schema-valid `confirmation_code` can be the wrong character after the callee agreed to a readback.

Contradicting source (FB-001, one call): intended identifier and extracted identifier differed by one character (`F`/`S`) after a full readback and “yes.” Schema checks passed.

## Evidence

- Live `/calls.md` and `/quickstart.md` fetched 2026-09-14.
- Do not paste the intended or extracted identifier into this file.
- No second live call.

## Impact if an operator or agent trusted the current contract

**Wrong write.** An agent copies `confirmation_code` / any exact reference from `structured_result` into a record because the page said the service already validated it. One character is enough to chase the wrong case.

## Ask (docs PR outline — do not open unless parent decides)

In `content/guides/calls.mdx` Structured results, after “the service validates the result before returning it,” add:

> Schema-valid is not independently verified. A readback plus “yes” is conversational confirmation. Do not write an exact operational identifier as a fact until a human types it from a second channel.

On the appointment `confirmation_code` field description, add: treat as spoken extraction; character-level mismatch remains possible.

## Do not claim

- Not a new FB-001. Stage (ASR vs conversation vs extraction) still not isolated.
- Do not leak intended identifiers into tasks or this file.
