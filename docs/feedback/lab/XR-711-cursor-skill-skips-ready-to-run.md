# XR-711 — Shipped Cursor skill never checks `ready_to_run` and forbids a second confirm

## Finding

Official MCP: `run_call` only after `ready_to_run=true` and the user clearly intends to place the call. The Cursor skill on integrations `main` (plugin 0.1.2) says: read `plan_id` and `confirm_token`, then “If the user's request is to place a call, **immediately** use `run_call`.” Step 4: “Do not ask for a second confirmation between `plan_call` and `run_call`.” The word `ready_to_run` does not appear. Distinct from XR-203 (CLI `call start` treats a missing flag as ready): this is the **Cursor template** telling the model to skip the flag entirely.

## Surface / version / commit or URL

- `call-e-integrations` `1ce9d77` `packages/cursor-plugin/plugin/skills/calle/SKILL.md` “MCP call flow” steps 2–4
- Official MCP `docs/mcp/openagent-oauth.md` `run_call` / `plan_call` rules
- Live `plan_call` often returns `confirm_token: null` when `ready_to_run: false` (this session)

## Expected

Skill step: if `ready_to_run !== true` or `confirm_token` is empty, do not call `run_call`. Ask or wait. Name the flag.

## Actual

Cursor `SKILL.md`:

```text
2. Read the returned `plan_id` and `confirm_token`.
3. If the user's request is to place a call, immediately use `run_call` with
   the exact `plan_id` and `confirm_token` returned by planning.
4. Do not ask for a second confirmation between `plan_call` and `run_call`.
```

Safety section also: “Do not configure CALL-E run_call for auto-run” — in tension with step 3–4.

This session’s incomplete plans returned `confirm_token: null`. An agent that “immediately” `run_call`s with a null token either errors or, if it omits the field, fails schema (`confirm_token` required).

## Evidence

Skill file on the 2026-09-14 clone. Live `plan_call` payloads in `mcp/plan-edges/summary.txt` (`confirm_token: null` whenever `ready_to_run: false`).

## Impact if an operator or agent trusted the current contract

User says “call the office about hours” (a place-a-call request). Skill fires `plan_call` then `run_call` in the same turn without checking readiness and without a second confirm. If planning was incomplete, `run_call` is attempted with a null token. If planning was complete, there is no human gate between plan and dial — the opposite of the MCP safety contract and of `run_call`’s own “use only after ready_to_run=true.”

## Ask

Insert an explicit `ready_to_run === true` gate before `run_call`. Delete “do not ask for a second confirmation” or replace it with “do not invent a third confirm after `ready_to_run` is true and the user already asked to dial.”

## Do not claim

XR-203 (CLI start). That `run_call` was invoked in this lab. Issue 126 / XR-002 (result envelope).
