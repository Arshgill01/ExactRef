# Docs lab rollup — 2026-09-14

No live CALL-E call. No form submit. No Discord. No PR opened.

Sources: live `docs.heycall-e.com` (including `.md` mirrors), `CALLE-AI/calle-docs` on GitHub `main` (local clone at `b387e01` is stale vs live `d4ef306`), `gh` on `server-sdk-python` / `server-sdk-typescript` / `call-e-integrations` / `calle-docs`, Devpost homepage + `/details/dates` + `/rules` HTML, extra-calls form GET only.

September 7 and 10 changelog entries do not retract identifier capture, `queued`, wait predicates, `track_ui_events`, `mcp call` `isError`, or issue 126. #158 is `structuredContent` vs text blocks, not `result{}`.

Unsigned webhooks: live `/webhooks` already says no secret, timestamp, or signature. awesome#209 merged 2026-08-24. Not a new incident.

## File index

| File | Kind | One-line |
| --- | --- | --- |
| [CONFIRM-XR-005.md](CONFIRM-XR-005.md) | confirm | Live `/sdks` still says Python source “not currently public”; repo is PUBLIC today |
| [CONFIRM-XR-006.md](CONFIRM-XR-006.md) | confirm | Dates table still omits Feedback (Rules: 18 Sep 23:45 SGT); judging 9:00 vs 10:00 SGT |
| [XR-301-playwright-locks-python-private.md](XR-301-playwright-locks-python-private.md) | new | `tests/docs-site.spec.ts` asserts the false Python-private cell |
| [XR-302-queued-means-idle.md](XR-302-queued-means-idle.md) | new | Live Calls table: `queued` = “The call task is queued.” |
| [XR-303-timeout-is-not-cancel.md](XR-303-timeout-is-not-cancel.md) | new | 120s wait examples; timeout does not hang up; default is 600s |
| [XR-304-identifier-schema-valid-overclaim.md](XR-304-identifier-schema-valid-overclaim.md) | new | Schema-valid `confirmation_code` presented as validated extraction |
| [XR-305-extra-calls-form-noon.md](XR-305-extra-calls-form-noon.md) | new | Form: 14 Sep 12pm SGT; Rules: 14 Sep 11:45pm SGT + 1–5 business days |
| [XR-306-changelog-structured-mcp-not-result-envelope.md](XR-306-changelog-structured-mcp-not-result-envelope.md) | new | Changelog #158 “fields directly” vs open 126 `result{}` |

Still true, not refiled as XR-3xx: XR-001 three-vs-four tools, XR-002 Cursor vs skills.sh / top-level summary, XR-003 `mcp call` `isError`, XR-004 Calls vs Goal `waitForResult` predicates.

## Ranked doc lies that cause a wrong write or a duplicate call

1. **XR-304 — schema-valid identifier is writable.** Live Calls: “CALL-E validates the structured result against it before returning the terminal call task state.” Appointment pattern requires `confirmation_code`. One live call (FB-001) substituted a character after readback + yes. **Wrong write.**

2. **XR-302 — `queued` means idle.** Live table: “The call task is queued.” FB-004: top-level `queued` during attempt activity. Agent creates again. **Duplicate call.**

3. **XR-303 — 120s timeout means the call ended.** Live examples use `timeoutMs: 120_000`. SDK throws locally, does not cancel, default 600s. One live result took ~4m39s. Agent POSTs a replacement. **Duplicate call.**

4. **XR-004 (owned) — same method name, different predicates.** Calls `waitForResult` returns on `completed\|failed\|canceled`. Goal waits until `result` or `error` is non-null. Live Goal page documents the Goal rule. Live Calls page says only “simple server-side polling.” Copying Goal’s “status completed ⇒ write `result`” onto Calls, or Calls’ status wait onto Goal, yields a null or premature write.

5. **XR-306 + XR-002 — changelog + Cursor template skip `result{}`.** “Access their fields without parsing JSON from text blocks (#158)” plus Cursor `[Call Summary] <post_summary or summary or message>` at the top level. Issue 126 still open. Agent writes an empty or invented identifier. **Wrong write.**

6. **XR-001 (owned) — docs say three tools; `tools/list` has returned four.** Readiness that stops at `plan_call` / `run_call` / `get_call_run` still leaves `track_ui_events` callable. Not re-listed this lab (no `mcp tools` this turn). Still the contract that sends an agent at an undocumented tool.

## Also true, weaker for write/duplicate

- **CONFIRM-XR-005 + XR-301.** Python source is public; page and Playwright say it is not. Causes skipped source reading (feeds #3), not a write by itself. The test lock is why the page lie survives a docs PR.
- **CONFIRM-XR-006.** Missing Feedback row through 18 Sep 23:45 SGT. Contest clock, not a call write.
- **XR-305.** Form noon SGT vs Rules 23:45 SGT + 1–5 business days. Last-day lockout. Can push a team into a rushed second create if they are out of free calls.

## Docs PR outlines (parent decides; none opened)

| Finding | File | Sentence to change |
| --- | --- | --- |
| XR-005 | `calle-docs` `content/guides/sdks.mdx` | “source repository is not currently public” → link `CALLE-AI/server-sdk-python` |
| XR-301 | `calle-docs` `tests/docs-site.spec.ts` | Drop expects for “Not currently public” / zero Python repo links; assert the public link |
| XR-302 | `calle-docs` `content/guides/calls.mdx` | `queued` meaning “The call task is queued.” → “may include an active attempt; do not create again” |
| XR-303 | `calls.mdx` + `sdks.mdx` | After `timeoutMs: 120_000`: “local poll only; does not cancel; do not POST a replacement” |
| XR-304 | `calls.mdx` Structured results | After “validates the result”: schema-valid ≠ independently verified |
| XR-004 | `calls.mdx` Polling | Side-by-side: Calls waits on terminal `status`; Goal waits on non-null `result`/`error` |
| XR-306 | `changelog.mdx` Sep 10 | After #158: not the `result{}` nest; cite 126 |
| XR-006 | Devpost dates table | Add Feedback through 18 Sep 23:45 SGT; judging begins 10:00 SGT |
| XR-305 | Extra-calls form + Devpost blurb | Print noon form cutoff next to Rules 23:45 SGT and 1–5 business days |

Prefer outlines only. Open a calle-docs PR only if the parent is sure and the test + prose land together.
