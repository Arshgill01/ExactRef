# XR-708 — Schema allows `to_phones[]`; live `next_step` is “Please try again later.”

## Finding

`plan_call.inputSchema` types `to_phones` as an array of strings. Two E.164 examples (the shape CLI `--to-phone` is documented to repeat) return `ready_to_run: false` and `next_step: "Please try again later."` while `clarifying_questions` says the default outbound line supports one number. An agent that honors `next_step` retries later instead of asking for a single number. An agent that honors the question asks now. Both are licensed by the same payload.

## Surface / version / commit or URL

- Live `plan_call` 2026-09-14
- CLI help: `--to-phone <phone>  Required; repeat once per destination phone number`
- MCP `to_phones` array + `get_call_run` output `result.batch` (batch fields exist on the result schema)

## Expected

If the default line is single-recipient, the schema is `maxItems: 1` (or CLI `--to-phone` is not repeatable). `next_step` matches `questions[]` (“provide one number”), not a later retry.

## Actual

```text
next_step: Please try again later.
clarifying_questions[0]: The default outbound line supports one phone number
  per task. Please provide a single phone number, or select an eligible
  purchased number for batch calls.
confirm_summary: (same as the question)
ready_to_run: false
isError: false
ok: true
EXIT: 0
```

CLI `call plan` help still says the flag is repeatable. `get_call_run` outputSchema includes `result.batch.{total_calls,completed_calls,…}`.

## Evidence

`mcp/plan-edges/multi-phone` in the lab dump. CLI `call plan --help` 2026-09-14. No `run_call`.

## Impact if an operator or agent trusted the current contract

A skill that repeats `--to-phone` (documented) or sends `to_phones: [a, b]` looks like a transient outage (`try again later`) and will `plan_call` again in a loop. Or it will invent a “purchased number” the user never bought. Batch fields in the result schema teach the model that N callees are supported.

## Ask

Either enable batch on the default line or: `maxItems: 1` on `to_phones`, make CLI `--to-phone` non-repeatable, drop `result.batch` from the default tool schema, and set `next_step` to “ask for a single number.”

## Do not claim

That batch calling is broken for purchased numbers (not tested). XR-108 (SDK CLI `--phone` → N recipients). A live multi-recipient call.
