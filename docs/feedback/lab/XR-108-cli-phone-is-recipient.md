# XR-108 — CLI `--phone` repeated creates N recipients, not N numbers

## Finding

OpenAPI `phones` is an array **on one recipient** (alternate numbers for one person). The TypeScript `calle` CLI maps each `--phone` to its own `recipients[]` row. Repeatable `--phone` therefore starts a batch of independent conversations, not a failover list.

## Surface / version / commit or URL

- TypeScript `@call-e/calle@0.7.0` `36ee6f1` `src/cli.ts`
- OpenAPI `CallTaskRecipientRequest.phones` (`openapi/calle.openapi.yaml`)
- Public Calls guide: https://docs.heycall-e.com/calls — “each recipient contains a `phones` array”

Python `calle-ai` has no CLI.

## Expected

`--phone` marked “Repeatable” would either:

- append to a single `recipients: [{ phones: [...] }]`, or
- usage would say each flag is a **new recipient** (a new conversation / structured result).

## Actual

```178:186:src/cli.ts
function createInput(flags: CliFlags): CreateCallInput {
  ...
  if (flags.phones.length > 0) {
    input.recipients = flags.phones.map((phone) => ({ phones: [phone] }));
  }
```

Usage: `--phone <number>            E.164 phone number. Repeatable.`

The library path is correct when the caller writes `recipients: [{ phones: [a, b] }]`. Only the CLI collapses “repeatable phone” into “repeatable recipient.”

## Evidence

- `server-sdk-typescript/src/cli.ts:74-78` (usage), `178-186` (`createInput`)
- `server-sdk-typescript/tests/cli.test.ts:146-150` — one `--phone` becomes `recipients: [{ phones: ["+14155550100"] }]`
- OpenAPI: `phones` `minItems: 1`, description “Phone numbers in E.164 format **for this recipient**”
- No test for two `--phone` flags

## Impact if an operator or agent trusted the current contract

`calle calls create --phone A --phone B --task "..." --wait` places **two** outbound conversations and two recipient results. An operator who meant “try B if A fails” double-spends and may write the wrong person’s answer. There is no public cancel after accept (gauntlet-004 / XR-504): the extra task keeps dialing.

## Ask

Change `createInput` to `recipients: [{ phones: flags.phones }]` **or** print `Creating N recipient(s)` before POST and document that each `--phone` is a separate recipient. Do not leave “Repeatable” unexplained.

## Do not claim

- That we placed a two-recipient live call.
- Refile of gauntlet-006 (SDK `recipient` / `phone` aliases). This is CLI cardinality.
- Refile of 109 / 123 / 126 / 127.
