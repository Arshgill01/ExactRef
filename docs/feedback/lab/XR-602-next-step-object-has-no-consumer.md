# XR-602 — The structured `next_step` contract has no client; its retry action collides with “never run twice”

New. 2026-09-14. Siblings, not the same card: XR-706 (the `plan_call` prose string forbids chat), XR-708 (`try again later`), XR-712 (four poll cadences). This card is about the machine-readable object the server emits and nobody reads.

## Finding

Live `run_call` and `get_call_run` return a typed `next_step` object: `action` enum (`poll_get_call_run`, `wait_for_scheduled_run`, `wait_for_scheduled_child_run`, `ask_user_for_missing_info`, `ask_user_for_retry_confirmation`, `plan_call_same_plan_id`, `report_result`, `report_blocked`), `tool_name`, `poll_after_seconds`, `scheduled_at`, `required_user_input[]`, `instruction`. `plan_call` accepts a matching input, `retry_confirmation_action` (`confirm_suggested_time` | `retry_now` | `set_custom_time`). The official guide tells clients to “follow `next_step` when present” and, for an unknown status, to “follow `next_step` rather than inferring terminality.”

No shipped client does. `rg -n next_step` over the CLI (`packages/cli/lib/cli.js`), the skills.sh skill, and the Cursor, Codex, Claude and OpenClaw plugins returns zero hits. Every skill hardcodes a 10-second (or 60s + 5–10s) loop and a static terminal list. `retry_confirmation_action` cannot be sent by any skill or by `calle call plan` (`buildPlanArguments` has no flag for it).

Two of the enum values are unsafe to obey literally with the rest of the contract:

- `plan_call_same_plan_id` → re-plan on the same `plan_id`, then `run_call` with that `plan_id`. `run_call.description`: “Do not call `run_call` more than once for the same `plan_id`.”
- `wait_for_scheduled_run` with `scheduled_at` hours away: skills that ignore it poll every 10 s until then (`SCHEDULED` is in the schema's example statuses and in no skill's terminal list).

Under one name, `next_step` is a **string** on `plan_call` (observed: an instruction about a plan card) and an **object** on `run_call` / `get_call_run`.

## Surface / version / commit or URL

- Live `tools/list` 2026-09-14 (`mcp tools --json`): `plan_call.inputSchema.retry_confirmation_action`; `run_call` / `get_call_run` `outputSchema.next_step`; `plan_call.outputSchema.next_step` (`type: string`)
- Live `get_call_run` on an unknown id (read-only): `next_step = { action: "report_blocked", poll_after_seconds: null, instruction: "Report the current terminal run status. Do not start another call." }`
- Live `plan_call` with no phone number (planning only, cannot dial): `next_step` = prose about a plan card
- `call-e-integrations` `1ce9d77`: `docs/mcp/openagent-oauth.md` 156–160 (handoff table), 234–235 (“follow `next_step` when present or poll every 5–10 seconds”), 252–253 (“For a status outside this documented set, follow `next_step` rather than inferring terminality from elapsed time”); `packages/cli/lib/cli.js`; five skill trees
- Live `get_call_run` unknown id, re-run 16:20 UTC: `/tmp/calle-lab/live2/get_call_run_unknown.json` (full `next_step` object quoted in XR-704 addendum)

## Expected

At least the first-party CLI reads `next_step`: `call status` exposes `terminal: bool` / `next_action`, `call start` sleeps `poll_after_seconds`, and `plan_call_same_plan_id` is either removed or documented as the one sanctioned second `run_call` (with the `run_call` description updated). Skills say “obey `next_step.action`; if it is `report_*`, stop.”

## Actual

Guide handoff table: `run_call` → “`run_id`, current `status`, and `next_step` when present”; `get_call_run` → “… and `next_step` when present.” CLI unit tests: no `next_step` fixture. CLI `call start` envelope (offline harness, shipped 0.5.1): top-level keys `ok, server_url, tool_name, call_started, result, run_id, status_query_succeeded, status_result, next_command, next_argv` — `next_argv` is the CLI's own recovery/status pointer, not the server's `next_step`; the server object stays buried in `status_result.structuredContent.next_step`.

## Evidence

- `/tmp/calle-lab/mcp-tools-pretty.json` (`next_step` schemas; `retry_confirmation_action`)
- Live `call status --run-id run_does_not_exist_xr6` output (same `next_step` object as XR-704)
- `/tmp/calle-lab/plan-smoke.json` (`next_step` string; `confirm_token: null`, no phone)
- `rg -n "next_step|poll_after_seconds|retry_confirmation_action|plan_call_same_plan_id" -g '*.js' -g '*.md' -g '*.mjs' --glob '!node_modules'` on `1ce9d77`: hits only in `docs/mcp/openagent-oauth.md`
- `/tmp/calle-lab/tslab/cli_probe.mjs` `[call start]` case, verbatim: `top-level keys: ok,server_url,tool_name,call_started,result,run_id,status_query_succeeded,status_result,next_command,next_argv | next_step surfaced at top level? false`

No `run_call`. No scheduled run observed; the `SCHEDULED` path is read from the schema and is labeled inferred.

## Impact if an operator or agent trusted the current contract

The server's only machine-readable “do not start another call” / “ask the user before retrying” signal is dropped on the floor by every client CALL-E ships. Retry decisions fall back to skill prose and a status string. When the server does want a retry (`plan_call_same_plan_id`, `ask_user_for_retry_confirmation`), no client can answer it (`retry_confirmation_action` unsent), so the planner never receives the structured choice and the agent either re-plans blind or stalls. A scheduled run is polled for hours (inferred).

## Ask

Ship one `next_step` consumer in `@call-e/core` and use it in `call start` / `call status` (expose `terminal`, honor `poll_after_seconds`, map `report_*` to stop). Make `next_step` an object on `plan_call` too. State in the `run_call` description whether `plan_call_same_plan_id` is the sanctioned exception to “never twice.” Add `--retry-confirmation-action` (or drop the input).

## Do not claim

XR-706 / XR-708 / XR-712 as this card. A live scheduled or retry-confirmation payload. A second live call. Refile of 109/123/126/127.
