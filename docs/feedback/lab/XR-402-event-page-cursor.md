# XR-402 — First events page is 100 rows, `queued`, and not the hangup

OffHire exception `OH-01` only.

## Finding

The live run’s event snapshot is page one only: 100 events, nonempty `next_cursor`, every event `status` is `queued`, including three `type: call.in_progress`. The page ends about two minutes before attempt hangup. Evaluation used the complete 53-turn terminal transcript, not this page. ExactRef `PASTE_READY` mentioned poll-until-terminal, not the cursor or the type/status split.

## Surface / version / commit or URL

GET `/v1/calls/{id}/events`, 2026-09-05. Python SDK 0.7.0 exposes `list_events(call_id, cursor=, limit=)`. The live runner did not call it; events were fetched once as a snapshot. TypeScript `@call-e/calle` 0.7.0 `listEvents` exists; `waitForResult` does not tail it.

## Expected

Either:

- event `status` tracks attempt activity, or
- docs say `type` is the activity signal and `status` may remain the top-level task status, and
- page one is not a complete log; clients must follow `next_cursor` through hangup and post-call materialization.

## Actual

Sanitized shape (no ids, no messages, no destination):

| Field | Value |
|---|---|
| `object` | list |
| `data.length` | 100 |
| `next_cursor` | present, nonempty |
| event `status` | `queued` × 100 |
| event `type` | `call.started` × 1, `call.in_progress` × 3, `call.updated` × 96 |
| `details` | empty object on all 100 |
| first event time | ~11s after create |
| last event on this page | ~2m22s before attempt `completed_at` |

GET polls in the same window: top-level `queued` while recipient/attempt were `in_progress` (see FB-004). The first events page never reaches `completed`.

## Evidence

- OffHire FB-004 card already notes “first 100 events; continuation cursor.”
- Audit `events-private.json` hash recorded in the private audit; not copied here.
- 23 GET polls: 22 `queued`, 1 `completed`.
- Python `list_events` accepts `cursor` and `limit`. Unused on the live path.
- Gauntlet LC05 (offline): waiter ignores events; not a second live page.

## Impact if an operator or agent trusted the current contract

A client that treats page one as the wait log will miss hangup and post-call extraction. A client that treats event `status` as attempt state will conclude the call is idle while `type` says `call.in_progress`. That is the same false-idle trap as top-level `queued`, one layer down.

## Ask

On the events guide: default page size, that `next_cursor` means “not done,” and that `type` / `status` can disagree (`call.in_progress` + `queued`). Optional: `onEvent` on Calls wait, which CLI `--wait` already approximates in the TypeScript package.

## Do not claim

- That we followed the cursor to a second page (we did not).
- A rate of truncated logs.
- Unsigned webhooks as a live incident.
- Refile of 109 / 123 / 126 / 127.
