# XR-609 — `calle call status` hardcodes `call_started: true` on every failure, including “not logged in”

New. 2026-09-14. Not XR-704 (unknown run is a successful `FAILED`); this is the *error* envelope of the same command, and it is a CLI source bug, not a server response.

## Finding

The CLI's error envelope carries two fields skills are told to read before deciding whether to retry: `call_started` and `retry_safe`. In `call start` they are computed per stage (plan → run → status). `call status` reuses the same stage helper and passes a literal `callStarted: true`, so any failure of `call status` — no token, network error, server 5xx, bad `run_id` shape — reports that a call has been started by this command.

On a fresh machine with no token:

```text
calle call status --run-id run_does_not_exist --json
→ ok: false, error.code: auth_required, stage: get_call_run, call_started: true, retry_safe: true   (exit 1)
```

No call was started; the command never reached the server with credentials.

## Surface / version / commit or URL

- `@call-e/cli@0.5.1` via `npx -y`, clean `--cache-root`, 2026-09-14
- `call-e-integrations` `1ce9d77` `packages/cli/lib/cli.js`:
  - `fetchCallStatus()` → `callCallStage({ ..., stage: "get_call_run", callStarted: true })`
  - `command === "status"` branch → `callCallStage({ ..., callStarted: true })`
  - Error envelope builder copies `error.callStarted` into `call_started`
- Skills (all five): “Read `ok`, `call_started`, `retry_safe` … If `call_started` is true, do not run `call start` again; use `call status`.”

## Expected

`call_started` on `call status` is `"unknown"` (the value the CLI already uses for an ambiguous `run_call`) or omitted: a status command cannot know whether the referenced call exists. `retry_safe: true` is fine — the tool is read-only.

## Actual

Envelope quoted above (token cache empty; run id fictitious). By source reading, the same literal reaches the envelope for any other `call status` failure (network, 5xx) — inferred, not run.

Contrast: `call start` on `run_call` missing `run_id` uses `callStarted: remoteError.call_started ?? "unknown"` — the codebase has the right tri-state and does not use it here.

## Evidence

- Live unauthenticated run above (`/tmp/calle-lab/empty-cache`; nothing stored)
- `rg -n "callStarted: true" packages/cli/lib/cli.js` on `1ce9d77` → the two `call status` sites only
- Skill grep: “If `call_started` is true”

## Impact if an operator or agent trusted the current contract

An agent that (correctly, per skill) checks `call_started` before deciding whether it may retry will conclude a call exists after a login failure or a typo'd `run_id` and will (a) stop and tell the user “your call is in progress” or (b) keep polling a run that does not exist (XR-704 makes the eventual answer `FAILED`). In the recovery flow, `call_started: true` also suppresses the one legitimate retry (`call start` again) after a pre-dial failure. The field the skill is told to trust is a constant.

## Ask

Pass `callStarted: "unknown"` (or omit) from `call status`; add a unit test asserting `call status` auth failure has no `call_started: true`. Document the tri-state in `cli-reference.md`.

## Do not claim

XR-704 as this card. That the server ever received the unauthenticated request. Refile of 109/123/126/127.
