# XR-706 — Live `plan_call.next_step` forbids chat; the official MCP guide requires chat

## Finding

Every incomplete `plan_call` in this session returned `ready_to_run: false` and `next_step` = “Do not ask or restate the missing questions in chat. Direct the user to fill in the plan card and click Continue.” The official MCP guide on `main` says the opposite: if `ready_to_run=false`, ask the user for the missing details and call `plan_call` again. CLI / Cursor / skills.sh have no plan card. An agent that obeys `next_step` goes silent. An agent that obeys the guide “disobeys” the tool.

## Surface / version / commit or URL

- Live `plan_call` via `calle mcp call` 2026-09-14 (empty `{}`, empty `user_input`, goal-only, unicode, long text, `ttl_seconds: 0`)
- Official guide: https://github.com/CALLE-AI/call-e-integrations/blob/main/docs/mcp/openagent-oauth.md (`plan_call` rules)
- CLI `@call-e/cli@0.5.1` has no card UI

## Expected

One instruction. If the client has no card, `next_step` must tell the model to ask in chat (or return a structured `questions[]` **and** permission to render it). The published guide must match the live string.

## Actual

Live (empty object `{}`, exit 0, `isError: false`):

```text
next_step: Do not ask or restate the missing questions in chat. Direct the user
to fill in the plan card and click Continue. Only if the user sends a follow-up
message instead, call plan_call again with plan_id="pFMJ1MW54".
```

A durable `plan_id` was created anyway.

Official guide (`plan_call` rules):

> If `ready_to_run=false`, ask the user for the missing details and call `plan_call` again.

Multi-phone (schema allows an array) returned a different contradiction: `next_step: "Please try again later."` while `clarifying_questions` asked for a single number (XR-708).

## Evidence

`/tmp/calle-lab-ts/mcp/plan-edges/summary.txt` (local lab dump). Guide fetched 2026-09-14. No `run_call`.

## Impact if an operator or agent trusted the current contract

Cursor MCP-first skill has no card. Obeying `next_step` means the agent never asks for the phone/goal; the user sees no card and no questions. Obeying the guide means the agent asks in chat and looks “non-compliant” with the tool. Empty `plan_call` still mints a `plan_id` that expires ~24h (or year 9999 when `ttl_seconds: 0`).

## Ask

Return a client-aware `next_step` (card vs chat). Change the GitHub MCP guide to the live rule **or** change the live string to the guide. Do not emit “fill the plan card” on CLI/`mcp call`.

## Do not claim

XR-203 (CLI `call start` treating missing `ready_to_run` as ready). That a plan card was actually shown. Live TTL semantics beyond the `expires_at` string.
