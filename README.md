# ExactRef

A CALL-E skill and local board that refuses to write a spoken identifier as a verified fact.

Schema-valid plus a conversational “yes” is not enough. The hero fixture is the 2026-09-05 live miss: intended `07198FECTIST`, extracted `07198SECTIST` after a full readback.

## Run

```bash
npm install
npm test
npm run dev
```

Open http://127.0.0.1:3450 — it lands on FS-01.

Live CALL-E create is disabled on the board. Replay fixtures. A second live call needs `EXACTREF_LIVE=1` and an explicit later change.

## Package

| Path | What |
| --- | --- |
| `skills/exact-ref/` | Agent Skill for awesome-phone-call-agents |
| `src/lib/` | Provenance, character diff, task compiler, wait honesty |
| `src/app/` | Review board |
| `bin/exactref.mjs` | Classify / verify / compile without the board |
| `schemas/` | Observation JSON Schema |

```bash
npm run exactref -- classify --intended 07198FECTIST --extracted 07198SECTIST --readback
npm run exactref -- verify --intended 07198FECTIST --extracted 07198SECTIST --typed 07198FECTIST --second-channel
```

Exit `0` only when the decision is writable. Exit `2` for a classified-but-blocked write.

## Tests

`npm test` — identifier classification, F/S and 0/O diffs, task leak check, wait honesty, verify gate, CLI.
`npm run test:e2e` — board replay, live-create lock, typed second-channel write-gate.

## Submission

This repository is the project. The hackathon PR copies `skills/exact-ref/` (and this README link) into [awesome-phone-call-agents](https://github.com/CALLE-AI/awesome-phone-call-agents).
