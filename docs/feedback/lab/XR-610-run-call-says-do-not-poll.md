# XR-610 — `run_call` tells the model “do not perform extra operations; the server will notify” — there is no notification outside ChatGPT

New. 2026-09-14. Not XR-712 (how often to poll) and not XR-706 (`plan_call` prose forbids chat). This is the `run_call` description telling non-ChatGPT agents to stop, while `get_call_run` tells them to poll.

## Finding

The live `run_call` description ends: “If the call starts, it runs asynchronously. **Do not perform extra operations; the server will notify on completion.** … Once started, **wait for the activity card updates**.” The very next tool, `get_call_run`, opens with “After calling `run_call`, poll `get_call_run` for realtime progress updates.”

“Server will notify” and “activity card” describe the ChatGPT Apps widget (`_meta.openai/outputTemplate: ui://one_shot_call/call_run_activity_widget.html`). The same `tools/list` is what Cursor, Claude Code, Codex, OpenClaw and the CLI receive. None of them has an activity card or a completion notification channel; the MCP server does not send `notifications/*` progress events (CLI `call start` polls `get_call_run` once and returns). An agent that reads the tool descriptions — which is what the MCP contract asks it to do — is told, in the same list, both to stop and to poll.

The `plan_call` description has the same shape: “When `ready_to_run` is true and a plan card UI is available, stop after `plan_call` and let the plan card continue execution.” A model that cannot see whether a card exists has to guess; guessing “yes” means it never dials and reports success; guessing “no” means it dials.

## Surface / version / commit or URL

- Live `tools/list` 2026-09-14 via `npx -y @call-e/cli@0.5.1 mcp tools --json`: `run_call.description`, `get_call_run.description`, `plan_call.description`, `run_call._meta`
- `call-e-integrations` `1ce9d77` `docs/mcp/openagent-oauth.md` “Reliable terminal-state workflow” (poll after run)
- Five skills (`1ce9d77`): all poll

## Expected

Tool descriptions are host-neutral, or the ChatGPT-only sentences are gated behind `_meta` the host can read. `run_call` says: “The run is asynchronous. Poll `get_call_run` (or follow `next_step`) until a terminal status.”

## Actual

Verbatim `run_call` description (live):

```text
Executes the planned call. Use only after 'plan_call' returns 'ready_to_run=true'.
Pass the 'confirm_token' exactly as received.
In ChatGPT, do not call 'run_call' in the same turn if a plan card UI is available and has already started the call.
Use 'run_call' there only when no plan card UI is available or the user explicitly asks to start or retry the call in chat.
If the call starts, it runs asynchronously. Do not perform extra operations; the server will notify on completion.
Do not call 'run_call' more than once for the same 'plan_id'. Once started, wait for the activity card updates.
```

Verbatim `get_call_run` description (live):

```text
After calling 'run_call', poll get_call_run for realtime progress updates.
Poll every 1-3 seconds while activity is changing, then slow down; do not call plan_call or run_call again.
```

## Evidence

- `/tmp/calle-lab/mcp-tools-pretty.json`
- Guide and skill text on `1ce9d77`

No `run_call` was invoked.

## Impact if an operator or agent trusted the current contract

Two failure modes for MCP-native agents (Cursor MCP, Claude Code MCP — anything that is not the CLI skill): (1) the agent obeys `run_call`, ends its turn “waiting for the notification,” and the user never learns the outcome of a paid phone call; (2) the agent obeys `plan_call`'s “stop and let the plan card continue” and never dials, then reports the task as handled. Both are wrong real-world outcomes caused by prose written for one host and served to all.

## Ask

Strip host-specific sentences from `description`; move them to a ChatGPT-specific `_meta` key or serve a different description per channel (the server already knows the channel: `openagent_oauth`). State “poll `get_call_run` / follow `next_step`” in `run_call`.

## Do not claim

XR-706 / XR-712 as this card. That the server never sends MCP notifications on any channel (observed only that the CLI does not receive/handle any). Refile of 109/123/126/127.
