# CONFIRM-XR-205 — `call start` never reads `confirm_expires_at` / `expires_at`; a plan already expired by years is still sent to `run_call`

2026-09-14. New evidence for XR-205 point 3 (plan/token lifetimes are unknown to the CLI). Offline harness only; no live `run_call`.

## What was re-verified

Shipped `@call-e/cli@0.5.1` `runCli`, fake Streamable-HTTP MCP server injected via `fetchImpl`. `plan_call` answers `ready_to_run: true` with `confirm_expires_at: "2020-01-01T00:00:00Z"` and `expires_at: "2020-01-01T00:00:00Z"`:

```text
[call start expired token] exit 0  tools invoked: plan_call -> run_call -> get_call_run
```

The CLI forwards the token to `run_call` without comparing either timestamp to the clock. `rg -n "confirm_expires_at|expires_at" packages/cli/lib/cli.js` on `1ce9d77` → no reads of the plan's expiry (the only `expires_at` handling is the OAuth token cache).

Live `plan_call` (planning only, no phone) does emit both fields; `expires_at` was ≈24 h after creation, `confirm_expires_at` present in the schema.

## Why it adds to XR-205

XR-205 inferred that recovery files carry no expiry. This shows the CLI ignores the server's own expiry even when it is handed one in the same response. The manual path (`call plan` → user thinks → `call run --plan-id --confirm-token`) and the `call recover` path (XR-206) therefore submit stale tokens; whatever the server does with a stale token (reject, or accept — not tested) is invisible to the CLI's `retry_safe` logic.

## Do not claim

Server behaviour on a stale `confirm_token` (not tested live). A live `run_call`. Refile of XR-205 / XR-206.
