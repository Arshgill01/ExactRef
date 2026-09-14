# XR-111 — `next_cursor` is not a portable page token (`cursor` vs `after`)

## Finding

Both list resources return `next_cursor`. The next request’s query name is **not** the same. Events want `cursor`. Goals want `after`. A generic “pass `next_cursor` as `cursor`” helper works for events and **replays page one forever** on Goals. The inverse (`after` on events) is ignored; the client never leaves the first events page.

This is the SDK/OpenAPI contract hole. It is not XR-402 (live page-one was 100 rows with a nonempty cursor; we did not follow it).

## Surface / version / commit or URL

- OpenAPI 0.7.0 `GET /v1/calls/{call_id}/events` query `cursor`; `GET /v1/goals` query `after`
- Both list schemas: response field `next_cursor`
- TypeScript `36ee6f1` `CalleCalls.listEvents` / `CalleGoals.list`
- Python `f7a4b82` `list_events` / `list`
- Public Goal guide: https://docs.heycall-e.com/goal-runs — “pass `next_cursor` unchanged as `after`”
- Public Calls guide events example: `listEvents(..., { limit: 50 })` — no `cursor` follow-up

## Expected

One pagination pair (`cursor` / `next_cursor`) on both lists, **or** a typed SDK helper (`listEventsPages`, `listGoalPages`) that cannot mix the names. Docs would show both follow-up calls side by side.

## Actual

Goal OpenAPI: “Use `next_cursor` as the next request's `after` value.”

Event OpenAPI: query parameter name is `cursor`. “Cursor returned by the previous event page.”

SDK is correct when you use the right method:

- TS `listEvents({ cursor })` / `list({ after })`
- Py `list_events(cursor=)` / `list(after=)`

There is no iterator. Public Calls docs stop at one `listEvents` call with `limit: 50`.

`EventList.next_cursor` is **not required**. `GoalList.next_cursor` **is required**. If the events page omits the field, TS maps `next_cursor ?? null` and clients stop. That is silent truncation, not the XR-402 live “cursor was present.”

Official CLI fixture (`tests/cli.test.ts`): a **later empty page still has `nextCursor: "2-0"`** (same token). OpenAPI text: “`null` means there are no more events.” Those two contracts disagree. A `while (next_cursor)` loop on a sticky tail token never terminates; an `if (!data.length) break` loop misses later events.

CLI `printNewEvents` fetches **one** page per poll (`limit: 100`) and only writes `state.cursor` when `nextCursor !== null`. That is gauntlet-005’s tail, plus this token-name / optional-field trap.

## Evidence

- `openapi/calle.openapi.yaml` Event query `cursor` vs Goal parameter `GoalListAfter` (`after`)
- `EventList` `required: [object, data]` — `next_cursor` optional
- `GoalList` `required: [object, data, next_cursor]`
- `server-sdk-typescript/src/calls.ts:245-266`, `182-187`
- `server-sdk-typescript/src/goals.ts:64-66`, `169-176`
- `server-sdk-python/src/calle/calls.py:46-48`
- `server-sdk-python/src/calle/goals.py:20-24`
- `server-sdk-typescript/src/cli.ts:310-334`
- `server-sdk-typescript/tests/cli.test.ts:50-54` (`emptyEvents.nextCursor === "2-0"`)
- https://docs.heycall-e.com/calls polling snippet (single `listEvents`, no loop)

## Impact if an operator or agent trusted the current contract

Copy-paste paginator from Goals onto events: first 50/100 events forever; hangup and post-call rows never appear (same operational miss as XR-402, different cause). Copy-paste from events onto Goals: first Goal page forever; later published Goals never run. Optional omitted `next_cursor` on a full events page stops the client early.

## Ask

1. Require `next_cursor` on `EventList` (null when done), matching `GoalList`.
2. Rename one query param so both lists use the same follow-up name, **or** export `iterateEvents` / `iterateGoals` that cannot mix `cursor` and `after`.
3. Document the CLI empty-page + sticky cursor as a tail token, or stop returning a non-null cursor when `data` is empty.

## Do not claim

- That we followed a live second page (XR-402: we did not).
- A rate of truncated logs.
- Refile of XR-402, gauntlet-005, or FB-004.
- Refile of 109 / 123 / 126 / 127.
