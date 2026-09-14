# XR-502 — MCP cannot attach `result_schema`

## Finding

The only machine check for an identifier lives on `POST /v1/calls`. `plan_call` / `run_call` and `calle call plan` have no `result_schema` (or `webhook_url`) field. ExactRef’s compiled schema cannot ride the agent path.

## Surface / version / commit or URL

- SDK `@call-e/calle` 0.7.0 `36ee6f1` `create({ resultSchema })`
- API OpenAPI `CreateCallRequest.result_schema` (`calle-docs` `b387e01`)
- MCP guide [openagent-oauth.md](https://github.com/CALLE-AI/call-e-integrations/blob/main/docs/mcp/openagent-oauth.md) `plan_call` / `run_call` inputs
- CLI 0.5.1 `4a53b01` `call plan` flags: phone, goal, language, region, timezone
- ExactRef `src/lib/task.ts` compiled schema

## Expected

If MCP is a first-class create path, it accepts the same extraction contract as the Calls API, or the guide says the agent path is unconstrained summary text.

## Actual

SDK/API: first-class `result_schema`. MCP: `user_input`, phones, region, language, goal, `plan_id`, `confirm_token`, `ttl_seconds`. CLI plan: no `--result-schema`. ExactRef compile emits a Calls-shaped schema the host cannot send through MCP.

## Impact

An agent that follows ExactRef compile, then `plan_call`, drops the identifier contract. Extraction falls back to unconstrained summary. Combined with XR-501, `COMPLETED` plus a printed summary looks writable.

## Ask

Either add `result_schema` (and document that MCP create is a different product without it) on `plan_call`, or say on the MCP guide: identifier capture requires the Calls API.

## Do not claim

Not a live defect. Not a refile of 126/127. Not a request for mid-call tools (123).
