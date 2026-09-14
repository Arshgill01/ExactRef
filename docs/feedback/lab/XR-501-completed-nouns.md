# XR-501 — four nouns for “done”

## Finding

Calls `completed`, MCP `COMPLETED`, Calls `task_completed`, and ExactRef `independently_verified` are documented as if they were the same success. They are not. An agent that treats any of the first three as “I may write the identifier” will persist a schema-valid substitution.

## Surface / version / commit or URL

- SDK `@call-e/calle` 0.7.0 `36ee6f1`; `calle-ai` 0.7.0 `f7a4b82`
- API `calle-docs` `b387e01` OpenAPI `CallStatus` + `task_completed`
- MCP guide `https://raw.githubusercontent.com/CALLE-AI/call-e-integrations/main/docs/mcp/openagent-oauth.md`
- CLI live verify `@call-e/cli` 0.5.1 `4a53b01` `packages/cli/docs/cli-verification.md`
- Cursor skill shipped 0.1.2 `4a53b01`; local working copy `560d61c` (same advertised version)
- ExactRef `skills/exact-ref/SKILL.md`

## Expected

One word for “the phone call reached a terminal lifecycle state,” one word for “the task succeeded,” and one word for “this identifier may be written.” Those words do not substitute.

## Actual

- SDK Calls `waitForResult` returns on top-level `completed` / `failed` / `canceled` and does not wait for `structuredResult` (`server-sdk-typescript/src/calls.ts` 274–276). Goal wait returns when `result` or `error` is non-null (`src/goals.ts` 280–281).
- API: `completed` is a lifecycle terminal after post-call outcome; `task_completed` is a separate “post-summary judgment” (OpenAPI 1203–1205, 1440–1444).
- MCP: “`COMPLETED` means the run completed; it does not by itself confirm that the requested task succeeded.”
- CLI live verify: only `COMPLETED` is a passing terminal (`cli-verification.md` 118).
- Shipped Cursor 0.1.2: on `COMPLETED`, print `[Call Summary]` as the final result. Local Cursor copy adds “not task success, and does not authorize a record write,” but still labels itself 0.1.2.
- ExactRef: “Treating MCP `COMPLETED` or Calls `task_completed` as permission to write” is a misuse. Only `independently_verified` is writable.

## Evidence (paths, commands, quotes). No tokens, no phone numbers, no Discord post.

Cited in [ROLLUP-surfaces.md](ROLLUP-surfaces.md) Fact 1. Hero identifier pair is the already-public FS-01 / FB-001 case (`07198FECTIST` vs `07198SECTIST`), one live call, 2026-09-05. No new call this pass.

## Impact if an operator or agent trusted the current contract

A Cursor or CLI agent that sees `COMPLETED` writes the extracted string. An SDK agent that sees `status: completed` and a schema-valid object does the same. ExactRef would stamp `mismatch`. The record gets the wrong confirmation number.

## Ask (one concrete docs or product change)

On the Calls `CallStatus` page and the MCP terminal-status paragraph, print the four nouns in one table: lifecycle / run-finished / post-summary judgment / writable. State that the first three never authorize an identifier write.

## Do not claim (rate, second live call, refile of 109/123/126/127)

Not a rate. Not a second live call. Not a refile of 126 or 127. SDK Calls-vs-Goal wait remains XR-004.
