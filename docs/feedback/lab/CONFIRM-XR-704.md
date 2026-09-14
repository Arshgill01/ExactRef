# CONFIRM-XR-704 — An 8000-character `run_id` is also `FAILED` / `isError: false`

New evidence only. Original card: unknown `run_id` → `ok: true`, `isError: false`, `status: FAILED`, CLI exit 0.

## Finding (added 2026-09-14, packaging pass)

`get_call_run` with `run_id` = 8000 × `x` is accepted (no maxLength in the inputSchema). The tool returns `isError: false`, `status: "FAILED"`, `message: "run_id not found."`, `next_step.action: "report_blocked"`, and echoes the **entire** 8000-character string into `run_id` and `next_step.run_id`. Same contract as a short fictitious id; plus a large payload bounce.

Missing / wrong-type / extra-field calls are `isError: true` (pydantic) — those are XR-904, not this confirm.

## Evidence

Raw JSON-RPC `tools/call` `get_call_run` `{ "run_id": "<8000 x's>" }` → HTTP 200, 497 ms. Sanitized summary in `/tmp/calle-lab/pkg/mcp-results/mcp-probe.json` (`get_call_run_oversized_8k`). CLI `call status --run-id not-a-real-id --json` exit 0 `ok: true` reconfirmed.

## Do not claim

A new id for the FAILED-on-missing-run behaviour. That the 8k echo is a token leak (it is attacker-controlled input reflected).
