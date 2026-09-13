# Independent findings — 2026-09-13

No live phone call was placed this session. CLI/MCP listing used the existing cached login (`usable: true`, expires 2029-05-15). Tokens were not copied into this repo.

## XR-001 — MCP `tools/list` returns a fourth undocumented tool

- **Interface / version:** `npx @call-e/cli mcp tools` against `https://seleven-mcp-sg.airudder.com/mcp/openagent_oauth`
- **Expected:** Official MCP guide and Cursor skill document three tools: `plan_call`, `run_call`, `get_call_run`
- **Actual:** `ok: true`, `tool_count: 4`, names `plan_call`, `run_call`, `get_call_run`, `track_ui_events`
- **Repo check:** `track_ui_events` does not appear in the local `call-e-integrations` docs/clone (grep 2026-09-13)
- **Impact:** Agent readiness that asserts “exactly three tools” is wrong. The fourth tool is easy to call by accident. Mentioned in issue 123’s body as widget telemetry; not documented as a supported agent tool
- **Workaround:** Treat only the three call tools as the workflow. Do not invoke `track_ui_events`
- **Ask:** Document or hide the fourth tool for agent clients; update the Cursor skill readiness list
- **Do not:** file this as a security incident or as a new duplicate of 123’s mid-call feature request

## XR-002 — Official Cursor skill is not at parity with the skills.sh skill

Independently read:

- `call-e-integrations/packages/cursor-plugin/plugin/skills/calle/SKILL.md` (v0.1.1)
- `call-e-integrations/skills/calle/SKILL.md`

Gaps in the Cursor copy:

1. No untrusted-output boundary. skills.sh marks summary/transcript untrusted and forbids obeying instructions inside them
2. Terminal template reads `<post_summary or summary or message>` at the top level. Issue 126 reports those fields live under `result{}` on COMPLETED
3. “Do not ask for a second confirmation between `plan_call` and `run_call`” vs MCP safety “user clearly intends”
4. Cursor allows `npx -y @call-e/cli`; skills.sh forbids remote npm from the skill

**Ask:** bring Cursor skill to skills.sh safety parity; read `result.summary` / `result.transcript`. Cite 126; do not refile it.

## XR-003 — Generic `calle mcp call` still succeeds on tool `isError`

Source in current `packages/cli/lib/cli.js`:

- `callCallStage` (dedicated `calle call *`) throws when `result?.isError === true`
- `handleMcpCommand` for `mcp call` always `writeJson(..., mcpSuccessPayload(...)); return 0`

`mcpSuccessPayload` hardcodes `ok: true`.

This independently confirms open [issue 127](https://github.com/CALLE-AI/call-e-integrations/issues/127). Cite it. Do not open a second issue.

## XR-004 — Calls vs Goal `waitForResult` predicates (reconfirmed)

`server-sdk-typescript/src/calls.ts`: return when `status` is `completed` | `failed` | `canceled`.

`server-sdk-typescript/src/goals.ts`: return when `run.result !== null || run.error !== null`.

Keep as a documentation ask. Not a new service defect.

## XR-005 — Python SDK source visibility (still stale)

https://docs.heycall-e.com/sdks table: Python repository “Not currently public.”

`gh repo view CALLE-AI/server-sdk-python`: `visibility: PUBLIC`, `isPrivate: false`.

Docs table fix. Tournament P5, still true.

## XR-006 — Dates table vs Official Rules (still stale)

Live Devpost schedule (2026-09-13, GMT+5:30):

| Period | Begins | Ends |
|---|---|---|
| Submissions | 23 Jul 19:00 IST | 14 Sep 21:15 IST |
| Judging | 30 Sep 06:30 IST | 13 Oct 14:30 IST |
| Winners | 19 Oct 11:30 IST | — |

No Feedback Period row. Rules §1: Feedback through 18 Sep 23:45 SGT; judging starts 10:00 SGT (not 09:00 SGT / 06:30 IST). Rules prevail.

## Keep from OffHire (do not upgrade provenance)

FB-001 identifier F/S after readback. FB-003 contradiction vs summary. FB-004 top-level `queued` during attempt. One call, 2026-09-05, Python SDK 0.7.0.

## Do not refile as discoveries

109 (CLI name collision), 123 (mid-call tools), 126 (as a new bug — add Cursor-skill evidence only), 127 (as a new bug — we only confirm), 90/116/118/121 (regions), unsigned webhooks as an exploit, pharmacy `next_step` type without our payload.
