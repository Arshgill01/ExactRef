# XR-205 — `timezone_offset_minutes` sign, no `ttl_seconds`, undocumented token lifetimes

## Finding

Three lifetime / clock contracts that agents will misread as “safe to reuse” or “already localized”:

1. `plan_call` `_meta.timezone_offset_minutes` for Asia/Shanghai is **-480**. Display code later **negates** that value to print `+08:00`. The field is JS-style (UTC minus wall), not ISO UTC offset minutes. Official MCP does not define the field.
2. Official MCP documents `ttl_seconds` on `plan_call` and `run_call`. CLI `buildPlanArguments` / `buildRunArguments` never send it. There is no `--ttl-seconds`. Retention of `plan_id`, `confirm_token`, and `run_id` is therefore whatever the server default is — unpublished.
3. Local recovery files store `plan_id` + `confirm_token` with **no expiry**. `auth status` `usable` / `expires_at` is a **local cache read**. It does not ping MCP. Login verifies the token once; status never does.

## Surface / version / commit

- `packages/cli/lib/cli.js` `timezoneOffsetMinutes`, `formatIsoTimestampInTimezone`, `buildPlanRequestMeta` — `f0c9cf5` / `4a53b01`
- `packages/cli/lib/cache.js` `writeCallRecovery` — `schema_version: 1`, `created_at`, no `expires_at`
- `packages/core/lib/cache.js` `tokenIsUsable` — local `expires_at` only
- `statusPayload` — no `verifyCachedTokenWithMcp`
- Official MCP `ttl_seconds` bullets under `plan_call` / `run_call`

## Expected

Offset metadata uses a named convention (IANA only, or ISO minutes east of UTC). Plan/run TTL is settable or documented as “server default, confirm_token not reusable after N.” `auth status` either probes MCP or labels itself `local_cache_only`.

## Actual

Unit test `mcp call` / `call plan` timezone meta (Asia/Shanghai):

```json
{
  "_meta": {
    "openai/userLocation": { "timezone": "Asia/Shanghai" },
    "timezone_offset_minutes": -480
  }
}
```

Formatter:

```javascript
const offset = Math.round((instant.getTime() - wallClockAsUtc) / 60000); // -480
const localOffsetMinutes = -offsetMinutes; // +480 → +08:00
```

Recovery record written before `run_call`:

```json
{
  "schema_version": 1,
  "created_at": "<iso>",
  "plan_id": "<opaque>",
  "confirm_token": "<opaque>",
  "timezone": "Asia/Shanghai"
}
```

`auth status` fields: `usable`, `expires_at`, `cache_exists`. Copy in skills.sh after login offers a **test call** via `POST_AUTH_HELP_MESSAGE` (“place a test call first, or start a real call directly”).

## Evidence (local / offline)

- Test assertion `timezone_offset_minutes: -480` for `Asia/Shanghai` in `packages/cli/test/cli.test.js`
- `buildRunArguments` is only `{ plan_id, confirm_token }`
- `statusPayload` does not call `listMcpTools`
- MCP guide: “a `run_id` is not queryable indefinitely” but no number; `confirm_token` reuse “across plans” is forbidden, same-plan lifetime is not stated

## Impact if an operator or agent trusted the current contract

**Wrong time on the call or the write.** If the planner treats `-480` as UTC offset minutes, Shanghai becomes UTC−8. Scheduled `scheduled_at` (also not exposed on the CLI) would be eight hours off.

**Failed or duplicate later lookup.** Agent stores `run_id` / `confirm_token` and retries hours later. Server may have expired the plan (default TTL). Agent creates a new plan and `run_call` again.

**Stale `usable: true`.** Status shows a far-future `expires_at` (local cache). MCP 401s. Agent treats that as a new session and re-plans.

## Ask

Document `timezone_offset_minutes` as “JS getTimezoneOffset direction” or stop sending it (IANA in `openai/userLocation` is enough). Expose or document `ttl_seconds`. Put `local_only: true` on `auth status`. Add expiry to recovery records. Remove “place a test call first” from post-auth assistant copy.

## Do not claim

Live default TTL. That 2029-dated cache entries are refresh tokens (not inspected). Live timezone bug on a real plan.

## Prior art (added 2026-09-14 22:30 IST)

Related prior art: [calle-docs #42](https://github.com/CALLE-AI/calle-docs/issues/42) (open, cnpierrepapi) — attempt timestamps lose their timezone on failed calls. Point 1 of this card (`timezone_offset_minutes` sign) is the MCP-side twin; cite #42 as filed by others.
