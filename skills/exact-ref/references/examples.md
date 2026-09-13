# Examples

## FS-01 — live substitution (hero)

Intended `07198FECTIST`. CALL-E extracted `07198SECTIST` after a full readback and “yes” (one authorized Calls API call, 2026-09-05, Python SDK 0.7.0). Schema-valid.

ExactRef: `mismatch`, not writable. Character 6 is F vs S. Summary “Sunday 5 PM” is ignored for scheduling.

## FS-02 — contradictory time

Recipient said Sunday morning and 5:00 PM. Structured field can keep both. The public summary picked 5 PM. ExactRef will not treat the summary clock time as a fact.

## FS-03 — matching ticket, still not writable

Intended and extracted `TK-44019`, readback confirmed, no second channel → `conversational_confirmed`. A human must type the value and claim a second channel before write.

## FS-04 — nothing extracted

`unknown`. Do not mint a pickup number.

## Agent flow

```text
1. Preview the compiled task. Confirm it does not contain the intended identifier.
2. Replay the fixture (default) or, if EXACTREF_LIVE=1 and the user confirms, create one Calls API request.
3. Classify the identifier.
4. If mismatch or spoken_only, stop. Offer keep-spoken-only or typed second-channel verify.
5. Never create a second call because status is queued.
```
