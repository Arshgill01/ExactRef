# Evening re-verify — 2026-09-13

No Google Form submit. No Discord post. No live phone call. No tokens or numbers.

Sources used: GitHub `CALLE-AI/call-e-integrations` `main` at `4a53b01` (2026-09-10), not the local clone (stale at `e497e1a`, 2026-08-27). Official MCP guide, Cursor skill, and skills.sh skill read from `raw.githubusercontent.com` / `docs.heycall-e.com` / `www.skills.sh`. Python repo via `gh repo view`.

One claim in this morning’s packet is stale. The rest of the survey text still holds.

## Changed

**XR-002 gap 4 is closed on current main.** Morning note cited Cursor skill **v0.1.1** and said it allows `npx -y @call-e/cli`. Published `@call-e/cursor-plugin@0.1.2` (release #96, 2026-09-10) forbids bare `calle` and `npx`, and routes CLI fallback through `scripts/run-agent-command.mjs`. skills.sh still forbids remote npm. Do not keep the npx contrast in Q-10/Q-11.

Still true after 0.1.2 (do not drop these):

1. No untrusted-output boundary on the Cursor copy. skills.sh still marks summary/transcript untrusted.
2. Cursor terminal template still reads `<post_summary or summary or message>` and `<transcript>` at the top level. [Issue 126](https://github.com/CALLE-AI/call-e-integrations/issues/126) is still open; those fields sit under `result{}` on COMPLETED.
3. Cursor still says “Do not ask for a second confirmation between `plan_call` and `run_call`.” Official MCP safety still says only run when the user clearly intends.

Cite Cursor **0.1.2**, not 0.1.1.

## Still true

- **#127 unfixed.** Issue open. Latest `packages/cli/lib/cli.js`: `callCallStage` throws on `result?.isError === true`; generic `handleMcpCommand` `mcp call` always writes `mcpSuccessPayload` (`ok: true`) and returns 0. CLI changelog tops out at 0.5.1; no isError-exit fix.
- **`track_ui_events` omitted.** [openagent-oauth.md](https://github.com/CALLE-AI/call-e-integrations/blob/main/docs/mcp/openagent-oauth.md) expected set is still `plan_call`, `run_call`, `get_call_run`. README still says “three tools.” Cursor readiness still checks those three. No `track_ui_events` string in those files on `main`.
- **Python source visibility.** https://docs.heycall-e.com/sdks table: “Not currently public.” `CALLE-AI/server-sdk-python` is `PUBLIC` / `isPrivate: false`.
- **Calls vs Goal wait.** TypeScript 0.7.0 source unchanged: Calls `waitForResult` returns on top-level `completed|failed|canceled`; Goal waits until `result !== null || error !== null`. No SDK release after 2026-09-03.
- **Live-call items (OffHire, 2026-09-05, one call).** FB-001 identifier F/S. FB-003 contradiction vs summary. FB-004 top-level `queued`. Do not upgrade provenance.
- **XR-006 dates table.** Not re-fetched this evening. Morning Devpost vs Rules gap still the working claim unless someone re-opens Devpost.

## Changelog since 2026-09-07 — does not retract filings

https://docs.heycall-e.com/changelog **September 10, 2026**:

- Windows agent commands / multiline goals (#111, #159)
- “Reliable CLI selection” (#109) — agent launcher, not a new finding for us
- “Structured MCP results” (#158) — `structuredContent` vs parsing JSON text blocks. Not the `result{}` envelope in issue 126

September 7 notes (failure reporting, Dashboard Call Records, KYC) do not touch identifier capture, `queued`, wait predicates, `track_ui_events`, or `mcp call` exit codes.

[#109](https://github.com/CALLE-AI/call-e-integrations/issues/109) is **closed** (2026-09-10). Shared binary name remains deferred on `server-sdk-typescript#20`. Still do not refile 109; do not imply it is an open integrations bug.

## Do not file

109 (closed; launcher shipped), 123 (mid-call tools; maintainer said do not repurpose `track_ui_events`), 126 as a new bug (cite Cursor-skill evidence only), 127 as a new bug (confirm only), 90/116/118/121 (regions), unsigned webhooks as a live incident, pharmacy `next_step` without our payload, `track_ui_events` as a security incident.

## Packet edit if you refresh paste-ready

- Drop “Cursor allows `npx`.”
- Keep Q-10 items 4–6 (fourth tool, untrusted/`result{}`, #127).
- Keep Q-11 Python-repo and MCP envelope asks.
