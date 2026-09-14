# XR-904 — `get_call_run` inputSchema omits `additionalProperties`, but extras are hard-rejected

## Finding

Live `tools/list` `get_call_run.inputSchema` has `required: ["run_id"]` and properties `run_id`, `cursor`, `limit`. It does **not** set `additionalProperties`. JSON Schema default is allow extras. The server still FastMCP/pydantic-rejects unknown keys (`unexpected_keyword_argument`, `isError: true`). Missing `run_id` and wrong types are also enforced (good). An 8000-character `run_id` string **passes** the schema and returns the XR-704 “not found / FAILED / isError: false” envelope.

## Surface / version / commit or URL

- Live `tools/list` 2026-09-14 (`/tmp/calle-lab/mcp-tools.json`)
- Live `tools/call` get_call_run (fictitious / oversized ids only)

## Expected

`additionalProperties: false` on every tool inputSchema that the runtime treats as closed. Overlong `run_id` is a validation error (`isError: true`), not a terminal FAILED run.

## Actual

**Observed** schema: `additionalProperties` is absent (`None` when dumped).

**Observed** `arguments: { "run_id": "not-a-real-id", "totally_unknown_field": "x" }`:

```text
1 validation error for call[get_call_run]
totally_unknown_field
  Unexpected keyword argument [type=unexpected_keyword_argument, input_value='x', input_type=str]
isError: true
```

**Observed** missing / wrong types (also `isError: true`, pydantic 2.12 URLs in the text):

```text
run_id  Missing required argument
run_id  Input should be a valid string [input_value=12345, input_type=int]
limit   Input should be a valid integer [input_value='nope']
```

**Observed** `run_id` = 8000 × `x`: `isError: false`, `status: "FAILED"`, `message: "run_id not found."` (CONFIRM-XR-704).

## Evidence

Raw JSON-RPC in `/tmp/calle-lab/pkg/mcp-results/mcp-probe.json`. No `run_call`.

## Impact if an operator or agent trusted the current contract

Hosts that attach tracing fields (`_meta` is fine; extra **arguments** are not) get a validation failure and may retry `run_call` instead of `get_call_run`. Schema-driven codegen emits open objects; runtime is closed. **Inferred:** a wrapper that forwards the whole LLM JSON object (including `thought` / `timezone`) will fail closed.

## Ask

Set `additionalProperties: false` on `plan_call` / `run_call` / `get_call_run` inputSchemas. Cap `run_id` length in the schema. Keep extra-field rejection; make the schema match.

## Do not claim

That extras are silently applied (they are rejected). Refile of XR-704 (unknown id → FAILED). XR-003 (`mcp call` `ok: true` on `isError`).
