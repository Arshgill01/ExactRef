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

## Tests

`npm test` — identifier classification, F/S diff, task leak check, wait honesty, verify gate.

## Submission

This repository is the project. The hackathon PR copies `skills/exact-ref/` (and this README link) into [awesome-phone-call-agents](https://github.com/CALLE-AI/awesome-phone-call-agents).
