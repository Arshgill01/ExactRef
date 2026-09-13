---
name: exact-ref
description: After a CALL-E call that captured an exact identifier, classify it as spoken_only, conversational_confirmed, mismatch, or independently_verified. Never write schema-valid plus readback-yes as a fact.
---

# ExactRef

Use this skill when a CALL-E structured result contains an identifier that will be written into a record: confirmation number, ticket, off-hire reference, order id, pickup number.

This skill does not place a call by itself. It compiles a safe task, then classifies the returned identifier. Fixture replay is the default. Live CALL-E create is host-owned and fail-closed.

## When to use

- The next write depends on an exact character string from a phone call
- CALL-E returned `structured_result` and someone is about to treat it as true
- You need a readback protocol in the outbound task without leaking the intended value
- Top-level status is `queued` and you must not create a second call

## When not to use

- The value is already on a portal, email, or paper — that is `no_call`
- Medical, legal, emergency, or payment-card capture
- Guessing a phone number, country, language, or `run_id`
- Calling `track_ui_events` or any undocumented MCP tool
- Treating MCP `COMPLETED` or Calls `task_completed` as permission to write

## Classify

Run the observation through ExactRef rules (see `references/examples.md`):

1. No extracted value → `unknown`. Do not invent one.
2. Intended value present and not equal (ignore spaces/hyphens/case) → `mismatch`. Readback-plus-yes does not override.
3. `secondChannelMatch` and extracted equals intended → `independently_verified`. Only this is writable.
4. Readback confirmed, no second channel → `conversational_confirmed`. Not writable.
5. Otherwise → `spoken_only`. Not writable.

To mark verified, a human must type the identifier and claim a second channel. Typing the extracted wrong value keeps `mismatch`.

## Compile the task

Use `compileIdentifierTask` / the board Preview. The task must:

- Ask for the whole identifier, then wait for an end marker
- Not interrupt during dictation
- Do one full readback
- Leave contradictory times unresolved
- Never include the intended identifier

## Wait honesty

- Calls `waitForResult` returns on top-level `completed` / `failed` / `canceled`. It does not wait for `structuredResult`.
- `queued` plus attempt activity is not idle. Do not create again.
- A local timeout is not hangup.
- Goal wait materializes when `result` or `error` is non-null.
- MCP summaries live under `result{}`. Do not read them at the top level.

## Host demo

Local board: `npm install && npm test && npm run dev` → http://127.0.0.1:3450

Open FS-01. The extracted string is `07198SECTIST`. The intended string is `07198FECTIST`. The write stays blocked.

Safety notes: `references/safety.md`.
