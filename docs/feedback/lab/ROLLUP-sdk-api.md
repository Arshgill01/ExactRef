# ROLLUP — SDK / API contract lab

2026-09-14. No `POST /v1/calls`. No `run_call`. No form submit. No GitHub issues. No tokens, phones, or intended identifiers.

Surfaces read (offline):

| Tree | Version | HEAD |
|---|---|---|
| `/Users/arshdeepsingh/Developer/CallE/repos/server-sdk-typescript` | `@call-e/calle@0.7.0` | `36ee6f1` (2026-09-03) |
| `/Users/arshdeepsingh/Developer/CallE/repos/server-sdk-python` | `calle-ai==0.7.0` | `f7a4b82` (2026-09-04) |
| OpenAPI in both trees | `0.7.0` | byte-identical (`diff -q`) |

Public docs cross-check only: https://docs.heycall-e.com/calls, `/sdks`, `/webhooks`, `/goal-runs`.

## New files this pass

| File | One line |
|---|---|
| [XR-107-validation-invisible-on-get.md](XR-107-validation-invisible-on-get.md) | Webhook type `call.result_validation_failed` has no CallTask field; wait/GET look like extract-miss |
| [XR-108-cli-phone-is-recipient.md](XR-108-cli-phone-is-recipient.md) | CLI `--phone` × N → N recipients, not N numbers on one recipient |
| [XR-109-cli-wait-exit-zero-on-failed-call.md](XR-109-cli-wait-exit-zero-on-failed-call.md) | `calle calls create --wait` exits 0 on `failed`/`canceled`; Goals exit 1 |
| [XR-110-python-recipients-skip-phone-alias.md](XR-110-python-recipients-skip-phone-alias.md) | Python plural `recipients[]` skips `phone`→`phones`; TS maps every row |
| [XR-111-cursor-vs-after.md](XR-111-cursor-vs-after.md) | Same `next_cursor`, query names `cursor` vs `after`; EventList field optional |
| [XR-112-canceled-webhook-is-call-failed.md](XR-112-canceled-webhook-is-call-failed.md) | Docs: canceled tasks arrive as `call.failed`; branch on `data.status` |
| [XR-113-retry-after-ignored.md](XR-113-retry-after-ignored.md) | Goal `Retry-After` documented; both waiters ignore it |
| [XR-114-docs-context-missing-in-sdk.md](XR-114-docs-context-missing-in-sdk.md) | Docs reserve SDK `context`; 0.7.0 types have no such field |
| [XR-115-webhook-snake-vs-call-camel.md](XR-115-webhook-snake-vs-call-camel.md) | TS webhook `data` is wire CallTask; `calls.get` is camelCase `Call` |
| [XR-116-e164-min-length-drift.md](XR-116-e164-min-length-drift.md) | Calls phones regex allows one fewer digit than Goal `phone` |

## Top 5 by operator harm

1. **XR-107** — Polling `waitForResult` / GET cannot see validation failure. `completed` + `structured_result: null` is written as “no answer.” Webhook-only apps that handle `call.completed` never see the type. Contract test **forbids** `result_validation` on CallTask.
2. **XR-108** — Repeatable `--phone` starts extra real conversations. No public cancel after accept.
3. **XR-109** — CLI `--wait` exit 0 on failed/canceled Calls. `&&` scripts commit the failure.
4. **XR-111** — Wrong follow-up query name (`cursor` vs `after`) or omitted `next_cursor` → first page forever / silent stop. Distinct from XR-402 (live page-one we did not continue).
5. **XR-110** — TS→Python port of `recipients: [{ phone }]` 400s or drops the number on the batch path.

Runners-up: XR-112 (cancel paged as `call.failed`), XR-113 (429 / poll stampede on Goals), XR-115 (undefined `taskCompleted` on webhook `data`).

## CONFIRMED — do not rebrand

| ID | Still true in 0.7.0 / docs | Not a new card |
|---|---|---|
| FB-001..005 | One 2026-09-05 call. No second live call. | conversation / queued / stitch |
| gauntlet-001 / XR-004 | Calls wait = `completed\|failed\|canceled`. Goal wait = `result \|\| error` non-null. OpenAPI text matches both predicates. | wait predicates |
| gauntlet-002 | Calls wait reads top-level `status` only. | queued ≠ idle |
| gauntlet-003 | `fromApiCall` does not revalidate `structuredResult`. Extra keys forwarded. | not XR-107 |
| gauntlet-004 / XR-504 | No Calls cancel. Local `CalleTimeoutError` ≠ hangup. Goal wait has duration guards + abort; Calls wait does not. **Do not file the abort gap as new.** | timeout ≠ hangup |
| gauntlet-005 | CLI `--wait` tails `listEvents`; library wait only `get`s. Sticky empty-page cursor is XR-111, not a refile of this. | CLI richer than library |
| gauntlet-006 | SDK `recipient` / `phone` are client-only aliases. **Plural Python skip is XR-110, not this.** | alias exists |
| gauntlet-007 | Mapped `Call` turns stay `offset_seconds`. **Whole webhook envelope is XR-115.** | turn casing |
| XR-001 | Fourth MCP tool `track_ui_events`. | do not file as security |
| XR-002 | Cursor skill vs skills.sh (`result{}`, untrusted). | cite 126 |
| XR-003 | generic `mcp call` `ok: true` on `isError`. | cite 127 |
| XR-005 | https://docs.heycall-e.com/sdks still “Python … Not currently public.” Repo is public. | docs table |
| XR-006 | Devpost dates vs Official Rules Feedback Period. | rules prevail |
| XR-401 | Stitched evidence (same live call as FB-005). | OffHire |
| XR-402 | Live events page one = 100 rows, cursor present, `type` vs `status`. We did not follow the cursor. | not XR-111 |
| XR-501..504 | Completed nouns / MCP no `result_schema` / `result{}` nouns / CLI 15s ≠ hangup. | surfaces rollup |
| FB-DOC-001 / awesome#209 | Current deliveries unsigned; `verify`/`unwrap` deprecated. **CONFIRM only. Not a new incident.** | webhook trust |
| FB-DOC-002 | Schema-valid ≠ true. Illustrated by FB-001. | fold into FB-001 |

## Explicitly not new

- CLI wait tails events (gauntlet-005) unless the cursor **name** / optional-field hole (XR-111).
- Recipient singular alias (gauntlet-006) unless Python **list** skip (XR-110).
- Schema not revalidated after wait (gauntlet-003) unless **validation-failed type missing on GET** (XR-107).
- `context` “drop” as a runtime strip — the field is **absent** (XR-114), not stripped.
- Canceled-after-timeout (gauntlet-004 / XR-504).
- Unsigned webhook verify (awesome#209 merged).

## Patch order if a CALL-E engineer has one day

1. CallTask: `failure_code: result_validation_failed` when webhook type would be that (XR-107).
2. CLI: one recipient per `--phone` list **or** warn N recipients; exit 1 on Call `failed`/`canceled` (XR-108, XR-109).
3. Python: `_normalize_recipient` on each `recipients[]` item; strip extras (XR-110).
4. OpenAPI: require EventList `next_cursor`; one pagination query name or SDK iterators (XR-111).
5. Goal wait: honor `Retry-After` (XR-113). Docs: delete `context` sentence (XR-114); webhook example switch on `data.status` (XR-112); export `fromApiCall` for webhook `data` (XR-115); align E.164 regexes (XR-116).
