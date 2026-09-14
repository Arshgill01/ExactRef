# XR-306 — Changelog “Structured MCP results” is #158; issue 126 `result{}` is still open

New public-changelog lock. Cite 126; do not refile it. Distinct from XR-002 (Cursor skill template).

## Finding

The live What’s New entry for 10 September 2026 says planning, execution, and status tools “now return structured results directly, so MCP integrations can access their fields without parsing JSON from text blocks (#158).” An agent that reads that sentence treats `get_call_run` summaries as top-level fields. Issue 126 is still **open** (updated 2026-09-14): COMPLETED payloads nest those fields under `result{}`. The official Cursor skill still reads `<post_summary or summary or message>` and `<transcript>` at the top level.

## Surface / version / commit or URL

- Live: https://docs.heycall-e.com/changelog and `/changelog.md` (September 10, 2026)
- calle-docs `main` commit `d4ef306` (2026-09-12) “docs: add September 10 release notes”
- https://github.com/CALLE-AI/call-e-integrations/issues/126 — `OPEN` on 2026-09-14
- Cursor skill on `main`: `packages/cursor-plugin/plugin/skills/calle/SKILL.md` v0.1.2
- skills.sh skill: `skills/calle/SKILL.md` (reads `result.structuredContent`)

## Expected

Changelog names #158 as `structuredContent` vs JSON text blocks, and says it does not move `summary` / `transcript` out of `result{}`. Cursor template reads `result.summary` / `result.transcript`.

## Actual

Live changelog sentence:

> Structured MCP results: Call planning, execution, and status tools now return structured results directly, so MCP integrations can access their fields without parsing JSON from text blocks (#158).

Issue 126 title (still open, 2026-09-14):

> docs(mcp): tool-call auth needs the CLI token, and get_call_run nests fields under result{}

Cursor skill terminal template (GitHub `main`, 2026-09-14):

```text
[Call Summary]
<post_summary or summary or message>
…
[Transcript]
<transcript or Not available.>
```

skills.sh (same day) labels those strings untrusted and reads `status_result.structuredContent` / `result.structuredContent`.

September 7 changelog (failure reporting, Dashboard Call Records, KYC) does not mention `result{}`, `queued`, wait predicates, or `track_ui_events`.

## Evidence

- Live `/changelog.md` fetched 2026-09-14.
- `gh issue view 126 --repo CALLE-AI/call-e-integrations` → `state: OPEN`, `updatedAt: 2026-09-14T04:27:57Z`.
- Raw Cursor and skills.sh SKILL.md from `CALLE-AI/call-e-integrations` `main` (`019478e`, 2026-09-14).

## Impact if an operator or agent trusted the current contract

**Wrong write / empty success.** Agent sees COMPLETED, changelog said fields are “direct,” reads top-level `summary` as missing, invents a confirmation, or writes a transcript instruction as a command. The nested `result{}` identifier is the one that would have been compared.

## Ask (docs PR outline — do not open unless parent decides)

In `content/guides/changelog.mdx` September 10, after the #158 sentence, add:

> This is `structuredContent` vs parsing JSON text blocks. It does not move `summary` / `transcript` out of `result{}` on `get_call_run` (see issue 126).

In the Cursor skill (integrations, not calle-docs): read `result.summary` / `result.transcript`; add the skills.sh untrusted boundary. Cite 126; do not open a second issue.

## Do not claim

- Do not refile 126 or 127. Do not call #158 a no-op; it is a different envelope.
- Do not treat `track_ui_events` as a new incident (XR-001).
- No live MCP `tools/call` this lab. No phone call.
