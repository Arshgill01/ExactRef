# CONFIRM-XR-006 — Devpost dates table still omits Feedback Period; judging start disagrees with Official Rules

Fetched 2026-09-14. No live CALL-E call. No form submit. No Discord.

## Finding

The live Devpost schedule table still has no Feedback Period row. Official Rules §1 still close Feedback on 18 September 23:45 SGT. The table’s judging start is one hour earlier than the Rules.

## Surface / version / commit or URL

- Schedule: https://call-e.devpost.com/details/dates (fetched 2026-09-14)
- Homepage clock: https://call-e.devpost.com/ — `Deadline: Sep 14, 2026 @ 11:45pm SGT`
- Official Rules HTML: https://call-e.devpost.com/rules (raw HTML, not a markdown converter)

## Expected

The dates table lists every period Official Rules §1 defines, with the same clock. Rules prevail over the marketing table.

## Actual

Live table (2026-09-14):

| Period | Begins | Ends |
| --- | --- | --- |
| Submissions | July 23 at 9:30pm SGT | September 14 at 11:45pm SGT |
| Judging | September 30 at 9:00am SGT | October 13 at 5:00pm SGT |
| Winners Announced | | October 19 at 2:00pm SGT |

No Feedback Period row.

Live Official Rules §1 (HTML, 2026-09-14):

> Submission Period: July 23, 2026 (9:30 pm SGT) – September 14, 2026 (11:45 pm SGT)

> Feedback Period: July 23, 2026 (9:30 pm SGT) – September 18 (11:45 pm SGT) (“Feedback Period”).

> Judging Period: September 30, 2026 (10:00 am SGT) – October 13, 2026 (5:00 pm SGT)

Table judging begins **9:00am SGT**. Rules judging begins **10:00 am SGT**. Submission end on the table matches Rules (11:45 pm SGT). Some markdown fetches of `/rules` flip that `pm` to `am`; the HTML is `pm`.

## Evidence

- `curl` of `/details/dates` and `/rules` on 2026-09-14.
- Homepage `data-iso-date="2026-09-14T11:45:00-04:00"` labeled `11:45pm SGT` (11:45am EDT). That instant matches Rules submission end, not the extra-calls form noon cutoff (see [XR-305-extra-calls-form-noon.md](XR-305-extra-calls-form-noon.md)).
- Rules: “Feedback must be submitted during the Feedback Period.”

## Impact if an operator or agent trusted the current contract

An agent that reads only the dates table treats 14 Sep 23:45 SGT as the end of all contest work, including Most Valuable Feedback. Official Rules keep Feedback open through 18 Sep 23:45 SGT. The missing row is the false contract. The 9:00 vs 10:00 judging start is a second clock lie; less likely to cause a duplicate call, still a Rules mismatch.

## Ask (docs PR outline — Devpost, not calle-docs)

On https://call-e.devpost.com/details/dates add a row:

`Feedback | July 23 at 9:30pm SGT | September 18 at 11:45pm SGT`

Change Judging begins from `September 30 at 9:00am SGT` to `September 30 at 10:00am SGT`. Print “Official Rules prevail” next to the table.

## Do not claim

- Not a new XR-006. This is a 2026-09-14 re-fetch.
- Do not claim Official Rules say 11:45 **am** SGT. Live HTML says **pm**.
- Do not treat the extra-calls noon cutoff as this card; that is XR-305.
