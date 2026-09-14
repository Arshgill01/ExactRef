# ADR 0001 — Off-hire is the exception, not the product

## Status
Accepted, 2026-09-14

## Context
OffHire Desk was a vertical calling console: queue, bench, multi-model comparison, live confirm. ExactRef was extracted as a write-gate after that desk failed the reusability test. The user asked to pick OffHire again and unify skills, contributions, ExactRef, and OffHire.

## Decision
Do not revive OffHire Desk. Keep the 2026-09-05 off-hire call as exception `OH-01`. That exception produced two write-gates (`FS-01` reference, `FS-02` collection window). ExactRef remains the only product. The docket is the package surface: exception → write-gate → skill/CLI → CALL-E PRs.

## Consequences
The board shows sibling writes when a case belongs to an exception. Home is a docket, not a silent redirect and not a marketing landing. Feedback may use OffHire evidence cards. It must not claim OffHire Desk as the submitted product.
