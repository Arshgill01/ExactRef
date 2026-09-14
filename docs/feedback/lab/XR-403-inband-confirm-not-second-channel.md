# XR-403 — In-band S-form plus yes is correlated with the extract

OffHire exception `OH-01` only. Cited by [XR-401](XR-401-stitched-evidence.md). Not a conversation-quality card.

## Finding

The structured reference equals the last in-band readback the recipient confirmed. That is transcript consistency, not a second channel, and not proof that CALL-E independently “dropped an F.” Stage (ASR vs conversation vs extract) was never isolated.

## Surface / version / commit or URL

Same 2026-09-05 Calls API terminal as FB-001. Python SDK 0.7.0. 53-turn transcript. Recipient later wrote the intended string on a separate channel (`recipient-adjudication.json`). No audio reviewed.

## Expected

A write-gate treats readback-plus-yes as `conversational_confirmed`. Writable requires a typed value plus an explicit second-channel claim. In-band yes must not be sold as independent verification.

## Actual

Sanitized turn facts (no destination, no ids):

- An earlier user turn contained an F-form fragment (`FECT`).
- A later user turn supplied an S-form fragment (`SECT. IST.`).
- The bot’s only full-string readback used S-form (`S E C T I S T`). No bot turn read back an F-form.
- The next user turn was an explicit yes.
- Extracted `reference` was the S-form string. `reference_confirmed` was `yes`. Schema-valid.
- The independently written intended string used F at the same character. That write is the second channel. It is not in the transcript.

ExactRef `PASTE_READY` A.1 already reports intended vs extracted. It does not say the extract matches the last spoken confirmation.

## Evidence

- Audit observation: “Final full reference readback at 122s; explicit confirmation at 130s. This is transcript consistency, not independent ground truth.”
- Adjudication: `exact_match: false`, `root_cause: not isolated`, `additional_calls: 0`.
- XR-401 stitch quotes the S-form fragments plus the yes, not the earlier F-form fragment.
- Pickup enum on the same object matched the recipient’s words. Identifier fidelity is the miss, not extraction plumbing.

## Impact if an operator or agent trusted the current contract

An operator who hears “they confirmed it” will write the extracted string. The confirmation is correlated with the extract. It does not independently verify the intended identifier. ExactRef must keep this as `conversational_confirmed` or `mismatch` after a typed second channel, never `independently_verified` from the yes alone.

## Ask

On structured-results docs: in-band confirmation is evidence that the recipient agreed with the agent’s last spoken form. It is not a second channel. If that spoken form and a later typed value disagree, return mismatch or null, not a silent substitution.

## Do not claim

- That CALL-E “dropped an F.”
- Isolated ASR, barge-in, or extractor root cause.
- A rate. One call.
- FB-002 interruption as the cause (hypothesis only; stays out of Q-10).
- A third live-call survey bullet. This card reframes A.1; it does not add a new incident.
