# ROLLUP — Grok TS surfaces (CLI / MCP / SDK / skill)

2026-09-14. No `run_call`, no `calle call run|start|recover`, no `calls.create`, no form, no GitHub issues. No tokens or full phone numbers in this tree. Clone/install under `/tmp/calle-lab-ts/`.

Pinned:

| Surface | Version / HEAD |
| --- | --- |
| `@call-e/cli` (npx) | **0.5.1** |
| `@call-e/calle` npm | **0.7.0** (git `2808e21` is unpublished 0.7.1 hygiene) |
| Live MCP `tools/list` | four tools; `plan_call` / `run_call` / `get_call_run` invoked only as listed below |
| integrations clone | `1ce9d77` |
| docs.heycall-e.com | `/sdks` `/calls` `/webhooks` `/goal-runs` `/errors` `/llms.txt` |
| Official MCP guide | GitHub `main` `docs/mcp/openagent-oauth.md` |
| Cursor skill | plugin **0.1.2** on that clone |
| skills.sh skill | GitHub `skills/calle/SKILL.md` **0.1.0** |

`plan_call` was used only as planning (empty, bad phones, unicode, long text, ttl). `get_call_run` / `call status` used only with the literal id `not-a-real-id`.

## File index (new this pass)

| File | Harm class | One line |
| --- | --- | --- |
| [XR-701-two-calle-bins.md](XR-701-two-calle-bins.md) | **wrong binary / wrong call path** | `@call-e/cli` and `@call-e/calle` both install `calle` |
| [XR-705-run-call-idempotent-hint.md](XR-705-run-call-idempotent-hint.md) | **duplicate real call** | Live `run_call.idempotentHint: true` vs “do not call twice” |
| [XR-704-missing-run-is-failed.md](XR-704-missing-run-is-failed.md) | **wrong write** | Unknown `run_id` → `ok: true`, `isError: false`, `status: FAILED`, exit 0 |
| [XR-711-cursor-skill-skips-ready-to-run.md](XR-711-cursor-skill-skips-ready-to-run.md) | **unintended call** | Cursor 0.1.2 never names `ready_to_run`; “immediately `run_call`” |
| [XR-706-next-step-plan-card-vs-chat.md](XR-706-next-step-plan-card-vs-chat.md) | **stuck / silent agent** | Live `next_step` forbids chat; official guide requires chat |
| [XR-707-plan-call-guesses-national-number.md](XR-707-plan-call-guesses-national-number.md) | **wrong destination** | Non-E.164 national number accepted; planner claims recipient + English |
| [XR-710-goal-id-vs-run-id.md](XR-710-goal-id-vs-run-id.md) | **wrong poll / second create** | SDK `id` / `runId` / `callId` are three paths |
| [XR-708-multi-phone-try-again-later.md](XR-708-multi-phone-try-again-later.md) | **retry loop** | Array schema + repeatable `--to-phone`; `next_step` is “try again later” |
| [XR-702-global-flags-before-command.md](XR-702-global-flags-before-command.md) | **script break** | `--json` / `--no-telemetry` before the command are the command name |
| [XR-703-status-positional-and-args-flag.md](XR-703-status-positional-and-args-flag.md) | **fresh-user miss** | `call status <id>` and `mcp call --args` exit 2 |
| [XR-709-phone-vs-to-phone.md](XR-709-phone-vs-to-phone.md) | **flag collision** | MCP CLI rejects `--phone`; SDK CLI only has `--phone` |
| [XR-712-poll-cadence-four-stories.md](XR-712-poll-cadence-four-stories.md) | **rate / silence** | Tool 1–3s vs guide/Cursor 60s+5–10s vs skills.sh 10s |

## Top by agent-harm

1. **Duplicate or unintended outbound call** — [XR-705](XR-705-run-call-idempotent-hint.md) (host retry of an “idempotent” destructive tool) + [XR-711](XR-711-cursor-skill-skips-ready-to-run.md) (no `ready_to_run` gate) + [XR-701](XR-701-two-calle-bins.md) (SDK `calls create` when the agent thought it had the MCP CLI). Complements owned XR-202 / XR-203 / XR-206; do not merge.
2. **False FAILED** — [XR-704](XR-704-missing-run-is-failed.md). Not XR-003: `isError` is false.
3. **Wrong number / wrong poll** — [XR-707](XR-707-plan-call-guesses-national-number.md), [XR-710](XR-710-goal-id-vs-run-id.md).
4. **Agent stall or retry storm** — [XR-706](XR-706-next-step-plan-card-vs-chat.md), [XR-708](XR-708-multi-phone-try-again-later.md), [XR-712](XR-712-poll-cadence-four-stories.md).
5. **Fresh-user / argv** — [XR-702](XR-702-global-flags-before-command.md), [XR-703](XR-703-status-positional-and-args-flag.md), [XR-709](XR-709-phone-vs-to-phone.md).

## Observed vs inferred

**Observed:** dual `--help` texts; flag-order and `--args` / positional / `--phone` exits; live `plan_call` and `get_call_run` JSON; `run_call` annotations (schema only; tool not called); Cursor vs skills.sh vs guide strings; SDK field mapping via an offline script.

**Inferred (labeled in the cards):** a host actually retrying on `idempotentHint`; a planner country for the national number; a live 404 from passing `run.runId` into `getRun`.

## Confirmed, not refiled

XR-001 fourth tool (listed, not called). XR-003 `mcp call` `ok: true` on `isError` (unknown tool, missing `run_id`, `ttl_seconds: -1`). XR-201 CLI plan omits `user_input`. XR-202 timeout flags. XR-203 `call start` vs `ready_to_run`. XR-204 docs site has no MCP page (`llms.txt` still omits it). XR-205 token/TTL. XR-108 / XR-109 SDK `--phone` / `--wait`. XR-111 cursor vs after. XR-113 Goal `Retry-After`. XR-114 `context`. XR-115 webhook casing. XR-116 E.164 min-length. XR-501–504 completed / result nouns / MCP schema / timeout≠hangup. XR-002 / 126 result envelope.

## Also noted, not filed

- CLI `engines.node >= 22` is not in `--help`; SDK tarball has no `engines`.
- Telemetry defaults **on** (`resolveTelemetryEnabled` → `true`); documented; `--no-telemetry` used for this lab.
- `docs.heycall-e.com/openapi/calle.openapi.yaml` returned HTTP 500 this session; `llms.txt` still links it.
- `regions list` prints only a GitHub URL, not a region table.
- `calle help` is an unknown command (exit 2).
- Git SDK 0.7.1 is not on npm; docs still pin 0.7.0.
- `--json` is a documented no-op on success; errors already emit JSON on stdout plus human stderr.

## Do not claim

A second OffHire/live call, form submit, Discord, GitHub issues, tokens, or real subscriber numbers. `track_ui_events` was not invoked.
