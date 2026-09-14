# XR-603 — `ttl_seconds: 0` keeps the plan, run, transcript and phone number permanently; the guide never says so

New. 2026-09-14. XR-205 (no `--ttl-seconds`, undocumented default TTL) is cited, not refiled. XR-706 noticed a year-9999 `expires_at` on `ttl_seconds: 0` as an aside; this is the retention card.

## Finding

The live `plan_call` and `run_call` input schemas define `ttl_seconds` as `integer >= 0` with the description “Omit to use the server default; **set to 0 to keep records permanently**.” The official MCP guide describes the same field only as “optional retention TTL for plan and run records” and “choose a retention window long enough for monitoring.” It never states the zero semantics. The README does not mention retention at all.

A run record includes `result.transcript`, `result.extracted` (callee number, times), `display_goal`, and `activity[]`. An agent or operator that reads “TTL 0” as “no retention / delete immediately” — the common meaning in caches and DNS — gets the opposite: indefinite retention of a phone number and a conversation transcript.

The word “TTL” is already overloaded on the same CLI: `--min-ttl-seconds` (default 300) is the *token* lifetime check, unrelated to record retention.

## Surface / version / commit or URL

- Live `tools/list` 2026-09-14: `plan_call.inputSchema.properties.ttl_seconds`, `run_call.inputSchema.properties.ttl_seconds` (`minimum: 0`, description quoted above)
- `call-e-integrations` `1ce9d77` `docs/mcp/openagent-oauth.md` lines 180, 201, 242–244
- `packages/cli/docs/cli-reference.md` line 237 (`--min-ttl-seconds`)
- CLI `buildPlanArguments` / `buildRunArguments`: no `ttl_seconds` (XR-205)
- Live `plan_call` with no phone (planning only): default `expires_at` ≈ created + 24 h (one sample)

## Expected

The guide states: default retention (observed ≈24 h for a plan), that `0` means permanent, and how to delete a record early. A value that means “forever” is spelled `null` / omitted / a named constant, not `0`.

## Actual

Schema text (live):

```text
ttl_seconds: Optional retention TTL for this plan and its call run records, in seconds.
             Omit to use the server default; set to 0 to keep records permanently.
```

Guide text (`main`):

```text
- `ttl_seconds`: optional retention TTL for plan and run records.
```

No “permanent,” “delete,” “retention,” or “privacy” sentence in the guide or README (`rg -i "retention|permanent|delete|privacy"` → only the “not queryable indefinitely” paragraph).

## Evidence

- `/tmp/calle-lab/mcp-tools-pretty.json`
- `/tmp/calle-lab/plan-smoke.json`: `expires_at: 2026-09-15T13:34:54Z` for a plan created 2026-09-14 ~13:34 UTC
- Grep on `1ce9d77` as above

No `run_call`. No `ttl_seconds: 0` sent by this lab.

## Impact if an operator or agent trusted the current contract

Privacy/retention: a callee's number and full transcript are retained indefinitely on a misreading that is the *default* reading of “TTL 0” elsewhere. No documented delete path. For hackathon builders who promise callees “we do not keep the recording,” one flag makes that promise false. Secondary: operators who want short retention cannot set it from the CLI (XR-205) and do not know the default.

## Ask

In the guide and tool description: “Default retention is N; `ttl_seconds: 0` means **permanent**; there is no early-delete operation.” Preferably change the sentinel to `null` / `"permanent"` and reject `0`. Expose `--ttl-seconds` on `call plan|start` (XR-205 ask).

## Do not claim

That records were retained beyond `expires_at` (not observed). The server default for runs (only one plan sample). XR-205 as new. Refile of 109/123/126/127.
