# XR-907 — Live OpenAPI examples fail their own E.164 patterns; Redocly/Spectral error

## Finding

`npx @redocly/cli lint` and `@stoplight/spectral-cli lint` (ruleset `spectral:oas`) both flag the official examples: `"<RECIPIENT_1_E164_PHONE>"` / `"<E164_PHONE>"` do not match `^\+[1-9]\d{6,14}$` (Calls) or `^\+[1-9]\d{7,14}$` (Goals). Spectral: **2 errors**. Redocly: 4 `no-invalid-media-type-examples` warnings plus `info-license`. The spec is otherwise structurally identical to the published TS 0.7.0 OpenAPI (path/enum/required/nullable). `openapi-typescript` → `tsc --noEmit --strict` on the live spec: **clean**.

This is not XR-116 (two regex minima) and not XR-812 (Python example regex). It is the **spec’s own examples** being invalid against the spec.

## Surface / version / commit or URL

- `/tmp/calle-lab/live-openapi.yaml` `info.version: 0.7.0` (byte-identical to `/tmp/calle-lab/openapi.yaml`)
- TS git `server-sdk-typescript` `2808e21` spec still `0.7.0`; description-only drift vs live (`failure_code` “No published enum”, `CallId` wording)
- Python git spec `0.7.1` (XR-802) — same paths/enums as live 0.7.0

## Expected

Examples use values that pass the published patterns (e.g. `+15555550100` reserved) **or** `example` is a non-evaluated annotation. Lint is clean in CI.

## Actual

**Observed** Spectral:

```text
/tmp/calle-lab/live-openapi.yaml
  34:27  error  oas3-valid-media-example  "0" property must match pattern "^\+[1-9]\d{6,14}$"
 483:26  error  oas3-valid-media-example  "phone" property must match pattern "^\+[1-9]\d{7,14}$"
✖ 11 problems (2 errors, 9 warnings)
```

**Observed** generated client: `npx openapi-typescript live-openapi.yaml -o /tmp/calle-lab/gen.ts` then `tsc --noEmit --strict` → 0 errors.

**Observed** hand-written `@call-e/calle@0.7.0` `Call.structuredResult: JsonObject | null` matches generated `structured_result: { [key: string]: unknown } | null`. Wire `phones` vs client alias `phone` is intentional (gauntlet-006 / XR-110). CallStatus enums match (`queued|in_progress|completed|failed|canceled`) — no `NO ANSWER` in REST (that enum lives on MCP, XR-601).

`Idempotency-Key` is documented. No `x-request-id` / rate-limit header in the spec (XR-906).

## Evidence

Commands above. `oa-diff.py` live vs TS-git / Py-git: zero path or enum adds/removes.

## Impact if an operator or agent trusted the current contract

Copy-paste from the spec into `calls.create` sends a placeholder that 400s (Calls) or is one digit short of the Goal minimum (XR-116). Generator tests that validate examples fail, so teams disable the lint and miss real drift.

## Ask

Replace placeholder phones in all OpenAPI examples with `+15555550100`-style reserved numbers that satisfy **both** regexes, or mark those examples `x-ignore`. Add Spectral `oas` to the SDK `verify:openapi` script.

## Do not claim

That live create accepts the placeholder (not posted). Refile of XR-116 / XR-812 / XR-802.
