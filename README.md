# ExactRef

A CALL-E Agent Skill and local board that refuses to write a spoken identifier as a verified fact.

Schema-valid plus a conversational “yes” is not enough. The hero fixture is the 2026-09-05 live miss: intended `07198FECTIST`, CALL-E extracted `07198SECTIST` after a full readback and a “yes”. One character. Schema-valid. Wrong.

ExactRef sits between the CALL-E result and the record. It names the provenance of the value (`spoken_only`, `conversational_confirmed`, `mismatch`, `independently_verified`), shows intended vs extracted at character level, and only opens the write after a human types the value and claims a second channel.

## Try it in ten seconds

```bash
node skills/exact-ref/scripts/exactref.mjs classify --intended 07198FECTIST --extracted 07198SECTIST --readback
# → provenance "mismatch", firstMismatch index 5 (F → S), exit 2
```

No install, no credentials, no call. The skill script is one zero-dependency Node 18+ file.

## Run the board

```bash
npm install
npm test
npm run dev
```

Open http://127.0.0.1:3450 — the docket. `OH-01` is the off-hire exception from the live call. `FS-01` is the reference write-gate: F became S, and the write stays blocked until you type `07198FECTIST` and tick the second-channel box.

Live CALL-E create is disabled on the board. Replay fixtures. A second live call needs `EXACTREF_LIVE=1` and an explicit later change.

## Package

| Path | What |
| --- | --- |
| `skills/exact-ref/` | Agent Skill for awesome-phone-call-agents: `SKILL.md`, `scripts/exactref.mjs`, fixtures, safety notes |
| `skills/exact-ref/scripts/exactref.mjs` | `classify` / `verify` / `compile` / `gate` / `fixtures`. Exit `0` only when writable |
| `src/lib/` | Same rules in TypeScript for the board: provenance, character diff, task compiler, wait honesty |
| `src/app/` | Docket plus write-gate board |
| `schemas/` | Observation JSON Schema |
| `docs/` | Package decision, ADR, feedback lab |

```bash
# Gate a saved CALL-E call object (REST, SDK, `calle call status --json`, or MCP result{})
node skills/exact-ref/scripts/exactref.mjs gate --call skills/exact-ref/references/call-fs01.json --intended 07198FECTIST

# Human typed the value from email/portal → independently_verified, exit 0
node skills/exact-ref/scripts/exactref.mjs verify --intended 07198FECTIST --extracted 07198SECTIST --typed 07198FECTIST --second-channel

# Compile an outbound CALL-E task; exit 2 if the intended value leaks into it
node skills/exact-ref/scripts/exactref.mjs compile --field "off-hire reference" --destination "the supplier desk" --intended 07198FECTIST
```

## How it differs from transcript ALLOW/BLOCK gates

Other verification skills check whether the transcript supports the claimed value. ExactRef assumes it does — the recipient really did say yes — and still refuses, because:

1. It compares against an **intended** value character by character (F/S, 0/O), not against the transcript.
2. Provenance is a **named state**, never a score or a green check.
3. The only writable state needs a **typed value plus a second-channel claim**. Readback is evidence, not verification.
4. The outbound task compiler **refuses to leak the intended value**, so the call cannot be led.
5. **Wait honesty**: `queued` plus attempt activity is not idle; a local timeout is not hangup; `completed` without `structured_result` is not extraction.

## Tests

`npm test` — identifier classification, F/S and 0/O diffs, task leak check, wait honesty, verify gate, and parity between the standalone skill script and the board rules.
`npm run test:e2e` — board replay, live-create lock, typed second-channel write-gate.

## CALL-E contributions from this work

- [call-e-integrations#128](https://github.com/CALLE-AI/call-e-integrations/pull/128) — `calle mcp call` treats tool `isError` as failure
- [call-e-integrations#129](https://github.com/CALLE-AI/call-e-integrations/pull/129) — Cursor skill reads `result{}` and marks output untrusted
- Feedback lab: `docs/feedback/lab/` (dozens of verified findings across SDK, CLI, MCP, docs)

## Submission

This repository is the project. The hackathon PR copies `skills/exact-ref/` into [awesome-phone-call-agents](https://github.com/CALLE-AI/awesome-phone-call-agents).
