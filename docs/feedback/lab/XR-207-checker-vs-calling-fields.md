# XR-207 — Plugin checker accepts wrong `extracted.calling` field names

## Finding

CLI fixtures and timestamp localization use `result.extracted.calling.started_at` and `ended_at`. skills.sh / Codex / Claude / OpenClaw command templates use those names. PR 129’s Cursor `SKILL.md` (the 126/`result{}` fix) tells the agent to read `result.extracted.calling.start` and `.end`.

The PR 129 checker requires only the substring `result.extracted.calling`. It passes. Published `@call-e/cursor-plugin@0.1.2` (`4a53b01`) still uses the vague `<start/end time>` slot and does not mention `started_at`. Neither checker pins the live fixture keys.

This is not a restatement of issue 126 / XR-002 (top-level `summary` vs `result.summary`). Those fields are a different path. This is the **details clock** after the envelope is already nested correctly.

## Surface / version / commit

- CLI localize + tests: `call-e-integrations` `4a53b01` / `f0c9cf5` — `started_at`, `ended_at` only
- PR 129 `call-e-integrations-plugin` `560d61c` — `packages/cursor-plugin/plugin/skills/calle/SKILL.md` Time line
- PR 129 `scripts/check-plugin.mjs` `assert(source.includes("result.extracted.calling"))`
- `4a53b01` checker: no `extracted.calling` assertion at all
- skills.sh `skills/calle/references/commands.md` on the same PR: `started_at and ended_at`

## Expected

Skill templates use the same keys the CLI prints. The checker fails the package if Time/Duration/Callee slots do not match `started_at`, `ended_at`, `duration_seconds`, `to_phones[0]`.

## Actual

PR 129 Cursor template:

```text
Time: <result.extracted.calling.start or result.extracted.calling.end or Not available>
```

CLI (and existing tests):

```javascript
if (Object.hasOwn(calling, "started_at")) {
  calling.started_at = formatIsoTimestampInTimezone(calling.started_at, timezone);
}
if (Object.hasOwn(calling, "ended_at")) {
  calling.ended_at = formatIsoTimestampInTimezone(calling.ended_at, timezone);
}
```

Checker (PR 129) green if the file merely contains `result.extracted.calling`.

Published 0.1.2 Cursor template still says `<start/end time or Not available>` at the Details layer and `<post_summary or summary or message>` at the top level (the latter is 126/XR-002 — cite only).

## Evidence (local / offline)

Fixture already in `packages/cli/test/cli.test.js`:

```json
{
  "result": {
    "extracted": {
      "calling": {
        "started_at": "2026-05-20T09:32:10.000Z",
        "ended_at": "2026-05-20T16:01:02.000Z"
      }
    }
  }
}
```

After `--timezone Asia/Shanghai` the CLI rewrites those two keys. There is no `start` / `end`. An agent following PR 129 prints `Not available` for Time and may invent a clock from `activity[].ts` or from untrusted summary text.

## Impact if an operator or agent trusted the current contract

**Wrong write.** Operator copies “Not available” or a guessed local time into a record. Identifier provenance is not the issue here; the call’s time window is. A checker-green publish will not catch it.

## Ask

Pin `started_at` and `ended_at` in `check-plugin.mjs` and in the Cursor Time slot. Align with skills.sh. Do not treat `includes("result.extracted.calling")` as enough.

## Do not claim

126/`result.summary` as a new bug (cite only). That published 0.1.2 already has the `start`/`end` typo — that typo is on the PR branch. Live `tools/list` schema for `extracted.calling`.
