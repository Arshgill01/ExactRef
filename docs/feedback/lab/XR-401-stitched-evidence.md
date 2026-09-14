# XR-401 — `reference_evidence` was a stitch, not a verbatim span

OffHire exception `OH-01` only. Not a product finding about OffHire Desk.

## Finding

On the 2026-09-05 Calls result, the custom field described as a verbatim recipient quote was a concatenated multi-turn excerpt. A sibling field on the same object was an exact turn. ExactRef `PASTE_READY` Q-10 omitted this.

## Surface / version / commit or URL

Calls API terminal `structured_result`, 2026-09-05, Python server SDK 0.7.0 (`server-sdk-python` `f7a4b826`). Schema asked for `reference_evidence` as a short verbatim quote and `pickup_evidence` the same way. One create, one attempt.

## Expected

A field whose schema description says “verbatim recipient quote” equals one `transcript_turns[].text`, or is empty, or is labeled synthesized. Ellipses and a `USER:` prefix are synthesis.

## Actual

`reference_evidence` joined three later user fragments with `USER:` and `...`. It was not an exact match to any single turn.

`pickup_evidence` equaled one user turn exactly.

OpenAPI task-level `evidence` is already “short evidence items,” not verbatim spans. Custom schema descriptions guide extraction; they are not hard rules.

## Evidence

Sanitized facts only. No phone, token, or recipient identity.

- Schema description (public task): “Short verbatim recipient quote supporting the final reference/correction.”
- Returned stitch (structure): `USER: 07198. ... SECT. IST. ... Yes, yes, that is exactly right.`
- `pickup_evidence` matched the arranged-not-collected user turn.
- Audit: `pickup_evidence_exact_quote: true`, `reference_evidence_exact_single_quote: false`.
- Offline analog: gauntlet LC03 classifies verbatim vs stitched vs synthesized against turns. Programmed envelope, not a second live observation.

## Impact if an operator or agent trusted the current contract

A stitched field can be pasted as “the quote that proves the identifier.” Combined with a schema-valid extract and an in-band yes, it looks like independent proof. It is not. ExactRef would label this synthesized support, not a second channel.

## Ask

Document two kinds: `verbatim_span` (must equal one turn) and `synthesized_support` (may concatenate). If the schema says verbatim and no single span exists, return empty rather than a stitch.

## Do not claim

- Rate or second live call.
- That CALL-E “dropped an F.” The stitch quotes the last in-band S-form plus yes (see XR-403).
- Refile of 109 / 123 / 126 / 127.

## Prior art (added 2026-09-14 22:30 IST)

Related prior art: [calle-docs #41](https://github.com/CALLE-AI/calle-docs/issues/41) — `structured_result` populated without evidence. The stitched “verbatim” field is the evidence-side twin of that report; cite as confirmed here.
