# XR-601 — Live status vocabulary is `NO ANSWER`; every skill's terminal list says `NO_ANSWER`

New. 2026-09-14. Not XR-712 (cadence) and not XR-704 (unknown run is `FAILED`). This is the terminal *set*.

## Finding

The live `run_call` / `get_call_run` output schema describes `status` as a free string whose examples are `PREPARING, SCHEDULED, COMPLETED, NO ANSWER, DECLINED, FAILED` — `NO ANSWER` with a space. The official MCP guide says “Treat `NO ANSWER` as the same terminal outcome as `NO_ANSWER`.” None of the five shipped skills carries that sentence. Their terminal lists contain only `NO_ANSWER`. The CLI does not classify terminality at all; it passes the string through. The CLI's own live e2e script accepts both spellings, so the vendor knows the wire can say `NO ANSWER`.

An agent following any skill on a `NO ANSWER` run keeps polling every 10 seconds and prints “Phone call is in progress!” until the user stops it.

## Surface / version / commit or URL

- Live `tools/list` via `npx -y @call-e/cli@0.5.1 mcp tools --json` (2026-09-14): `run_call.outputSchema.properties.status.description` and the same on `get_call_run`
- `call-e-integrations` `1ce9d77`:
  - `docs/mcp/openagent-oauth.md` lines 246–249 (`NO ANSWER` ≡ `NO_ANSWER`)
  - `skills/calle/SKILL.md` 189–190 and `references/commands.md` 227–235 (skills.sh 0.1.0)
  - `packages/cursor-plugin/plugin/skills/calle/SKILL.md` 86–87 (Cursor 0.1.2)
  - `packages/codex-plugin/.../SKILL.md` 170 (0.1.12), `packages/claude-plugin/.../SKILL.md` 158 (0.2.3), `packages/openclaw-cli-skill/.../SKILL.md` 180 (0.1.0)
  - `packages/cli/scripts/live-e2e.mjs` 14–22: `TERMINAL_STATUSES` includes both `"NO ANSWER"` and `"NO_ANSWER"`

## Expected

`status` is an enum on the wire, or every skill's terminal list is generated from one source that includes every spelling the server emits. A status the skill cannot classify stops polling and asks, rather than polling forever.

## Actual

Live schema:

```text
status: "Run status (for example, PREPARING, SCHEDULED, COMPLETED, NO ANSWER, DECLINED, FAILED)."  (type: string, no enum)
```

skills.sh / Cursor / Codex / Claude / OpenClaw:

```text
Terminal statuses include `COMPLETED`, `FAILED`, `NO_ANSWER`, `DECLINED`,
`CANCELED`, `CANCELLED`, `VOICEMAIL`, `BUSY`, and `EXPIRED`.
```

Polling rule in the same files: “Keep using `call status` … until the call reaches a terminal status or the user asks you to stop. Poll every 10 seconds.”

Offline harness against shipped `@call-e/cli@0.5.1` (fake MCP server returning `status: "NO ANSWER"`), verbatim:

```text
[call status NO ANSWER] exit 0 ok: true status: NO ANSWER terminal flag in envelope? []
```

The envelope has no terminal flag; classification is left entirely to the skill text.

`rg -n "NO ANSWER"` across `skills/`, `packages/*/plugin`, `packages/openclaw-cli-skill`: zero hits. Only the guide and `live-e2e.mjs` know the spaced form.

## Evidence

- `/tmp/calle-lab/mcp-tools-pretty.json` (live `tools/list`, tokens not stored) — `status.description` on `run_call` and `get_call_run`
- `/tmp/calle-lab/tslab/cli_probe.mjs` `[call status NO ANSWER]` case — passthrough, no terminal flag
- Grep results above on `1ce9d77`

No live `run_call`. No run reached `NO ANSWER` in this lab; the spelling comes from the server's own schema text and the guide.

## Impact if an operator or agent trusted the current contract

Infinite poll. The user is told the call is in progress after the callee never picked up. On the CLI path that is one `get_call_run` every 10 seconds until a human intervenes; on the Cursor MCP path the same. A less careful agent that decides “still in progress after N minutes, retry” re-plans and dials again. Also a documentation-trust failure: the guide's one sentence that would fix it was never propagated to the skills the guide links.

## Ask

Make `status` an enum in the tool `outputSchema` (single spelling), or add “treat `NO ANSWER` as `NO_ANSWER`” to every skill's terminal list from one `sync-with` block. Until then, add “if `status` is not in this list and `next_step.action` is `report_result` or `report_blocked`, stop polling.”

## Do not claim

A live `NO ANSWER` observation. XR-712 (cadence) or XR-704 (missing run). A second live call. Refile of 109/123/126/127.
