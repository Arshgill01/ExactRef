# XR-609 — `calle call status` hardcodes `call_started: true` on every failure, including “not logged in”

New. 2026-09-14 (quotes corrected 21:50 IST; an earlier draft paraphrased the skill rule — the exact contract text is below). Not XR-704 (unknown run is a successful `FAILED`); this is the *error* envelope of the same command, and it is a CLI source bug.

## Finding

The CLI defines `call_started` as a tri-state (`true` / `false` / `"unknown"`) with a documented meaning: `true` is emitted when `run_call` returned a stable `run_id` — a call exists — and the reader must “not submit the call again.” `call status` reuses the stage helper and passes a literal `callStarted: true`, so any failure of `call status` — no token, network error, server 5xx — reports that a call has been started.

On a fresh machine with no token:

```text
npx -y @call-e/cli@0.5.1 call status --run-id run_does_not_exist --cache-root <empty> --no-telemetry --json
{
  "ok": false,
  "error": { "code": "auth_required", "message": "A usable CALL-E auth token is required." },
  "login_command": "...", "login_argv": [...],
  "stage": "get_call_run",
  "call_started": true,
  "retry_safe": true
}
exit=1
```

No call was started; the command never reached the server with credentials.

## Surface / version / commit or URL

- `@call-e/cli@0.5.1` via `npx -y`, clean `--cache-root`, 2026-09-14 (run twice: 13:xx UTC and 16:2x UTC)
- `call-e-integrations` `1ce9d77` `packages/cli/lib/cli.js`:
  - `fetchCallStatus()` → `callCallStage({ ..., stage: "get_call_run", callStarted: true })` (line ~1245)
  - `command === "status"` → `callCallStage({ ..., callStarted: true })` (line ~1511)
  - contrast `run_call_missing_run_id` → `callStarted: remoteError.call_started ?? "unknown"` (line ~1228)
- Contract text, `packages/cli/docs/cli-reference.md` `1ce9d77`:
  - 176–180: “Call workflow failures include a `stage` … plus `call_started` and `retry_safe` guidance. A `plan_call` failure reports `call_started: false` and is safe to retry. If `run_call` may have been accepted but no stable `run_id` was received, the CLI reports `call_started: "unknown"`, `retry_safe: false` …”
  - 194–199: “If `run_call` returns a `run_id` but the first `get_call_run` query fails, … exit successfully with `ok: true`, `call_started: true`, the stable `run_id`, … do not submit the call again.”
  - 200–201: “… boolean `retry_safe` and boolean-or-`"unknown"` `call_started` guidance.”
- Skill rule that consumes the field (all five skills, `sync-with` block), e.g. `skills/calle/SKILL.md:153–155`: “If CLI `call start` or `call run` returns `call_started: "unknown"` with `retry_safe: false`, the call may already be in progress. Do not create a new plan or repeat `call start` or `call run`.”

## Expected

`call status` failures carry `call_started: "unknown"` (the value the CLI already uses for ambiguity) or omit the field: a status lookup cannot know whether the referenced call exists, and the reference reserves `true` for “stable `run_id` received.” `retry_safe: true` is correct — the tool is read-only.

## Actual

Envelope quoted above (token cache empty; run id fictitious). By source reading the same literal reaches the envelope for network and 5xx failures of `call status` (inferred, not run).

Note the skills only branch on `"unknown"`; nothing in the skills branches on `true`. The consumer of `true` is the CLI reference's own definition and any operator script that logs `call_started` to decide whether a dial happened.

## Evidence

- Live unauthenticated run above (`/tmp/calle-lab/empty-cache`; nothing stored)
- `rg -n "callStarted: true" packages/cli/lib/cli.js` on `1ce9d77` → the two `call status` sites only
- `sed -n 174,203p packages/cli/docs/cli-reference.md`

## Impact if an operator or agent trusted the current contract

An operator or script that uses the reference's definition (`true` ⇒ a call exists with a stable `run_id`) records a phone call that never happened after a login failure or a typo'd id, and any “did we dial?” audit built on the envelope is wrong. An agent that takes `call_started: true` at face value tells the user “your call is in progress” before it has even authenticated. Severity is medium: the skills' own recovery rule keys on `"unknown"`, so the shipped skill path is not misdirected by this bug; the CLI's documented contract is.

## Ask

Pass `callStarted: "unknown"` (or omit) from `call status`; add a unit test asserting `call status` auth failure has no `call_started: true`; state in `cli-reference.md` what `call_started` means on `call status`.

## Do not claim

That a skill instructs “if `call_started` is true, do not run `call start` again” — no shipped skill says that; the skills branch on `"unknown"`. XR-704 as this card. That the server ever received the unauthenticated request. Refile of 109/123/126/127.
