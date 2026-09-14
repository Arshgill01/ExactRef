# XR-504 — CLI 15s timeout is not hangup

## Finding

`--timeout-seconds` is an HTTP request timeout (default 15s; `plan_call` 150s). The Calls API has no client cancel after accept. MCP says a client deadline does not fail the phone call. Shipped Cursor never says so. An agent that retries create/`run_call` after timeout places a duplicate.

## Surface / version / commit or URL

- API `calle-docs` `calls.mdx` 404–408: no client cancel; in-flight calls continue
- SDK 0.7.0: `CalleTimeoutError`; wait loop does not hang up
- CLI 0.5.1 `cli-reference.md`: `--timeout-seconds` “Request timeout in seconds.” `--poll-timeout-seconds` is login only
- MCP guide: “Reaching a client-side monitoring deadline or stopping the polling process does not fail or cancel the phone call.” Resume `get_call_run`. Do not `run_call` again
- Cursor 0.1.2 shipped: poll until terminal or the user asks to stop. No timeout≠hangup sentence

## Expected

Timeout copy names the object that expired (HTTP request, local waiter, login poll) and says the phone may still be up.

## Actual

CLI 15s is easy to read as “the call failed.” API + MCP say the contrary. ExactRef already: “A local timeout is not hangup.”

## Impact

Duplicate real call after `get_call_run` timeout or `CalleTimeoutError`. Same class as Ray-56’s no-retry P1 on PR 129.

## Ask

On CLI `--timeout-seconds` and Cursor poll instructions: this expires the client wait, not the call. Recover with `get_call_run` / GET call id. Do not `run_call` or `POST /v1/calls` again.

## Do not claim

Not a live duplicate we observed. Not a refile of 123.
